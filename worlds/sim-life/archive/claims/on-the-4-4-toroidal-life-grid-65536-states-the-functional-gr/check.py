import sys
from collections import Counter
from life import step, from_set, to_set

W = H = 4
N = W * H

def build_map():
    f = [0] * (1 << N)
    for s in range(1 << N):
        live = {(i % W, i // W) for i in range(N) if (s >> i) & 1}
        g2 = step(from_set(live, H), W, H)
        s2 = 0
        for (x, y) in to_set(g2, W, H):
            s2 |= 1 << (x + W * y)
        f[s] = s2
    return f

f = build_map()
n = 1 << N
assert n - len(set(f)) == 47657, "GoE count"

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
spec = Counter(len(c) for c in cycles)
assert dict(spec) == {1: 53, 2: 180, 4: 16, 8: 96}, f"spectrum {dict(spec)}"

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
assert max(depth) == 9, f"max transient {max(depth)}"

def perm_from(fn):
    p = [0] * N
    for y in range(H):
        for x in range(W):
            nx, ny = fn(x, y)
            p[x + W * y] = (nx % W) + W * (ny % H)
    return tuple(p)

def apply(p, s):
    s2 = 0
    for i in range(N):
        if (s >> i) & 1:
            s2 |= 1 << p[i]
    return s2

translations = {}   # perm -> (dx, dy)
for dx in range(W):
    for dy in range(H):
        translations[perm_from(lambda x, y, dx=dx, dy=dy: (x + dx, y + dy))] = (dx, dy)
rot180s = set()
for dx in range(W):
    for dy in range(H):
        rot180s.add(perm_from(lambda x, y, dx=dx, dy=dy: (W - 1 - x + dx, H - 1 - y + dy)))

def cheb(d):
    return max(min(abs(d[0]), W - abs(d[0])), min(abs(d[1]), H - abs(d[1])))

for cyc in cycles:
    if len(cyc) == 4:
        vecs = [d for p, d in translations.items() if apply(p, cyc[0]) == cyc[1]]
        assert vecs, "period-4 cycle not a translating wave"
        assert all(cheb(d) == 2 for d in vecs), f"period-4 shift Chebyshev != 2: {vecs}"
    elif len(cyc) == 8:
        assert not any(apply(p, cyc[0]) == cyc[4] for p in translations), \
            "period-8 cycle translation-closed at half-period"
        assert any(apply(p, cyc[0]) == cyc[4] for p in rot180s), \
            "period-8 cycle lacks rot180 half-period twist"

# orbit counts under full 128-element group
D4 = [
    lambda x, y: (x, y),                 lambda x, y: (y, W - 1 - x),
    lambda x, y: (W - 1 - x, H - 1 - y), lambda x, y: (H - 1 - y, x),
    lambda x, y: (W - 1 - x, y),         lambda x, y: (x, H - 1 - y),
    lambda x, y: (y, x),                 lambda x, y: (W - 1 - y, H - 1 - x),
]
group = set()
for g in D4:
    for dx in range(W):
        for dy in range(H):
            group.add(perm_from(lambda x, y, g=g, dx=dx, dy=dy:
                                (g(x, y)[0] + dx, g(x, y)[1] + dy)))
assert len(group) == 128

cyc_id = {s: ci for ci, cyc in enumerate(cycles) for s in cyc}
parent = list(range(len(cycles)))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a
for ci, cyc in enumerate(cycles):
    for p in group:
        parent[find(ci)] = find(cyc_id[apply(p, cyc[0])])
orb = Counter()
sizes = Counter()
for ci, cyc in enumerate(cycles):
    sizes[(len(cyc), find(ci))] += 1
for (plen, root), sz in sizes.items():
    orb[plen] += 1
assert dict(orb) == {1: 6, 2: 8, 4: 1, 8: 2}, f"orbit counts {dict(orb)}"
assert sorted(sz for (plen, r), sz in sizes.items() if plen == 8) == [32, 64]

print("all checks passed")
sys.exit(0)
