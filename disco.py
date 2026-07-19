#!/usr/bin/env python3
"""disco — a minimal discovery harness. Predict, run, be surprised, compress, archive."""
import argparse
import json
import sys

from kernel import archive, audit, config, ledger, loop


def cmd_run(args):
    for i in range(args.n):
        print(f"thread {i + 1}/{args.n}")
        try:
            outcome = loop.run_thread()
        except RuntimeError as e:
            print(f"  aborted (endpoint?): {e}", file=sys.stderr)
            break
        print(f"  ended: {outcome['ending']} after {outcome['steps']} step(s)")


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
    rs = sub.add_parser("reset", help="fresh start: move archive/runs/ledger to attic/<ts>/")
    rs.set_defaults(fn=cmd_reset)
    sd = sub.add_parser("seed", help="park a human question in archive/open-questions/")
    sd.add_argument("title", help="one-line territory to explore")
    sd.add_argument("body", nargs="?", default="", help="optional context/details")
    sd.set_defaults(fn=cmd_seed)
    wl = sub.add_parser("worlds", help="list worlds and their claim counts")
    wl.set_defaults(fn=cmd_worlds)
    nw = sub.add_parser("newworld", help="create a world: a territory for discovery")
    nw.add_argument("name", help="world name (used with -w)")
    nw.add_argument("description", help='territory text, e.g. "Your world is the codebase at /path/..."')
    nw.set_defaults(fn=cmd_newworld)
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
