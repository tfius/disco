# Eval baselines

Committed scorecards from `disco eval` on the sealed held-out set
([../heldout.json](../heldout.json)) — the permanent before/after record for the
"does training teach discovery" experiment. Live scorecards land in `exports/`
(gitignored); the ones worth keeping as anchors are copied here and tracked.

Each file is the exact `disco eval` output: `{model, backend, ts,
threads_per_world, rows[], aggregate}`. Read **per-family**, not just aggregate —
surprise carries signal on emergent worlds (ca, collatz, percolation), while
claims-per-thread and closure carry it on spec-then-derive worlds (vm, dfa,
curve, modpoly).

## Records

- **`eval-sonnet-20260727-232348.json`** — Sonnet, raw policy (no evolved
  methodology), 8 worlds × 3 threads. Aggregate: claims/thread 0.833,
  first-contact surprise 1.17, closure 1.25. The *ceiling* — a strong teacher's
  discovery on worlds no corpus describes; headroom concentrated in vm (1/3
  admitted), dfa (2/3), tag (2/3).
  **Caveat:** ran on the pre-fix set — the collatz row is seed **7000006**,
  since found degenerate (map `T(x)=2x`, nothing to discover) and replaced by
  **7000012** afterward. So its collatz row (surprise 0 / closure 0) is an
  artifact of that seed, not the model. n=3 is noisy; treat as provisional.

## Still wanted

- A clean Sonnet baseline on the **current** set (post collatz fix), at n≥5.
- A **small base model** baseline on the same set — the *floor* the training run
  must lift. The gap between floor and the Sonnet ceiling is the transfer signal.
