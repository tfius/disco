# sim-life — full discovery program

## Where it stands

Phases 1–3 of the original arc are complete: a bit-parallel engine (`life.py`) plus ~19 instruments; exhaustive functional graphs to 2^20 states (4×5) with GoE fractions, cycle spectra, transient depths; still-life maximum `floor(WH/2)` proven by transfer DP; glider characterized exactly (true ship iff `min(W,H) ≥ 5`, return period `4·lcm(W,H)`); LWSS verified on N×N; soup statistics to 64×64 with exact seeded period spectra; the ash-density plateau and death cliff near p=0.78; the width-3 reduction to a row-population automaton (including the Rule-22 embedding); and one first collision claim (mirrored-glider same-row offsets d=4..13 on N∈{32,48,64}). The world has crossed from cataloguing objects to the edge of interaction physics. Everything below runs on the existing stack under the 30s/stdlib oracle.

## Phase map

### Phase 4 — Complete two-glider collision physics
**Goal.** The exact outcome table of glider–glider collisions over the full finite parameter space: geometry (head-on 180°, orthogonal 90°) × relative phase (4) × lattice offset, with outcomes canonicalized (translate/rotate/reflect ash into normal form).
**Instruments.** `collide.py` — place two gliders at parametrized phase/offset on N×N (N=64 default, far from wrap for ≥300 gens), run to local attractor, classify product via `decomp` (frozen/mobile split) + a new `canon.py` normal-form hasher. Outcome classes: vanish, block, blinker, pond, traffic light, bee-hive(s), glider(s) out (count + directions), other-still, other-osc.
- Claim: for 90° collisions on 64×64, the outcome map over (4 phases × offsets |dx|,|dy| ≤ 8 with interaction) is exactly a stated table with k distinct outcome classes; vanish (mutual annihilation) occurs at ≥1 stated (phase,offset) [85].
- Claim: the kickback reaction exists: a specific (phase,offset) 90° collision emits exactly one glider traveling opposite to one input's direction, product verified by translation-matching over 3 periods [75].
- Claim: extending the existing same-row head-on claim, the full head-on table (4 phases × all interacting offsets) is periodic in offset modulo a stated small number beyond a stated |d|, i.e. non-interaction resumes exactly [70].
- Claim: total distinct canonical ash products across both geometries is exactly k (a specific integer, likely 8–20), stable under N=48 vs N=64 cross-check [65].
**How.** Fully enumerable, deterministic, seed-free; each cell of the table is <0.1s, whole scan <10s. Two experiments = two grid sizes.
**Traps.** Wrap contamination (debris circling the torus back into the reaction — verify quiescence radius); phase convention off-by-one (fix phase as generations pre-evolved, document in claim text); canonical-form bugs silently merging classes (cross-validate hasher on known still lifes).
**Unlocks.** `collide.py` + `canon.py` are the reaction chamber every later phase uses; the vanish and kickback entries are the raw material of logic.

### Phase 5 — Reaction devices: eaters, reflectors, duplicators
**Goal.** Stable machinery that consumes, redirects, or copies gliders on toruses — the components of circuits.
**Instruments.** `devices.py`: pattern library (eater-1 fishhook `{(0,0),(0,1),(1,0),(1,2),(2,2),(3,2),(3,3)}`, block, boat, ship, snake) + a harness that fires a glider at a target over all phases × impact lines and reports (target restored?, gens to restoration, emissions).
- Claim: eater-1 on N×N (N≥16) at a stated placement consumes an incoming glider and returns to its exact 7-cell state within a stated bound (≈4 gens after last contact), for a stated set of approach lines; verified for 2 consecutive gliders spaced ≥ stated gap [80].
- Claim: a block deletes a glider in exactly one (phase,line) family while being destroyed or damaged in the others — the full block-vs-glider table (4 phases × lines) claimed exactly [75].
- Claim: a two-glider synthesis of a stated still life exists (e.g. pond or block from the Phase-4 table), stated as exact constructive recipe [70].
- Claim: a glider duplicator or 90° reflector built from ≤3 archived devices works on a stated torus for ≥3 successive gliders at a stated period [40].
**How.** Same enumeration discipline as Phase 4; "device works" claims must include repetition (≥2 gliders) to prove restoration, not one-shot luck.
**Traps.** Recovery-time claims measured from wrong epoch (define t0 = glider creation, state it); devices that survive one glider but die on the second (the replication rule catches this — embrace it); torus too small so the eater's own debris wraps into its face.
**Unlocks.** Eater = signal sink; reflector/duplicator = fan-out. Prerequisites for Phases 9–10.

