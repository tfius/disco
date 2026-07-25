# Pre-registered predictions: what each world should yield, and how

This document runs disco's own protocol on its authors: predictions committed
*before* the threads run. Score us later. It lives in `docs/` deliberately — the
kernel never injects it into agent context, so nothing here can leak into the
discovering. When the agent's path diverges from these arcs, that divergence is
data: either about the agent's blind spots or about ours.

Each world: **Terrain** (what is actually there to find), **Expected arc** (the
likely instrument-and-law ladder), **Predicted claims** (concrete and falsifiable,
with confidence), **How** (the experimental strategy that gets there), **Traps**
(world-specific ways to fail).

---

## python — the interpreter as territory

**Terrain.** CPython 3.14 is a large artifact whose documented surface undersells
its actual behavior: object identity and interning, the adaptive specializing
interpreter, incremental GC, dict/set implementation guarantees, float and hash
edge cases, import machinery, closure semantics. Truth lives in behavior, not docs.

**Expected arc.**
1. *Census* — interpreter identity, build flags, sizes (already done: the first
   claim ever admitted).
2. *Subsystem probes* — GC generations (done), annotation laziness (done),
   subinterpreters (done), t-strings (done).
3. *Deeper mechanics* — small-int cache boundaries, string interning rules
   (compile-time vs runtime, ASCII-identifier rule), dict insertion-order
   machinery, when the specializing interpreter de-optimizes, frame object
   lifecycle, `sys.intern` behavior.
4. *Cross-version frontier* — behavioral diffs against documented 3.13 semantics;
   the agent's pretrained priors ARE 3.13-flavored, so its wrong priors map the
   diff for free (this already happened: version surprise, GC surprise).

**Predicted claims** (confidence in brackets):
- String literals that are identifier-like are interned at compile time; runtime
  concatenations are not, except via `sys.intern` [85].
- The small-int cache is exactly [-5, 256] and survives arithmetic only through
  compile-time constant folding within a code object [90] — half already shown.
- Specializing interpreter: a function's bytecode adapts after ~8 calls with
  stable types and de-optimizes on type instability, observable via
  `dis`/`sys._getframe` side channels [55].
- dict preserves insertion order and `popitem()` is LIFO by contract [95].

**How.** Identity probes (`is`), `sys.getsizeof` deltas, `dis` output diffs,
`gc.get_stats` deltas, exception-message forensics. The `envprobe` pattern —
snapshot tools that make every later claim cheaper.

**Traps.** Timing-based claims (noisy, machine-bound); hash-randomization
nondeterminism (must fix `PYTHONHASHSEED` inside experiments or claim modulo it);
overclaiming machine-specifics as universal (must scope to this build).

---

## sim-life — one universe, studied deeply

**Terrain.** Conway's Life on toruses: finite state spaces (exhaustible up to
~2^24), soup statistical mechanics, pattern zoology (still lifes, oscillators,
spaceships), and the interaction between wraparound topology and pattern motion.

**Expected arc** (24 claims in; phases 1–3 largely done).
1. *Engine + validation* → 2. *exhaustive small-torus censuses* → 3. *soup
   statistics and pattern characterization* — all achieved, including two glider
   discoveries and the ash-density cliff.
4. *Interaction physics* — glider–glider collisions: annihilation, reflection,
   and constructive products (eaters, blocks); collision outcome tables as exact
   claims. This is the door to Life-as-computation.
5. *Resonance laws* — spaceship period as a function of torus size
   (period = 4·lcm-type laws, partially claimed); which (W,H) admit which
   travelers; interference of a ship with its own wraparound wake.
6. *Statistical frontier* — ash density asymptote (~0.0287 on large grids),
   methuselah lifetime distributions, finite-size scaling of the density cliff.

**Predicted claims:**
- An exact 2-glider collision outcome table for head-on and 90° geometries at
  all phase offsets on a large-enough torus [80].
