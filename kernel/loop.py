"""The discovery loop: observe -> predict -> run -> surprise -> branch -> archive."""
import json
import re
import time

from . import archive, config, ledger, llm, prompts, world


class ParseError(Exception):
    pass


def _sections(text: str) -> dict:
    """Split '### HEADER\\n body' blocks into {header: body}."""
    parts = re.split(r"^###\s+([A-Z_]+)\s*$", text, flags=re.M)
    if len(parts) < 3:
        raise ParseError("no ### sections found")
    out = {}
    for header, body in zip(parts[1::2], parts[2::2]):
        out[header.strip()] = body.strip()
    return out


def _code(body: str) -> str:
    m = re.search(r"```(?:python)?\n(.*?)```", body, re.S)
    if m:
        return m.group(1)
    if body.strip():
        return body  # bare code without fences
    raise ParseError("empty code block")


def _experiment_fields(sec: dict) -> dict:
    for key in ("PREDICTION", "EXPERIMENT"):
        if key not in sec:
            raise ParseError(f"missing ### {key}")
    conf = re.search(r"\d+", sec.get("CONFIDENCE", "50"))
    return {
        "focus": sec.get("FOCUS", ""),
        "prediction": sec["PREDICTION"],
        "confidence": min(100, int(conf.group()) if conf else 50),
        "code": _code(sec["EXPERIMENT"]),
    }


def _syntax_error(code: str):
    try:
        compile(code, "experiment.py", "exec")
        return None
    except SyntaxError as e:
        return f"SyntaxError: {e.msg} (line {e.lineno})\n{(e.text or '').rstrip()}"


def _repair_syntax(messages, code: str, on_event, max_repairs: int = 2):
    """Compile before execution; bounce SyntaxErrors back without burning a step
    or polluting the surprise signal. Returns runnable code or None."""
    for attempt in range(max_repairs + 1):
        err = _syntax_error(code)
        if err is None:
            return code
        if attempt == max_repairs:
            return None
        on_event(f"  syntax error — repair {attempt + 1}/{max_repairs}")
        messages.append({"role": "user", "content": prompts.SYNTAX_REPAIR.format(error=err)})
        resp = llm.chat(messages)
        messages.append({"role": "assistant", "content": resp})
        sec = _sections(resp)
        if "EXPERIMENT" not in sec:
            raise ParseError("repair reply missing ### EXPERIMENT")
        code = _code(sec["EXPERIMENT"])


def _ask(messages, parser):
    """One model call; on parse failure, feed the error back once."""
    resp = llm.chat(messages)
    try:
        return resp, parser(resp)
    except ParseError as e:
        messages.append({"role": "assistant", "content": resp})
        messages.append({"role": "user", "content": prompts.FORMAT_RETRY.format(error=e)})
        resp = llm.chat(messages)
        return resp, parser(resp)  # second failure propagates


def judge_surprise(prediction: str, confidence: int, result: dict) -> dict:
    """Separate judge call, fresh context — no memory of the agent's reasoning."""
    raw = llm.chat(
        [
            {"role": "system", "content": prompts.JUDGE_SYSTEM},
            {"role": "user", "content": prompts.JUDGE_USER.format(
                confidence=confidence,
                prediction=prediction,
                result=world.format_result(result),
            )},
        ],
        temperature=config.JUDGE_TEMPERATURE,
        max_tokens=200,
    )
    surprise, note = llm.json_score(raw, "surprise", default=5)
    return {"surprise": surprise, "note": note}


