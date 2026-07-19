"""The archive: claims (checked facts), tools (reusable code), open questions.

Frozen rule: no claim without a runnable check. check.py must exit 0 to enter.
Only the kernel writes here; the agent writes via admission functions only.
"""
import json
import re
import time
from pathlib import Path

from . import config, world


def slugify(text: str, maxlen: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:maxlen].strip("-")
    return slug or f"item-{int(time.time())}"


def admit_claim(statement: str, check_code: str, thread_id: str, history: list) -> dict:
    """Run the check; admit the claim only if it exits 0."""
    slug = slugify(statement)
    scratch = config.RUNS / thread_id / f"check-{slug}"
    result = world.run_python(check_code, scratch)
    if result["timeout"] or result["exit"] != 0:
        return {"admitted": False, "slug": slug, "result": result}

    dest = config.CLAIMS / slug
    if dest.exists():
        return {"admitted": False, "slug": slug, "result": result, "reason": "duplicate slug"}
    dest.mkdir(parents=True)
    (dest / "claim.md").write_text(statement.strip() + "\n")
    (dest / "check.py").write_text(check_code)
    (dest / "meta.json").write_text(json.dumps({
        "thread": thread_id,
        "admitted_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "surprise_trajectory": history,
    }, indent=2))
    return {"admitted": True, "slug": slug, "result": result}


def save_question(title: str, body: str, thread_id: str) -> str:
    slug = slugify(title)
    path = config.QUESTIONS / f"{slug}.md"
    path.write_text(f"# {title.strip()}\n\n{body.strip()}\n\n(thread: {thread_id})\n")
    return slug


def save_tool(name: str, code: str):
    """Archive a reusable module. Returns (filename, None) or (None, reason).
    Rejected: stdlib-shadowing names (a tool named enum.py breaks `import fractions`
    for every future experiment) and code that doesn't compile (poisons the path)."""
    import sys
    base = re.sub(r"[^a-z0-9_]", "_", name.removesuffix(".py").lower()).strip("_") or "tool"
    if base in sys.stdlib_module_names:
        return None, f"name '{base}' shadows a Python stdlib module — choose another name"
    try:
        compile(code, base, "exec")
    except SyntaxError as e:
        return None, f"does not compile: {e.msg} (line {e.lineno})"
    filename = base + ".py"
    (config.TOOLS / filename).write_text(code)
    return filename, None


def resolve_question(slug: str):
    path = config.QUESTIONS / f"{slug}.md"
    if path.exists():
        path.unlink()


def verify_all(on_event=print) -> dict:
    """Claims-rot audit: re-run every archived check. Claims must keep touching the world."""
    from . import ledger
    claims = sorted(config.CLAIMS.iterdir()) if config.CLAIMS.exists() else []
    failed = []
    for d in claims:
        check = d / "check.py"
        if not check.exists():
            failed.append(d.name)
            continue
        result = world.run_python(check.read_text(), config.RUNS / "verify" / d.name)
        if result["timeout"] or result["exit"] != 0:
            failed.append(d.name)
            on_event(f"  ROTTED: {d.name} (exit {result['exit']}, timeout={result['timeout']})")
    entry = {"total": len(claims), "passed": len(claims) - len(failed), "failed": failed}
    ledger.log("verify", **entry)
    on_event(f"verify: {entry['passed']}/{entry['total']} claim checks still pass")
    return entry


def _signatures(path: Path) -> str:
    """' | f(a, b), g(x)' — top-level def signatures so the agent can call without rereading."""
    try:
        sigs = re.findall(r"^def\s+(\w+\([^)]*\))", path.read_text(), re.M)
    except OSError:
        return ""
    return " | " + ", ".join(sigs[:5]) if sigs else ""


def _first_line(path: Path) -> str:
    try:
        for line in path.read_text().splitlines():
            line = line.strip().lstrip("# ")
            if line:
                return line[:120]
    except OSError:
        pass
    return "(unreadable)"


def index(max_items: int = 40) -> str:
    """Compact archive digest injected into the agent's context."""
    lines = []
    claims = sorted(config.CLAIMS.iterdir()) if config.CLAIMS.exists() else []
    if claims:
        lines.append(f"CLAIMS ({len(claims)}):")
        for d in claims[-max_items:]:
            lines.append(f"  - [{d.name}] {_first_line(d / 'claim.md')}")
    tools = sorted(config.TOOLS.glob("*.py"))
    if tools:
        lines.append("TOOLS (importable in experiments):")
        for t in tools[-max_items:]:
            lines.append(f"  - {t.stem}: {_first_line(t)}{_signatures(t)}")
    questions = sorted(config.QUESTIONS.glob("*.md"))
    if questions:
        lines.append(f"OPEN QUESTIONS ({len(questions)}):")
        for q in questions[-max_items:]:
            lines.append(f"  - [{q.stem}] {_first_line(q)}")
    return "\n".join(lines) if lines else "(archive empty — everything is undiscovered)"


def claims_digest(max_items: int = 60) -> str:
    """Fuller claim statements, for the audit's with-archive condition."""
    lines = []
    claims = sorted(config.CLAIMS.iterdir()) if config.CLAIMS.exists() else []
    for d in claims[-max_items:]:
        try:
            lines.append("- " + (d / "claim.md").read_text().strip().replace("\n", " ")[:300])
        except OSError:
            continue
    return "\n".join(lines) if lines else "(no claims)"