- Existence and construction of a glider eater on a torus; exact claim of the
  consumed-in-N-generations form [65].
- Ash density on N×N approaches 0.028–0.030 as N grows through 64→128 within
  seeded tolerance [75].
- A (W,H) admissibility law for LWSS analogous to the glider's min(W,H) ≥ 5 [70].

**How.** Collision scans are seeded, enumerable (relative phase × offset is a
finite grid), and check-friendly — this world's methods are mature; the frontier
is combinatorial patience plus the existing tool stack (`life`, `attract`,
`drift`, `lwss`).

**Traps.** Grid-size ambition vs the 30s timeout (128×128 long runs must be
budgeted); compound claims (the promoted eca methodology's "one claim per thread"
rule applies here too); unseeded soup statistics (already burned once).

---

## eca — a space of universes, taxonomized

**Terrain.** 256 rules containing: a linear/affine subfamily solvable exactly
over GF(2), a small bijective family, a large boring majority, and a thin band
of complexity (rules 30, 54, 110...) where particles and computation live. The
deep known results are all reachable: 88 equivalence classes, the balance
theorem for surjectivity, Moore–Myhill garden-of-Eden duality, cycle structure
of linear rules via polynomial algebra.

**Expected arc** (7 claims in).
1. *Linear rules cracked* — done: 90 and 150 as GF(2) matrices, singularity laws.
2. *Global censuses* — done: 6 bijective, 16 affine.
3. *Equivalence quotient* — mirror + complement symmetries collapse 256 rules to
   exactly 88 classes; the census claim writes itself and the check is pure
   computation [predicted next, 85].
4. *Surjectivity census* — surjective ⟺ balanced de Bruijn condition; exactly 30
   rules on unbounded tape; on periodic tapes injectivity/surjectivity interplay
   → Moore–Myhill verified exhaustively for small N [70].
5. *Cycle algebra* — for linear rules, cycle lengths follow from the
   multiplicative order of the rule polynomial modulo x^N − 1 over GF(2); the
   agent has both GF(2) tools and the data to find the factorization law [60].
6. *Complexity frontier* — rule 110/54 particle census: background ether,
   particle types, collision products. Hardest; needs pattern-matching
   instruments it hasn't built yet [45 within ten sessions].

**Predicted claims:** the four numbered above, plus: rule 30's center column
passes basic randomness batteries at claimed lengths [70].

**How.** Censuses via brute force over 256×small-N (cheap); algebra via its
existing GF(2) rank tools extended to polynomial quotient rings; particles via
space-time diagram diffing against the ether background.

**Traps.** Infinite-tape claims aren't checkable — everything must be phrased
periodic or windowed (world.md enforces); equivalence-class bookkeeping errors
(left/right mirror off-by-one is classic); rule 110 particle taxonomy is
genuinely hard — expect parked questions, which is the system working.

---

## sandpile — algebra hiding in avalanches

**Terrain.** The Abelian sandpile on N×N: a dynamical system that is secretly a
finite abelian group. The reachable deep facts: order-independence of toppling
(the abelian property), the burning test for recurrence, the sandpile group
whose order equals the number of spanning trees (matrix–tree theorem), the
fractal identity element, and power-law avalanches under random driving.

**Expected arc.**
1. *Engine + abelian property* — implement toppling; predict order-dependence
   (natural prior), discover order-independence with surprise; claim exact
   final-configuration invariance across seeded topple orders [90].
2. *Stabilization bounds* — max grains before instability, stabilization time
   scaling on small N [80].
3. *Recurrence* — burning test rediscovered or reinvented; recurrent-config
   census on 2×2, 3×3 exact [70].
4. *The group* — addition of recurrent configs mod stabilization forms a group;
   identity element computed for N up to ~20; its self-similar structure claimed
   exactly per N [65].
5. *The crown* — |group| = det(reduced Laplacian) = spanning tree count,
   verified exactly on small N: a cross-domain identity discovered by computing
   both sides independently [50 — this is the one to hope for].
