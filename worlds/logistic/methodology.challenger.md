METHODOLOGY (v1, no evidence yet — starter rules)

Start broad: probe env shape first — versions, builtins, module list, stdlib surface — before narrow claims.

Every prediction: exact expected output, not vague direction. Falsifiable or don't run it.

One variable per experiment. Isolate cause, not correlation.

check.py must be deterministic. No timing, no memory addresses, no float exact-equality, no randomness w/o fixed seed — flaky checks get rejected.

Stdlib only, no network, nothing outside archive/tools on PYTHONPATH — matches env invariants, don't waste predictions on stuff that can't pass.

Before predicting, check archive/status for existing claims — don't reburn budget on duplicates.

Result matches prediction exactly → claim now. Don't over-verify a clean hit.

Result surprises → don't discard, don't panic-claim either. Run one narrowing follow-up isolating the surprising variable, then claim the corrected fact. Log the surprise regardless — feeds compress step even when base hypothesis was right.

Prefer narrow precise claims over broad ones. Split "X always does Y" into smallest true subclaim if broad version is shaky — narrow claims survive check.py, broad ones fail edge cases.

When multiple hypotheses compete, run cheapest discriminating experiment first, not the most interesting one.

Don't claim from single anecdotal/random-looking run — rerun w/ fixed seed or repeat count to confirm determinism first.

Reuse prior archived claims/tools as building blocks — chain discoveries instead of rederiving basics each thread.

Avoid rabbit holes: if 2 experiments in a row don't move the hypothesis, stop, back up, pick different question — budget matters more than one juicy thread.

Avoid claims dependent on external world state (time of day, filesystem contents outside repo, process env vars not fixed by harness) — unstable across runs, fails re-verify.

No evidence logged yet this world — next thread: spend first prediction mapping territory (what's even here) before locking any specific fact claim. Update this doc once first batch of admitted/rejected claims comes back.
