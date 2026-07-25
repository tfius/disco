# eca — full discovery program

## Where it stands

Seven claims in, all in the linear/bijective corner: rules 90 and 150 characterized as circulant GF(2) maps with exact singularity laws, the exactly-6-bijective and exactly-16-affine censuses, bijective cycle structure, and a rule 30 transient census. Toolbox holds GF(2) rank machinery (`eca_linear_gf2.py`, `eca_rule150_gf2.py`) but no general 256-rule engine yet. The world carries disco's first PROMOTED methodology — single falsifiable claims, concrete scoreable predictions — which is exactly the discipline the next phases stress-test. Everything below is phrased periodic (cyclic width N) or windowed (finite space-time patch); infinite-tape statements are banned by world.md and unenforceable by check.py anyway.

## Phase map

### Phase 1 — Symmetry quotient: 256 → 88

**Goal.** Collapse the rule space under mirror (left-right reflection) and complement (0↔1 conjugation) before any further census; every later claim inherits an ×~3 discount.
**Instruments.** `eca_engine.py` (bit-parallel stepper for all 256 rules on cyclic tapes — the world's Life-engine moment); `rule_symmetry.py` (mirror/complement/both as truth-table permutations, canonical-representative function).
**Predicted claims.**
- Mirror, complement, and mirror∘complement are the only nontrivial members of the symmetry group; orbit census yields exactly 88 equivalence classes [90].
- Orbit sizes distribution summing to 256 (8 self-symmetric-under-all rules incl. 51, 204) claimed exactly [75].
- Dynamical invariance: for every rule pair related by mirror, cycle-length multisets on cyclic N ≤ 10 are identical; for complement pairs, identical after state conjugation — verified exhaustively [85].
- The 6 bijective rules occupy exactly 3 classes and the 16 affine rules exactly 7 or 8 classes (re-expressing prior claims in quotient terms) [70].
**How.** Truth-table index permutation for mirror (bit-reverse the 3-cell neighborhood), complement (conjugate input and output); brute-force orbit enumeration is microseconds. Dynamical check simulates all 2^N states for N ≤ 10.
**Traps.** The classic mirror off-by-one (reflecting neighborhood bits 0↔2, forgetting the output bit is untouched); claiming "88" from a buggy canonicalization that happens to hit 88 by compensating errors — cross-check via two independent canonical forms. Complement conjugates *states*, so cycle multisets match only after the conjugation map; predicting raw equality would be falsified.
**Unlocks.** Class-representative iteration for all later censuses; `eca_engine.py` becomes the universal instrument.

### Phase 2 — Surjectivity census and garden-of-Eden duality

**Goal.** Decide surjectivity for all 256 rules exactly; tie orphan words to erasability (Moore–Myhill, windowed).
**Instruments.** `debruijn.py` (de Bruijn graph of 2-cell overlaps; subset-construction decision for surjectivity; shortest-orphan-word finder); preimage counter on cyclic tapes.
**Predicted claims.**
- Exactly 70 rules have balanced truth tables (four neighborhoods → 1), exactly 30 are surjective by the de Bruijn subset construction; balance is necessary but not sufficient, 40-rule gap [85].
- Every non-surjective rule has an orphan (garden-of-Eden) word of length ≤ 6 windowed; every surjective rule has none up to length 12 — exhaustive over 256 rules [70].
- Windowed Moore–Myhill: for every rule, an orphan word of length ≤ L exists ⟺ a mutually erasable pair of length ≤ L′ exists; verified as an exact biconditional over all 256 rules at tested L [60 — the finite-L bound coupling is the risk].
- On cyclic tapes: for each of the 30 surjective rules, the count of unreachable states at width N is 0 exactly when the induced map is injective at that N; rule 90 exhibits both behaviors (N odd vs even), reconciling surjectivity-on-words with singularity-on-cycles [80].
**Traps.** Conflating infinite-tape surjectivity with cyclic-tape surjectivity — rule 90 is surjective as a word map yet 4-to-1 on even N (prior singularity claims already prove this); any claim mixing the two dies at check. Orphan length bounds must be stated as tested constants, not "always."
**Unlocks.** The surjective-30 list feeds Phase 3 (linear surjective rules) and Phase 5 (rule 30 is surjective and left-permutative — mechanism behind its randomness).

### Phase 3 — Cycle-length algebra for the linear family

**Goal.** Replace simulation with algebra: cycle lengths of rules 90/150 (and the full 16 affine) from the multiplicative order of the rule polynomial in GF(2)[x]/(x^N + 1).
**Instruments.** `gf2poly.py` (polynomial arithmetic mod x^N+1, gcd, factorization of x^N+1 over GF(2), multiplicative order); extends inherited rank tools.
**Predicted claims.**
- For odd N in 3..25, the maximal rule 90 cycle length equals ord of (x + x^(N−1)) in the unit group of GF(2)[x]/(x^N+1), and every cycle length divides it [80].
- For even N, max cycle length obeys the same law on the invertible subspace: quotient by ker gives ord computed mod (x^N+1)/gcd(x^N+1, x^2+1) — matching the known Martin–Odlyzko–Wolfram structure, verified N ≤ 24 [65].
- Rule 150 analogue with polynomial 1 + x + x^2 (shifted), singular exactly when gcd(1+x+x^2, x^N+1) ≠ 1 i.e. 3 | N — algebra reproduces the archived singularity law and predicts max periods for N ≤ 25 [75].
- In-degree structure: every state of rule 90 at width N has in-degree 0 or exactly 2^(N − rank), uniform — tree-crowns on cycles, verified exhaustively N ≤ 16 [85].
- Affine rules (XOR complement class, e.g. 105): periods equal linear-part periods up to factor ≤ 2, verified N ≤ 16 [55].
**Traps.** Sign/exponent conventions (x vs x^(N−1) for left neighbor) silently shift polynomials; verify algebra against brute-force simulation at every claimed N — the engine is the oracle, the algebra is the claim.
**Unlocks.** First "theory beats simulation" claims: checks that compute predictions algebraically then confirm by stepping. Template for exact-solvability claims.

### Phase 4 — Rigorous taxonomy: measurable Wolfram classes

**Goal.** Turn Wolfram's I–IV eyeball classes into numbers: every one of the 88 classes gets (compression ratio, damage-spreading rate, transient/period stats) and a reproducible class label.
**Instruments.** `spacetime.py` (windowed space-time patch generator, zlib-compression ratio metric); `damage.py` (Lyapunov-like: flip center cell, track Hamming-distance front speed and mass, averaged over random ICs, fixed seeds).
**Predicted claims.**
- Compression ratio of the space-time patch (width 400, 400 steps, density-0.5 IC, fixed seed set) separates the 88 classes into 4 clusters with the classic members placed correctly: class III (30, 45, 106…) high, class I/II low, rules 54/110 strictly between — exact thresholds committed before measurement [55].
- Damage spreading: rules 90, 150 have exact front speed 1 both directions (algebra forces it); rule 30 has right-front speed 1 and left-front speed strictly between 0.2 and 0.3 (measured asymmetry), reproducible across seed sets [70].
- Class-IV candidates by joint criterion (mid compression, sub-ballistic damage, long transients) = exactly the classes of {54, 110} plus at most 2 surprises among 88 [50].
- Taxonomy is symmetry-invariant: both metrics agree within tolerance across each 88-class orbit [80].
**Traps.** Seed-sensitivity — all stochastic metrics must fix seeds and claim exact values on those seeds, plus tolerance bands as separate claims; zlib version drift (pin claim to observed byte counts on this stdlib, or claim ratios coarse enough to survive).
**Unlocks.** A quantitative shortlist of complex rules justifying Phases 6–8; damage instrument reused for rule 30 diffusion.

### Phase 5 — Rule 30 randomness batteries

**Goal.** Substantiate "rule 30's center column is random-looking" as exact windowed statistics, and pin the mechanism (left-permutativity).
**Instruments.** `battery.py` (monobit frequency, block frequency, serial correlation, k-gram chi-square, longest-run, windowed period search); wide-tape windowed stepper (light-cone-exact: width 2T+1 suffices for T steps of center column from single-1 IC).
**Predicted claims.**
- Center column, first 2^16 steps from single 1 on light-cone-sufficient tape: monobit count within 3σ, all 8-gram chi-square statistics inside committed bounds, serial correlation |r| < 0.01 — exact computed values archived as constants [75].
- No period ≤ 2^13 in the first 2^16 center-column bits (windowed aperiodicity) [90].
- Rule 30 is left-permutative (fixing right two neighbors, output is a bijection of left cell) — mechanism claim, exhaustive over 8 neighborhoods, and consequently every finite column window has full preimage diversity: all 2^k right-extensions realized, tested k ≤ 12 [80].
- Contrast control: same battery on rule 90's center column fails (Pascal-mod-2 structure), exact failure mode predicted [85].
- Rule 90 Sierpinski–Lucas correspondence: from single 1, cell (t, i) nonzero iff k AND (t−k) = 0 for k=(t+i)/2 (Lucas), verified cell-exact on the full window t ≤ 512 [85].
**Traps.** Battery thresholds are statistics — commit exact observed constants so verify re-derives deterministically; the 30s timeout caps window sizes (center column only needs width 2·2^16+1 with bit-parallel stepping ≈ seconds; measure first, then size the claim).
**Unlocks.** Battery instrument for any rule; the Lucas claim seeds algebraic pattern-claims for other additive rules.

### Phase 6 — Particle physics of rule 54

**Goal.** The easier class-IV rule first: identify the ether, build the particle catalog, tabulate collisions — establishing the background-subtraction and tracking instruments 110 will need.
**Instruments.** `ether.py` (detect spatially/temporally periodic background by autocorrelation of space-time patches; ether-subtraction mask); `particles.py` (connected defect tracking, velocity/period fingerprinting); `collide.py` (place two particles at controlled phases/gaps, classify outcome window against catalog).
**Predicted claims.**
- Rule 54 ether: spatial period 4, temporal period 4, exact tile committed; random ICs on cyclic N ≡ 0 mod 4 condense to ether+defects within T ≤ 2N steps at tested widths [70].
- Fundamental particles: two gliders (velocity ±1) and at least one stationary composite; catalog closed — random-soup census at widths ≤ 1000, every persistent defect matches a catalog entry [60].
- Collision table: w⁺ + w⁻ outcomes depend only on relative phase mod ether period; complete table (one claim per collision class) with cell-exact result windows [65].
- A bound composite ("molecule") exists with period > 4 formed by a specific tabulated collision, reproducible from a committed IC [55].
**Traps.** Phase bookkeeping — collision outcome depends on relative phase and gap mod 4; a table ignoring phase gets falsified immediately. Cyclic-width interference: keep tapes wide enough that light cones don't wrap before the outcome window closes; state the width in the claim.
**Unlocks.** The whole particle toolchain, validated on the easy case; collision-claim template (IC bitstring + step count + expected output window = perfectly checkable).

### Phase 7 — Particle physics of rule 110

**Goal.** The real catalog: ether, the glider zoo, and a collision table for the pairs that matter for computation.
**Instruments.** Phase 6 toolchain; `glider110.py` (library of known-by-discovery gliders as ether-phase-tagged templates: expect ≈ a dozen distinct velocity/period classes, though the agent must earn them from soup).
**Predicted claims.**
- Ether: spatial period 14, temporal period 7, exact tile committed; soups condense to ether+gliders at tested widths [70].
- Glider census from N ≤ 2000 soups: at least 8 distinct (velocity, period) fingerprint classes, each with a committed template reproducible from a minimal IC on ether background [60].
- Per-pair collision claims: at least 6 collision classes fully tabulated cell-exact as a function of phase/gap class [50].
- A breeding collision exists: some tabulated collision emits ≥ 3 gliders including one of the incoming types, committed IC [45].
- Extended structures: a block family used as tape data admits a stability claim — blocks are transparent to a specific glider type, cell-exact [40].
**Traps.** Hardest phase for the harness: glider identification is pattern-matching against a period-7×14 background — off-by-one in ether phase makes every template mismatch; 30s timeout forces widths ≤ ~4000 and step counts ≤ ~10^4 with a bit-parallel engine. Expect parked questions; that is the system working.
**Unlocks.** Everything Phase 8 needs: gliders as stable, placeable, phase-addressable objects.

### Phase 8 — Universality scaffolding (far endgame)

**Goal.** Not a universality proof — a checkable ladder toward it: gliders as signals, collisions as gates, one verified compound computation in Cook's style.
**Instruments.** `assembler110.py` (compile a spec — glider types, phases, gaps — into an IC bitstring on ether); collision-sequence verifier.
**Predicted claims.**
- Signal fidelity: a glider train of k gliders with committed spacings propagates intact for T ≥ 5000 steps, cell-exact at arrival window, k ≤ 4 [65].
- A two-input collision implementing a distinguishable binary interaction: presence/absence of glider X at phase p flips the outcome class of a downstream collision — an honest "gate-like" claim with all four input cases committed [45].
- A cyclic-tag-system fragment: a prepared tape executes one production step — appendant emitted iff leading symbol is 1 — verified cell-exact after committed T, for 2 committed tape words [30].
- Negative/boundary claim: the same construction on cyclic width below a committed threshold self-destructs by wraparound interference — quantifying why universality claims cannot close on periodic tapes [60].
**Traps.** This is where "no infinite-tape claims" bites hardest: Cook's proof needs periodic-but-unbounded background; every claim here must be a finite windowed instance with explicit T, W. Assembly is brittle — one phase error and 10^4 steps of garbage; build the assembler's self-test first. Timeout pressure is maximal: bit-parallel stepping (Python ints as tapes) is mandatory.
**Unlocks.** Endgame. Anything past this is open research.

## Endgame

**Completed archive looks like:** ~45–65 claims. The 88-class quotient with dynamical invariance; surjectivity fully censused (70 balanced / 30 surjective / orphan-word bounds / windowed Moore–Myhill); the 16-rule affine family exactly solved (cycle algebra from polynomial orders, singularity laws, in-degree structure, Lucas correspondence); a numeric taxonomy over all 88 classes with committed metrics; rule 30 batteries plus mechanism (left-permutativity) plus control contrasts; closed particle catalogs and collision tables for 54 and 110 at tested widths; at least one verified multi-glider computation and one wraparound-failure boundary claim. Toolbox: engine, symmetry, de Bruijn, GF(2) polynomials, space-time metrics, ether/particle/collision/assembler stack — each earned by the claims that needed it.

**Stopping criteria:** (1) every one of the 88 classes carries at least a taxonomy claim; (2) the linear family needs no further simulation — algebra predicts, checks confirm; (3) soup censuses at the largest timeout-feasible widths produce no uncataloged persistent defect for 54 and 110; (4) the Phase 8 ladder has one rung verified and the next rung demonstrably exceeds the 30s/width budget. When new threads only re-derive class members' known metrics, the world is mined out at this harness's resolution.

**Open-research boundary (unclaimable here, honestly parked):** rule 30 center-column aperiodicity beyond any window (a real open problem — only windowed bounds are checkable); full rule 110 universality (requires unbounded periodic background; the harness can hold the scaffolding, never the theorem); exact topological entropy of nonlinear chaotic rules; asymptotic (N→∞) cycle-length laws stated as limits. These live in `open-questions/` as the permanent horizon.

## Harness strain

The 30s timeout is the binding constraint from Phase 6 on: collision and signal-fidelity experiments need width ~10^3–10^4 × steps ~10^4, feasible only with bit-parallel integer tapes — a slow engine silently converts hard claims into timeouts. Verify cost compounds: every check re-simulates, so a 60-claim archive with 5s checks is a 5-minute verify before *every* run session; checks must stay ≤ a few seconds, pushing toward smaller committed windows than the discovery experiments used. The PROMOTED one-claim-per-thread methodology collides with table-shaped results (a collision *table* wants either one claim per collision class or a single claim over a committed table checksum; expect friction and methodology text addressing it). Stochastic metrics (Phase 4–5) strain the "no environment-varying claims" rule — resolved only by fixed seeds and exact archived constants. Judge scoring strains on highly technical predictions where surprise is binary rather than graded. Stdlib-only is comfortable throughout (zlib, no numpy needed given int-bitmask tapes).

## Methodology attractor

Fitness (+3 admitted, −2 rejected) pulls toward the census attractor: exhaustive small-N enumeration claims are nearly rejection-proof, and Phases 1–3 supply a long queue of them — expect the methodology to stay in its current "single exact claim, concrete prediction" basin and sharpen toward *atlas-building*: enumerate, tabulate, quotient. The danger is Phase 6–8 avoidance: particle claims carry real rejection risk (phase bookkeeping, timeout), so evolution may select methodologies that rationally never leave the solvable corner — the uplift audit and human seeds ("what survives in rule 110 soup?") are the counter-pressure. Predicted methodology mutations if the program runs long: (1) an *instrument-first* clause — spend a thread building/validating a tool with no claim, eating the fitness cost to unlock a claim-rich vein; (2) a *claim-granularity* clause — decompose tables into per-entry claims; (3) a *committed-constants* clause — always archive exact measured values with seeds, born from the first stochastic-claim rejection. If a variant ever promotes "prefer claims whose check is algebra confirmed by simulation," the world has taught the agent the difference between computing and understanding — the best possible ending.
