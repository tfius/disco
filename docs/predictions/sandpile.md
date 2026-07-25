# sandpile — full discovery program

## Where it stands

Untouched — no claims, no tools, no ledger; the agent meets the world cold.

## Phase map

### Phase 1 — engine, correctness, and the abelian shock

**Goal.** A trusted toppling engine, then the world's founding surprise: stabilization order does not matter.

**Instruments.** `pile.py` — flat-list N×N grid, worklist (deque) stabilizer returning (final config, per-site toppling counts, total topplings); pluggable site-selection order (FIFO, LIFO, seeded-random, raster); boundary cells dissipate off-grid grains. Correctness harness: brute-force single-step reference vs worklist engine on seeded random configs.

**Predicted claims.**
- Engine validity: worklist stabilizer agrees with naive repeat-scan stabilizer on 200 seeded random configs, N ∈ {3..8}, grains per cell 0..7 [92].
- The natural wrong prior fires — the agent predicts final configuration depends on toppling order, reality refuses: for 100 seeded configs on N ∈ {4,6,8}, FIFO/LIFO/random/raster orders yield identical final configs [90].
- Stronger invariance: the per-site toppling *counts* (odometer), not just the final config, are order-independent — same experiment, compare count vectors [80].
- Termination: every config on finite N stabilizes; bounded by an explicit topple budget that is never exhausted across the seeded sweep [85].

**How.** Predict order-dependence first (commit it — the surprise score is the point). Run the four orders on identical seeds, diff configs, then diff odometers. Validate the engine before anything else; every later claim inherits it.

**Traps.** Boundary handling — grains must vanish off-edge or nothing terminates; an accidental torus makes stabilization impossible and burns the 30s timeout. Comparing configs by printing (whitespace bugs) instead of tuple equality. Claiming order-independence from one seed.

**Unlocks.** Every subsequent phase; `pile.py` becomes the world's kernel tool.

### Phase 2 — stabilization laws, invariants, least action

**Goal.** Quantitative bounds and the variational structure hiding in the dynamics.

**Instruments.** `odometer.py` (per-site counts, dissipation accounting); `grow.py` (single central pile of M grains, radius/topple metrics).

**Predicted claims.**
- Maximal stable config is all-3s (3N² grains); adding one grain anywhere to it triggers an avalanche in which **every site topples exactly once** — verified exhaustively for all N² drop sites, N ∈ {3..8} [75].
- Conservation ledger: initial grains = final grains + dissipated, where dissipated equals the exact sum over boundary-site topplings of off-grid edges — checked on seeded sweeps [85].
- Single-pile growth: M grains at the center of a large-enough grid stabilize inside radius c·√M, fitted c ∈ [0.5, 1.2] for M ∈ {2⁶..2¹⁴}, seeded and exact per M [70].
- Least-action property: any legal toppling sequence reaching stability performs exactly the odometer at every site; adversarial orders (topple-farthest-first, seeded shuffles) never beat it — 50 seeded configs, N ∈ {4,8} [65].
- Total topplings for the central-pile stabilization grow superlinearly in M, log-log fitted exponent within [1.3, 2.2] (band deliberately wide; tightening it is the experiment) [55].

**How.** Odometer already exists from Phase 1; least action falls out of comparing count vectors across pathological orders. Radius via bounding box of changed cells.

**Traps.** M large enough to hit 30s in pure Python — budget M by timing at small sizes first; claiming the topple-count exponent to false precision; forgetting that on small N the central pile hits the boundary and the √M law breaks (scope claims to M ≪ N²).

**Unlocks.** Odometer machinery for waves and avalanches (Phase 6); trust in exact accounting for group arithmetic.

### Phase 3 — recurrence and the burning test

**Goal.** Split configuration space into transient and recurrent; find Dhar's burning test (or reinvent an equivalent).

**Instruments.** `burn.py` — burning test: fire from the sink, a site burns when its height exceeds unburnt-neighbor count; recurrent ⟺ all sites burn. `census.py` — exhaustive enumeration of all 4^(N²) stable configs for N ≤ 3.

**Predicted claims.**
- Reachability defines recurrence: under seeded random driving (drop-and-stabilize), the chain enters a closed class it never leaves; membership is decidable by the burning test — burning verdict matches long-run reachability on 2×2 exhaustively [70].
- Exact census: 2×2 has **192** recurrent configs out of 256 stable [85].
- Exact census: 3×3 has **100352** recurrent out of 4⁹ = 262144 (fraction ≈ 0.3828) [75].
- Forbidden-subconfiguration characterization: a stable config is transient iff it contains a subset of sites each with fewer grains than its neighbors-within-subset count — equivalent to burning, cross-checked on the full 2×2 and sampled 3×3 [60].
- Stationarity: under seeded driving on 2×2, the empirical distribution over the 192 recurrent states is uniform within a stated chi-square bound at 10⁶ seeded drops [60].

