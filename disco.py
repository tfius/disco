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


def cmd_audit(args):
    audit.run(k=args.k)


def cmd_status(args):
    config.ensure_dirs()
    print(archive.index())
    print("\nrecent:")
    print(ledger.tail(20))


def main():
    sys.stdout.reconfigure(line_buffering=True)  # live progress even when piped/backgrounded
    p = argparse.ArgumentParser(prog="disco", description=__doc__)
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
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
