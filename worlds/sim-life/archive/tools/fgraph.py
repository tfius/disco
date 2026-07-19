"""Functional-graph analysis for exhaustive small-torus Life state spaces.

build_map(W, H)      -> list f where f[s] = successor state (bitmask, bit i = cell (i%W, i//W))
attractors(f)        -> (cycles, depth): cycles = list of state-lists (each one attractor cycle,
                        in step order); depth[s] = transient distance from s to its cycle (0 if on-cycle)
sym_group(W, H)      -> dict perm -> list of (d4_name, dx, dy) labels; full translationxD4 group
                        (rotations/diagonal flips only valid when W == H)
translations(W, H)   -> dict perm -> (dx, dy), pure translations only
apply_perm(p, s, N)  -> image of state s under cell permutation p
Feasible up to ~2^20 states (e.g. 4x5). Requires the `life` tool.
"""
from life import step, from_set, to_set

D4_NAMES = ['id', 'rot90', 'rot180', 'rot270', 'flipx', 'flipy', 'diag', 'antidiag']

def _perm_from(fn, W, H):
    p = [0] * (W * H)
    for y in range(H):
        for x in range(W):
            nx, ny = fn(x, y)
            p[x + W * y] = (nx % W) + W * (ny % H)
    return tuple(p)

def build_map(W, H):
    N = W * H
    f = [0] * (1 << N)
    for s in range(1 << N):
        live = {(i % W, i // W) for i in range(N) if (s >> i) & 1}
        g2 = step(from_set(live, H), W, H)
        s2 = 0
        for (x, y) in to_set(g2, W, H):
            s2 |= 1 << (x + W * y)
        f[s] = s2
    return f

def attractors(f):
    n = len(f)
    state = [0] * n
    on_cycle = [False] * n
    for s0 in range(n):
        if state[s0]:
            continue
        path, s = [], s0
        while state[s] == 0:
            state[s] = 1
            path.append(s)
            s = f[s]
        if state[s] == 1:
            for c in path[path.index(s):]:
                on_cycle[c] = True
        for p in path:
            state[p] = 2
    seen = [False] * n
    cycles = []
    for s in range(n):
        if on_cycle[s] and not seen[s]:
            cyc, t = [], s
            while not seen[t]:
                seen[t] = True
                cyc.append(t)
                t = f[t]
            cycles.append(cyc)
    depth = [0 if on_cycle[s] else None for s in range(n)]
    for s0 in range(n):
        if depth[s0] is not None:
            continue
        stack, s = [], s0
        while depth[s] is None:
            stack.append(s)
            s = f[s]
        d = depth[s]
        while stack:
            d += 1
            depth[stack.pop()] = d
    return cycles, depth

def sym_group(W, H):
    d4 = [
        lambda x, y: (x, y),                 lambda x, y: (y, W - 1 - x),
        lambda x, y: (W - 1 - x, H - 1 - y), lambda x, y: (H - 1 - y, x),
        lambda x, y: (W - 1 - x, y),         lambda x, y: (x, H - 1 - y),
        lambda x, y: (y, x),                 lambda x, y: (W - 1 - y, H - 1 - x),
    ]
    if W != H:
        d4 = [d4[0], d4[2], d4[4], d4[5]]   # drop rotations/diagonals on non-square
    names = [D4_NAMES[i] for i in (range(8) if W == H else (0, 2, 4, 5))]
    elems = {}
    for name, g in zip(names, d4):
        for dx in range(W):
            for dy in range(H):
                p = _perm_from(lambda x, y, g=g, dx=dx, dy=dy:
                               (g(x, y)[0] + dx, g(x, y)[1] + dy), W, H)
                elems.setdefault(p, []).append((name, dx, dy))
    return elems

def translations(W, H):
    out = {}
    for dx in range(W):
        for dy in range(H):
            out[_perm_from(lambda x, y, dx=dx, dy=dy: (x + dx, y + dy), W, H)] = (dx, dy)
    return out

def apply_perm(p, s, N):
    s2 = 0
    for i in range(N):
        if (s >> i) & 1:
            s2 |= 1 << p[i]
    return s2