**How.** First discover recurrence empirically (drive long, log revisited states), then hunt a static test that predicts membership. The agent may reinvent burning via "can this config be reached from all-3s?" — also correct, also checkable.

**Traps.** Conflating "stable" with "recurrent" (the classic error that poisons Phase 4); 3×3 census is 262144 burn tests — cheap, but a per-test allocation sloppiness blows the timeout; burning-test direction confusion (fire *from* the sink inward).

**Unlocks.** The group's underlying set; the census numbers Phase 5 must independently re-derive.

### Phase 4 — the sandpile group

**Goal.** Recurrent configs under (pointwise add, then stabilize) form a finite abelian group; compute its identity exactly and probe its structure.

**Instruments.** `sgroup.py` — ⊕ operation, identity construction, inverse solver, element order; identity renderer (text art) for eyeballing structure.

**Predicted claims.**
- Closure and commutativity: r ⊕ s is recurrent and r ⊕ s = s ⊕ r, exhaustive on 2×2 (192² pairs), seeded samples on 3×3 [80].
- Identity construction: e = stabilize(2σmax − stabilize(2σmax)) is recurrent and satisfies e ⊕ r = r for **all** 192 recurrent 2×2 configs and 500 seeded 3×3 recurrent configs [75].
- Inverses: every recurrent r has a unique recurrent inverse with r ⊕ r⁻¹ = e, exhaustive on 2×2 [75].
- The identity is *not* neutral on transient configs: exhibit a stable transient t with t ⊕ e ≠ t — the discriminating experiment that proves the group lives on recurrent configs only [70].
- Identity computed exactly for N ∈ {2..16} in one 30s budget; stored as exact grids; its center is a growing patch of all-2s [65].

**How.** The 2σmax construction is the known-shaped experiment; whether the agent finds it or discovers e as the driving chain's "do-nothing" element is itself informative. Element orders via repeated ⊕ give first structural data (exponent of the group divides lcm of sampled orders).

**Traps.** Testing e ⊕ t = t on transients and "refuting" the group (scope!); pointwise subtraction producing negative cells (the construction is subtract-then-stabilize in the right order); identity for N = 16 needs the fast engine, not a naive scan.

**Unlocks.** Exact identities feed Phase 7's scaling study; group order sampling motivates Phase 5.

### Phase 5 — the crown: |G| = det Δ′ = spanning trees

**Goal.** Three independent computations of one number: burning-test census, determinant of the reduced Laplacian, and a spanning-tree count of the sink-augmented graph — exact agreement.

**Instruments.** `bareiss.py` — fraction-free integer determinant (exact, stdlib); `treecount.py` — spanning-tree counter by deletion–contraction with memo, or direct enumeration for tiny graphs; `laplacian.py` — Δ′ = 4I − A builder.

