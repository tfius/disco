# logistic — full discovery program

## Where it stands

Untouched: no claims, no tools, no open questions — the archive is empty and every instrument below must be earned from a bare `x -> r*x*(1-x)`.

## Phase map

### Phase 1 — Orbit machinery and the exact fixed-point skeleton

**Goal.** Build the core instrument (iterate, burn-in, period-detect) and nail the algebraically exact facts before touching anything float-fuzzy.

**Instruments to bank.** `orbit(r, x0, n_burn, n_keep)`; `detect_period(tail, tol)` returning smallest p with `|x[i+p]-x[i]| < tol` over a full window; `logistic_exact(r, x)` over `fractions.Fraction`; `fp_derivative(r)` = |f'(x*)| = |2−r| symbolically.

**Predicted claims.**
- C1.1: x* = 1−1/r satisfies f(x*) = x* exactly in `Fraction` arithmetic for 20 rationals r ∈ (1,4]; check is pure algebra, zero tolerance. [95]
- C1.2: |f'(1−1/r)| = |2−r| exactly (Fraction), hence stability iff 1 < r < 3; boundary r = 3 exact. [92]
- C1.3: for r ∈ {2.5, 2.8, 2.9} orbits from x0 ∈ {0.1, 0.31, 0.77} converge to 1−1/r within 1e−12 after 10,000 iterations. [90]
- C1.4: for 0 < r < 1, all orbits from x0 ∈ (0,1) reach x < 1e−10 within 5,000 iterations (extinction); at r = 2 convergence is superexponential — claim < 1e−15 by iteration 10 from x0 = 0.3. [80]

**How.** Two experiments per claim minimum: one float, one `Fraction` where algebra permits. Burn-in default 1,000, escalating to 100,000 near r = 3 (transient time diverges like 1/|r−3|). All x0 seeds stated literally in check.py.

**Traps.** Period detection with fixed tol misfires near bifurcations where convergence is algebraic, not geometric — burn-in must scale as ~10/|r−r_c|. x0 = 0.5 hits the critical point (useful later, misleading now). Never claim "converges at r = 3.0 exactly" — it does, but at O(1/n), slower than any budget suggests.

**Unlocks.** Every later phase imports `orbit`/`detect_period`. Exact-substitution habit (Fraction algebra as oracle) becomes the world's signature move.

### Phase 2 — Period-2 branch and the first irrational threshold

**Goal.** Characterize the 2-cycle born at r = 3 and prove its death at exactly r = 1+√6, the first bifurcation value that is algebraic but irrational.

**Instruments to bank.** `cycle2_points(r)` (closed form); `poly_check` — verify a candidate cycle by polynomial substitution in `Fraction`; polynomial-coefficient arithmetic (symbolic r as coefficient lists).

**Predicted claims.**
- C2.1: for r ∈ (3, 1+√6), the 2-cycle points satisfy f(f(x)) = x, x ≠ x*; verified by exact Fraction substitution at rational r ∈ {13/4, 17/5, 10/3}. [85]
- C2.2: 2-cycle multiplier is −r² + 2r + 4 (polynomial identity in r, provable by exact expansion of f∘f at the cycle); equals −1 exactly when r² − 2r − 5 = 0, i.e. r = 1+√6. Check via ℚ(√6) two-element field implementation, plus numeric bracket with multiplier crossing −1 within 1e−9. [75]
- C2.3: numerically, period-2 detected for r ∈ {3.1, 3.2, 3.4} and period-4 for r ∈ {3.46, 3.5}, tol 1e−9, burn-in 200,000, from x0 = 0.4 and x0 = 0.65 (two seeds = two experiments). [85]
- C2.4: bisection on "detected period ≤ 2" locates r₂ = 3.449490 ± 5e−6, and |r₂ − (1+√6)| < 5e−6. [80]

**How.** The multiplier identity is the pivot: derive it by expanding f(f(x)) − x, factoring out (x − x*), then Vieta on the remaining quadratic — all doable in `fractions` with symbolic r as polynomial coefficient lists (bank this mini poly-arithmetic tool; it pays off in Phase 4).

**Traps.** Near r = 1+√6 the 2-cycle is neutrally stable — convergence stalls; bisection on *detected period* is robust where convergence-based tests hang. Don't bisect with fixed burn-in; double it each time the detector returns "no period found."

**Unlocks.** Polynomial-coefficient arithmetic tool; ℚ(√d) exact checks; the bisection-on-period template used for the whole cascade.

### Phase 3 — Cascade, superstable ladder, Feigenbaum δ

**Goal.** Measure r₃…r₇ (or as deep as float64 allows), extract δ to 3–4 significant digits with an honest error bar.

