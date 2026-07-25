"""Ash (attractor) decomposition pipeline for toroidal Life soups.
Fixes the gotcha: cyc.find_cycle(g,W,H) returns (start_offset, period) as plain
ints, NOT a grid state — you must re-simulate from the soup to reach the
cycle-start grid before calling decomp.cycle_states.

soup_ash(seed, W, H, p=0.5, cap=6000) -> dict with keys:
  period, start, states (list of live-cell sets over one cycle),
  frozen (set, intersection over cycle = still-life part),
  mobile (set, union-minus-frozen = oscillating/moving part),
  avg_live (float, mean population per cycle frame)
"""
from fixpath import load
cyc = load("cyc")
decomp = load("decomp")
life = load("life")


def soup_ash(seed, W, H, p=0.5, cap=6000):
    g0 = life.soup(seed, W, H, p)
    start, period = cyc.find_cycle(g0, W, H, cap=cap)
    g = g0
    for _ in range(start):
        g = life.step(g, W, H)
    states = decomp.cycle_states(g, period, W, H)
    frozen, everseen = decomp.frozen_mobile(states)
    mobile = everseen - frozen
    avg_live = sum(len(s) for s in states) / len(states)
    return {
        "period": period,
        "start": start,
        "states": states,
        "frozen": frozen,
        "mobile": mobile,
        "avg_live": avg_live,
        "frac_frozen": (len(frozen) / avg_live) if avg_live > 0 else float("nan"),
    }
