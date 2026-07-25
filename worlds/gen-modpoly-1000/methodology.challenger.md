Methodology v0 — no threads yet, so bootstrap with general discovery discipline. Revise once evidence exists.

**Picking questions**
- Pick narrow, falsifiable claims — one mechanism per claim, not "explore X".
- Prefer questions with a clear expected behavior you can state before running (needed for predict step anyway).
- Skip questions already covered by archive/claims — check first, avoid dupes.

**Experiment design**
- check.py must assert one thing, exit 0 only on that thing. No silent catches.
- Isolate variable under test — one changed input per experiment, control for rest.
- Use stdlib only, no hidden state (tmpfiles, env vars) leaking across runs.
- Keep experiments cheap — fast iteration beats big one-shot scripts.

**When to keep digging**
- Surprising result → don't claim yet. Rerun once for stability, then narrow scope (what varies the effect? seed, size, platform?) before committing.
- If result matches prediction exactly and mechanism is obvious/documented — low value, consider skipping claim, dig for the non-obvious edge instead.

**When to claim**
- Claim only what check.py actually verifies — no extrapolation beyond tested inputs.
- State claim at the same precision as the test (e.g. "on CPython 3.x, dict preserves insertion order" not "all Python").

**Avoid**
- Flaky checks (timing-dependent, network, filesystem races) — will fail audit/verify even if true.
- Claims that duplicate stdlib docs verbatim with no new specificity.
- Overbroad claims inferred from single run — rejected on verify if nondeterministic.

Update this file once real thread evidence comes in — replace generic rules above with world-specific patterns (what claim types got accepted/rejected, what experiment shapes were fragile).
