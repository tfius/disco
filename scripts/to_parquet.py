#!/usr/bin/env python3
"""Flatten disco's exported JSONL episodes into one Parquet file for training.

NOT part of the disco kernel — the kernel is stdlib-only and emits JSONL, the
lossless canonical format. This is an optional boundary tool for trainers who
want columnar/compressed storage. It needs a third-party lib by design, kept
out of the core:

    pip install polars        # (or edit for pandas+pyarrow)
    python3 scripts/to_parquet.py                       # all exports/*.jsonl -> exports/dataset.parquet
    python3 scripts/to_parquet.py exports/all.jsonl out.parquet

Scalar episode fields become columns; nested fields (steps, transcript,
loss_mask, calibration, filters, claim, check) are kept as JSON-encoded string
columns — robust to schema drift and trivially re-parsed with json.loads in the
trainer. This preserves everything `disco export` produces, losslessly.
"""
import glob
import json
import sys
from pathlib import Path

try:
    import polars as pl
except ImportError:
    sys.exit("this optional tool needs polars — `pip install polars` "
             "(the disco kernel itself stays stdlib-only)")

SCALAR = ["world", "agent", "thread", "slug", "ending", "admitted", "reward",
          "mean_surprise", "closure", "group", "rollout"]
NESTED = ["steps", "transcript", "loss_mask", "calibration", "filters", "claim", "check"]


def _rows(paths):
    for p in paths:
        src = Path(p).stem
        for line in Path(p).read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            row = {k: e.get(k) for k in SCALAR}
            for k in NESTED:
                v = e.get(k)
                row[k + "_json"] = json.dumps(v) if v is not None else None
            row["source"] = src
            yield row


def main():
    out = "exports/dataset.parquet"
    inputs = []
    for a in sys.argv[1:]:
        if a.endswith(".parquet"):
            out = a
        else:
            inputs.append(a)
    if not inputs:
        inputs = [p for p in sorted(glob.glob("exports/*.jsonl"))
                  if Path(p).name != "all.jsonl"]  # avoid double-counting the pooled file
    if not inputs:
        sys.exit("no exports/*.jsonl found — run `disco export --all` first")

    data = list(_rows(inputs))
    if not data:
        sys.exit("no episodes in the given files")
    df = pl.DataFrame(data)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out)
    print(f"{len(df)} episodes from {len(inputs)} file(s) -> {out}")
    print(df.group_by("world").len().sort("world"))


if __name__ == "__main__":
    main()
