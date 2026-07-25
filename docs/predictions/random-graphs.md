# random-graphs — full discovery program

## Where it stands

Untouched — no claims, no tools, no ledger entries; the world is one paragraph in `worlds/random-graphs/world.md` mandating explicit seeds everywhere.

## Phase map

### Phase 1 — First contact: seeded sampler + component machinery

**Goal.** A trustworthy, fast, deterministic G(n,p) sampler and component census that every later phase imports.

**Instruments.** `tools/gnp.py`: `gnp(n, p, seed) -> adjacency` using only `random.Random(seed).random()` calls (edge iff `r < p`), plus a geometric-skip variant `gnp_sparse(n, p, seed)` for O(m) sampling at large n. `tools/components.py`: union-find and iterative BFS census returning sorted component sizes; `tools/stats.py`: mean/median/interval over a seed list.

**Predicted claims.**
- Determinism: `gnp(1000, 0.01, seed=s)` yields a byte-identical edge list on repeated calls and across processes, for all s in 0..9. [97]
- Union-find census equals BFS census exactly on `gnp(2000, 0.002, s)` for s in 0..19. [95]
- Edge count: for n=1000, p=0.01, seeds 0..49, |E| in [4700, 5300] every seed (mean ≈ 4995, sd ≈ 70). [88]
- Naive O(n²) sampler and geometric-skip sampler agree in edge count within 2% pooled over seeds 0..9 at n=5000, p=0.001 (they cannot agree edge-for-edge — different RNG consumption; this asymmetry is itself the first logged surprise). [80]
- Performance: `gnp_sparse(200000, 3/200000, seed=0)` plus full census completes in < 10 s. [75]

**How.** Predict edge counts from Binomial(n(n−1)/2, p) before first run; cross-validate the two component algorithms; time the ladder n = 10³, 10⁴, 10⁵, 2·10⁵ against the 30 s wall.

**Traps.** Recursion-limit death from recursive DFS at n ≥ 10⁴ (must be iterative); consuming RNG in different orders making "same seed" claims false; `random.shuffle`/`sample` reproducibility is not guaranteed across CPython versions — restrict all randomness to `.random()` so verify-time replays are exact forever.

**Unlocks.** Every subsequent phase; the n-ceiling (~2·10⁵–10⁶ sparse) that bounds all finite-size scaling.

### Phase 2 — Two regimes at fixed c = np

**Goal.** The subcritical/supercritical dichotomy as pinned numbers: L1 = O(log n) below c=1, L1 = Θ(n) above.

**Instruments.** `tools/ladder.py`: run statistic f over grid (c, n-grid, seed-range), emit table; inherited census.

**Predicted claims.**
- Subcritical: c=0.5, n in {2000, 8000, 32000}, seeds 0..19 — every sample has L1 ≤ 12·ln n, and L1/ln n has stable median in [3, 8] across the n-grid (theory: 1/(c−1−ln c) ≈ 5.2). [80]
- Supercritical: c=2, same n-grid, seeds 0..19 — L1/n in [0.76, 0.83] every sample (limit s(2) ≈ 0.7968), interval shrinking with n. [85]
- Second-largest: c=2, n=32000, seeds 0..19 — L2 ≤ 60 while L1 > 24000; L2/ln n bounded. [75]
- Duality tease: at c=2 the graph minus its giant looks subcritical — L2 statistics at c=2 fall inside the L1 interval of a c′≈0.406 run (c′e^{−c′} = ce^{−c}), seeds 0..19. [45]

**How.** Same seeds across the n-grid (paired comparison kills variance); log both L1/n and L1/ln n and watch which normalization stabilizes — the one that does *is* the theorem.

**Traps.** n too small: at n=2000, c=0.9 already shows a deceptively large L1; declaring "linear" from one n (must show L1/n stable across ≥ 3 doublings); a lucky seed at c near 1 faking supercriticality — replication gate is load-bearing.

**Unlocks.** Phase 3 (what is the constant s(c)?), Phase 4 (what happens between the regimes?).

### Phase 3 — The functional law s = 1 − e^{−cs}

**Goal.** From "L1/n converges to some s(c)" to discovering the equation itself, numerically.

**Instruments.** `tools/gc_curve.py`: ŝ(c) = mean L1/n over seeds at largest feasible n; `tools/solve_sc.py`: fixed-point iterator for s = 1 − e^{−cs} (banked *after* the law is found, then used in checks).