def run_thread(thread_id: str = None, on_event=print) -> dict:
    """One thread: up to MAX_STEPS experiments, ends in CLAIM/QUESTION/NOISE/exhausted."""
    config.ensure_dirs()
    thread_id = thread_id or time.strftime("%Y%m%d-%H%M%S")
    thread_dir = config.RUNS / thread_id

    system = prompts.KERNEL_SYSTEM.format(
        world=config.world_description(),
        archive_index=archive.index(),
        ledger_tail=ledger.tail(for_agent=True),
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompts.OPEN_THREAD},
    ]

    trajectory = []
    focus = ""
    outcome = {"thread": thread_id, "ending": "exhausted", "steps": 0}

    for step in range(1, config.MAX_STEPS + 1):
        parser = (lambda r: _experiment_fields(_sections(r))) if step == 1 else _parse_decision
        try:
            resp, parsed = _ask(messages, parser)
            messages.append({"role": "assistant", "content": resp})

            if step > 1:
                decision, payload = parsed
                _bank_tool(payload, thread_id, on_event)
                if decision == "CLAIM" and len(trajectory) < config.MIN_CLAIM_EXPERIMENTS:
                    # replication gate: one observation is an anecdote — bounce once
                    on_event("  claim refused — replication required")
                    messages.append({"role": "user", "content": prompts.REPLICATE.format(
                        n=len(trajectory), min=config.MIN_CLAIM_EXPERIMENTS)})
                    resp, (decision, payload) = _ask(messages, _parse_decision)
                    messages.append({"role": "assistant", "content": resp})
                    _bank_tool(payload, thread_id, on_event)
                    if decision == "CLAIM":  # insists — park it, kernel does not bend
                        title = payload["claim"].strip().splitlines()[0][:80]
                        slug = archive.save_question(
                            "unreplicated: " + title,
                            payload["claim"] + "\n\nproposed check:\n```python\n"
                            + payload["check"] + "\n```", thread_id)
                        ledger.log("question", thread=thread_id, slug=slug,
                                   reason="premature claim parked")
                        on_event(f"  premature claim parked as question: {slug}")
                        outcome.update({"ending": "question", "slug": slug, "steps": step - 1})
                        return outcome
                if decision != "CONTINUE":
                    outcome.update(_finish(decision, payload, thread_id, trajectory, focus, on_event))
                    outcome["steps"] = step - 1
                    return outcome
                parsed = payload  # experiment fields for the next probe

            code = _repair_syntax(messages, parsed["code"], on_event)
        except ParseError as e:
            ledger.log("noise", thread=thread_id, focus=focus, reason=f"unparseable after retry: {e}")
            on_event(f"  thread abandoned — unparseable response: {e}")
            outcome["ending"] = "parse-failure"
            return outcome
        if code is None:
            ledger.log("noise", thread=thread_id, focus=focus, reason="syntax repairs exhausted")
            on_event("  thread abandoned — syntax repairs exhausted")
            outcome["ending"] = "syntax-failure"
            return outcome

        focus = parsed.get("focus") or focus
        step_dir = thread_dir / f"step-{step}"
        result = world.run_python(code, step_dir)
        verdict = judge_surprise(parsed["prediction"], parsed["confidence"], result)
        trajectory.append(verdict["surprise"])

        step_dir.mkdir(parents=True, exist_ok=True)
        (step_dir / "prediction.md").write_text(
            f"confidence: {parsed['confidence']}\n\n{parsed['prediction']}\n")
        (step_dir / "result.json").write_text(json.dumps(result, indent=2))
        ledger.log("step", thread=thread_id, step=step, focus=focus,
                   confidence=parsed["confidence"], surprise=verdict["surprise"],
                   judge_note=verdict["note"], exit=result["exit"], timeout=result["timeout"])
        on_event(f"  step {step}: surprise {verdict['surprise']}/10 — {verdict['note']}")

        messages.append({"role": "user", "content": prompts.STEP_RESULT.format(
            result=world.format_result(result),
            surprise=verdict["surprise"],
            judge_note=verdict["note"],
            trajectory=trajectory,
            min_claim=config.MIN_CLAIM_EXPERIMENTS,
        )})
        outcome["steps"] = step

    ledger.log("noise", thread=thread_id, focus=focus, reason="max steps exhausted")
    return outcome


def _parse_decision(resp: str):
    sec = _sections(resp)
    if "DECISION" not in sec:
        raise ParseError("missing ### DECISION")
    decision = sec["DECISION"].split()[0].upper().strip("|")
    if decision == "CONTINUE":
        payload = _experiment_fields(sec)
    elif decision == "CLAIM":
        if "CLAIM" not in sec or "CHECK" not in sec:
            raise ParseError("CLAIM decision needs ### CLAIM and ### CHECK sections")
        payload = {"claim": sec["CLAIM"], "check": _code(sec["CHECK"])}
    elif decision == "QUESTION":
        if "QUESTION" not in sec:
            raise ParseError("QUESTION decision needs ### QUESTION section")
        payload = {"question": sec["QUESTION"]}
    elif decision == "NOISE":
        payload = {"why": sec.get("WHY", "")}
    else:
        raise ParseError(f"unknown decision {decision!r}")
    if "TOOL" in sec:  # tool banking allowed on any decision
        payload["tool"] = _code(sec["TOOL"])
        payload["tool_name"] = sec.get("TOOL_NAME", "tool").splitlines()[0]
    return decision, payload


def _bank_tool(payload: dict, thread_id: str, on_event):
    if "tool" not in payload:
        return
    name, reason = archive.save_tool(payload["tool_name"], payload["tool"])
    if name:
        ledger.log("tool", thread=thread_id, name=name)
        on_event(f"  tool archived: {name}")
    else:
        ledger.log("tool", thread=thread_id, name=None, rejected=reason)
        on_event(f"  tool rejected — {reason}")


def _finish(decision, payload, thread_id, trajectory, focus, on_event) -> dict:
    if decision == "CLAIM":
        res = archive.admit_claim(payload["claim"], payload["check"], thread_id, trajectory)
        ledger.log("claim", thread=thread_id, slug=res["slug"], admitted=res["admitted"])
        if res["admitted"]:
            on_event(f"  CLAIM admitted: {res['slug']}")
            m = re.match(r"question:\s*([a-z0-9-]+)", focus.strip(), re.I)
            if m:
                archive.resolve_question(m.group(1))
        else:
            on_event(f"  CLAIM rejected — check failed: {res['slug']}")
        return {"ending": "claim", "admitted": res["admitted"], "slug": res["slug"]}
    if decision == "QUESTION":
        lines = payload["question"].strip().splitlines()
        slug = archive.save_question(lines[0], "\n".join(lines[1:]), thread_id)
        ledger.log("question", thread=thread_id, slug=slug)
        on_event(f"  question parked: {slug}")
        return {"ending": "question", "slug": slug}
    ledger.log("noise", thread=thread_id, focus=focus, reason=payload.get("why", ""))
    on_event("  abandoned as noise")
    return {"ending": "noise"}
