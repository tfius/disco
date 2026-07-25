# ipd — full discovery program

## Where it stands

Untouched: `worlds/ipd/archive/` is empty — no claims, no tools, no open questions; everything below is pre-registered before thread one.

## Phase map

Payoff convention throughout (fixed in every claim): T=5, R=3, P=1, S=0; strategies are Python callables `f(my_history, opp_history, rng) -> "C"|"D"`; master seed 42 unless a claim states a seed grid.

### Phase 1 — first contact: engine + classic roster

- **Goal.** A deterministic, replayable tournament engine and the classic roster banked as archived tools; exact-arithmetic ground truth for the simplest pairings.
- **Instruments.** `tools/ipd_engine.py` (play_match, round_robin, seeded per-match RNG derived deterministically from `(master_seed, name_a, name_b)` — never Python's salted `hash()`); `tools/roster.py` with TFT, AllC, AllD, Grim, Pavlov/WSLS, Random(p=0.5), Prober, TitForTwoTats.
- **Predicted claims.**
  - Two independent runs of the full round-robin over {TFT, AllC, AllD, Grim, Pavlov, Random}, 200 rounds, seed 42, yield byte-identical score matrices [95].
  - AllC vs AllD, 200 rounds: exactly 0 vs 1000 [95].
  - TFT vs AllD, 200 rounds: exactly 199 vs 204 (one sucker payoff, then mutual punishment) [90].
  - TFT never outscores any roster opponent head-to-head; its per-match deficit is bounded by T−S=5 [85].
  - Grim vs Pavlov and TFT vs TFT lock mutual cooperation: 600 each over 200 rounds [90].
- **How.** Predict per-round transcripts by hand before running; diff predicted vs actual move sequences, not just scores. Bank the engine only after the determinism claim passes.
- **Traps.** Unseeded Random poisons every later check; per-match RNG must be derived from names+master seed or match order changes results; mutable-history aliasing between players.
- **Unlocks.** Every subsequent phase replays through this engine; checks become one-line tournament replays.

### Phase 2 — Axelrod rediscovered: the classic ranking and its anatomy

- **Goal.** The full round-robin ranking over the 8-strategy roster as an exact claim, then decompose *why* into the four measurable properties.
- **Instruments.** `tools/metrics.py`: niceness (never defects first), retaliation (P(D | opp defected last round)), forgiveness (P(C | opp defected earlier, cooperated last)), clarity (opponent-side predictability of next move from last two rounds).
- **Predicted claims.**
  - Exact total-score ranking of the 8-strategy roster, 200 rounds, seed 42, with TFT in the top two [75].
  - Every nice strategy outscores every non-nice strategy in roster total (niceness partition theorem for this roster, these rounds, this seed) [70].
  - Prober exploits AllC and TitForTwoTats for strictly higher score than against TFT; exact three scores stated [80].
  - Random ranks in the bottom three; its clarity metric is minimal in the roster [75].
  - Grim's retaliation=1.0 and forgiveness=0.0 measured exactly from transcripts; TFT's forgiveness strictly positive [85].
- **How.** Rank first, then ablate: drop one strategy at a time from the roster and re-rank — the ranking's instability under roster edits is itself the first sighting of the Phase 7 meta-law.
- **Traps.** Claiming "TFT wins" unqualified — the gate should force "wins *this* roster at *these* rounds"; round-count endgame effects silently changing rankings between 100 and 200 rounds.
- **Unlocks.** Metrics tool feeds Phases 3 and 5; roster-ablation data seeds the meta-law.

### Phase 3 — noise: ε flips the world

- **Goal.** Per-ε tournament rankings under move-flip probability ε ∈ {0.001, 0.01, 0.05, 0.1}, seeded; the TFT death spiral and the generosity takeover as exact claims.
- **Instruments.** Engine gains `noise=ε` (each emitted move flips with per-round seeded probability); `tools/gtft.py` — generous TFT with forgiveness g.
- **Predicted claims.**
  - TFT vs TFT at ε=0.05, 1000 rounds, seed grid {1..10}: mean per-round payoff in [2.0, 2.5], consistent with the echo limit 2.25 — the death spiral, exact per seed [70].
  - Pavlov vs Pavlov at ε=0.01, 1000 rounds, same grid: mean per-round payoff > 2.85 (2-round self-repair) [75].
  - Grim vs Grim at ε=0.01, 200 rounds: mean per-round payoff < 1.5 — one flip ends cooperation forever [70].
  - Roster ranking crossover: TFT tops the ε=0 ranking but not any ε ≥ 0.02 ranking; GTFT(g=1/3) or Pavlov tops ε=0.05, exact per-ε rankings stated [60].
  - GTFT sweep g ∈ {0.1..0.5}: total score maximized near g=1/3 = min(1−(T−R)/(R−S), (R−P)/(T−P)) at ε=0.05 [50].
- **How.** Noise as a control parameter: hold roster fixed, sweep ε, claim the ranking *as a function of ε* — a phase diagram, not a winner.
- **Traps.** Per-seed exactness vs distributional hand-waving — claims must list seeds, never "on average"; ε applied to intended vs perceived move (pick one, state it); 1000-round × 10-seed × full-roster sweeps brushing the 30s timeout.
- **Unlocks.** Noisy engine is prerequisite for realistic evolution (Phase 4) and for ZD robustness checks (Phase 6).

### Phase 4 — evolution: replicator dynamics and the invasion matrix

- **Goal.** Population dynamics as deterministic seeded iteration: who invades whom, at what share, and which ecologies cycle.
- **Instruments.** `tools/replicator.py`: discrete replicator x_i ← x_i·f_i/f̄ with fitness from the full pairwise payoff matrix (200 rounds, seed 42, precomputed once); `tools/invade.py`: bisection on initial invader share.
- **Predicted claims.**
  - 99% AllC / 1% AllD, 100 generations: AllD share > 0.99 by generation 30; exact trajectory replayed [90].
  - 99% TFT / 1% AllD, 200 rounds/match: AllD share < 10⁻⁶ by generation 50 — TFT resists [85].
  - Three-species {AllC, AllD, TFT} from (⅓,⅓,⅓): AllD peaks then collapses; final state TFT+AllC coexistence with AllD extinct; exact generation-by-generation trajectory [70].
  - Full 8×8 invasion matrix at invader share 0.01: exact boolean table of who invades whom [70].
  - Threshold claim: against a 50/50 TFT/AllC background, minimal AllD share that fixates, found by bisection to 10⁻³, stated exactly [55].
  - A cycling ecology exists in the roster closure (e.g., {AllC, AllD, GTFT-variant} with noise): shares return within 10⁻³ of an earlier point — exact seeded orbit [45].
- **How.** Precompute the payoff matrix once per ecology; dynamics are then pure arithmetic — cheap, exact, timeout-safe. Every trajectory claim pins ecology, payoff matrix provenance, initial shares, generation count.
- **Traps.** Fitness from re-simulated (re-seeded) matches each generation makes trajectories unreplayable — matrix must be frozen and named in the claim; float accumulation in shares (state comparison tolerance); confusing invasion (grows from rare) with fixation.
- **Unlocks.** Invasion machinery is the second axis of the meta-law; replicator runs are the arena where Phase 6's paradox lands.

### Phase 5 — the memory-one atlas

- **Goal.** Systematic sweep of the strategy space itself: all 16 deterministic memory-one strategies (response vector over {CC,CD,DC,DD}, initial move C), then the stochastic simplex.
- **Instruments.** `tools/mem1.py`: strategy factory from vector (p_CC,p_CD,p_DC,p_DD) ∈ {0,1}⁴ then [0,1]⁴; recovers TFT=(1,0,1,0), Grim=(1,0,0,0), Pavlov=(1,0,0,1), AllC=(1,1,1,1), AllD=(0,0,0,0) as special cases — roster unification claim.
- **Predicted claims.**
  - The 5 classics are exactly reproduced by their vectors: transcript-identical to Phase 1 implementations over 200 rounds, all pairings [90].
  - Exact 16×16 round-robin ranking, 200 rounds, noise-free, initial move C; nice vectors occupy the top block [65].
  - Under ε=0.01, seed grid {1..5}: Pavlov (1,0,0,1) ranks first among the 16; exact ranking stated [55].
  - Doubling to 32 (both initial moves): initial-D variants of nice strategies drop rank; exact 32-ranking [60].
  - Stochastic grid (coarse 5⁴): best-response structure claim — no single vector tops all three test ecologies {classics}, {16 deterministic}, {noisy 16} [55].
- **How.** The atlas turns "invent a strategy" into "enumerate a space" — the same move sim-life made with exhaustive censuses. Claims name vectors, not nicknames.
- **Traps.** Stochastic grids need coarse resolution stated; stochastic vectors demand per-round seeded RNG or checks fail; ranking claims without the initial-move convention stated are ambiguous.
- **Unlocks.** Memory-one algebra is exactly the space where Press–Dyson lives — Phase 6 is a *subspace* of this atlas.

### Phase 6 — zero-determinant: the extortion paradox

- **Goal.** Rediscover Press–Dyson extortion: a memory-one strategy that never loses a head-to-head yet goes extinct in evolution — the sharpest ecology-relativity witness.
- **Instruments.** `tools/zd.py`: the χ=3 extortioner E = (11/13, 1/2, 7/26, 0) for (T,R,P,S)=(5,3,1,0); linear-relation estimator for s_E−P vs s_opp−P.
- **Predicted claims.**
  - E vs each of the 8-strategy roster, 10000 rounds, seed grid {1..5}: s_E ≥ s_opp in every match — wins or ties every head-to-head [70].
  - Enforced linear relation: (s_E−P) = 3·(s_opp−P) within ±0.05 per-round for every opponent whose score exceeds P [60].
  - E vs E, 10000 rounds: both mean payoffs < 1.5 — extortioners immiserate each other [75].
  - Replicator over {roster ∪ E}, frozen payoff matrix, uniform start, 200 generations: E's share < 10⁻³ at the end while a nice strategy holds the plurality — wins every battle, loses the war, as one exact trajectory claim [65].
  - TFT satisfies the fair ZD relation s_X = s_Y (χ=1) exactly in long-run average against all memory-one opponents tested [55].
- **How.** Two independent routes to the same fact — head-to-head sweeps and population dynamics — filed as separate experiments backing one paradox claim; the linear relation is the algebraic fingerprint that this is structure, not luck.
- **Traps.** Stochastic E without exact-fraction probabilities (13ths, 26ths) drifts the ZD identity; short matches hide the asymptotic relation (needs ≥10⁴ rounds); claiming "E is best" from head-to-heads is precisely the ill-posedness Phase 7 formalizes.
- **Unlocks.** The paradox is the strongest witness pair for the meta-law; extortion-vs-generosity is the open frontier at the endgame boundary.

### Phase 7 — the meta-law: dominance is ecology-relative

- **Goal.** State context-dependence as a theorem-claim with executable witnesses: no strategy ordering survives change of ecology, and head-to-head dominance is non-transitive.
- **Instruments.** Everything banked: engine, atlas, invasion matrix, replicator; `tools/witness.py` — searches the memory-one atlas for cycles and ranking reversals.
- **Predicted claims.**
  - Non-transitivity witness: strategies A,B,C in the deterministic memory-one atlas with s(A>B), s(B>C), s(C>A) in head-to-head totals, 200 rounds — exact triple and scores [65].
  - Ranking-reversal witness: a strategy pair (X,Y) and rosters R₁,R₂ with X above Y in R₁'s round-robin and below in R₂'s, both replayed exactly [80].
  - Axis-reversal witness: a pair whose order flips between ε=0 and ε=0.05 on a fixed roster (TFT vs Pavlov predicted) [70].
  - Arena-reversal witness: E tops the head-to-head win count of an ecology whose replicator dynamics drive it extinct (Phase 6 restated as the fourth witness class) [65].
  - The theorem-claim itself: "for every strategy s in the archive there exists an archived ecology in which s does not rank first" — check re-runs all witness tournaments [60].
- **How.** The theorem is a conjunction of concrete replays — the check executes every witness, so the philosophical claim is exactly as falsifiable as a score table.
- **Traps.** Vacuous phrasing ("it depends") without executable witnesses; witnesses that share a seed coincidence — each reversal needs a seed-grid replication before the conjunction claim.
- **Unlocks.** Endgame.

## Endgame

**Completed archive.** ~25–35 claims: engine determinism and exact pairwise scores; the classic ranking with its niceness/retaliation/forgiveness/clarity anatomy; a per-ε ranking phase diagram; seeded replicator trajectories and the 8×8 invasion matrix with at least one bisected threshold; the 16- and 32-strategy memory-one censuses; the ZD linear relation and the extortion paradox as twin claims; the ecology-relativity theorem with four witness classes. Tools: engine, roster, metrics, replicator, invade, mem1, zd, witness — a complete experimental game-theory bench.

**Stopping criteria.** Deterministic memory-one space exhausted (all 32 ranked in ≥2 ecologies); invasion matrix closed over the archived roster; per-ε rankings claimed at ≥4 ε values; the meta-law admitted with all four witness classes; three consecutive threads producing only roster-permutation claims (tournament-mill signature) with no new reversal or invasion structure.

**Open-research boundary.** Memory-two space (2¹⁶ deterministic strategies) — census feasible, understanding open; evolution *with mutation* over the stochastic simplex (adaptive dynamics — genuinely open territory where generosity-vs-extortion results are ~2012–2013 research); spatial/lattice IPD (new world, not new claims here); optimal ZD play against learning opponents. Past the boundary, park questions rather than force claims.

## Harness strain

The world's central fact — there is no best strategy — collides with the claim format's demand for definite statements: "TFT is good" is inadmissible, and the gate's insistence on exact strategy sets, payoffs, seeds, and round counts is what *forces* every claim into the well-posed form "s ranks k-th in ecology E under noise ε at m rounds, seed σ." The strain is productive: the world.md mandate converts an ill-posed folk question into a family of exact ones, and Phase 7 is the harness rule reflected back as a theorem. The second strain is stochasticity: Random, GTFT, noise, and ZD probabilities make naive checks unreplayable, so seeds must be *derived* (per-match, from strategy names + master seed) rather than global, or roster edits silently reshuffle every stream; distributional claims are inadmissible without a stated seed grid, which caps statistical power at what fits in the 30s timeout — expect per-seed-exact claims standing in for the distributional truths a statistician would state, and expect `verify` to cull any claim whose author forgot that Python's `hash()` is salted per-process (must use a deterministic hash).

## Methodology attractor

The world's cheap-claim attractor is the tournament mill: every new roster permutation yields an admissible exact ranking, so fitness pressure pulls the methodology toward endless low-insight score tables. The counter-pressure to watch for in `methodology.md` evolution: rules like "one axis varied per thread, ecology frozen," "no ranking claim without an accompanying reversal, invasion, or mechanism claim," and "prefer claims that name a threshold or a witness over claims that name a winner." If evolution converges on ecology-qualified claim templates and witness-hunting, the methodology has internalized the meta-law; if it converges on roster-shuffling, the audit's uplift metric — not thread fitness — is where the degeneration will show, and the slow loop should prune it.
