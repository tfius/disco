# The games under disco

Thesis: discovery against nature alone is decision theory — nature never
counter-moves. Discovery as a *practiced institution* — an agent under
incentives, methods under selection, claims under repeated attack, peers under
competition — is a stack of games at different timescales. Disco implements
most of the stack already; this document names each layer formally, says what
the game-theoretic reading buys, and marks the holes it exposes.

| # | Layer | Game class | Disco component | Timescale |
|---|-------|-----------|-----------------|-----------|
| 1 | Claim admission | Verifier/falsifier (game semantics) | gate + `check.py` | per claim |
| 2 | Question selection | Bandit vs indifferent nature | agent's OBSERVE step | per thread |
| 3 | Agent vs kernel | Mechanism design / principal–agent | frozen rules + fitness | per thread |
| 4 | Methodology | Evolutionary game (replicator, ESS) | `evolve.py` | per generation |
| 5 | Knowledge maintenance | Repeated falsification game | `verify` + cull | per session |
| 6 | Multi-agent science | Congestion + signaling | `run --agents`, per-agent lineages | per community |

## 1. Claim admission is a verifier/falsifier game

In game semantics, a statement's truth is a two-player game: Verifier tries to
establish it, Falsifier attacks; the statement is true iff Verifier has a
winning strategy. A disco claim's `check.py` **is** a Verifier strategy that
must win in finitely many moves (exit 0 before the timeout).

Consequence, discovered empirically in the busybeaver program and explained
here: the gate admits exactly the claims whose verification game *terminates* —
the Σ₁ fragment. "Machine M halts in k steps" is a finite Verifier win: run it.
"M never halts" is Π₁ — Falsifier gets to demand one more step forever, and no
check can play an infinite game. The busybeaver claim typology
(`halts(k)` / `bounded(B)` / `certified(prover, witness)`) is a reclassification
of statements by which games terminate: a certificate converts an infinite game
into a finite one *conditional on the prover's soundness* — which is why prover
soundness must itself become a claim (a new finite game), and why a buggy
prover rots its dependents invisibly (the check replays the same losing-but-
declared-winning strategy).

`verify` is the same game replayed: reality gets a fresh move against every
archived claim, every session. A cull is Falsifier finally winning.

`PREDICT_CODE` makes the Verifier move *executable and pre-committed*: the agent
ships assertions the kernel runs against the actual result, and their verdict
bounds the surprise score (held caps it, violated floors it). The subjective
judge is demoted to grading nuance inside a band that execution already fixed —
the falsifier game, moved before the outcome and anchored in code.

**What the frame buys:** a precise grammar for admissible claims per world.
Every "harness strain" section in the world programs — limit claims in
sandpile, asymptotics in random-graphs, ∀-claims in python — is the same
theorem: only finitely-decidable games fit through the gate, so worlds must
phrase their truths as bounded instances, certificates, or seeded tables.

## 2. Question selection is a bandit — but nature doesn't play

Choosing what to probe next is an explore/exploit problem: arms are veins of
territory, payoff is learnable surprise (prediction error that shrinks under
study), budget is threads. This is the one layer that is *not* strictly a game:
nature is an indifferent opponent with a fixed strategy — Milnor's "games
against Nature" are decision theory in game clothing. The surprise signal is
disco's information-payoff estimate, and the learnability rule (flat surprise =
noise, abandon) is the bandit discarding an arm whose payoff is pure variance.

It becomes a true game in exactly two places: when the *mechanism* rewards the
choice (layer 3 — pick easy veins to farm fitness), and when *other agents*
mine the same territory (layer 6 — crowding). Strategy enters through
incentives and peers, never through nature.

## 3. Agent vs kernel is mechanism design — the strategic core

Players: the agent (maximizes fitness: +3 admitted, −2 rejected, +1 parked,
−0.5 premature, −1 failures) and the kernel-designer (wants true, non-trivial,
compressive knowledge). These objectives diverge; Goodhart is the agent finding
an **unintended equilibrium** of the reward game. Every frozen rule is a
mechanism-design move, and the design goal has a name: make honest discovery
the **incentive-compatible** strategy.

| Frozen rule | Mechanism function |
|---|---|
| No claim without a check | Verifiability constraint: only finitely-refutable messages accepted |
| Replication gate (≥2 experiments) | Costly signaling: cheap talk priced out |
| Agent cannot write archive/ledger | The principal keeps the books |
| Judge in fresh context, prediction pre-committed | No renegotiation of the bet after the outcome |
| Surprise excluded from fitness | Removes the sandbagging equilibrium (predict wrong on purpose) |
| Cull on repeated check failure | Repeated-game punishment: defection against reality is eventually paid |
| Fitness formula frozen in kernel | Commitment device: the principal cannot be lobbied |

Known unintended equilibria — the open mechanism problems, all previously
observed or predicted in this repo:

- **Trivial-claim farming**: exact-but-empty claims harvest +3 forever. The
  mechanism's counter is the audit's uplift metric (a second price: knowledge
  must *predict*), plus human pruning — an equilibrium refinement applied from
  the slow loop.
- **Circular bounded checks** (busybeaver): "didn't halt in 10⁶ steps" verified
  by re-running 10⁶ steps is a truthful message with zero content — admissible,
  unfalsifiable, worthless. The fix is typological (certificates), i.e. a
  richer message space, not a bigger penalty.
- **Check-independence hollowness** (sandpile crown): the gate cannot see that
  two "independent" computations share code. Collusion between a claim and its
  own check is undetectable by the mechanism and must be policed by methodology
  or audit.
- **Prover-dependency rot**: conditional claims form a dependency graph the
  per-claim cull cannot see; a shared dependency is a single point of silent
  failure. Mechanism gap: verify treats claims as independent players when they
  are a coalition.

