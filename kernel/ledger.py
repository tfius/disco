"""Append-only ledger. Only the kernel writes; the agent sees a tail in its context."""
import json
import time

from . import config


def log(kind: str, **fields):
    entry = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": kind,
             "agent": config.AGENT, **fields}
    with open(config.LEDGER, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def tail(n: int = 12, for_agent: bool = False) -> str:
    """for_agent=True hides audit entries — the fast loop must never see its own audit metric."""
    try:
        lines = config.LEDGER.read_text().splitlines()[-n * 2:]
    except OSError:
        return "(no activity yet)"
    out = []
    for line in lines:
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = e.get("kind")
        if for_agent and kind in ("audit", "verify", "evolution"):
            continue
        if kind == "step":
            out.append(f"- step {e.get('thread')}/{e.get('step')}: surprise {e.get('surprise')}/10 — {e.get('focus', '')[:80]}")
        elif kind == "claim":
            out.append(f"- CLAIM {'admitted' if e.get('admitted') else 'REJECTED (check failed)'}: {e.get('slug')}")
        elif kind == "tool":
            if e.get("rejected"):
                out.append(f"- tool rejected: {e.get('rejected')}")
            else:
                out.append(f"- tool archived: {e.get('name')}")
        elif kind == "question":
            out.append(f"- question parked: {e.get('slug')}")
        elif kind == "noise":
            out.append(f"- noise abandoned: {e.get('focus', '')[:80]}")
        elif kind == "audit":
            out.append(f"- AUDIT: uplift {e.get('uplift')} (with archive {e.get('with_archive')} vs without {e.get('without_archive')})")
        elif kind == "evolution":
            scores = (f" ({e.get('challenger_score')} vs {e.get('champion_score')})"
                      if e.get("challenger_score") is not None else "")
            out.append(f"- EVOLUTION gen {e.get('generation')}: {e.get('event')}{scores}")
        elif kind == "verify":
            culled = f", culled: {', '.join(e['culled'])}" if e.get("culled") else ""
            out.append(f"- VERIFY: {e.get('passed')}/{e.get('total')} claim checks still pass{culled}")
    return "\n".join(out[-n:]) if out else "(no activity yet)"
