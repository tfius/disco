"""Attractor decomposition for toroidal Life: frozen/mobile split, 8-connected
clusters, translation detection, and glider-shape recognition (both phases).

cycle_states(g0, period, W, H) -> list of cell-sets over one full cycle
frozen_mobile(states)          -> (frozen, everlive) cell-sets
clusters(cells, W, H)          -> list of 8-connected components (torus wrap)
translation_of(c0, c1, W, H)   -> (dx,dy) with c0+(dx,dy)==c1 mod (W,H), or None
is_glider(cells)               -> True iff cells match either glider phase up to
                                  the 8 square symmetries (translation-normalized)
"""
import life

def cycle_states(g0, period, W, H):
    states = []
    g = g0
    for _ in range(period):
        states.append(life.to_set(g, W, H))
        g = life.step(g, W, H)
    return states

def frozen_mobile(states):
    return set.intersection(*states), set.union(*states)

def clusters(cells, W, H):
    cells = set(cells); out = []
    while cells:
        start = cells.pop(); stack = [start]; comp = {start}
        while stack:
            x, y = stack.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    p = ((x+dx) % W, (y+dy) % H)
                    if p in cells:
                        cells.remove(p); comp.add(p); stack.append(p)
        out.append(comp)
    return out

def translation_of(c0, c1, W, H):
    if len(c0) != len(c1):
        return None
    ax, ay = min(c0)
    for bx, by in c1:
        dx, dy = (bx-ax) % W, (by-ay) % H
        if {((x+dx) % W, (y+dy) % H) for x, y in c0} == c1:
            return (dx, dy)
    return None

def _sym_variants(cells):
    out = set()
    for fx in (1, -1):
        for fy in (1, -1):
            for sw in (0, 1):
                v = {(x*fx, y*fy) for x, y in cells}
                if sw:
                    v = {(y, x) for x, y in v}
                mx = min(x for x, y in v); my = min(y for x, y in v)
                out.add(frozenset((x-mx, y-my) for x, y in v))
    return out

def _glider_forms():
    G0 = {(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)}
    BB = 16
    g = life.from_set({(x+5, y+5) for x, y in G0}, BB)
    g = life.step(g, BB, BB)
    G1 = life.to_set(g, BB, BB)
    return _sym_variants(G0) | _sym_variants(G1)

GLIDER_FORMS = _glider_forms()

def is_glider(cells):
    if len(cells) != 5:
        return False
    mx = min(x for x, y in cells); my = min(y for x, y in cells)
    return frozenset((x-mx, y-my) for x, y in cells) in GLIDER_FORMS