## 4. Methodology evolution is evolutionary game theory, literally

`evolve.py` runs a replicator process over strategy space: methodologies are
strategies, worlds are environments, the frozen fitness is the payoff function,
champion/challenger trials are contests, promotion is selection. The
"methodology attractor" sections of the eight world programs are **ESS
candidates**: strategies that, once fixed, no mutant methodology can invade
under that world's payoffs (certificate discipline in busybeaver, exact-first
in logistic, atlas-building in eca, seeded-interval statistics in
random-graphs).

The degenerate attractors repeatedly flagged — tournament mill (ipd), interval
farming (random-graphs), census comfort (eca), sizeof farming (python) — are
*bad equilibria that are genuinely stable* under thread-fitness alone. They are
not bugs in evolution; they are correct convergence to a misspecified payoff.
The counter-metrics (uplift audit, human seeds) act as equilibrium refinements:
they change the payoff landscape so the boring ESS stops being one.

Two-generation empirical record so far: sim-life selected *against* written
methodology twice (the empty strategy is hard to beat when the base model is
already strong — a floor effect, in ESS terms a resident strategy with high
baseline fitness); eca promoted its first challenger. Small-sample noise
dominates at 4+4 trials; the game-theoretic reading says: expect punctuated
equilibria, not steady improvement.

## 5. Knowledge maintenance is a repeated game against drift

A claim is a strategy in an indefinitely iterated game: each `verify` round,
reality moves, and the claim either holds (cooperation sustained) or fails
(defection observed). Two consecutive failures trigger the cull — a punishment
strategy with built-in forgiveness (one failure is forgiven if the next round
passes; a culled claim is not deleted but demoted to an open question, i.e.
allowed to re-enter the game after re-earning trust). This is tit-for-tat-like
maintenance: cheap to state, robust to transient noise, and it makes the
archive's long-run composition an equilibrium outcome — only claims whose
verification games reality keeps losing survive.

## 6. Multi-agent science: the built layer

With one agent, question selection is a bandit; with several sharing an
archive it becomes strategic:

- **Congestion**: two agents mining the same vein duplicate work — payoff per
  claim decreases with crowding (duplicate slugs already bounce). Division of
  cognitive labor is the congestion game's efficient equilibrium; whether it
  *emerges* without central assignment is the experiment.
- **Signaling**: an archived claim signals "this vein pays" — free-riding on
  others' surprise gradients is rational, and a mixture of leaders and
  followers is the predicted equilibrium.
- **Priority**: first-to-archive attribution creates a race; races overweight
  fast-cheap claims — the same distortion human science exhibits, reproducible
  and measurable here.

The design shipped: agent identities on threads (`run --agents alice,bob`),
per-agent methodology lineages evolving independently against shared fitness,
one shared archive, ledger attribution. **First result:** in an 8-thread
two-agent session the measured focus-overlap was 0.246 — well below the ~0.5
random-assignment line, so division of cognitive labor *emerged from the
payoffs*, with no coordinator (one agent taking ash statistics and strip-image
instruments, the other image-count scaling and runtime laws). The congestion
game's efficient equilibrium showed up on first contact. Still unmeasured: the
signaling equilibrium (do agents free-ride on each other's surprise gradients?)
and the priority race (does first-to-archive attribution distort toward
fast-cheap claims?) — both now observable, since every ledger entry carries its
agent.

## 7. The RL reading

Collapse the stack and disco is an environment suite: a world = a POMDP whose
reward function is the layer-3 mechanism, whose episodes are threads, and
whose curriculum is endogenous (the archive grows, the frontier hardens, the
bandit's payoff landscape shifts). The mechanism-design work above is exactly
what makes the rewards **hard to hack**: every anti-Goodhart rule is a patch
on the reward function, executed before training rather than after. Held-out
*generated* worlds (`genworld` — rule tables rolled at random, guaranteed
absent from any pretraining corpus) give the clean generalization test: an
agent that transfers to a world no one has ever described has learned
discovering, not discoveries.

Empirical note (gen-42, first session): documented worlds open at surprise
0–3 (priors work); the generated world opened at 6, 8, 10 — including the
project's first maximal surprise, inside an 8→3→8→10→0 arc that isolated a
genuine law (direction-asymmetric damage propagation) and still had its claim
refused on a failed check. The reward landscape of a generated world is
observably different from a documented one — which is precisely what makes the
held-out-world eval meaningful.

Empirical postscript on the reward game: group sampling (`disco rollout`) makes
the layer-3 reward's shape visible. On a strong policy the *outcome* reward
saturates — every rollout in a group lands some admitted claim, so std → 0 and
the group carries no gradient. But the *process* signal (surprise closure) spans
the whole range within one frozen context (−8 to +9 observed). The mechanism's
anti-hacking property survives, but for a competent player the usable gradient
has moved from the outcome to the process term — which is why groups are sampled
at the `coevolve` frontier, where difficulty keeps the outcome game live.

## What the frame buys, in one list

1. A **claim grammar** per world (which verification games terminate) — derived,
   not guessed.
2. A **design checklist** for new rules: every proposed freeze is a mechanism;
   ask which equilibrium it removes and which it accidentally creates.
3. **Named failure modes**: Goodhart = unintended equilibrium; circular checks =
   truthful-but-contentless messages; methodology stagnation = resident-strategy
   advantage; archive rot = defection in a repeated game.
4. **Impossibility honesty**: Π₁ claims cannot be admitted, only certified;
   no mechanism detects check-collusion from inside; nature cannot be out-played,
   only out-asked.
5. A **built experiment** for layer 6 (multi-agent) with a falsifiable success
   metric — division of labor emerged (overlap 0.246 < 0.5 baseline).