**Instruments to bank.** `bisect_period_doubling(p, lo, hi, tol_r)`; `superstable_r(p)` — solve f^p(1/2) = 1/2 by bisection/secant in r; `delta_estimates(rs)`.

**Predicted claims.**
- C3.1: bisection values r₁ = 3.000000(1), r₂ = 3.449490(1), r₃ = 3.544090 ± 2e−5, r₄ = 3.564407 ± 2e−5, r₅ = 3.568759 ± 5e−5; burn-in 5·10⁵, tol 1e−10, x0 = 0.4, each value replicated from x0 = 0.6. [75]
- C3.2: superstable parameters R_n are cleaner: R₁ = 2 exact (Fraction check), R₂ = 3.2360680 ± 1e−6 (= 1+√5, exact check via r²−2r−4=0), R₃ = 3.4985617 ± 1e−6. [70]
- C3.3: δ_n from the superstable ladder gives δ₄ ∈ [4.65, 4.69]; claim δ = 4.669 ± 0.01. [70]
- C3.4: accumulation point r∞ = 3.569946 ± 1e−4 by geometric extrapolation r∞ ≈ r_n + (r_n − r_{n−1})/(δ−1). [65]

**How.** Superstable points are numerically cleaner because f'(1/2) = 0 makes the cycle maximally attracting — convergence is quadratic, immune to critical slowing, and f^p(1/2) − 1/2 is a smooth function of r with a simple zero, ideal for the secant method. This is the phase's key methodological discovery; predict it, then demonstrate the contrast.

**Traps.** The trap named in predictions.md: claiming digits of δ beyond what float64 + finite cascade depth supports. By n = 8 spacing ~1e−6 rides on orbit noise — stop at the level where two seeds disagree beyond tol_r, and state that as the cutoff rule inside the claim.

**Unlocks.** δ machinery reused verbatim in Phase 7 (universality). r∞ pins the chaos frontier for Phases 4–5.

### Phase 4 — Windows in chaos: period 3, self-similarity, Sharkovskii evidence

**Goal.** Map the periodic windows above r∞; prove the period-3 window opens at exactly r = 1+√8.

**Instruments to bank.** `find_windows(r_lo, r_hi, dr, max_period)` scanner; reuse poly-arithmetic for f³ algebra.

**Predicted claims.**
- C4.1: stable period-3 detected for r ∈ [3.8285, 3.8415] (tol 1e−9, burn-in 10⁶, x0 = 0.5 — critical-point seed finds the attractor whenever one exists); no period ≤ 64 detected at r = 3.8280 from 5 seeds. [80]
- C4.2: window opens by tangent bifurcation at r = 1+√8 = 3.8284271…; check: at r = 1+√8, f³(x) − x acquires a double root — verified by exact arithmetic in ℚ(√2), plus numeric bracket: period-3 exists at r = 3.82843, absent at 3.82842. [65]
- C4.3: inside the window the 3-cycle period-doubles: period 6 at r = 3.8445 ± 5e−4, period 12 near 3.8494; window-internal δ estimate ∈ [4.2, 5.1] (only 2–3 levels reachable — wide bar, honestly stated). [65]
- C4.4: window census on [3.57, 4.0] at dr = 1e−4: windows of basic period 3, 5, 6 ranked by width; period-3 widest (~0.0136), period-5 near 3.7382 width ~2e−3, period-6 near 3.6265. [70]
- C4.5: Sharkovskii evidence: at r = 3.8284272 (period 3 stable) unstable periodic orbits of every period p ≤ 10 exist — located as roots of f^p(x) − x via sign-change scan + bisection; whereas at r = 3.5 (period-4 regime) no period-3 or period-5 orbit points exist. [60]

**How.** Root-count on f^p(x) − x is the honest Sharkovskii instrument: "period 3 implies all periods" becomes a countable, checkable statement about polynomial roots in [0,1]. Two experiments: root census at two r values on each side of the window edge.

**Traps.** At tangency, intermittency: orbits spend 10⁵+ iterations in near-period-3 laminar phases below the window — the period detector reports false 3s if tol is loose. Tighten tol to 1e−11 and require persistence over 1,000 consecutive windows. f^p as an explicit polynomial has astronomical coefficients for p > 6 — evaluate by iterated Horner, never expand beyond p = 4 symbolically except the p = 3 exact check.

**Unlocks.** Window map feeds cartography (Phase 6); tangent-bifurcation concept distinguishes the two ways periodicity is born.

### Phase 5 — Lyapunov exponent and the exactly-solvable summit at r = 4

**Goal.** Quantify chaos: λ(r) machinery, its zero-crossings at bifurcations, and the exact result λ = ln 2 at r = 4.

