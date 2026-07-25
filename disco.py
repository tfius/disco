#!/usr/bin/env python3
"""disco — a minimal discovery harness. Predict, run, be surprised, compress, archive."""
import argparse
import json
import os
import sys

from kernel import archive, audit, config, evolve, export, ledger, loop


def cmd_run(args):
    if config.CLAIMS.exists() and any(config.CLAIMS.iterdir()):
        print("pre-run verify (selection):")
        archive.verify_all()
    evolving = os.environ.get("DISCO_EVOLVE", "1") != "0"
    for i in range(args.n):
        print(f"thread {i + 1}/{args.n}")
        try:
            variant, methodology = evolve.current() if evolving else ("champion", None)
            if evolving:
                print(f"  methodology variant: {variant} (gen {evolve._state()['generation']})")
            outcome = loop.run_thread(methodology=methodology)
        except RuntimeError as e:
            print(f"  aborted (endpoint?): {e}", file=sys.stderr)
            break
        print(f"  ended: {outcome['ending']} after {outcome['steps']} step(s)")
        if evolving:
            evolve.note(outcome, variant)


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
    hist = config.WORLD_DIR / "methodology-history"
    print(f"world: {config.WORLD} — generation {s['generation']}, "
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


def _gen_ca(rng, seed):
    k, r = rng.choice([(2, 2), (3, 1)])  # never (2,1): elementary CAs are documented
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


def _gen_modpoly(rng, seed):
    m = rng.randrange(53, 251)
    coeffs = [rng.randrange(m) for _ in range(4)]  # a0 + a1 x + a2 x^2 + a3 x^3
    return (f"x -> ({coeffs[3]}x^3+{coeffs[2]}x^2+{coeffs[1]}x+{coeffs[0]}) mod {m}",
            f"Your world is the dynamical system f(x) = ({coeffs[3]}*x**3 + "
            f"{coeffs[2]}*x**2 + {coeffs[1]}*x + {coeffs[0]}) % {m} iterated on "
            f"Z_{m} = {{0..{m - 1}}}. Discover its functional graph exactly: fixed "
            f"points, cycle spectrum, tail lengths, preimage structure (which points "
            f"have none, the in-degree distribution), how orbits of all {m} starting "
            f"points partition, and any algebraic structure that explains what you "
            f"find. The full graph is exhaustively computable — exact claims only. ")


def _gen_tag(rng, seed):
    d = rng.choice([2, 3])
    prods = {s: "".join(rng.choice("ab") for _ in range(rng.randrange(0, 5)))
             for s in "ab"}
    return (f"tag system d={d}, a->{prods['a'] or 'ε'}, b->{prods['b'] or 'ε'}",
            f"Your world is a tag system on the alphabet {{a, b}}: at each step, if "
            f"the word has fewer than {d} symbols the system halts; otherwise read "
            f"the first symbol, delete the first {d} symbols, and append 'a' -> "
            f"'{prods['a']}' or 'b' -> '{prods['b']}' (empty string allowed). "
            f"Discover: which initial words halt, grow forever, or cycle; growth "
            f"rates; periodic structures; decidable non-halting patterns. Bound every "
            f"simulation with explicit step budgets, and phrase non-halting claims "
            f"only via decidable certificates. ")


def cmd_genworld(args):
    """Procedurally generated world — rules rolled from a seed, so their truths
    cannot exist in any pretraining corpus. The contamination-free territories."""
    import random as _random
    rng = _random.Random(f"{args.family}-{args.seed}")
    summary, body = {"ca": _gen_ca, "modpoly": _gen_modpoly, "tag": _gen_tag}[args.family](rng, args.seed)
    name = f"gen-{args.seed}" if args.family == "ca" else f"gen-{args.family}-{args.seed}"
    config.set_world(name)
    if (config.WORLD_DIR / "world.md").exists():
        sys.exit(f"world '{name}' already exists — run it: python3 disco.py -w {name} run")
    config.ensure_dirs()
    (config.WORLD_DIR / "world.md").write_text(body + GEN_CLOSING.format(seed=args.seed))
    print(f"world '{name}' created — {summary}")
    print(f"run: python3 disco.py -w {name} run -n 3")


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
    for path in (config.ARCHIVE, config.RUNS, config.LEDGER):
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
    gw.set_defaults(fn=cmd_genworld)
    st = sub.add_parser("stats", help="discovery-efficiency metrics for the world")
    st.set_defaults(fn=cmd_stats)
    args = p.parse_args()
    if args.world:
        config.set_world(args.world)
    if args.fn not in (cmd_newworld, cmd_worlds) and config.WORLD != "python" \
            and not (config.WORLD_DIR / "world.md").exists():
        sys.exit(f"world '{config.WORLD}' has no world.md — create it first:\n"
                 f"  python3 disco.py newworld {config.WORLD} \"Your world is ...\"")
    args.fn(args)


if __name__ == "__main__":
    main()
