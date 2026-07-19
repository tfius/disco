"""Exact cycle detection for toroidal Life — full-state hashing, no cap-4096 pitfall.

find_cycle(g, W, H, cap=6000) -> (transient, period) or (None, None) if no cycle within cap.
soup_cycle(seed, W, H, p=0.5, cap=6000) -> (transient, period) for a random soup.
spectrum(seeds, W, H, p=0.5, cap=6000) -> (Counter{period: count}, [transients], [failed seeds])

Note: attract.find_attractor's default cap (4096) is too small for 32x32 soups —
transient + period regularly exceeds it. Use this module for exact results.
"""
import life
from collections import Counter


def find_cycle(g, W, H, cap=6000):
    if isinstance(g, list):
        g = tuple(g)
    seen = {g: 0}
    for t in range(1, cap + 1):
        g = life.step(g, W, H)
        if isinstance(g, list):
            g = tuple(g)
        if g in seen:
            return seen[g], t - seen[g]
        seen[g] = t
    return None, None


def soup_cycle(seed, W, H, p=0.5, cap=6000):
    return find_cycle(life.soup(seed, W, H, p), W, H, cap)


def spectrum(seeds, W, H, p=0.5, cap=6000):
    periods = Counter()
    transients = []
    fails = []
    for s in seeds:
        tr, per = soup_cycle(s, W, H, p, cap)
        if per is None:
            fails.append(s)
        else:
            periods[per] += 1
            transients.append(tr)
    return periods, transients, fails
