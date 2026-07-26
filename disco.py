#!/usr/bin/env python3
"""disco — a minimal discovery harness. Predict, run, be surprised, compress, archive."""
import argparse
import json
import os
import sys

from kernel import archive, audit, config, evolve, export, ledger, loop


def _run_session(n, agents=None) -> bool:
    """Run n threads in the current world, optionally interleaving agent
    identities (each agent has its own methodology lineage; the archive is
    shared). Returns False on backend abort."""
    if config.CLAIMS.exists() and any(config.CLAIMS.iterdir()):
        print("pre-run verify (selection):")
        archive.verify_all()
    evolving = os.environ.get("DISCO_EVOLVE", "1") != "0"
    for i in range(n):
        if agents:
            config.set_agent(agents[i % len(agents)])
            print(f"thread {i + 1}/{n} [agent {config.AGENT}]")
        else:
            print(f"thread {i + 1}/{n}")
        try:
            variant, methodology = evolve.current() if evolving else ("champion", None)
            if evolving:
                print(f"  methodology variant: {variant} (gen {evolve._state()['generation']})")
            outcome = loop.run_thread(methodology=methodology)
        except RuntimeError as e:
            print(f"  aborted (endpoint?): {e}", file=sys.stderr)
            return False
        print(f"  ended: {outcome['ending']} after {outcome['steps']} step(s)")
        if evolving:
            evolve.note(outcome, variant)
    return True


def cmd_run(args):
    agents = [a.strip() for a in args.agents.split(",")] if args.agents else None
    _run_session(args.n, agents=agents)


def cmd_grind(args):
    """Batch rollout runner: generated worlds x threads, unattended. The gate
    filters quality, so weak/cheap models still yield usable training episodes."""
    from kernel import stats
    for seed in args.seeds:
        name = _genworld_create(args.family, seed, must_create=False)
        config.set_world(name)
        print(f"===== grind: {name}")
        if not _run_session(args.n):
            print("backend down — stopping grind", file=sys.stderr)
            break
        print(stats.render(stats.compute()))
        path, count = export.episodes()
        print(f"exported {count} episodes -> {path}")


def cmd_verify(args):
    archive.verify_all()


FIT_TEST = """fit test — a world works for disco when ALL four hold:
  1. cheap oracle    — reality answers in seconds and cannot be argued with
  2. predictable     — outcomes can be stated up front, specifically enough to be wrong
  3. re-checkable    — claim checks can re-ask reality anytime, forever (verify)
  4. safe to poke    — observing does not mutate or damage the world
"""


def cmd_worlds(args):
    config.WORLDS.mkdir(exist_ok=True)
    names = sorted(d.name for d in config.WORLDS.iterdir() if d.is_dir())
    if "python" not in names:
        names.insert(0, "python")
    for name in names:
        wd = config.WORLDS / name
        desc_file = wd / "world.md"
        desc = (desc_file.read_text().strip().splitlines()[0][:90]
                if desc_file.exists() else config.DEFAULT_WORLD_TEXT)
        claims_dir = wd / "archive" / "claims"
        n = len(list(claims_dir.iterdir())) if claims_dir.exists() else 0
        marker = "*" if name == config.WORLD else " "
        print(f"{marker} {name} ({n} claims): {desc}")


def cmd_newworld(args):
    config.set_world(args.name)
    if (config.WORLD_DIR / "world.md").exists():
        sys.exit(f"world '{args.name}' already exists — run it: python3 disco.py -w {args.name} run")
    config.ensure_dirs()
    (config.WORLD_DIR / "world.md").write_text(args.description.strip() + "\n")
    print(f"world '{args.name}' created — territory: {config.WORLD_DIR / 'world.md'}\n")
    print(FIT_TEST)
    print(f"then: python3 disco.py -w {args.name} run -n 3")


def cmd_evolve(args):
    s = evolve._state()
    champ = evolve.champion_text()
    chal = evolve.challenger_text()
    hist = evolve._hist_dir()
    print(f"world: {config.WORLD} — agent {config.AGENT} — generation {s['generation']}, "
          f"{len(list(hist.glob('gen-*.md'))) if hist.exists() else 0} promoted ancestors")
    print(f"\nchampion methodology:\n{champ or '(empty — never evolved)'}")
    if chal is not None:
        print(f"\nchallenger on trial "
              f"({len(s['champion'])}+{len(s['challenger'])}/{config.TRIAL_THREADS}×2 threads):\n{chal}")
    else:
        print("\nno challenger on trial (one will be proposed at next run)")


