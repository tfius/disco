"""Attractor analysis for toroidal Life soups.

find_attractor(seed, W, H, p=0.5, cap=4096) -> (grid, period, transient) — runs a
    soup to its first recurrence; (None, None, None) if no recurrence within cap.
translations(c0, W, H) -> dict mapping each torus-translate of cell-set c0 to its (dx, dy).
drift(g0, period, W, H) -> (t, (dx, dy)) — minimal t>0 with state_t a pure translation
    of state_0; t == period with shift (0,0) means a non-drifting oscillator,
    t < period with nonzero shift means a drifting (spaceship-type) attractor.
shift_order(dx, dy, W, H) -> order of the shift in the translation group Z_W x Z_H.
"""
import fixpath
life = fixpath.load('life')


def find_attractor(seed, W, H, p=0.5, cap=4096):
    g = life.soup(seed, W, H, p)
    seen = {tuple(g): 0}
    t = 0
    while t < cap:
        g = life.step(g, W, H)
        t += 1
        k = tuple(g)
        if k in seen:
            return g, t - seen[k], seen[k]
        seen[k] = t
    return None, None, None


def translations(c0, W, H):
    return {frozenset(((x + dx) % W, (y + dy) % H) for x, y in c0): (dx, dy)
            for dx in range(W) for dy in range(H)}


def drift(g0, period, W, H):
    c0 = frozenset(life.to_set(g0, W, H))
    tr = translations(c0, W, H)
    g = g0
    for t in range(1, period + 1):
        g = life.step(g, W, H)
        c = frozenset(life.to_set(g, W, H))
        if c in tr:
            return t, tr[c]
    return None, None


def shift_order(dx, dy, W, H):
    o, ax, ay = 1, dx % W, dy % H
    while (ax, ay) != (0, 0):
        ax = (ax + dx) % W
        ay = (ay + dy) % H
        o += 1
    return o
