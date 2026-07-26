# Goal: disco as a discovery engine

> Make disco a discovery engine with worlds as RL environments — agent vs.
> kernel with methodology evolution, knowledge maintenance, and multi-agent
> science.

The formal skeleton for all of this is [games.md](games.md): each pillar below
is one layer of the game stack made executable.

## Pillar status

**Agent vs. kernel (mechanism) — built.** Frozen fitness, replication gate,
check-gated admission, pre-committed predictions, fresh-context judge. Open
mechanism problems (from games.md §3): trivial-claim farming, circular bounded
checks, check-collusion, prover-dependency rot. Each needs a mechanism patch,
not a bigger penalty.

**Methodology evolution — built.** Champion/challenger replicator per world.
Empirical record: two discards (sim-life — strong resident baseline), one
promotion (eca). Known weakness: 4+4 trials are noisy; fitness saturates when
admission rate is high. Candidate upgrade: delayed verify-survival scoring
(claims earn full fitness only after surviving their next verify; culls score
retroactively against the variant that made them).

**Knowledge maintenance — built.** Auto-verify before every session; rot
counters; cull-to-open-question with re-earning. Gap: claim dependency graphs
(a claim whose check imports a tool, or cites a prover, rots silently when the
dependency breaks) — verify treats claims as independent when they are a
coalition.

**Worlds as RL environments — bootstrapped this commit.**
- `disco.py export`: threads → episode JSONL (trajectory, surprise scores,
  outcome, mechanism reward, transcript). Positive/negative labels are
  execution-anchored (gate + verify), never judge-opinion.
- `disco.py genworld <seed>`: procedurally generated CA worlds whose rule
  tables are rolled at random — truths guaranteed absent from any pretraining
  corpus. These are the contamination-free train/eval territories.
- Next: batch rollout runner (many worlds × many threads unattended, cheap
  local models acceptable — the gate filters quality); reward summaries per
  episode aligned with `evolve.SCORES`; calibration extraction (stated
  confidence vs judged outcome → proper scoring data).
- Eval protocol: train on N generated worlds, evaluate on held-out generated
  worlds. Transfer = learned discovering; no transfer = memorized discoveries.

**Multi-agent science — built** (games.md §6), in the order planned:
agent identity with ledger attribution on every entry; per-agent methodology
lineages (`methodology-NAME.md`, independent champion/challenger evolution)
over one shared archive; crowding-overlap metric in `stats`; the interleaved
runner (`run --agents alice,bob`). The division-of-labor experiment (overlap
vs random-assignment baseline) awaits a live two-agent session. Later:
priority/attribution effects, leader/follower signaling.

## First empirical result: the surprise signature

gen-42's first session (2026-07-25) validated the contamination argument with
data. First contact with documented worlds (sim-life, eca) opened at surprise
0–3 — priors doing the work, "discovery" partly recall. First contact with
gen-42 opened at 6, 8, 10 — the project's first maximal surprise — because no
priors exist. The thread-3 arc (8, 3, 8, 10, 0) discovered a genuine law of the
generated universe (damage propagation is direction-asymmetric: a 1→0 flip
spreads unbounded, a 0→1 flip stays frozen forever), closed it to surprise 0,
and still had its claim refused on a failed check — the mechanism holding at
peak drama. **Mean first-contact surprise now measurably separates recall from
discovery**, which gives the RL framing its eval signature: on generated
worlds, surprise is high and earned, and a model that has learned discovering
should close it efficiently. `disco stats` reports these numbers per world;
the per-episode surprise trajectories in `disco export` are the process signal.

## Sequencing

1. **Now**: export + genworld (done); first generated-world session (done —
   above); world families beyond CA (`genworld --family modpoly|tag`) and
   per-world discovery-efficiency stats (done).
2. **Short — done**: batch rollout runner (`disco grind <seeds> --family F -n T`:
   generate + run + stats + export per world, unattended; the gate filters
   quality so cheap local models still yield usable episodes); delayed fitness
   v1 (culls are charged to the lineage that made the claim — live-trial
   penalty −3 when applicable, permanent ledger attribution otherwise);
   dependency tracking (`disco deps` claim→tool graph; verify names suspect
   imports on failures); turn-level process rewards + trajectory filter labels
   in export.
