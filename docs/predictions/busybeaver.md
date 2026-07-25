# busybeaver — full discovery program

## Where it stands

Untouched: `worlds/busybeaver/` holds only `world.md` — no claims, no tools, no ledger entries.

## Phase map

### Phase 1 — Simulator, canonical encoding, n=1 census

**Goal.** One trusted oracle for halting-within-budget, one canonical machine representation, and the first exact census.

**Instruments.** `tm.py` (banked tool): machine = tuple of 2n transitions, each `(write, move, next)` or `HALT`; standard-text codec (`1RB1LB_1LA1RZ` style) so claims and checks name machines unambiguously; `run(machine, budget)` returning `(halted, steps, ones, tape_extent)` — budget mandatory, no unbounded call exists in the API.

**Predicted claims.**
- Simulator validated: on 5+ hand-built machines the step/ones counts match hand simulation exactly [95].
- Raw n-state, 2-symbol machine-space is exactly `(4n+1)^(2n)`: 25, 6561, 4826809, 6975757441 for n=1..4 [95].
- n=1 exact census over all 25 machines: Σ(1)=1, S(1)=1; exact halting count on blank tape [92].
- Every n=1 non-halter is decided by a ≤4-step argument (can't leave one cell productively), so the census carries zero undecided residue [85].

**How.** Build simulator; predict its outputs on toy machines before running (calibration surprises are free data). Enumerate all 25 n=1 machines with budget 10; the checks re-enumerate and re-simulate from scratch in under a second.

**Traps.** Encoding ambiguity (does halt transition write? move? — pick the standard convention where the halt transition writes 1 and counts as a step, else S(2)=6 won't reproduce); off-by-one in step counting; simulator bugs poisoning every later claim — validate before censusing.

**Unlocks.** Every subsequent phase; the codec makes all future claims machine-addressable.

### Phase 2 — Tree-normal-form enumeration, n=2 exact census

**Goal.** Collapse the symmetric bulk and take the first nontrivial census: Σ(2)=4, S(2)=6.

**Instruments.** `enum.py` (careful: name must not shadow stdlib — call it `tmenum.py`): tree-normal-form (TNF) generator — fix first transition A0→1RB, introduce new states in first-use order, quotient left/right reflection and state permutation; only reachable, started machines enumerated.

**Predicted claims.**
- TNF collapses raw n=2 space (6561) by more than an order of magnitude; exact TNF count claimed and re-derivable [80].
- Exact n=2 census: every machine either halts within budget 50 or is certified non-halting by an elementary argument; Σ(2)=4, S(2)=6, achieved by named champion machines in standard text [85].
- Exact count of n=2 blank-tape halters, with halting-time histogram (max 6) [82].
- TNF is census-lossless: every raw machine's blank-tape behavior is realized by a TNF representative (checked exhaustively at n=2 by simulating both sides) [75].

**How.** Enumerate TNF, run each with budget 50, sort survivors into "needs proof" pile. At n=2 the survivor pile is small enough to certify with the Phase-3 provers' simplest rungs, or even by hand-coded case analysis. Two experiments minimum: census computed twice from independent enumeration orders.

**Traps.** TNF bookkeeping errors (mirror off-by-one, unreachable-state leakage) silently drop machines — the lossless-quotient claim is the guard; claiming the census before survivors are certified (bounded ≠ never).

**Unlocks.** Enumeration engine for n=3/4; the survivor pile is the forcing function for Phase 3.

### Phase 3 — Non-halting prover ladder, rungs 1–3

**Goal.** A growing proof library: deciders that certify "never halts", each a banked tool with a measured coverage count.

**Instruments.** `provers.py`, one rung per thread: (1) **exact-state cycle** — full configuration (state, head, tape) repeats; (2) **runaway head** — head moves monotonically off one end in a repeating state/symbol pattern over blank tape; (3) **translated cycling** — configuration recurs shifted by a fixed offset (same local tape, head translated). Each prover returns a certificate (the recurrence witness: step indices, offset) that the check replays.

**Predicted claims.**
- Exact per-class counts on n=2 TNF space: cycle-catches, runaway-catches, translated-cycle-catches, with classes applied in fixed pipeline order so counts are reproducible [80].
- On n=3 TNF space, the three rungs plus budget-B simulation decide ≥95% of machines; exact decided count claimed [70].
- Prover soundness cross-check: no prover fires on any machine that actually halts within 10⁵ steps — tested against the full known-halter set [85].
- Pipeline-order dependence: per-class counts change under reordering but the total decided set does not [65].

**How.** Run each new prover over the current undecided pile; claim its exact catch count. Soundness experiments run provers against halters — one false positive falsifies the rung. Certificates make checks cheap: replay the witness, don't re-search.

**Traps.** A buggy prover whose check re-runs the same buggy prover passes forever — soundness claims are the only external anchor; certificate replay must be independent code from certificate search.

**Unlocks.** n=3 census; the certificate discipline that Phases 5–7 live on.

### Phase 4 — n=3 census with honest residue, prover rungs 4–5

**Goal.** Σ(3)=6, S(3)=21 exact, and an explicitly quantified undecided residue driven to zero by two stronger rungs: **Lin recurrence** (systematic recurrence search over windows) and **backward reasoning** (from each halt transition, search predecessor configurations; finite backward tree ⇒ halt unreachable).

**Predicted claims.**
- Interim census: with rungs 1–3 and budget 10³, exactly D of the n=3 TNF machines are decided; the residue is a named, listable set of size R [75].
- Lin recurrence decides the majority of the residue; exact catch count [70].
- Backward reasoning empties the remainder; final census claim: every n=3 machine is halting (with step count ≤21) or pattern-proven non-halting; Σ(3)=6, S(3)=21 [65].
- The n=3 champion set: exact list of machines attaining S=21 and Σ=6 up to TNF symmetry [60].
- Residue is monotone in prover power: each rung's decided set strictly contains no machine decided differently by another rung (consistency claim) [70].

**How.** Census as a pipeline artifact: enumerate → simulate (budget 10³) → prover cascade → residue file banked in `tools/` as data. Each rung is its own thread with its own claim. If residue does not reach zero, the census claim is *phrased conditionally*: "S(3)≥21, Σ(3)≥6, and = holds if the R-machine residue contains no halter" — honest, checkable, upgradeable.

**Traps.** Backward reasoning state-space blowup inside 30s (depth-cap it, treat cap as part of the claim); Lin-recurrence window too small (missed recurrences look like undecided, which is safe — but claiming a window "suffices" without stating it is not).

**Unlocks.** Complete prover ladder; the conditional-claim template that n=4 requires.

### Phase 5 — n=4 campaign: checkpointed, multi-thread

**Goal.** Σ(4)=13, S(4)=107 via a census too big for one thread: ~7×10⁹ raw, TNF-pruned to a tractable but multi-session enumeration.

**Instruments.** `campaign.py`: chunked TNF enumeration with a persistent frontier — progress checkpoints written into `archive/tools/` as data modules (the only cross-thread memory the harness offers), so thread k+1 resumes where thread k stopped. Undecided machines accumulate in a holdouts file.

**Predicted claims** — all phrased as monotone partials until closure:
- Checkpoint integrity: re-running any chunk from its checkpoint reproduces identical decided/undecided partitions (determinism claim) [80].
- Rolling lower bounds: "S(4)≥96, Σ(4)≥13 witnessed by named machines" upgraded across threads until S(4)≥107 [75].
- Rolling coverage: "≥N TNF machines decided, holdout set size ≤H", strictly improving per session [70].
- Budget sufficiency: no n=4 halter needs more than 107 steps *among decided machines* — phrased over the decided set only until closure [65].
- Final: exact n=4 census, Σ(4)=13, S(4)=107, holdouts zero or explicitly listed with the census conditional on them [full closure 40; conditional form 75].

**How.** Each 30s experiment processes one enumeration chunk with the full prover cascade; claims are cumulative counters whose checks replay only certificates plus chunk hashes, not the whole enumeration. Human seeding of "resume the campaign" open questions keeps threads on task.

**Traps.** One hot machine eating the 30s (per-machine step budget inside the chunk budget); checkpoint corruption silently skipping chunks (integrity claim is the guard); the temptation to claim the census while holdouts remain — the conditional template from Phase 4 is mandatory.

**Unlocks.** Champion corpus for Phase 6; holdout set for prover research.

### Phase 6 — Champion structure analysis

**Goal.** From censuses, extract *why* champions are champions.

**Instruments.** `trace.py`: phase-space traces, tape-growth profiles, state-transition graphs, control-flow decomposition (does the machine factor into "phases" or is every state entangled with every other).

**Predicted claims.**
- n=2..4 champions all use every state and every transition (no dead code in champions) — exact structural check [75].
- Champion tape growth: n=4 step champion's tape extent and ones-count trajectory follow a claimed exact profile (recomputable trace) [70].
- Spaghetti signature: champions' state graphs are strongly connected with no nontrivial modular decomposition, while median-lifetime halters decompose — quantified by an explicit graph statistic over both populations [55].
- At least one n=4 near-champion implements a recognizable arithmetic iteration (counter/Collatz-like behavior identified via trace regularity) [45].

**How.** Comparative anatomy: champions vs random halters vs longest non-champions, all from the archived census — no new enumeration needed. Claims are structural predicates over named machine lists.

**Traps.** Reading narrative into traces (a "phase" must be a checkable predicate, not a story); small-n champions are too tiny for statistics — the spaghetti claim needs the n=4 halter population as its base.

**Unlocks.** Vocabulary for the n=5 boundary probe and the Phase-7 meta-claims.

### Phase 7 — Meta-discovery: the oracle's limits as claims

**Goal.** Make the epistemology itself archive material.

**Instruments.** The whole prover library, turned on itself.

**Predicted claims.**
- Every non-halting claim in this archive is conditional on a named decidable pattern; the archive contains no unconditional "never halts" — checked by parsing all claim certificates for their prover tag [60].
- The prover hierarchy is strict on real machines: for each adjacent rung pair, a witness machine decided by the stronger and not the weaker rung [65].
- Existence of budget-circularity: a demonstration claim showing a check of the form "didn't halt in B steps" passes verify forever while asserting nothing about halting — filed as a *negative* exhibit with the fix (certificate-bearing claims) [50].
- n=5 boundary probe: the 47,176,870-step champion reproduced as a lower-bound claim, S(5)≥47176870, via a compressed/accelerated simulation tool fitting the 30s budget [55].

**How.** Claims about claims: their checks parse `archive/claims/` and replay certificates. The n=5 probe needs a macro-machine or run-length-compressed tape tool — itself a bankable instrument.

**Traps.** Self-referential checks going stale as the archive grows (phrase over claim metadata, not file layout); the n=5 champion in naive Python may exceed 30s — the acceleration tool is load-bearing, and its correctness needs its own validation claim against small-n exact traces.

**Unlocks.** Endgame; the harness-strain findings below, stated by the agent itself.

## Endgame

**Completed archive.** A verified simulator and codec; TNF enumerator with a lossless-quotient claim; exact censuses for n=1..4 with Σ = 1, 4, 6, 13 and S = 1, 6, 21, 107, every non-halter carrying a replayable certificate naming its prover; a five-rung proof library (cycle, runaway, translated cycling, Lin recurrence, backward reasoning) with exact per-class coverage counts and soundness cross-checks; champion anatomy claims; the meta-claims about conditional non-halting; S(5)≥47,176,870 as a reproduced lower bound.

**Stopping criteria.** Stop when (a) n≤4 censuses are exact with zero or explicitly-listed holdouts, (b) every prover has both a coverage claim and a soundness claim, (c) the meta-claim about conditionality is admitted, and (d) new threads produce only refinements of existing claims for two consecutive sessions.

**Open-research boundary.** BB(5) = 47,176,870 was only settled in 2024 (bbchallenge's machine-checked proof); a full n=5 census is beyond a 30s-stdlib harness — the honest ceiling is reproduced lower bounds plus holdout sampling. BB(6) is open research: its value is known to exceed 10↑↑15, and settling it is entangled with open Collatz-like problems. Any thread that drifts toward "deciding" n=6 machines should be steered back to phrasing bounds; the world's frontier is genuinely undecidable territory, and the archive's job is to state exactly where its own methods stop.

## Harness strain

This world attacks the check-rule itself. The harness's contract — "no claim without a check that exits 0" — assumes reality can re-answer any admitted question. Halting claims honor that: the check re-runs the machine, counts steps, exits 0. Non-halting claims cannot: "never halts" is a Π₁ statement, and no finite execution witnesses it. The only checkable surrogate is *pattern-proven* non-halting — the check replays a certificate through a decider. That substitution has three consequences. First, **truth becomes conditional**: every non-halting claim is really "non-halting *if prover P is sound*", so the archive acquires a dependency structure the per-claim verify/cull loop does not model — a bug in one prover silently rots every claim citing it, and verify will never notice, because the check re-runs the same buggy prover and still exits 0. The counter-measure is to make prover soundness itself a claim surface (provers must never fire on known halters; independent replay code) — culling then has something real to bite. Second, **circularity is admissible**: "M doesn't halt in 10⁶ steps" checked by re-running 10⁶ steps passes forever while asserting nothing beyond its bound; the gate cannot distinguish it from knowledge. The discipline is typological: every claim is *halts(k)*, *bounded(B)*, or *certified(P, witness)* — never a bare "never halts". Third, **residue is data**: machines undecided by all provers are not failures to hide but the most honest objects in the archive — they are the world's local image of undecidability, and their count per n is itself a claim.

## Methodology attractor

Every world selects a methodology; this one selects **certificate discipline**, and the evolution loop should converge on it. Threads that simulate-and-observe die here: their claims are either bounded trivialities or inadmissible universals, scoring rejections. Threads that build deciders, emit replayable witnesses, phrase censuses as monotone partials, and checkpoint enumeration state into banked artifacts score steady admissions — so the champion methodology should come to read like a formal-verification project's working rules: one claim per thread; every claim typed as halts/bounded/certified; every prover paired with a soundness test before its coverage is claimed; every long computation resumable from an archived checkpoint; undecided residue reported, never elided. The predicted meta-signature: by mid-campaign the tools directory *is* the knowledge — a proof library plus a census ledger — and the claims are largely pointers into it. If the evolved methodology instead drifts toward easy bounded claims (the fitness function's known pressure), that divergence is evidence about the harness, not the territory: it means the gate rewards circular bounds and needs the certificate typology enforced in `world.md` itself.
