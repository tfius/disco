#!/usr/bin/env python3
"""Offline end-to-end test: scripted LLM responses drive one full thread
(predict -> run -> surprise -> CONTINUE -> CLAIM w/ check + tool) against
temp dirs. No endpoint needed."""
import json
import sys
import tempfile
from pathlib import Path

from kernel import archive, config, ledger, llm, loop, world

SCRIPT = [
    # agent step 1 — deliberate syntax error, must trigger repair without burning a step
    """### FOCUS
does int caching survive arithmetic

### PREDICTION
prints False, because 256+1 creates a new int object each time

### CONFIDENCE
70

### EXPERIMENT
```python
a = 256 + 1
b = 257
print(a is b
```""",
    # repair reply
    """### EXPERIMENT
```python
a = 256 + 1
b = 257
print(a is b)
```""",
    # judge step 1
    '{"surprise": 7, "note": "predicted False, got True"}',
    # agent decision: dig deeper AND bank a tool mid-thread
    """### DECISION
CONTINUE

### PREDICTION
prints True then False: compile-time constant folding interns small results within one code object, but not across exec boundaries

### CONFIDENCE
60

### EXPERIMENT
```python
from identity_probe import same_object_across_exec
a = 256 + 1
b = 257
print(a is b)
print(same_object_across_exec("257"))
```

### TOOL_NAME
identity_probe

### TOOL
```python
\"\"\"Probe object identity for equal values across code-object boundaries.\"\"\"
def same_object_across_exec(literal_src):
    local = eval(literal_src)
    ns = {}
    exec(f"x = {literal_src}", ns)
    return local is ns["x"]
```""",
    # judge step 2
    '{"surprise": 1, "note": "matched both lines"}',
    # agent decision: claim (tool already banked)
    """### DECISION
CLAIM

### CLAIM
In CPython, integer constants appearing in the same code object are deduplicated by the compiler, so `256 + 1 is 257` is True within one module, but identity does not hold for equal ints created in separate code objects outside the small-int cache range (-5..256).

### CHECK
```python
import sys
a = 256 + 1
b = 257
ns = {}
exec("x = 257", ns)
ok = (a is b) and not (ns["x"] is b)
sys.exit(0 if ok else 1)
```""",
]


GATE_SCRIPT = [
    # step 1
    """### FOCUS
what does list.append return

### PREDICTION
prints the list itself, enabling chaining

### CONFIDENCE
55

### EXPERIMENT
```python
print([1].append(2))
```""",
    '{"surprise": 6, "note": "printed None, not the list"}',
    # premature claim after one experiment — kernel must refuse
    """### DECISION
CLAIM

### CLAIM
list.append returns None.

### CHECK
```python
import sys; sys.exit(0 if [1].append(2) is None else 1)
```""",
    # replicate bounce -> agent continues
    """### DECISION
CONTINUE

### PREDICTION
None again for other mutators: sort and extend also return None

### CONFIDENCE
80

### EXPERIMENT
```python
xs = [3, 1]
print(xs.sort(), xs.extend([4]))
```""",
    '{"surprise": 0, "note": "None None as predicted"}',
    # now backed by two experiments — admissible
    """### DECISION
CLAIM

### CLAIM
CPython list mutator methods (append, sort, extend) return None rather than the list.

### CHECK
```python
import sys
xs = [1]
ok = xs.append(2) is None and xs.sort() is None and xs.extend([3]) is None
sys.exit(0 if ok else 1)
```""",
]


def _patch_config():
    tmp = Path(tempfile.mkdtemp(prefix="disco-selftest-"))
    config.ARCHIVE = tmp / "archive"
    config.CLAIMS = config.ARCHIVE / "claims"
    config.TOOLS = config.ARCHIVE / "tools"
    config.QUESTIONS = config.ARCHIVE / "open-questions"
    config.RUNS = tmp / "runs"
    config.LEDGER = tmp / "ledger.jsonl"
    return tmp


def scenario_gate():
    _patch_config()
    responses = iter(GATE_SCRIPT)
    llm.chat = lambda *a, **k: next(responses)
    outcome = loop.run_thread(thread_id="gate-test", on_event=lambda m: print(m))
    assert outcome["ending"] == "claim" and outcome["admitted"], outcome
    assert outcome["steps"] == 2, f"gate should have forced a second experiment: {outcome}"
    assert not list(config.QUESTIONS.glob("*.md")), "nothing should be parked"
    print("gate scenario OK — premature claim refused, replication forced, then admitted\n")


def main():
    tmp = _patch_config()

    responses = iter(SCRIPT)
    llm.chat = lambda *a, **k: next(responses)

    outcome = loop.run_thread(thread_id="selftest", on_event=lambda m: print(m))

    assert outcome["ending"] == "claim", outcome
    assert outcome["admitted"] is True, outcome
    assert outcome["steps"] == 2, f"syntax repair must not burn a step: {outcome}"
    claim_dir = config.CLAIMS / outcome["slug"]
    assert (claim_dir / "claim.md").exists() and (claim_dir / "check.py").exists()
    meta = json.loads((claim_dir / "meta.json").read_text())
    assert meta["surprise_trajectory"] == [7, 1], meta
    assert (config.TOOLS / "identity_probe.py").exists(), "mid-thread tool banking failed"
    kinds = [json.loads(l)["kind"] for l in config.LEDGER.read_text().splitlines()]
    assert kinds == ["step", "tool", "step", "claim"], kinds
    idx = archive.index()
    assert "int" in idx and "identity_probe" in idx
    assert "same_object_across_exec(literal_src)" in idx, f"signature missing from index:\n{idx}"

    # tool inheritance: archived tools must be importable in later experiments
    r = world.run_python(
        "from identity_probe import same_object_across_exec\n"
        "print(same_object_across_exec('257'))",
        config.RUNS / "tool-import-test")
    assert r["exit"] == 0, f"archived tool not importable: {r}"

    # claims-rot audit: the admitted check must still pass
    v = archive.verify_all(on_event=lambda m: None)
    assert v == {"total": 1, "passed": 1, "failed": []}, v

    print(f"\nselftest OK — claim admitted ('{outcome['slug']}'), tool archived AND "
          f"importable, verify passes, ledger consistent ({tmp})")


if __name__ == "__main__":
    main()
    scenario_gate()
