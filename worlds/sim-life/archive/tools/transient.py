"""Transient-depth analysis for exhaustive toroidal Life functional graphs.

depths(f)            -> (dist, oncycle, order): exact distance-to-cycle per state
                        via indegree peel + reverse BFS; order is BFS visit order
                        (nondecreasing dist), usable for basin propagation.
dies_mask(f, dist, order) -> bytearray, 1 iff state's attractor is the empty
                        fixed point {0}.
period_of(f, s, steps) -> (period, landing_state) after advancing s by steps.
grid_gens(W, H)      -> dict of bit-permutation generators (translations, flips,
                        rot90 iff W == H) for state encoding bit = r*W + c.
apply_perm(s, m)     -> apply bit permutation m to state integer s.
"""
from collections import deque


def depths(f):
    N = len(f)
    indeg = [0] * N
    for s in range(N):
        indeg[f[s]] += 1
    stack = [s for s in range(N) if indeg[s] == 0]
    removed = bytearray(N)
    while stack:
        s = stack.pop()
        removed[s] = 1
        t = f[s]
        indeg[t] -= 1
        if indeg[t] == 0:
            stack.append(t)
    head = [-1] * N
    nxt = [-1] * N
    for s in range(N):
        t = f[s]
        nxt[s] = head[t]
        head[t] = s
    dist = [-1] * N
    order = []
    dq = deque()
    for s in range(N):
        if not removed[s]:
            dist[s] = 0
            dq.append(s)
    while dq:
        u = dq.popleft()
        order.append(u)
        p = head[u]
        while p != -1:
            if dist[p] == -1:
                dist[p] = dist[u] + 1
                dq.append(p)
            p = nxt[p]
    oncycle = bytearray(0 if removed[s] else 1 for s in range(N))
    return dist, oncycle, order


def dies_mask(f, dist, order):
    N = len(f)
    dies = bytearray(N)
    for u in order:
        if dist[u] == 0:
            dies[u] = 1 if u == 0 else 0
        else:
            dies[u] = dies[f[u]]
    return dies


def period_of(f, s, steps):
    for _ in range(steps):
        s = f[s]
    per = 1
    t = f[s]
    while t != s:
        t = f[t]
        per += 1
    return per, s


def grid_gens(W, H):
    n = W * H

    def pm(fn):
        m = [0] * n
        for r in range(H):
            for c in range(W):
                r2, c2 = fn(r, c)
                m[r * W + c] = r2 * W + c2
        return m

    gens = {
        "tx": pm(lambda r, c: (r, (c + 1) % W)),
        "ty": pm(lambda r, c: ((r + 1) % H, c)),
        "hf": pm(lambda r, c: (r, W - 1 - c)),
        "vf": pm(lambda r, c: (H - 1 - r, c)),
    }
    if W == H:
        gens["rot90"] = pm(lambda r, c: (c, W - 1 - r))
    return gens


def apply_perm(s, m):
    out = 0
    b = 0
    while s:
        if s & 1:
            out |= 1 << m[b]
        s >>= 1
        b += 1
    return out