**Instruments to bank.** `lyapunov(r, x0, n_burn, n)` = mean of ln|r(1−2x)| along the orbit; `theta_orbit` — the conjugacy x_n = sin²(2ⁿ θ π) as an independent predictor.

**Predicted claims.**
- C5.1: λ < 0 on periodic regime, λ = 0 ± 0.002 at r₁, r₂ (measured at r ± 1e−6), λ first sustains > 0 at r = 3.56995 ± 2e−4, matching r∞ from Phase 3 within combined tolerance — two independent instruments agreeing is the claim. [70]
- C5.2: λ(4) = ln 2 ± 0.001 with n = 10⁷, burn-in 10³, averaged over seeds x0 ∈ {0.123, 0.456, 0.789} (each within ±0.003 individually). [80]
- C5.3: closed form at r = 4: x_n = sin²(2ⁿ arcsin(√x0)) reproduces the iterated orbit — but only for ~50 steps in float64 before exponential error growth destroys agreement; claim: max n with agreement < 1e−6 lies in [40, 60] for x0 = 0.3. Verify the formula exactly to n = 200 using `decimal` at 100 digits. [70]
- C5.4: λ dips below 0 inside every window found in Phase 4 (period-3 window: λ(3.835) < −0.05), and λ(r) has spike structure with sup on [3.57,4] attained at r = 4. [70]
- C5.5: at r = 4, orbit of any rational x0 = sin²(pπ/q) is eventually periodic; e.g. x0 = sin²(π/9) has period 3 under the exact map — checkable in `decimal` at 60 digits over 100 iterations, plus a second rational angle. [60]

**How.** The conjugacy h(θ) = sin²(πθ) turns f₄ into θ → 2θ mod 1; λ = ln 2 is then the doubling map's expansion rate — invariant under smooth conjugacy. The check pairs a long-run float average against the closed form's `decimal` ground truth: the exact solution grades the statistical instrument.

**Traps.** At r = 4 float orbits eventually hit 0 (absorbing) from unlucky seeds via x = 1 → 0; detect and restart, and say so in the claim. λ near bifurcations converges as 1/n — budget n ≥ 10⁷ there, not the 10⁵ that suffices mid-chaos.

**Unlocks.** λ(r) is the instrument that turns the bifurcation diagram from pictures into numbers; `decimal`-oracle pattern (high-precision ground truth grading float claims) becomes standard.

### Phase 6 — Bifurcation cartography as data claims

**Goal.** Compress the whole r-axis into machine-checkable structural facts.

**Instruments to bank.** `attractor_sample(r, n_keep)`; `diagram(r_grid)` — the full census, cached deterministically.

