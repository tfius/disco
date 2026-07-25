"""Discovery-efficiency metrics: how surprise behaves and closes in a world.

First-contact surprise separates recall from discovery (documented worlds open
0-3, generated worlds 5-8); closure rate is the trainable quantity.
"""
import json
from collections import defaultdict

from . import config


def compute() -> dict:
    if not config.LEDGER.exists():
        return {}
    threads = defaultdict(list)   # thread -> [surprise per step, in order]
    endings = defaultdict(int)
    admitted = 0
    for line in config.LEDGER.read_text().splitlines():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("kind") == "step" and e.get("surprise") is not None:
            threads[e["thread"]].append(e["surprise"])
        elif e.get("kind") in ("claim", "question", "noise") and e.get("thread"):
            endings[e["kind"]] += 1
            if e.get("kind") == "claim" and e.get("admitted"):
                admitted += 1
    if not threads:
        return {}
    ordered = [threads[t] for t in sorted(threads)]
    all_s = [s for tr in ordered for s in tr]
    firsts = [tr[0] for tr in ordered if tr]
    multi = [tr for tr in ordered if len(tr) >= 2]
    closure = [tr[0] - tr[-1] for tr in multi]  # positive = surprise closed
    return {
        "threads": len(ordered),
        "steps": len(all_s),
        "endings": dict(endings),
        "admitted": admitted,
        "mean_surprise": round(sum(all_s) / len(all_s), 2),
        "mean_first_step_surprise": round(sum(firsts) / len(firsts), 2),
        "mean_closure": round(sum(closure) / len(closure), 2) if closure else None,
        "closed_threads": sum(1 for c in closure if c > 0),
        "first_contact_surprise": round(sum(ordered[0]) / len(ordered[0]), 2) if ordered[0] else None,
        "mean_steps_per_thread": round(len(all_s) / len(ordered), 2),
    }


def render(s: dict) -> str:
    if not s:
        return "(no threads yet)"
    lines = [
        f"threads: {s['threads']} ({s['steps']} steps, {s['mean_steps_per_thread']} steps/thread)",
        f"endings: {s['endings']} — {s['admitted']} claims admitted",
        f"surprise: mean {s['mean_surprise']}, first-step mean {s['mean_first_step_surprise']}, "
        f"first-contact thread {s['first_contact_surprise']}",
    ]
    if s["mean_closure"] is not None:
        lines.append(f"closure: mean {s['mean_closure']} per multi-step thread "
                     f"({s['closed_threads']} threads closed surprise)")
    return "\n".join(lines)
