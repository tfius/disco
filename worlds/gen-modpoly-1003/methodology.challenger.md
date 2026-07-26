Methodology v1 (no prior threads — baseline rules from protocol constraints only)

1. Pick questions with a crisp, checkable invariant: exact output, exact exit code, or exact exception type. Avoid vague/statistical claims ("usually", "tends to") — check.py needs a deterministic pass/fail.

2. Before running: write predicted output first, then design the smallest experiment that isolates one variable. One claim = one mechanism. Don't bundle multiple behaviors into one prediction.

3. Prefer boundary/edge cases over happy-path: empty inputs, zero, negative, max/min values, type coercion edges, off-by-one. These surprise more often and yield sharper claims.

4. When result matches prediction exactly: claim immediately, don't over-explore for confirmation. When it surprises: dig one level deeper (why, not just what) before claiming — root-cause claims are more durable than symptom claims.

5. Reject candidate claims that depend on: timing/performance (non-deterministic across runs), external state (files, network, env vars not controlled), or specific object identity/memory addresses.

6. Keep check.py minimal — assert the one thing predicted, nothing extra. Overspecified checks fail on irrelevant variance and waste the claim.

7. If an experiment errors unexpectedly (not the predicted error), treat the error itself as the new prediction target — don't discard the thread, re-predict against the traceback/exception type.

8. Avoid re-deriving stdlib docs verbatim; only claim what you actually ran and verified in this environment (version-specific, build-specific quirks are highest value).

9. If a claim's check.py needs more than ~10 lines, the claim is probably still two claims — split it.

10. Log failed predictions honestly; a rejected claim with a clear reason is cheaper than a vague accepted one that erodes trust in the archive.