**Predicted claims.**
- C6.1: regime table for r-grid 2.5 to 4.0 step 0.001 (x0 = 0.5, burn-in 10⁵, keep 512, period-tol 1e−9): exact grid indices where detected period changes 1→2→4→8; table hash-stable across two independent runs and re-derivable in check.py from stated seeds. [80]
- C6.2: attractor width: sup of attractor samples over r ∈ [3.6,4.0] equals f(1/2) = r/4 within 1e−6 at every grid point (critical point maps to the attractor's top edge). [75]
- C6.3: band-merging (reverse cascade): 2 chaotic bands merge to 1 at r = 3.6786 ± 5e−4 (detected: odd/even iterates' ranges first overlap), 4→2 at 3.5926 ± 5e−4; merging points accumulate to r∞ from above with ratio ≈ δ (2 levels, tolerance ±0.5 on the ratio). [60]
- C6.4: fraction of grid points on [3.57, 4.0] with detected period ≤ 64 (i.e., inside windows) ∈ [0.09, 0.15] at dr = 1e−4 — a measured "windows have substantial measure" claim, deterministic given grid and seeds. [65]

**How.** Every cartography claim is a pure function of (grid, seeds, budgets) — no randomness, so checks re-derive rather than re-sample. Cache the census as a tool-generated artifact but let check.py rebuild the claimed rows from scratch within timeout (subsample rows if needed; state which).

**Traps.** 30s timeout is the binding constraint: full 1,500-point grid × 10⁵ burn-in ≈ 1.5·10⁸ map evaluations ≈ 30–60s in pure Python — checks must verify a stated random-free subsample rather than the full census. Declare that in the claim, or it culls itself on a slow machine.

**Unlocks.** The regime table is the world's atlas; C6.3's band-merging gives an independent third estimate of δ and r∞.

### Phase 7 — Universality: same δ for a different unimodal map

**Goal.** The deepest reachable fact: Feigenbaum δ is a property of the *class* (smooth unimodal, quadratic maximum), not the formula.

**Instruments to bank.** Parametrize the whole pipeline over the map: `cascade(map_fn, r_lo, r_hi)`; apply to s(x) = r·sin(πx) on [0,1], r ∈ (0,1], and optionally x → r − x².

**Predicted claims.**
- C7.1: sine map cascade: period-doubling at r₁ = 0.71999 ± 1e−4, r₂ = 0.83326 ± 1e−4, superstable ladder computed to level 5 via secant on s^p(1/2) = 1/2. [70]
- C7.2: sine-map δ estimate ∈ [4.62, 4.72], overlapping the logistic estimate 4.669 ± 0.01 from C3.3 — the universality claim proper, stated as interval overlap of two independently computed ladders with stated budgets. [65]
- C7.3: Feigenbaum α from orbit geometry: ratio of successive distances d_n = |s^{2^{n-1}}(1/2) − 1/2| at superstable parameters gives |α| ∈ [2.45, 2.56] for both maps (true 2.5029). [55]
- C7.4: contrast control: the tent map (non-smooth maximum) does *not* period-double — no stable period-2 detected anywhere on its parameter range; universality's boundary demonstrated by a map outside the class. [60]

**How.** Zero new theory — pure reuse. If Phase 3's tools were written map-generic, this phase is cheap; if not, refactor first (the refactor itself is evidence the methodology matured). Two experiments per claim = two maps or two seed sets per ladder.

**Traps.** Sine map's math.sin costs 5–10× a multiply — budgets that fit 30s for logistic overflow here; halve orbit lengths and widen tolerances accordingly, honestly. α needs one more clean cascade level than δ; don't force C7.3 if level 5 is noisy — park it as an open question instead.

**Unlocks.** Endgame. A claim that survives here is a statement about all unimodal maps, earned inside one Python process.

## Endgame

**Completed archive.** ~25–30 claims in four strata: (i) exact algebra — x*, |2−r|, r = 3, 1+√6, 1+√5 superstable, 1+√8 tangency, ln 2, rational-angle periodic orbits — all checked by `fractions`/ℚ(√d)/`decimal` with zero tolerance; (ii) measured constants — δ = 4.669 ± 0.01 from three routes (bisection ladder, superstable ladder, band-merging), r∞, α; (iii) structural cartography — regime table, window census, λ(r) profile, band merges; (iv) universality — sine-map concordance plus tent-map counterexample. Tools: orbit/period core, poly arithmetic over ℚ and ℚ(√d), superstable secant solver, Lyapunov, map-generic cascade, decimal oracle.

**Stopping criteria.** Stop when (1) every claim above is admitted or refuted with the refutation archived; (2) the marginal digit of δ requires exceeding 30s or float64 — both hard walls; (3) three consecutive threads produce surprise scores < 3 (learnability exhausted at this resolution).

**Open-research boundary.** Beyond the wall: proving δ's universality (renormalization fixed point — real math, not experiment); density of hyperbolic windows; exact arithmetic of r∞ (not known algebraic); measure of the chaotic parameter set (Jakobson — positive, but unmeasurable at this budget). These get parked as open questions with a note that the oracle cannot decide them — the honest edge of an experimental epistemology.

## Harness strain

Two designed collisions with the harness. First, **float-tolerance claims meeting an exact-execution oracle**: verify reruns check.py on any machine, and FMA/libm differences can shift a 10⁷-step chaotic orbit's mean by more than a naive tolerance — every statistical claim must carry tolerances derived from error analysis, not from "what I observed twice," or it will be culled as rot when it was really overclaiming. The exact-algebra stratum is the counterweight: Fraction checks are bit-identical everywhere and can never rot. Second, **critical slowing near bifurcations**: at r_c convergence is O(1/n), so any fixed iteration budget inside a 30s timeout fails for r close enough to r_c — claims must state the excluded neighborhood (e.g., "for |r − 3| > 1e−4") or use superstable/exact formulations that sidestep slowing entirely. The world teaches tolerance discipline by punishing its absence with culls; expect 2–4 early claims to die this way and treat each cull as data.

## Methodology attractor

The strategy this world selects for, which methodology.md should converge to: **prefer the exact formulation of every question.** Whenever a threshold is algebraic, replace "bisect until the float wiggles" with "verify the polynomial identity in Fraction" — those claims are immortal under verify, cost microseconds, and score +3 forever. Whenever a quantity must be measured, anchor it to a superstable or closed-form point where convergence is quadratic and the exact oracle can grade the float instrument. Derive tolerances before running, from error models, and state seeds/budgets as part of the claim's identity. Build every tool map-generic on first writing, because the last and best claim in this world is the one where the same code, pointed at a different map, returns the same constant.