3. **Mid — done**: multi-agent science (above); cull cascades on tool overwrite
   with one transitive tool→tool hop; `disco calib` cross-world calibration
   (r(confidence, surprise) = −0.54 over the current corpus).

## Epistemics upgrades (2026-07-26)

- **Executable predictions**: PREDICT_CODE assertions run against the actual
  result; the objective verdict bounds the judge (held ≤3, violated ≥6). The
  surprise signal — and everything downstream: closure, process rewards,
  evolution fitness — is now execution-anchored end to end. Per-step
  `objective` field ships in exports.
- **Theory threads**: claims can supersede archived claims they generalize;
  the kernel folds instances into the law and the archive compresses. The
  measure of understanding is now literally the shrinking of the index.

## Known limitations (honest ledger)

- Trial contamination: champion outcomes recorded while no challenger exists
  count toward the next trial once one is proposed — mild asymmetry, visible in
  evolution.json, not yet corrected.
- Cascade depth: tool→tool dependency tracking goes one transitive hop; deeper
  chains fall back to the session-level full verify.
- Coevolve judges worlds on cumulative stats, not a recent window — a world
  that starts hard and gets cracked can look mediocre forever; windowed judging
  is the upgrade.
- Multi-agent crowding uses token-Jaccard on focus lines — a crude similarity;
  fine for the emergence experiment's yes/no, too blunt for anything finer.

## GRPO readiness

`disco rollout --group G [--question "..."] [--commit-best]` samples G threads
from one frozen, identical context (same archive snapshot, methodology, and
optional pinned question), each on an isolated copy of the world — archive
mutations discarded, episodes appended to `exports/rollouts-<world>.jsonl`
with a shared `group` id. Group-relative advantages are printed and trivially
recomputable by a trainer; execution-anchored rewards make them hard to hack.
Two facts matter for training runs: (1) group-relative normalization cancels
per-world difficulty, so multi-world batches need no reward engineering;
(2) saturated worlds produce std=0 groups (all +3) with zero GRPO signal —
groups must be sampled at the coevolve frontier, which is what the frontier
is for. `--commit-best` turns group sampling into a best-of-G archive-growth
policy: better training data and a better archive from the same compute.

Empirical conclusion after two live groups (10 rollouts, gen-42 and the
frontier world gen-1002): outcome reward saturates at +3 for a strong model —
every rollout lands some admitted claim — while process signals vary widely
within the same group (closure −8..+9, mean surprise 0.0..6.33). For GRPO on
strong models the group reward must be outcome shaded with process terms; all
needed fields ship in every episode, so the weighting stays a trainer-side
choice. Same lesson applied to best-of-G selection: outcome ties now break
toward highest closure, then mean surprise — the first pure-outcome pick chose
the rollout that asked a question it already knew the answer to.

## External recipe check (Nanbeige 4.2-3B)

A published compact-agent recipe maps 1:1 onto disco's outputs: environment
integrations = the documented worlds; large-scale environment synthesis =
`genworld` families × seeds; task/asset/scaffold diversity = self-generated
questions + per-world tools + evolving methodology; trajectory-level filtering
with test-case validation = gate + verify survival (`filters` in export);
turn-level filtering with rubric assessment = per-step judge surprise; outcome
rewards = frozen fitness; process rewards = per-step surprise closure
(`process_reward` in export). Empirical exhibit: gen-42's rejected thread has
outcome reward −2 but contains a +10 process-reward step (the surprise-10→0
close) — exactly the trajectory that outcome-only filtering loses and combined
rewards keep.
4. **Long — partly built**: `disco coevolve` (POET loop) and `disco rollout`
   (GRPO groups) shipped; still open: cross-world
   methodology transfer (does a busybeaver-evolved methodology help in a
   generated world?); RL training loop proper, with held-out-world eval as the
   only score that counts.
