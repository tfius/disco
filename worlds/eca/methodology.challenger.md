Pick questions with a single falsifiable claim and a clear pass/fail check — no compound predictions ("X and Y"), split them into separate claims instead.

Before running: write the prediction in concrete, checkable terms (exact value, exact error type, exact output string) — not vague direction ("probably faster"). A prediction you can't score precisely later is a wasted run.

Design experiments minimal: smallest script that isolates the one variable in question. Strip anything not needed to falsify the prediction — extra logic in an experiment just adds noise to the surprise signal.

Read the actual result before writing surprise. Don't rationalize a near-miss into a match — if predicted value and observed value differ, that's a surprise, log it as one.

Prefer questions where you don't already know the answer with confidence. Re-deriving something obvious wastes a thread; the goal is real surprises, not confirmations.

When a run surprises you, dig one level deeper immediately with a follow-up experiment in the same thread before compressing — chase the mechanism, not just the symptom. Stop digging once you can state a mechanism in one sentence backed by a passing check; don't chain more than 2-3 follow-ups per thread or you'll never reach archive.

Only write check.py when you can state the exact condition that makes the claim true or false in code, not prose. If you can't write that condition, the claim isn't ready — narrow it first.

Avoid claims that depend on environment specifics likely to vary run-to-run (timing thresholds, memory addresses, thread scheduling order) unless the claim is specifically about variance itself — these get rejected on replay.

Avoid claims stated in terms of implementation folklore ("CPython does X") without a check that actually exercises CPython-specific behavior — verify, don't assume.

When archiving, compress the claim statement to the reusable fact only — drop the experimental narrative, keep just what future threads need to build on.
