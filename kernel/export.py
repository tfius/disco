"""Export a world's threads as structured training episodes (JSONL).

One line per thread: the full predict->run->surprise->revise trajectory with
its outcome and mechanism reward. Positive/negative labels come from the gate
and verify, not from any judge's opinion — execution-anchored, high cost-to-fake.
"""
import json

from . import config, evolve


def _ledger_maps():
    """(thread, step) -> step entry; thread -> outcome entry."""
    steps, outcomes = {}, {}
    if not config.LEDGER.exists():
        return steps, outcomes
    for line in config.LEDGER.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind, thread = e.get("kind"), e.get("thread")
        if kind == "step":
            steps[(thread, e.get("step"))] = e
        elif kind in ("claim", "question", "noise"):
            outcomes[thread] = e  # last outcome-ish entry wins
    return steps, outcomes


def episodes(out_path=None):
    """Write episodes JSONL for the current world; returns (path, count)."""
    config.ensure_dirs()
    out_dir = config.ROOT / "exports"
    out_dir.mkdir(exist_ok=True)
    out_path = out_path or (out_dir / f"{config.WORLD}.jsonl")
    step_map, outcome_map = _ledger_maps()

    count = 0
    with open(out_path, "w") as out:
        for thread_dir in sorted(config.RUNS.iterdir() if config.RUNS.exists() else []):
            if not thread_dir.is_dir() or not (thread_dir / "step-1").exists():
                continue
            thread = thread_dir.name
            steps = []
            for i, sd in enumerate(sorted(thread_dir.glob("step-*"),
                                          key=lambda p: int(p.name.split("-")[1])), 1):
                step = {"n": i}
                pf, cf, rf = sd / "prediction.md", sd / "experiment.py", sd / "result.json"
                if pf.exists():
                    step["prediction"] = pf.read_text()
                if cf.exists():
                    step["code"] = cf.read_text()
                if rf.exists():
                    step["result"] = json.loads(rf.read_text())
                led = step_map.get((thread, i), {})
                for key in ("surprise", "judge_note", "confidence", "focus", "objective", "turn"):
                    if key in led:
                        step[key] = led[key]
                steps.append(step)
            if not steps:
                continue

            led_out = outcome_map.get(thread, {})
            ending = {"claim": "claim", "question": "question", "noise": "noise"}.get(
                led_out.get("kind"), "unknown")
            outcome = {"thread": thread, "ending": ending,
                       "admitted": bool(led_out.get("admitted")),
                       "parked": "unreplicated" in str(led_out.get("slug", ""))}
            surprises = [s["surprise"] for s in steps if "surprise" in s]
            # turn-level process reward: how much surprise this step closed
            prev = None
            for s in steps:
                if "surprise" in s:
                    s["process_reward"] = (prev - s["surprise"]) if prev is not None else None
                    prev = s["surprise"]
            first_led = step_map.get((thread, 1), {})
            episode = {
                "world": config.WORLD,
                "thread": thread,
                "agent": first_led.get("agent", "solo"),
                "steps": steps,
                "ending": ending,
                "slug": led_out.get("slug"),
                "admitted": outcome["admitted"],
                "reward": evolve.score(outcome),
                "mean_surprise": round(sum(surprises) / len(surprises), 2) if surprises else None,
                "closure": (surprises[0] - surprises[-1]) if len(surprises) >= 2 else None,
                "calibration": [[s.get("confidence"), s["surprise"]]
                                for s in steps if "surprise" in s],
                # trajectory-level filter labels: test-case-anchored, longitudinal
                "filters": {
                    "gate_passed": outcome["admitted"],
                    "verified_alive": bool(led_out.get("slug"))
                        and (config.CLAIMS / str(led_out.get("slug"))).exists(),
                    "closed_surprise": len(surprises) >= 2 and surprises[0] > surprises[-1],
                },
            }
            slug = led_out.get("slug")
            if ending == "claim" and outcome["admitted"] and slug:
                cd = config.CLAIMS / slug
                if (cd / "claim.md").exists():
                    episode["claim"] = (cd / "claim.md").read_text()
                if (cd / "check.py").exists():
                    episode["check"] = (cd / "check.py").read_text()
            tf = thread_dir / "messages.jsonl"
            if tf.exists():
                transcript = [json.loads(l) for l in tf.read_text().splitlines()]
                episode["transcript"] = transcript
                # turnkey loss mask, aligned 1:1 to transcript: train on every
                # assistant turn EXCEPT experiment turns whose committed assertions
                # were violated (a losing bet); system/user turns are never targets.
                # Default policy — a trainer can recompute from steps[].turn/objective.
                losing_turns = {s["turn"] for s in steps
                                if s.get("objective") == "violated" and "turn" in s}
                episode["loss_mask"] = [
                    m["role"] == "assistant" and i not in losing_turns
                    for i, m in enumerate(transcript)
                ]
            out.write(json.dumps(episode) + "\n")
            count += 1
    return out_path, count