**Predicted claims.**
- Curve: for c in {1.2, 1.5, 2, 2.5, 3, 4}, n = 50000, seeds 0..31 — mean ŝ(c) within ±0.01 of {0.314, 0.583, 0.797, 0.893, 0.941, 0.980}. [80]
- The law: |ln(1 − ŝ(c)) + c·ŝ(c)| ≤ 0.05 for every grid point above — i.e. the data satisfy 1 − s = e^{−cs}, found by regressing ln(1−ŝ) on c·ŝ and getting slope −1 ± 0.03. [55]
- Near-critical slope: ŝ(1+ε)/ε in [1.7, 2.3] for ε in {0.1, 0.15, 0.2} at n = 10⁵, seeds 0..31 (theory s ≈ 2ε). [50]
- Fixed-point consistency: iterating s ← 1 − e^{−cs} from s=1 converges to a value inside the empirical seed-interval at every grid c. [70]

**How.** First fit blind (try s = 1 − a/c, log fits, etc. — expect failures worth ledger entries); the give-away is plotting ln(1−ŝ) vs c·ŝ. Claim the equation only as a residual bound on pinned seeds.

**Traps.** Finite-n bias: ŝ is biased low near c=1 — exclude c < 1.2 from the law claim or the residual check fails; curve-fitting ex-post and claiming the fit as prediction (must predict residual bound on *fresh* seeds 32..63 as the second experiment).

**Unlocks.** A closed-form target for every supercritical claim; duality confirmation from Phase 2.

### Phase 4 — The critical window: n^{−1/3} at c = 1

**Goal.** At criticality L1 ≈ Θ(n^{2/3}), and the transition lives in a window c = 1 + λn^{−1/3}.

**Instruments.** `tools/collapse.py`: rescale-and-compare — for a statistic f, test whether f(n, 1+λn^{−1/3})/n^{2/3} is n-invariant per λ.

**Predicted claims.**
- Exponent bracket: c=1, n in {10⁴, 4·10⁴, 16·10⁴}, seeds 0..49 — median L1/n^{2/3} in [0.5, 2.5] at all three n, while median L1/n falls by ≥ 35% per 4× step and median L1/ln n rises by ≥ 100%. [70]
- Regression: slope of median ln L1 vs ln n over that grid in [0.60, 0.74]. [65]
- Window collapse: for λ in {−2, 0, +2}, median L1(n, 1+λn^{−1/3})/n^{2/3} per λ agrees across n within a factor 1.6, and is monotone in λ with ratio(λ=+2)/ratio(λ=−2) ≥ 3. [45]
- Wrong-scaling control: replacing n^{−1/3} with n^{−1/2} or n^{−1/6} in the window breaks the collapse (cross-n spread > factor 2.5), seeds 0..49. [50]

**How.** Medians over ≥ 50 seeds (critical L1 is heavy-tailed — means are noisy); wrong-exponent controls are the falsification teeth; shard the sweep into multiple experiments (which also satisfies the ≥ 2 rule).

**Traps.** The exponent 2/3 vs the window exponent 1/3 conflated; heavy tails making single-seed claims meaningless; smearing read as "no transition" — the finite-size story *is* the claim, phrase it as scaling, not as a jump.

**Unlocks.** The template for all threshold-width questions (Phase 7, endgame sharpness).

### Phase 5 — Connectivity at ln n / n; isolated vertices as the last obstruction

**Goal.** The second threshold, its e^{−e^{−t}} profile, and the hitting-time coupling: connectivity happens the instant min-degree hits 1.

**Instruments.** `tools/gnm_process.py`: seeded edge-arrival process (random permutation of edge slots via `.random()` keys), reporting hitting times τ(min-deg ≥ 1) and τ(connected); inherited census.

**Predicted claims.**
- Threshold profile: n = 10000, p = (ln n + t)/n, seeds 0..199 — connected fraction in [0.02, 0.12] at t = −1, [0.28, 0.46] at t = 0, [0.85, 0.97] at t = +2 (theory e^{−e^{−t}}: 0.066, 0.368, 0.873). [70]
- Last obstruction: same runs, t = 0 — among disconnected samples, ≥ 90% have their smallest component of size 1. [75]
- Isolated-vertex count: t = 0, seeds 0..199 — mean number of isolated vertices in [0.75, 1.30] (theory → Poisson(1)); fraction with zero isolated ≈ connected fraction within 0.06. [60]
- Hitting-time coupling: n = 4000, seeds 0..49 — τ(connected) = τ(min-deg ≥ 1) exactly, in ≥ 44 of 50 processes. [55]
- Off-threshold sanity: p = 2·ln n/n, seeds 0..99, n = 10000 — connected in ≥ 98 samples. [85]