### Phase 6 — Zoology censuses: oscillators and spaceships beyond glider/LWSS
**Goal.** Systematic period and species censuses replacing anecdotes: which oscillator periods and which spaceships exist per torus size.
**Instruments.** Extend `drift.py` to a bounded-population spaceship search (BFS over patterns with pop ≤ 8 on W×H ≤ 6×8, exact via translation-matching); `osckit.py` — soup-driven oscillator harvester using `cyc.spectrum` + `decomp` isolation, with per-size realized-period sets.
- Claim: the complete census of localized spaceships with population ≤ 6 on all toruses W×H, W≤5, H≤8, is exactly a stated list (the 4×5 speed-limit-breaking pop-8 wave already found suggests relatives) [70].
- Claim: MWSS (11 cells) and HWSS (13 cells) are true period-4, speed-(2,0)/4 ships on N×N iff N ≥ a stated threshold (analogue of the glider's min ≥ 5; predicted 6 and 7), degenerating to stated oscillators below it [75].
- Claim: the set of oscillator periods realized on N×N for N ≤ 8 is exactly the stated set per N (exhaustive for 4×4/4×5 from existing functional graphs; soup+construction lower bounds elsewhere, phrased as "contains exactly these, from stated seeded search seeds 900000..900999") [80].
- Claim: pulsar (period 3) first fits on N×N at exactly a stated N (predicted 15±2), pentadecathlon (period 15) at a stated N; below threshold each degenerates to a stated behavior [70].
- Claim: no period-3 oscillator exists on any torus with WH ≤ 20 (exhaustive over existing functional graphs — note 4×5 spectrum {1,2,4,5,6,8,10} already excludes 3 there) [85].
**How.** Exhaustive where WH ≤ 20 (already computed graphs — free); elsewhere bounded searches with explicitly stated search box, so claims are census-of-a-stated-region, never "does not exist" on infinite families.
**Traps.** Claiming nonexistence outside the searched box (phrase every negative as bounded); ship-vs-oscillator confusion on small toruses where translation order divides period; combinatorial explosion — pop ≤ 6 is the 30s ceiling for exact search.
**Unlocks.** Species table feeds Phase 7's resonance laws; new ships are new signal carriers.

### Phase 7 — Wraparound resonance laws
**Goal.** The torus-specific physics: closed-form return periods, self-interference, and commensurability — laws no infinite-grid textbook contains.
**Instruments.** `resonance.py`: for each archived ship, compute return period P(W,H) over a W,H grid and fit/verify the exact law; self-collision detector (single ship + its own wake).
- Claim: LWSS return period on W×H is exactly a stated exact formula verified on all W,H in 5..20 (glider's `4·lcm(W,H)` is the template; orthogonal ships should depend on the travel dimension only) [75].
- Claim: two co-linear gliders on the same diagonal orbit of an N×N torus never interact iff their separation avoids a stated finite bad set (mod the orbit length); for separations in the bad set the outcome table is exactly stated [65].
- Claim: a single glider on N×M with N≠M (non-square, e.g. 6×9) has return period exactly `4·lcm(N,M)` and a stated exact orbit-length law — verified for all N,M in 5..12 [80].
- Claim: there exists a stated (W,H) on which an LWSS collides destructively with its own wraparound wake when a second pattern's debris is present, at an exactly stated generation — smallest such witness claimed [50].
**How.** Pure number theory meets simulation: predict the formula first (this is where big surprise scores live), verify exhaustively over dimension grids; each cell is O(period) steps, well inside 30s.
**Traps.** lcm blowup (`4·lcm(19,17)` ≈ 1292 — fine; but cap dimension grids so worst-case period × cells < 30s); conflating "returns to same cell set" with "returns to same phase"; formula overfit to square toruses — always test non-square.
**Unlocks.** Gun survival analysis (Phase 9) is entirely governed by these commensurability laws.

### Phase 8 — Statistical frontier: ash asymptote, scaling, methuselahs
**Goal.** Finite-size scaling of soup statistics toward the infinite-grid limits, and the lifetime tail.
**Instruments.** `ashscale.py` (ash density vs N with seeded ensembles, existing `attract`/`cyc`); `methus.py` (transient-length distributions; top-k longest-lived small patterns via bounded exact search).
- Claim: mean ash density of density-0.5 soups on N×N, seeds 820000..820199 per N, is monotone in N over N ∈ {16,32,48,64,96,128} and lands in a stated ±0.002 interval per N, with the N=128 value in [0.026, 0.032] (consistent with the infinite-grid ≈0.0287) [75].
- Claim: the death-cliff location p_c(N) (stated operational definition: ash density falls below half its plateau value) shifts by a stated signed amount from N=16 to N=64, seeds stated, monotone [65].
- Claim: R-pentomino lifetime on N×N converges: for all N ≥ a stated N* it stabilizes in exactly a stated generation count with stated final census (infinite-grid value 1103 + 6 gliders is the reference; on a torus the escaping gliders return, so the settled value is torus-specific per N until N* where a stated periodic regime takes over — claim the exact N-indexed table for N ∈ 16..64 step 8) [70].
- Claim: acorn (7 cells) on 128×128 stabilizes at an exactly stated generation with stated ash population and period (infinite-grid 5206 is the anchor; wrap will change it — the delta is the discovery) [65].
- Claim: among all ≤5-cell patterns on 32×32 (exhaustive over canonical forms), the maximum transient is exactly stated, achieved by exactly stated pattern(s) — the true smallest methuselah of this universe [60].
**How.** Everything seeded and ensemble-sized to fit 30s (128×128 long runs: budget ≤ 20 soups per experiment, split across experiments — replication comes free); exact claims where exhaustive, interval claims with stated seeds elsewhere.
**Traps.** The already-burned unseeded-statistics trap; 128×128 transients can exceed 4096 (use `cyc`, no cap pitfall); "monotone" claims are fragile — state the exact seeded sequence instead of the adjective when in doubt.
**Unlocks.** Calibrated large-torus budgets (steps/sec at 128×128) — the engineering data Phases 9–10 need.

### Phase 9 — Guns under wraparound
**Goal.** The Gosper gun (36 cells, period 30, emits one glider per period) on a closed universe: its emitted stream must wrap and hit something — quantify exactly what and when.
**Instruments.** `gun.py`: gun pattern + placement helpers; stream-integrity monitor (glider count vs t); attractor detection for gun+stream systems.
- Claim: on N×N with the gun at a stated placement, the gun self-destructs (first damage to its own cells) at an exactly stated generation for each N ∈ {32, 40, 48, 64} — the wraparound suicide table [80].
- Claim: there exists a stated (N, placement, orientation) where the returning stream misses the gun and the system enters a cycle: exact transient and period stated (population is bounded on a torus, so a cycle is guaranteed — the discovery is which N give gun-survival vs suicide) [65].
- Claim: gun + eater-1 placed downstream on a stated torus yields an exact period-30 attractor containing the intact gun, eater, and a stated number of in-flight gliders, verified over ≥3 full periods [70].
- Claim: the diagonal-vs-grid commensurability law from Phase 7 exactly predicts, for stated N, whether the wrapped stream re-enters the gun's bounding box — prediction table matches simulation on all N ∈ 32..64 step 4 [60].
**How.** Deterministic, seed-free; 64×64 × ~10k gens is comfortably < 30s with the bit-parallel engine. Two placements = replication.
**Traps.** Gun coordinates transcription errors (validate 30-periodicity in isolation on a huge torus first — a mandatory experiment 1); "survives" claims need a stated horizon plus a cycle-detection argument, not "ran 10k gens and looked fine"; stream density on small toruses causing glider–glider collisions upstream of the gun (a legitimate sub-discovery, not noise).
**Unlocks.** A surviving gun + eater = clocked signal source and sink: the power supply of Phase 10.

### Phase 10 — Computation: collisions become logic
**Goal.** Demonstrate computation inside the world and claim it with a runnable check: glider presence = bit, collision physics = gates.
**Instruments.** `logic.py`: circuit assembler placing guns/gliders/eaters from archived recipes; `readout(cells, t, probe_box)` decoding output bits; truth-table driver running all input combinations in one check.
- Claim: an AND gate — two input glider streams (or single gliders), annihilation/pass-through geometry from the Phase-4 vanish entry, eater cleanup — computes the full 4-row truth table on a stated torus (≈96×96), each evaluation ≤ a stated generation bound, output read as glider presence in a stated probe box at a stated time [70].
- Claim: a NOT gate (suppressor stream geometry: constant stream deleted by the input via kickback/vanish) computes its 2-row truth table under the same protocol [55].
- Claim: gate composability — an XOR or NAND built from ≥2 archived gate recipes evaluates its full truth table on a stated torus within stated bounds [45].
- Claim (crown): a half-adder (sum + carry) evaluates all 4 input pairs correctly — a genuine arithmetic computation performed by Life physics on a torus, one `check.py`, exit 0 [35].
- Claim (beyond, if reached): a 2-bit ripple adder computes all 16 cases; the check prints "2+3=5" derived only from cell states [15].
**How.** Everything is deterministic assembly of already-claimed reactions; the hard part is geometry bookkeeping, so build `logic.py` incrementally with per-junction unit experiments. All-cases-in-one-check keeps each claim a single fact.
**Traps.** The 30s wall: 16-case adder × ~2000 gens × large grid must be budgeted (pre-measure steps/sec from Phase 8); timing closure (glider path lengths must be phase-matched mod 4 — off-by-one in path length silently flips bits); compound-claim temptation (one gate per claim; the adder is one claim because it is one check).
**Unlocks.** Endgame. Every later question ("what else can it compute?") is open research.

## Endgame

**Completed archive** = the six strata each closed by exact claims: (1) exhaustive microcosm — functional graphs, GoE, cycle spectra for all WH ≤ 20, plus still-life/oscillator/ship censuses with explicit bounds; (2) interaction physics — complete two-glider tables and a device library (eater, reflector or duplicator) with restoration proofs; (3) resonance laws — closed-form return periods and commensurability rules verified over dimension grids; (4) statistical laws — seeded ash asymptote, cliff scaling, methuselah extremes; (5) gun physics — the wraparound suicide/survival table; (6) a working logic gate, and ideally the half-adder. **Stopping criteria:** every phase has ≥3 admitted claims and its instruments banked; two consecutive sessions produce only claims that are corollaries of archived laws (surprise scores persistently ≤2); all parked open questions are either resolved or provably out of oracle range (>30s minimal witness). **Crossing into open research:** anything requiring toruses ≳256² over long horizons, universal-constructor or Turing-completeness claims (the finite torus makes true universality false — bounded computation is the honest ceiling and proving that boundedness could itself be a claim), enumeration beyond ~2^24 states, and asymptotic (N→∞) laws, which can only ever be claimed as bounded seeded trends. A half-adder inside a 30-second stdlib check is the natural terminus: past it, this stops being a room a kid can poke and becomes Life engineering.

## Harness strain

The 30s timeout is the binding constraint everywhere after Phase 8: 128×128 ensembles, the 16-case adder, and gun horizons all require splitting one logical fact across the ≥2-experiment replication structure — which the harness happens to reward. Checks that re-verify expensive claims strain `verify` (the whole-archive re-run now includes a million-state census plus, prospectively, circuit evaluations — verify wall-clock grows linearly with archive ambition and has no per-world budget). Stdlib-only forbids numpy; the integer-bitmask engine covers it, but 256² would not fit. Tool namespace collisions on PYTHONPATH already forced `fixpath.py` — the growing library (`collide`, `canon`, `devices`, `logic`) raises shadowing risk. No cross-thread mutable state means circuit recipes must live as tools (code), not notes; that is the correct pressure but makes Phase 10's geometry bookkeeping expensive per thread. Finally, 8 steps/thread is tight for Phase 10 assembly work — expect multi-thread claim arcs mediated by parked open questions.

## Methodology attractor

Evolution should converge on: (1) **exact-table claims** — "the outcome map over this finite parameter grid is exactly T" beats adjectives; every phase above is a finite grid, and the gate rewards enumerate-then-state; (2) **seed-or-exhaust discipline** — nothing statistical without literal seed lists (already learned the hard way); (3) **one claim per thread, one fact per check** — compound claims die at the gate; (4) **formula-first prediction** — commit the closed-form law (resonance, thresholds) before the scan, because that is where surprise scoring pays; (5) **instrument-before-question** — a thread that banks `collide.py` unlocks ten claims, so fitness favors tool-building threads even at −0 claims; (6) **budget arithmetic in the prediction** — steps/sec × grid × horizon stated up front, since timeout deaths score as failures; and (7) **negative results as bounded censuses** — "none with pop ≤ 6 in this box" is admissible where "none exists" never is. The stable attractor is a methodology that reads as an experimental physicist's lab protocol: fixed conventions (phase epoch, canonical forms, seed ranges), enumerate exhaustively, state exactly, replicate across a second grid size.