def cmd_stats(args):
    from kernel import stats
    print(f"world: {config.WORLD}")
    print(stats.render(stats.compute()))


def cmd_export(args):
    path, count = export.episodes(args.out)
    print(f"exported {count} episodes -> {path}")


GEN_CLOSING = ("This system was generated at random from seed {seed}; nothing about it "
               "exists in any literature — every law is undiscovered, and there are no "
               "names for anything: define every term operationally. Claims must be "
               "exact, seeded, and checked by re-running the system.\n")


def _gen_ca(rng, seed, difficulty=0):
    tiers = [[(2, 2), (3, 1)], [(3, 2)], [(4, 2)]]
    k, r = rng.choice(tiers[min(difficulty, 2)])  # never (2,1): elementary CAs are documented
    n = k ** (2 * r + 1)
    table = [rng.randrange(k) for _ in range(n)]
    table[0] = 0  # quiescent background so structure has somewhere to live
    return (f"{k} states, radius {r}, {n}-entry random table",
            f"Your world is a one-dimensional cellular automaton with {k} states and "
            f"radius {r}, on finite cyclic tapes and bounded windows. Each cell's next "
            f"state is given by this rule table, indexed by the neighborhood read as a "
            f"base-{k} number (leftmost cell most significant):\n\n{table}\n\n"
            f"Implement the rule once as a tool, validate it against the table, then "
            f"discover: backgrounds and invariants, cycle structure on small widths, "
            f"particles and their collisions, statistical behavior of random tapes. ")


def _is_prime(n):
    if n < 2 or n % 2 == 0:
        return n == 2
    return all(n % d for d in range(3, int(n ** 0.5) + 1, 2))


def _gen_modpoly(rng, seed, difficulty=0):
    lo, hi = [(53, 251), (251, 1500), (1500, 8000)][min(difficulty, 2)]
    # prime modulus above tier 0: composite m leaks CRT decomposition the model
    # already knows (observed live twice) — primes force genuine graph discovery
    m = rng.randrange(lo, hi)
    if difficulty > 0:
        while not _is_prime(m):
            m = rng.randrange(lo, hi)
    coeffs = [rng.randrange(m) for _ in range(4)]  # a0 + a1 x + a2 x^2 + a3 x^3
    return (f"x -> ({coeffs[3]}x^3+{coeffs[2]}x^2+{coeffs[1]}x+{coeffs[0]}) mod {m}",
            f"Your world is the dynamical system f(x) = ({coeffs[3]}*x**3 + "
            f"{coeffs[2]}*x**2 + {coeffs[1]}*x + {coeffs[0]}) % {m} iterated on "
            f"Z_{m} = {{0..{m - 1}}}. Discover its functional graph exactly: fixed "
            f"points, cycle spectrum, tail lengths, preimage structure (which points "
            f"have none, the in-degree distribution), how orbits of all {m} starting "
            f"points partition, and any algebraic structure that explains what you "
            f"find. The full graph is exhaustively computable — exact claims only. ")


def _gen_tag(rng, seed, difficulty=0):
    d = rng.choice([2, 3])
    alphabet = "ab" if difficulty == 0 else "abc"
    maxlen = 5 + 2 * min(difficulty, 3)
    prods = {s: "".join(rng.choice(alphabet) for _ in range(rng.randrange(0, maxlen)))
             for s in alphabet}
    rules = ", ".join(f"'{s}' -> '{prods[s]}'" for s in alphabet)
    return (f"tag system d={d}, " + ", ".join(f"{s}->{prods[s] or 'ε'}" for s in alphabet),
            f"Your world is a tag system on the alphabet {{{', '.join(alphabet)}}}: at "
            f"each step, if the word has fewer than {d} symbols the system halts; "
            f"otherwise read the first symbol, delete the first {d} symbols, and append "
            f"its production: {rules} (empty string allowed). "
            f"Discover: which initial words halt, grow forever, or cycle; growth "
            f"rates; periodic structures; decidable non-halting patterns. Bound every "
            f"simulation with explicit step budgets, and phrase non-halting claims "
            f"only via decidable certificates. ")