**Predicted claims.**
- det Δ′(2×2) = **192** = recurrent census = spanning trees of the 2×2 grid plus sink (trees enumerated directly) — three-way exact equality [70].
- det Δ′(3×3) = **100352** = burning census; tree count re-derived by deletion–contraction, not determinant, so the two sides are computationally independent [60].
- Extension: det Δ′ equals seeded structural evidence on 4×4 (order sampling: every sampled element's order divides det; chain period statistics consistent) where full census is infeasible [55].
- Growth law: log det Δ′(N) / N² converges toward ≈ 1.166 (numerically, N up to 32 via Bareiss), stated with tolerance ±0.01 [55].
- Smith normal form of Δ′ gives invariant factors whose product is det and which match the orders of sampled group elements on 2×2 and 3×3 exactly [50].

**How.** The danger is circularity — the check must compute both sides by different code paths. Deletion–contraction with a cache is stdlib-feasible to 4×4 (25-vertex graph, memoized). SNF via exact integer row/column reduction is a one-file tool.

**Traps.** Float determinants (must be Bareiss/integer — a float det "verifying" 100352±ε is not a proof); tree counting by matrix–tree *is* the determinant (circular); 4×4 tree enumeration without memoization explodes.

**Unlocks.** The archive's flagship cross-domain identity; SNF machinery for full group-structure claims.

### Phase 6 — criticality: avalanche statistics

**Goal.** Self-organized criticality under seeded random driving — power laws with stated exponents and honest tolerances.

**Instruments.** `drive.py` — seeded drop-stabilize-record loop logging avalanche size s (topplings), duration (parallel wave steps), area (distinct toppled sites); `fitloglog.py` — windowed log-log slope with explicit fit range.

**Predicted claims.**
- After a seeded burn-in on N = 32, the system sits at mean height ≈ 2.12 ± 0.03 grains/site, exactly reproducible from the seed [75].
- Stationary height densities at center match the exact-solution values p₀ ≈ 0.074, p₁ ≈ 0.174, p₂ ≈ 0.307, p₃ ≈ 0.446 within ±0.012, seeded, N = 32, 2·10⁵ drops [55].
- Avalanche-size distribution: fitted exponent τ ∈ [1.15, 1.35] over a stated decade window on N = 64, fixed seed [60].
- Duration exponent fitted in [1.3, 1.7] same protocol [50].
- Cutoff scaling: the largest avalanche size grows with N (32 vs 64, seeded), i.e. the power law's cutoff is a finite-size effect, not physics [65].

**How.** Everything seeded and windowed; the check replays the exact run. N = 64 with 10⁵ drops is the 30s ceiling for pure Python — profile first.

**Traps.** Unseeded statistics (the sim-life burn); fitting through the cutoff bump; claiming a clean power law when BTW famously multiscales — if the fitted slope drifts with window, *that drift* is the honest claim; burn-in too short so transient contaminates.

**Unlocks.** The multiscaling anomaly is the parked question that feeds the endgame.

### Phase 7 — the identity's shape and the frontier

**Goal.** Structure of the identity element as N grows; last exact claims before open research.

**Instruments.** Phase 4 identity pipeline pushed to the timeout edge; `imgdiff.py` — exact comparison of identity sub-blocks across N.

**Predicted claims.**
- Identity symmetry: e(N) is invariant under the dihedral group of the square (all 8 symmetries), exactly, for every computed N [80].
- The central all-2 square's side length grows at least linearly in N over N ∈ {8..48}, monotone, exact per N [60].
- Self-similar filigree: the corner motif of e(2N) contains an exact or near-exact (stated Hamming tolerance) copy of structures in e(N) for at least two N pairs [40].
- e(N) computable to N ≈ 64 within 30s with the tuned engine; per-N grids archived exactly as data for any future claim [60].

**How.** Compute once, archive grids as tool data; claims compare stored exact artifacts, so checks are instant.

**Traps.** "Fractal" as a vibe instead of a measured statement — every self-similarity claim needs a pixel-exact or tolerance-stated comparison; timeout cliff at large N (bisect the feasible N first, claim inside it).

**Unlocks.** Nothing after — this phase's parked questions *are* the boundary.

## Endgame

**Completed archive looks like:** a validated engine plus ~10 tools (stabilizer, odometer, burning test, group arithmetic, Bareiss determinant, tree counter, SNF, seeded driver, fitters); ~25–30 claims spanning: abelian property and odometer invariance; least action; maximal-config wave; exact recurrent censuses (192, 100352); full group axioms with exhaustive 2×2 verification; the three-way crown identity on 2×2 and 3×3; identity elements archived to N ≈ 64 with symmetry and core-growth claims; seeded height densities and avalanche exponents with tolerances; the tree-entropy growth constant.

**Stopping criteria.** Stop when (1) every exact claim reachable under 30s/stdlib is admitted and verified twice, (2) remaining questions all require either asymptotics (N → ∞) or non-grid graphs, and (3) two consecutive sessions produce only refinements of existing tolerances, not new structure.

**Open-research boundary.** Three walls, honestly marked: the *identity scaling limit* — whether e(N)/N converges to a limiting fractal object is genuinely open mathematics (Levine–Pegden-adjacent); the harness can archive evidence (motif recurrence rates vs N) but no check can decide a limit. *Avalanche exponent universality* — whether τ is identical across grid shapes touches the unresolved multiscaling of BTW; the agent can claim seeded per-shape fits and their disagreement, not universality. *Exact τ* — no closed form is known; any claim of one should be treated as an error, not a discovery.

## Harness strain

Pure-stdlib toppling caps throughput near ~10⁶ topplings/sec — Phase 6 statistics and Phase 7 large-N identities press directly on the 30s wall; expect the agent to spend threads on engine tuning that a numpy world wouldn't need (this is fine: the engine *is* a discovery). The crown claim strains the check-independence norm — the gate can't see that det and tree count share code, so circular verification is admissible-but-hollow; watch whether the agent polices itself. Limit claims (Phase 7, endgame) strain the claim grammar itself: "converges" is uncheckable, so honest phrasing degenerates to finite tables — the busybeaver lesson recurring in analytic form. Exhaustive 3×3 work sits right at timeout; a slow burn implementation flips exact censuses from cheap to impossible.

## Methodology attractor

This world rewards a recognizable strategy and should evolve toward it: **compute exact small, conjecture from the table, verify the next case independently.** The winning methodology will likely converge on rules like: one claim per thread; every number derived two ways before claiming; scope every claim to explicit N; seed everything; archive computed artifacts (identities, censuses) as tool data so later checks are lookups. The failure attractor to watch: statistical Phase 6 comfort — endless exponent refits are cheap fitness while the group-theoretic phases demand harder, riskier threads. If evolution promotes a methodology that avoids algebra for avalanche fitting, the counter-signal is audit uplift, and the human lever is seeding `archive/open-questions/` with "what is the order of the group?"