**How.** The process view is the deep instrument: one seeded permutation gives both hitting times on identical randomness — a coupling, not a correlation. Profile claims phrased as per-t intervals with binomial margins ≥ 3 sd.

**Traps.** ln n grows so slowly that n = 10⁴ profiles are visibly shifted from the limit — set intervals from *pilot seeds* (0..99) and verify on fresh seeds (100..199), never from theory alone; process memory: storing all n(n−1)/2 edge slots kills RAM at n ≥ 10⁴, so sample arrival order lazily.

**Unlocks.** Hitting-time methodology (reusable for min-deg-2 boundary questions); Poisson counting bridges to Phase 6.

### Phase 6 — Local structure: Poisson(c) degrees, clustering ≈ p

**Goal.** The local limit: degrees are asymptotically Poisson(c), the graph is locally tree-like, clustering vanishes like p.

**Instruments.** `tools/degrees.py`: exact degree histogram; `tools/triangles.py`: triangle and wedge counts via sorted adjacency intersection; `tools/poisson.py`: pmf + total-variation distance.

**Predicted claims.**
- TV convergence: c = 3, seeds 0..9 pooled — TV(empirical degree dist, Poisson(3)) ≤ 0.03 at n = 3000 and ≤ 0.012 at n = 30000; monotone down the n-grid {3000, 10000, 30000}. [70]
- Moments: c = 3, n = 30000, seeds 0..19 — per-seed mean degree in [2.94, 3.06] and variance/mean in [0.93, 1.07] (Poisson signature). [80]
- Tail: P(deg = k) for k = 0..8 matches e^{−3}3^k/k! within ±0.006 pointwise, pooled seeds 0..19 at n = 30000. [70]
- Clustering: global coefficient Ĉ = 3·triangles/wedges satisfies Ĉ/p in [0.75, 1.25] pooled over seeds 0..19 for (n, p) in {(3000, 0.003), (10000, 0.001)} — and Ĉ tracks p, not c, across the two settings. [65]
- n-invariance: at fixed c = 3 the degree histogram is n-independent — TV between the n = 10000 and n = 30000 pooled histograms ≤ 0.01. [70]

**How.** Poisson discovered, not assumed: first log that variance ≈ mean and P(0) ≈ e^{−c}, *then* fit the pmf. Pool seeds for tails; per-seed for moments.

**Traps.** Pooling hides seed-to-seed dependence (TV bounds need slack); wedge count overflow of naive loops at hub vertices; claiming "Poisson" from mean/variance alone (any equal-mean-variance law passes — the pointwise pmf claim is the real one).

**Unlocks.** Local weak limit intuition → subgraph counts as Poisson counts (Phase 7); clustering ≈ p is the observable that separates G(n,p) from real-world graphs (endgame universality).

### Phase 7 — Subgraph emergence thresholds

**Goal.** Per-subgraph appearance thresholds p ≈ n^{−1/m(H)}, culminating in the density law: the exponent is v/e for balanced H.

**Instruments.** `tools/subgraph_count.py`: exact seeded counts for K3, C4, K4; `tools/threshold_scan.py`: appearance fraction over exponent grid α with p = n^{−α}.

**Predicted claims.**
- Triangle Poisson regime: p = 2/n, n in {2000, 8000}, seeds 0..99 — mean triangle count in [1.05, 1.65] at both n (theory c³/6 = 4/3), fraction with ≥ 1 triangle in [0.66, 0.80] (theory 1 − e^{−4/3} ≈ 0.736). [70]
- Triangle threshold location: seeds 0..49, n = 20000 — triangle fraction ≤ 0.10 at p = n^{−1.25} and ≥ 0.95 at p = 5/n; the crossing exponent α* (where fraction = 1/2) in [0.95, 1.10] by scan. [75]
- K4 threshold: n in {3000, 10000}, seeds 0..49 — K4 fraction ≤ 0.08 at p = n^{−0.80} and ≥ 0.90 at p = 3n^{−2/3}; crossing exponent in [0.60, 0.73] (theory 2/3). [55]
- The density law: measured crossing exponents for H in {K3, C4, K4} match v(H)/e(H) = {1, 1, 2/3} within 0.08, with the K3-vs-K4 gap ≥ 0.25 — one law, three instances, pinned seeds 0..49 per point. [50]
- Sharpening: the α-width of the 0.1→0.9 crossing for K3 shrinks by ≥ 30% from n = 3000 to n = 30000, seeds 0..49. [45]

