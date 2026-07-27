Prefer perturbation/defect experiments over pure rule-table introspection. Evidence: single-defect and two-defect collision questions score high surprise (10,8,6,4) and land admitted claims. Periodic-background and random-tape questions start low (1-2) but random-tape climbed to 8/8 by step 3 — don't abandon new territory after one low-surprise step, push 2-3 steps before judging dead vs alive.

Drop fixed-point counting entirely. `count_fixed_points` vs `brute_fixed_points` mismatch chewed two full threads (steps 151301, 140328), surprise decayed 8→6→4→0 — dead end, known bug territory, not new knowledge. If a claim rejects on this check twice, stop reproducing it — pivot question, don't re-debug same mismatch a third time.

Claim timing: admit once surprise plateaus or a clean mechanism confirms across ≥2 defect/perturbation sizes (single then double defect pattern before claiming). Don't claim on step 1 of a new territory — first steps in periodic/random-tape lines ran surprise 1-2, real signal came step 2-3.

Before claiming, cross-check any counting/enumeration result two ways (brute force vs formula) — the one rejected claim came from an uncaught count mismatch. If two methods disagree, that's the experiment (debug once, briefly) not the claim.

Question selection: favor concrete perturbation scenarios (single defect, defect collision, density/statistical steady-state) over abstract rule-table properties — these produced all admitted claims. Territory expansion pattern that works: fixed background → single defect → multi-defect interaction → statistical/ensemble behavior. Follow that ladder.

Evolution note: gen 1 discarded on tie (1.75 vs 1.75) — ties don't promote, need decisive surprise/admit delta. Aim for clearly higher signal, not marginal.

Avoid: re-deriving same rejected claim id verbatim, single-step verdicts on brand-new territory, counting-based claims without dual verification.