6. *Criticality* — avalanche size distribution power law with seeded driving,
   exponent within stated tolerance [60].

**How.** The identity element is found by a known-shaped experiment (stabilize
2·max-config minus its stabilization); whether the agent finds this construction
or invents another route is itself informative. The spanning-tree link requires
it to compute a determinant and count trees — both stdlib-feasible.

**Traps.** Naive toppling is O(slow) — needs an efficient engine or small N;
boundary-condition confusion (grains must fall off edges or nothing works);
conflating transient and recurrent configurations in group claims.

---

## busybeaver — the frontier where checking itself breaks

**Terrain.** Small Turing machines are the cheapest access to genuine
undecidability. Ground truth exists for n ≤ 4 (Σ: 1, 4, 6, 13; S: 1, 6, 21,
107) and n = 5 is research-grade. But the deeper thing this world teaches is
epistemic: a check can verify a halt (run it), but "never halts" is only
checkable when a decidable pattern proves it. This world will stress the
claim-with-check rule itself.

**Expected arc.**
1. *Simulator + n=1* — trivial census, exact [95].
2. *n=2 full census* — Σ(2)=4, S(2)=6 rediscovered exactly; halting fraction of
   machine-space claimed [85].
3. *Non-halting taxonomy* — the forced move: to census n=3 it must prove
   non-halting for most machines; expect claims classifying simple loops,
   runaway heads, translated cycling, with exact per-class counts [75].
4. *n=3 census* — Σ(3)=6, S(3)=21 with a decided/undecided split; possibly a
   small residue of machines undecided by its methods, honestly quantified [65].
5. *n=4 partial* — lower bounds via champions found by seeded search; full
   census likely out of reach without tree-normal-form pruning [claims as
   bounds, 60; full census 25].
6. *Meta-discovery* — some claim of the form "every claim about non-halting in
   this world is conditional on a decidable pattern" — the agent articulating
   the limits of its own oracle [35, but watch for it].

**How.** Enumeration with canonical-form pruning; step-budgeted simulation
(world.md mandates explicit budgets); non-halt provers as archived tools —
this world's tool ladder is essentially a growing proof library.

**Traps.** The big one: claiming "never halts" from a bounded run — the gate
will admit it if the check merely re-runs the bound, which makes the claim
circular-but-true-looking. Watch whether verify/cull or the agent itself
catches the weakness. Timeout management: one hot machine can eat the 30s.

---

## logistic — continuous mathematics under a discrete oracle

**Terrain.** The logistic map's bifurcation cascade is exact mathematics
(r₁ = 3, r₂ = 1+√6, period-3 window at 1+√8, Feigenbaum δ = 4.669...) accessed
through floating-point experiments. The tension between exact algebra and float
tolerance is the territory.

**Expected arc.**
1. *Fixed points* — x* = 1−1/r, stability lost at r=3; exact and clean [90].
2. *Period-2 branch* — birth at r=3, its own instability at 1+√6 ≈ 3.4495;
   the algebraic value verifiable by substitution — first exact-algebra claim [75].
3. *Cascade* — r₃, r₄... located by bisection on orbit period; δ estimated from
   successive ratios to 3–4 significant digits with stated tolerance [70].
4. *Windows* — period-3 tangent bifurcation at 1+√8 exactly; period-doubling
   inside the window (self-similarity) [65].
5. *Chaos proper* — Lyapunov exponent crossing zero at accumulation point
   r∞ ≈ 3.5699; λ = ln 2 exactly at r = 4 via conjugacy to the tent map —
   if it finds the sin² closed form at r=4, that's the crown [40].

**Predicted claims:** the algebraic values above; δ ∈ [4.6, 4.75] with seeded
initial conditions and stated iteration counts [70].

**How.** Orbit-period detection with transient burn-in; bisection on r;
`fractions`/`decimal` for exact substitution checks where algebra permits;
tolerance-scoped claims everywhere else (world.md mandates stated tolerances).

