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
    config.WORLD_DIR = tmp
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

    # replay: the full message transcript must be persisted
    transcript = [json.loads(l) for l in
                  (config.RUNS / "selftest" / "messages.jsonl").read_text().splitlines()]
    assert transcript[0]["role"] == "system" and transcript[-1]["role"] == "assistant"
    assert len(transcript) >= 7, f"transcript too short: {len(transcript)}"

    # tool inheritance: archived tools must be importable in later experiments
    r = world.run_python(
        "from identity_probe import same_object_across_exec\n"
        "print(same_object_across_exec('257'))",
        config.RUNS / "tool-import-test")
    assert r["exit"] == 0, f"archived tool not importable: {r}"

    # claims-rot audit: the admitted check must still pass
    v = archive.verify_all(on_event=lambda m: None)
    assert v == {"total": 1, "passed": 1, "failed": [], "culled": []}, v

    # selection: sabotage the check — two consecutive verify failures must cull the claim
    (claim_dir / "check.py").write_text("import sys; sys.exit(1)\n")
    v = archive.verify_all(on_event=lambda m: None)
    assert v["failed"] == [outcome["slug"]] and not v["culled"], f"first fail should only rot: {v}"
    v = archive.verify_all(on_event=lambda m: None)
    assert v["culled"] == [outcome["slug"]], f"second fail should cull: {v}"
    assert not claim_dir.exists(), "culled claim dir must be gone"
    demoted = list(config.QUESTIONS.glob("demoted-*.md"))
    assert len(demoted) == 1, f"demotion should create an open question: {demoted}"

    # stdlib-shadow guard: a tool named like a stdlib module must be rejected
    name, reason = archive.save_tool("enum", "x = 1")
    assert name is None and "stdlib" in reason, (name, reason)
    name, reason = archive.save_tool("json", "x = 1")
    assert name is None, "json must be rejected too"

    print(f"\nselftest OK — claim admitted ('{outcome['slug']}'), tool archived AND "
          f"importable, verify passes, ledger consistent ({tmp})")


def scenario_evolution():
    _patch_config()
    config.ensure_dirs()
    from kernel import evolve
    quiet = lambda m: None

    # generation 1: winning challenger gets promoted over the empty champion
    llm.chat = lambda *a, **k: "Probe boundaries first. Replicate everything twice."
    variant, meth = evolve.current(on_event=quiet)
    assert variant == "challenger" and "Probe boundaries" in meth
    for i in range(config.TRIAL_THREADS):
        evolve.note({"thread": f"c{i}", "ending": "claim", "admitted": True}, "challenger", on_event=quiet)
        evolve.note({"thread": f"m{i}", "ending": "noise"}, "champion", on_event=quiet)
    assert "Probe boundaries" in evolve.champion_text(), "winner must be promoted"
    s = evolve._state()
    assert s["generation"] == 2 and not s["champion"] and not s["challenger"], s

    # generation 2: losing challenger dies, champion survives
    llm.chat = lambda *a, **k: "Claim instantly without evidence."
    evolve.propose(on_event=quiet)
    for i in range(config.TRIAL_THREADS):
        evolve.note({"thread": f"x{i}", "ending": "claim", "admitted": False}, "challenger", on_event=quiet)
        evolve.note({"thread": f"y{i}", "ending": "claim", "admitted": True}, "champion", on_event=quiet)
    assert "Probe boundaries" in evolve.champion_text(), "champion must survive"
    assert evolve.challenger_text() is None, "loser must be discarded"
    assert evolve._state()["generation"] == 3

    # over-cap proposals are rejected
    llm.chat = lambda *a, **k: "word " * (config.METH_WORD_CAP + 10)
    evolve.propose(on_event=quiet)
    assert evolve.challenger_text() is None, "over-cap proposal must be rejected"

    # multi-agent lineage isolation: alice's methodology never touches solo's
    config.set_agent("alice")
    llm.chat = lambda *a, **k: "Alice: measure twice, claim once."
    evolve.propose(on_event=quiet)
    assert "Alice" in evolve.challenger_text()
    assert evolve._state()["generation"] == 1, "alice starts her own lineage"
    config.set_agent("solo")
    assert evolve.challenger_text() is None, "solo lineage must be untouched by alice"
    assert evolve._state()["generation"] == 3, "solo generation preserved"
    print("evolution scenario OK — promotion, discard, cap rejection, agent isolation")


def scenario_cascade():
    _patch_config()
    config.ensure_dirs()
    from kernel import world
    # a claim whose check imports a tool; then the tool breaks; cascade must catch it
    archive.save_tool("probe9", "def nine():\n    return 9\n")
    res = archive.admit_claim(
        "probe9.nine() returns 9.",
        "import sys\nfrom probe9 import nine\nsys.exit(0 if nine() == 9 else 1)\n",
        "cascade-test", [5, 1])
    assert res["admitted"], res
    assert archive.dependents("probe9") == [res["slug"]], "dependency edge must be visible"
    archive.save_tool("probe9", "def nine():\n    return 8\n")  # break the tool
    v = archive.verify_all(on_event=lambda m: None, only=[res["slug"]])
    assert v["failed"] == [res["slug"]] and v["subset"] is True, f"first fail must rot: {v}"
    v2 = archive.verify_all(on_event=lambda m: None, only=[res["slug"]])
    assert v2["culled"] == [res["slug"]], f"broken dependency must cull the claim: {v2}"
    print("cascade scenario OK — tool break rots then culls its dependent claim")


def scenario_slug_collision():
    _patch_config()
    config.ensure_dirs()
    prefix = "For rule table RULE = [0, 0, 0, 0, 1, 1, 2, 0, 2, 1, 0, 2] the system "
    ok = "import sys; sys.exit(0)"
    r1 = archive.admit_claim(prefix + "has a quiescent background.", ok, "t1", [3, 1])
    r2 = archive.admit_claim(prefix + "has exactly two fixed points.", ok, "t2", [4, 1])
    assert r1["admitted"] and r2["admitted"], (r1, r2)
    assert r1["slug"] != r2["slug"], "different claims must get distinct slugs"
    r3 = archive.admit_claim(prefix + "has a quiescent background.", ok, "t3", [2, 1])
    assert not r3["admitted"] and r3["reason"] == "duplicate claim", r3
    print("slug-collision scenario OK — distinct claims disambiguated, true duplicates priced")


if __name__ == "__main__":
    main()
    scenario_gate()
    scenario_evolution()
    scenario_cascade()
    scenario_slug_collision()