def _genworld_create(family, seed, must_create=True, difficulty=0) -> str:
    import random as _random
    rng = _random.Random(f"{family}-{seed}")
    summary, body = {"ca": _gen_ca, "modpoly": _gen_modpoly, "tag": _gen_tag}[family](
        rng, seed, difficulty)
    name = f"gen-{seed}" if family == "ca" else f"gen-{family}-{seed}"
    config.set_world(name)
    if (config.WORLD_DIR / "world.md").exists():
        if must_create:
            sys.exit(f"world '{name}' already exists — run it: python3 disco.py -w {name} run")
        return name
    config.ensure_dirs()
    (config.WORLD_DIR / "world.md").write_text(body + GEN_CLOSING.format(seed=seed))
    print(f"world '{name}' created — {summary}")
    return name


def cmd_genworld(args):
    """Procedurally generated world — rules rolled from a seed, so their truths
    cannot exist in any pretraining corpus. The contamination-free territories."""
    name = _genworld_create(args.family, args.seed, difficulty=args.difficulty)
    print(f"run: python3 disco.py -w {name} run -n 3")


def cmd_calib(args):
    """Cross-world calibration: stated confidence vs judged surprise. High
    confidence should mean low surprise; r is the anti-correlation to watch."""
    pairs = []
    if not config.WORLDS.exists():
        print("(no worlds yet)")
        return
    for wd in sorted(config.WORLDS.iterdir()):
        lf = wd / "ledger.jsonl"
        if not lf.is_file():
            continue
        for line in lf.read_text().splitlines():
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("kind") == "step" and e.get("confidence") is not None \
                    and e.get("surprise") is not None:
                pairs.append((e["confidence"], e["surprise"]))
    if not pairs:
        print("(no calibration data yet)")
        return
    buckets = {}
    for c, s in pairs:
        b = min(c // 20, 4)
        buckets.setdefault(b, []).append(s)
    print(f"{len(pairs)} (confidence, surprise) pairs across all worlds:")
    for b in sorted(buckets):
        ss = buckets[b]
        print(f"  confidence {b*20:>3}-{b*20+19:<3}: mean surprise "
              f"{sum(ss)/len(ss):.2f}  (n={len(ss)})")
    n = len(pairs)
    mc = sum(c for c, _ in pairs) / n
    ms = sum(s for _, s in pairs) / n
    cov = sum((c - mc) * (s - ms) for c, s in pairs)
    vc = sum((c - mc) ** 2 for c, _ in pairs) ** 0.5
    vs = sum((s - ms) ** 2 for _, s in pairs) ** 0.5
    r = cov / (vc * vs) if vc and vs else 0.0
    print(f"correlation(confidence, surprise) = {r:.3f}  "
          f"(calibrated agents are strongly negative)")


def cmd_coevolve(args):
    """POET-shaped loop: keep a population of generated worlds at the frontier
    of the agent's competence — graduate the too-easy (raising difficulty),
    park the too-hard (lowering it), roll replacements, run sessions, export."""
    from kernel import stats
    state_file = config.ROOT / "coevolve.json"
    st = json.loads(state_file.read_text()) if state_file.exists() else \
        {"active": [], "retired": [], "next_seed": 1000, "difficulty": 0}
    families = ["ca", "modpoly", "tag"]
    try:
        while len(st["active"]) < args.pop:
            fam = families[st["next_seed"] % len(families)]
            name = _genworld_create(fam, st["next_seed"], must_create=False,
                                    difficulty=st["difficulty"])
            st["active"].append(name)
            st["next_seed"] += 1
        for name in list(st["active"]):
            config.set_world(name)
            print(f"===== coevolve: {name} (difficulty {st['difficulty']})")
            if not _run_session(args.n):
                print("backend down — stopping coevolve", file=sys.stderr)
                return
            s = stats.compute()
            path, count = export.episodes()
            print(stats.render(s))
            print(f"exported {count} episodes -> {path}")
            if s and s["threads"] >= args.judge_after:
                rate = s["admitted"] / s["threads"]
                if rate >= 0.75 and s["mean_surprise"] <= 3:
                    print(f"  GRADUATED (too easy: admit {rate:.0%}, "
                          f"surprise {s['mean_surprise']}) — difficulty up")
                    st["active"].remove(name)
                    st["retired"].append({"name": name, "why": "graduated"})
                    st["difficulty"] += 1
                elif s["admitted"] == 0:
                    print("  PARKED (too hard: nothing admitted) — difficulty down")
                    st["active"].remove(name)
                    st["retired"].append({"name": name, "why": "too-hard"})
                    st["difficulty"] = max(0, st["difficulty"] - 1)
            # persist after every world: a hard kill must not lose judgments
            state_file.write_text(json.dumps(st, indent=2))
    finally:
        state_file.write_text(json.dumps(st, indent=2))
        print(f"coevolve state: {len(st['active'])} active, "
              f"{len(st['retired'])} retired, difficulty {st['difficulty']}")


def cmd_deps(args):
    """Claim -> tool dependency graph: which knowledge stands on which instruments."""
    config.ensure_dirs()
    tool_users = {t.stem: [] for t in config.TOOLS.glob("*.py")}
    claims = sorted(config.CLAIMS.iterdir()) if config.CLAIMS.exists() else []
    for d in claims:
        check = d / "check.py"
        deps = archive.tool_imports(check.read_text()) if check.exists() else []
        if deps:
            print(f"{d.name[:56]} <- {', '.join(deps)}")
        for dep in deps:
            tool_users.setdefault(dep, []).append(d.name)
    print()
    for tool, users in sorted(tool_users.items(), key=lambda kv: -len(kv[1])):
        tag = f"{len(users)} dependent claim(s)" if users else "no dependent claims (unused by checks)"
        print(f"tool {tool}: {tag}")


def cmd_rollout(args):
    """GRPO group sampling: G independent threads from one frozen, identical
    context (same archive snapshot, same methodology, same optional question),
    each on an isolated copy of the world — archive mutations discarded, episodes
    kept with a shared group id. Optionally commit the best rollout's claim."""
    import hashlib
    import shutil
    import time
    src, world_name = config.WORLD_DIR, config.WORLD
    meth = ""
    mf = src / "methodology.md"
    if mf.exists():
        meth = mf.read_text().strip()
    context = config.world_description() + "\n" + meth + "\n" + archive.index() \
        + "\n" + (args.question or "")
    gid = hashlib.sha256(context.encode()).hexdigest()[:12]
    base = config.ROOT / "rollouts" / f"{world_name}-{time.strftime('%Y%m%d-%H%M%S')}"
    out_dir = config.ROOT / "exports"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / f"rollouts-{world_name}.jsonl"
    print(f"group {gid}: {args.group} rollouts from frozen context")

    episodes, dirs = [], []
    try:
        for i in range(args.group):
            rdir = base / f"r{i}"
            shutil.copytree(src, rdir, ignore=shutil.ignore_patterns(
                "runs", "rollouts", "__pycache__"))
            (rdir / "ledger.jsonl").unlink(missing_ok=True)
            if args.question:
                qdir = rdir / "archive" / "open-questions"
                qdir.mkdir(parents=True, exist_ok=True)
                for q in qdir.glob("*.md"):
                    q.unlink()
                (qdir / "rollout-question.md").write_text(f"# {args.question}\n")
            config.point_at(rdir, world_name)
            print(f"rollout {i + 1}/{args.group}")
            try:
                loop.run_thread(methodology=meth)
            except RuntimeError as e:
                print(f"  aborted (endpoint?): {e}", file=sys.stderr)
                break
            _, count = export.episodes(out_path=rdir / "episodes.jsonl")
            if count:
                ep = json.loads((rdir / "episodes.jsonl").read_text().splitlines()[-1])
                ep["group"], ep["rollout"] = gid, i
                with open(out_file, "a") as f:
                    f.write(json.dumps(ep) + "\n")
                episodes.append(ep)
                dirs.append(rdir)
                print(f"  ended: {ep['ending']} — reward {ep['reward']}")
    finally:
        config.set_world(world_name)

    if not episodes:
        print("no episodes produced")
        return
    rewards = [e["reward"] for e in episodes]
    mean = sum(rewards) / len(rewards)
    var = sum((r - mean) ** 2 for r in rewards) / len(rewards)
    std = var ** 0.5
    advs = [round((r - mean) / std, 2) if std else 0.0 for r in rewards]
    print(f"group rewards: {rewards} — mean {mean:.2f}, std {std:.2f}")
    print("process signals (outcome-flat groups still differ here):")
    for e in episodes:
        print(f"  r{e['rollout']}: steps {len(e['steps'])}, "
              f"mean_surprise {e['mean_surprise']}, closure {e['closure']}")
    print(f"advantages:    {advs}" + ("  (std=0: degenerate group — world too easy/hard "
                                      "for GRPO signal; use the coevolve frontier)" if not std else ""))
    print(f"episodes appended -> {out_file}")

    if args.commit_best:
        # ties in outcome reward break toward the rollout that LEARNED most —
        # outcome-only selection picks the safest question, not the best science
        best = max(range(len(episodes)),
                   key=lambda i: (episodes[i]["reward"],
                                  episodes[i].get("closure") or 0,
                                  episodes[i].get("mean_surprise") or 0))
        ep, rdir = episodes[best], dirs[best]
        if ep["admitted"] and ep.get("slug"):
            src_claims = {d.name for d in (src / "archive" / "claims").iterdir()} \
                if (src / "archive" / "claims").exists() else set()
            new = [d for d in (rdir / "archive" / "claims").iterdir()
                   if d.name not in src_claims]
            for d in new:
                shutil.copytree(d, src / "archive" / "claims" / d.name)
            src_tools = {t.name for t in (src / "archive" / "tools").glob("*.py")} \
                if (src / "archive" / "tools").exists() else set()
            for t in (rdir / "archive" / "tools").glob("*.py"):
                if t.name not in src_tools:
                    shutil.copy(t, src / "archive" / "tools" / t.name)
            print(f"best-of-{args.group} committed: rollout {best} "
                  f"({[d.name for d in new]}) — next verify will police it")
        else:
            print("best rollout admitted nothing — nothing committed")


def cmd_seed(args):
    config.ensure_dirs()
    slug = archive.save_question(args.title, args.body or "(seeded by human — territory, not instructions)", "human-seed")
    print(f"seeded open question: {slug}")


def cmd_reset(args):
    import shutil
    import time
    attic = config.ROOT / "attic" / f"{config.WORLD}-{time.strftime('%Y%m%d-%H%M%S')}"
    attic.mkdir(parents=True)
    moved = []
    lineage = [p for pat in ("methodology*", "evolution*.json")
               for p in config.WORLD_DIR.glob(pat)]
    for path in [config.ARCHIVE, config.RUNS, config.LEDGER] + lineage:
        if path.exists():
            shutil.move(str(path), str(attic / path.name))
            moved.append(path.name)
    config.ensure_dirs()
    print(f"moved {', '.join(moved) or 'nothing'} -> {attic}")
    print("archive is empty — everything is undiscovered again")


def cmd_audit(args):
    audit.run(k=args.k)


def cmd_status(args):
    config.ensure_dirs()
    print(f"world: {config.WORLD} — {config.world_description().splitlines()[0][:90]}\n")
    print(archive.index())
    print("\nrecent:")
    print(ledger.tail(20))


def main():
    sys.stdout.reconfigure(line_buffering=True)  # live progress even when piped/backgrounded
    p = argparse.ArgumentParser(prog="disco", description=__doc__)
    p.add_argument("-w", "--world", default=None,
                   help="world to explore (default: $DISCO_WORLD or 'python')")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run discovery threads")
    r.add_argument("-n", type=int, default=1, help="number of threads")
    r.add_argument("--agents", default=None,
                   help="comma-separated agent names to interleave (shared archive, per-agent methodology)")
    r.set_defaults(fn=cmd_run)
    a = sub.add_parser("audit", help="measure archive uplift on a naive agent")
    a.add_argument("-k", type=int, default=8, help="samples")
    a.set_defaults(fn=cmd_audit)
    s = sub.add_parser("status", help="archive index + recent ledger")
    s.set_defaults(fn=cmd_status)
    v = sub.add_parser("verify", help="re-run all claim checks (claims-rot audit)")
    v.set_defaults(fn=cmd_verify)
    rs = sub.add_parser("reset", help="fresh start: move the world's archive/runs/ledger to attic/<world>-<ts>/")
    rs.set_defaults(fn=cmd_reset)
    sd = sub.add_parser("seed", help="park a human question in the world's open-questions/")
    sd.add_argument("title", help="one-line territory to explore")
    sd.add_argument("body", nargs="?", default="", help="optional context/details")
    sd.set_defaults(fn=cmd_seed)
    wl = sub.add_parser("worlds", help="list worlds and their claim counts")
    wl.set_defaults(fn=cmd_worlds)
    nw = sub.add_parser("newworld", help="create a world: a territory for discovery")
    nw.add_argument("name", help="world name (used with -w)")
    nw.add_argument("description", help='territory text, e.g. "Your world is the codebase at /path/..."')
    nw.set_defaults(fn=cmd_newworld)
    ev = sub.add_parser("evolve", help="show methodology evolution state for the world")
    ev.set_defaults(fn=cmd_evolve)
    ex = sub.add_parser("export", help="export the world's threads as training episodes (JSONL)")
    ex.add_argument("-o", "--out", default=None, help="output path (default exports/<world>.jsonl)")
    ex.set_defaults(fn=cmd_export)
    gw = sub.add_parser("genworld", help="generate a contamination-free random world from a seed")
    gw.add_argument("seed", type=int, help="generation seed")
    gw.add_argument("--family", choices=["ca", "modpoly", "tag"], default="ca",
                    help="world family: 1D cellular automaton, polynomial map on Z_m, tag system")
    gw.add_argument("--difficulty", type=int, default=0, help="difficulty tier (0-2+)")
    gw.set_defaults(fn=cmd_genworld)
    cb = sub.add_parser("calib", help="cross-world calibration: confidence vs surprise")
    cb.set_defaults(fn=cmd_calib)
    cv = sub.add_parser("coevolve", help="POET loop: world population at the competence frontier")
    cv.add_argument("--pop", type=int, default=3, help="active world population size")
    cv.add_argument("-n", type=int, default=3, help="threads per world per pass")
    cv.add_argument("--judge-after", type=int, default=6,
                    help="threads before a world can graduate or park")
    cv.set_defaults(fn=cmd_coevolve)
    ro = sub.add_parser("rollout", help="GRPO group sampling: G threads from one frozen context")
    ro.add_argument("--group", "-g", type=int, default=4, help="rollouts per group")
    ro.add_argument("--question", default=None, help="pin a single question for the whole group")
    ro.add_argument("--commit-best", action="store_true",
                    help="commit the best rollout's new claims/tools to the real archive")
    ro.set_defaults(fn=cmd_rollout)
    st = sub.add_parser("stats", help="discovery-efficiency metrics for the world")
    st.set_defaults(fn=cmd_stats)
    dp = sub.add_parser("deps", help="claim -> tool dependency graph for the world")
    dp.set_defaults(fn=cmd_deps)
    gr = sub.add_parser("grind", help="batch rollout: generate worlds and run sessions unattended")
    gr.add_argument("seeds", type=int, nargs="+", help="world seeds to grind")
    gr.add_argument("--family", choices=["ca", "modpoly", "tag"], default="ca")
    gr.add_argument("-n", type=int, default=3, help="threads per world")
    gr.set_defaults(fn=cmd_grind)
    args = p.parse_args()
    if args.world:
        config.set_world(args.world)
    worldless = (cmd_newworld, cmd_worlds, cmd_genworld, cmd_grind, cmd_coevolve, cmd_calib)
    if args.fn not in worldless and config.WORLD != "python" \
            and not (config.WORLD_DIR / "world.md").exists():
        sys.exit(f"world '{config.WORLD}' has no world.md — create it first:\n"
                 f"  python3 disco.py newworld {config.WORLD} \"Your world is ...\"")
    args.fn(args)


if __name__ == "__main__":
    main()