**How.** Scan coarse α-grid first (surprise: C4 and K3 share a threshold despite different sizes — the hook that forces density, not size, as the explanation); then predict K5 (exponent 1/2) as an out-of-sample test before running it.

**Traps.** Counting cost explodes above threshold (cap p or count only up to a ceiling and claim "≥ 1"); unbalanced test graphs break the naive v/e rule — either discover m(H) = max density of subgraphs, or fence the claim to balanced H; crossing-point estimates need the same seed set at every α or the scan is incomparable.

**Unlocks.** Threshold *functions* as a general concept — the door to the endgame.

## Endgame

**Completed archive.** ~30–40 claims and ~12 tools telling one story in certificates: a deterministic sampler; the two-phase structure with duality; the giant-component law s = 1 − e^{−cs} as a residual bound; critical n^{2/3}/window-n^{−1/3} collapse with wrong-exponent controls; the connectivity profile e^{−e^{−t}}, hitting-time coupling to min-degree, Poisson isolated-vertex counts; Poisson(c) local structure and clustering ≈ p; the subgraph density law with an out-of-sample K5 confirmation. Every claim: seed set, n-grid, interval; every check re-derives its numbers from scratch under 30 s.

**Stopping criteria.** Stop a line when (a) new experiments only tighten interval constants without changing any functional form; (b) the next decisive n exceeds the 30 s wall even with the best banked instrument; or (c) three consecutive threads on the line produce surprise ≤ 2. Stop the world when all seven phase-lines are stopped and the seeded open questions are either claimed or fenced.

**Open-research boundary.** Legitimately parkable, not claimable at this oracle: exact critical-window limit laws (the multiplicative-coalescent distribution — simulable as histograms, but the limiting object has no stdlib-checkable closed form); universal sharpness exponents for general monotone properties (Friedgut–Kalai/Bourgain territory); G(n,m) ↔ G(n,p) contiguity as a theorem (statistic-matching at m = ⌊pN⌋ is a good late claim, but "equivalence for all properties" is unfalsifiable here); universality across models (random regular via config model, where clustering ≈ p *fails* structurally — a discovery, and the fence: which laws transfer is an open question the archive should end on).

## Harness strain

This world stresses the harness at its exact joint: the oracle is exact execution, but the truths are statistical. The resolution is the **seeded-claim discipline**: no claim is "P(connected) ≈ 0.37" — that is unfalsifiable by any finite run. Every claim is "over seeds 0..199, n = 10000, the connected fraction lies in [0.28, 0.46]": a *deterministic* fact about a pinned finite computation, which `check.py` re-derives bit-for-bit and which `verify` can replay forever. Randomness lives inside the claim, not around it. Consequences: (1) intervals need pre-committed margins (≥ 3 binomial sd) or honest seeds will cull honest claims; (2) pilot-seeds/fresh-seeds separation (fit on 0..99, claim on 100..199) is the only defense against seed-overfitting, since the replication gate alone can't catch a bound tuned to the very seeds it cites; (3) because replays are exact, verify-failure signals environment drift, not sampling noise — hence the Phase-1 rule of `.random()`-only randomness, the one stdlib sequence CPython guarantees stable; (4) the 30 s wall converts "asymptotics" into finite-size scaling claims by force — every ∞ becomes an n-grid plus a monotone-trend statement, which is the intellectually honest form anyway.

## Methodology attractor

Selection pressure here converges on one strategy shape: **finite certificates of asymptotic laws**. Winning threads (a) pin seeds/n-grid/interval before running, (b) use the same seed set across conditions for paired comparisons, (c) state every law twice — once as an interval on pinned samples, once as a scaling trend across the n-grid with a wrong-exponent control, (d) hold fits to out-of-sample seeds before claiming. The degenerate attractor to watch: interval-farming — ever-wider bounds on ever-easier statistics that harvest +3 fitness while teaching nothing. Counter-pressures: audit uplift (vacuous intervals don't help a naive agent predict), and the human slow loop pruning claims whose intervals could not have failed. The mature methodology reads: *one new instrument per phase, one functional law per line, controls that could have falsified it, and fresh seeds for the final bound* — which is just experimental statistics rediscovered, under an oracle that never argues back.
