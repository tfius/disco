# gen-* — discovery program for the generated-world class

Unlike the other programs, this one covers a *class*: procedurally generated
territories (`disco genworld <seed> [--family ...]`) whose rules are rolled at
random, so their truths cannot exist in any pretraining corpus. Per-seed
specifics are unpredictable by construction; what is predictable is the *shape*
of discovery when priors are absent — which is the point. These worlds are the
train/eval set for learning discovery itself.

## Why this class exists

In documented worlds, first-contact surprise runs 0–3: the model recalls.
In gen-42's first session it ran 6, 8, 10: the model discovers. The class
provides (a) unbounded fresh territory at controllable difficulty, (b) an
uncontaminated eval — transfer to a held-out generated world measures the
skill, not the memory — and (c) honest surprise signal for process rewards.

## The expected arc (any family)

1. **Engine + validation** — implement the rolled rule exactly; validate
   against the literal table/spec in world.md. Surprise ~0; mandatory.
   [admitted 90]
2. **Backgrounds and invariants** — quiescent states, conserved quantities,
   symmetry of the rolled rule (generated rules are usually asymmetric — the
   first anti-prior discovery: textbook intuitions assume symmetry that isn't
   there). [surprise ≥5 somewhere in this phase: 80]
3. **Exact small-space structure** — fixed points, cycles, functional-graph
   censuses on small widths/moduli; the same census machinery every documented
   world developed transfers directly. [admitted claims: 85]
4. **Propagation physics** — damage spreading, particle-like defects, growth
   laws. Gen-42 already produced the class's signature find here (direction-
   asymmetric propagation). Expect at least one law per seed that no symmetric
   intuition predicts. [70]
5. **Statistical laws** — seeded ensemble behavior, densities, relaxation.
   [65]
6. **Cross-seed meta-claims** (the class endgame) — laws *about the family*:
   e.g. what fraction of rolled CA rules have frozen backgrounds, how cycle
   structure distributes across seeds. These are claims a single world cannot
   host; they need a meta-world whose experiments roll many seeds. [not yet
   supported by the harness — roadmap]

## Per-family notes

- **ca** (1D CA, k states, radius r; elementary CAs excluded as documented):
  richest particle physics; census machinery from eca transfers whole.
- **modpoly** (iterated random polynomial maps on Z_m): pure functional-graph
  territory — rho shapes, cycle spectra, preimage trees; number-theoretic
  structure of the random modulus leaks in and is discoverable.
- **tag** (random tag systems): busybeaver-flavored — halting vs growth vs
  periodicity, with the same certificate discipline needed for "never halts".
- **vm** (random register machines): reverse-engineer an artificial computer —
  halting sets, the function short programs compute, per-opcode invariants,
  reachable-state structure. The apex of the computation flavor.
- **dfa** (random finite automata): formal-language theory — the accepted
  language, accepted-count-per-length recurrences, minimal DFA (Myhill-Nerode),
  finite/cofinite classification, pumping structure.
- **curve** (elliptic curves E(F_p), random p/a/b): finite-group structure —
  order, Hasse bound, cyclic-vs-product decomposition, point orders, torsion.
- **percolation** (random-neighborhood site percolation): spatial criticality —
  the threshold p_c, giant-cluster fraction, cluster-size laws, finite-size
  scaling; the seeded-claim discipline is mandatory.
- **collatz** (generalized affine-residue maps): open-frontier integer dynamics —
  which starts reach cycles under a budget, cycles and basins, stopping-time
  statistics; 'diverges'/'always halts' only as budgeted, seeded observations.
- **game** (random normal-form bimatrix games): equilibrium theory — pure and
  mixed Nash, dominated strategies, zero-sum detection, Pareto outcomes.
- **combgame** (random impartial subtraction games): combinatorial game theory —
  P/N-positions, Grundy/nimber values, Grundy-sequence periodicity, Sprague-Grundy.
- **coalition** (random cooperative games): cooperative theory — superadditivity,
  the Shapley value, non-emptiness of the core and a core allocation.
- **auction** (random sealed-bid auctions): mechanism design — dominant strategies,
  incentive-compatibility, pure Nash bidding, revenue, efficiency.
- **congestion** (random Braess routing networks): price of anarchy — Nash flow vs
  social optimum, and whether deleting an edge lowers equilibrium cost (Braess).
- **voting** (random preference profiles): social choice — Condorcet winner/cycles,
  plurality vs Borda vs Condorcet disagreement, single-voter manipulability.

## Signature metrics (why this class is the eval)

- **First-contact surprise**: mean surprise of the first session's steps.
  Documented worlds ~0–3; generated ~5–8. A model trained on discovery should
  keep *encountering* high surprise (it asks real questions) while *closing*
  it faster.
- **Closure rate**: mean surprise decay per step within threads (the 8→3→8→10→0
  arc closed; flat trajectories are noise-mining). The trainable quantity.
- **Admission efficiency**: verified claims per thread at fixed step budget.
- **Calibration**: stated confidence vs judged outcome across steps (exported
  per episode).

## Traps specific to the class

Rules with degenerate rolls (everything dies / everything freezes) make thin
worlds — the generator's quiescence constraint reduces but does not eliminate
this; a boring seed is cheap to discard, and "this seed is degenerate, here is
the exact fixed-point proof" is itself a legitimate small claim. No literature
means no names: the agent must invent terminology, and claims must define
every term operationally or checks become ambiguous. Judge scoring is harder
here (no shared vocabulary with pretraining) — expect noisier surprise scores
and lean on the exact-execution parts of checks.
