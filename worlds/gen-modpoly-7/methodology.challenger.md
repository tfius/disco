Methodology v1 — no evidence yet, first-principles draft.

**Pick questions**
Start narrow, concrete, falsifiable. One variable at a time. Avoid vague "explore X" — pin exact input/output you expect before touching code.

**Design experiments**
Predict exact output first, commit it, then run. Keep check.py deterministic — no timing, no randomness, no filesystem side effects outside archive/tools. Prefer print/assert over floating comparisons unless tolerance stated in prediction. Small inputs first — scale up only after core claim holds.

**When to dig deeper**
Surprise (predicted ≠ actual) means investigate root cause before next claim — don't paper over with adjusted prediction. Chase minimal reproduction: strip experiment down until surprise still triggers. If surprise vanishes when isolated, prediction was wrong for wrong reason — don't claim yet.

**When to claim**
Claim only what check.py actually verifies, nothing broader. If claim generalizes ("all X do Y"), test at least 2-3 boundary/edge cases before claiming — else scope claim narrowly ("for N in tested range").  A claim that only reproduces known stdlib docs isn't worth archive space — chase environment-specific or version-specific facts instead.

**Avoid**
- Third-party deps — check.py runs stdlib only, imports will fail silently or noisily, wastes a cycle.
- Reusing prior claim's exact experiment with cosmetic change — no new info, likely rejected as duplicate.
- Overlong experiments — long-running/looping scripts risk timeout, burn cycle for no claim.
- Claiming behavior tied to nondeterministic state (dict ordering pre-3.7, hash randomization, GC timing) unless explicitly testing that instability itself.
- Skipping the "why" — if you can't explain surprise mechanism, don't archive it as understood; note as open question instead.

**Tooling**
Build small reusable tools/ helpers only after 2+ experiments need the same primitive — premature tool-building wastes cycles on unverified abstractions.

**Efficiency**
One claim per experiment when possible — bundling multiple assertions in one check.py risks partial failure killing whole claim. Split.

Revise this file after next batch of evidence — replace guesses above with what threads actually show.