**Traps.** Critical slowing near bifurcations (transients diverge — burn-in
must scale); float noise mimicking chaos near onset; claiming digits of δ
beyond what float64 + finite cascade depth supports.

---

## random-graphs — sharp thresholds from seeded noise

**Terrain.** G(n,p)'s phase transitions are among the most beautiful facts in
combinatorics: giant component at p = 1/n (fraction solving s = 1−e^{−cs}),
connectivity at p = ln n / n with isolated vertices as the last obstruction,
Poisson degree structure. All statistical — the discipline world: every claim
must survive seeding.

**Expected arc.**
1. *Sampler + component machinery* — union-find or BFS tool; seeded [90].
2. *Giant component* — subcritical/supercritical contrast at c = np fixed;
   largest-component fraction jump across c=1 sharpens with n [85].
3. *The functional law* — supercritical giant fraction matches the solution of
   s = 1−e^{−cs} within tolerance across c grid — discovering the equation, not
   just the jump [45; finding the *shape* numerically 70].
4. *Connectivity* — threshold at ln n / n; and the finer fact that at the
   moment of connectivity, min-degree-0 vanishing is the bottleneck [60].
5. *Degree structure* — Poisson(c) fit with exact seeded statistics [75].

**How.** Fixed seed grids (world.md mandates); finite-size scaling: same c,
growing n, watch sharpness; claims phrased as "for these seeds and n ∈ {...},
statistic in [a,b]" — the exact style the sim-life rejection taught.

**Traps.** Finite-size smearing near thresholds read as "no transition";
pseudo-discoveries from a lucky seed (the replication gate is load-bearing
here); n large enough to see asymptotics vs 30s timeout.

---

## ipd — laws of an ecology, not of a mechanism

**Terrain.** The iterated prisoner's dilemma has no "best strategy" — only
context-dependent dominance, which is itself the discovery: Axelrod's TFT
results, noise flipping the ranking toward generosity (generous-TFT, Pavlov),
invasion asymmetries, and — the deep end — zero-determinant/extortion
strategies (Press–Dyson) that win every head-to-head yet lose every ecology.

**Expected arc.**
1. *Engine + classic roster* — tournament tool, seeded, exact payoffs [90].
2. *Axelrod rediscovered* — TFT wins the classic round-robin; niceness/
   retaliation/forgiveness pattern claimed as exact tournament results [80].
3. *Noise changes everything* — with flip probability ε, TFT death-spirals;
   Pavlov/generous-TFT dominate; exact seeded rankings per ε [70].
4. *Evolutionary dynamics* — replicator-style population runs: AllD invades
   AllC; TFT resists; cycling ecologies possible; exact seeded trajectories [65].
5. *The deep end* — a strategy that beats every opponent pairwise while losing
   population dynamics — rediscovering the extortion paradox, even without the
   ZD algebra [35; with the determinant algebra 15].
6. *Meta-law* — an explicit claim that dominance is non-transitive /
   ecology-relative in this world [55 — the agent stating context-dependence as
   a theorem would be the philosophical win].

**How.** Strategies as archived tools (the roster grows across threads);
tournaments replayed exactly by checks (world.md pins payoffs, seeds, rounds);
population dynamics as deterministic seeded iteration.

**Traps.** "Best strategy" claims without ecology qualification (ill-posed —
watch whether the gate's replication requirement forces the qualification);
stochastic strategies without seeds; payoff-matrix sensitivity silently
unstated.

---

## Reading this document later

Three uses. (1) *Score the agent*: which predicted claims arrived, which arcs
were skipped, what did it find that we never imagined — the last category is
the payoff. (2) *Score us*: every prediction here carries a confidence; we are
exactly as calibrated as those numbers turn out to be. (3) *Score the harness*:
worlds where the agent systematically stalls below phase 3 are telling us about
missing kernel affordances (pattern-matching instruments, longer budgets,
cross-thread memory), not about the territory.
