import sys
from collections import Counter, defaultdict

W, H = 4, 5
N = 1 << (W * H)

def newrow(a, r, b):
    out = 0
    for j in range(W):
        jm, jp = (j - 1) % W, (j + 1) % W
        n = ((a >> jm) & 1) + ((a >> j) & 1) + ((a >> jp) & 1) \
          + ((r >> jm) & 1) + ((r >> jp) & 1) \
          + ((b >> jm) & 1) + ((b >> j) & 1) + ((b >> jp) & 1)
        c = (r >> j) & 1
        if n == 3 or (c and n == 2):
            out |= 1 << j
    return out

T = [0] * 4096
for a in range(16):
    for r in range(16):
        base = (a << 8) | (r << 4)
        for b in range(16):
            T[base | b] = newrow(a, r, b)

f = [0] * N
for s in range(N):
    r0 = s & 15; r1 = (s >> 4) & 15; r2 = (s >> 8) & 15
    r3 = (s >> 12) & 15; r4 = (s >> 16) & 15
    f[s] = (T[(r4 << 8) | (r0 << 4) | r1]
            | (T[(r0 << 8) | (r1 << 4) | r2] << 4)
            | (T[(r1 << 8) | (r2 << 4) | r3] << 8)
            | (T[(r2 << 8) | (r3 << 4) | r4] << 12)
            | (T[(r3 << 8) | (r4 << 4) | r0] << 16))

# image / GoE
img = len(set(f))
assert img == 279165, img
assert N - img == 769411
assert abs(100.0 * (N - img) / N - 73.3768) < 0.0001

# functional graph decomposition
state = bytearray(N)
dist = [0] * N
cycles = []
for s in range(N):
    if state[s]:
        continue
    path = []; v = s
    while state[v] == 0:
        state[v] = 1; path.append(v); v = f[v]
    if state[v] == 1:
        idx = path.index(v)
        cyc = path[idx:]
        cycles.append(cyc)
        for u in cyc:
            state[u] = 2; dist[u] = 0
        base = idx
    else:
        base = len(path)
    d = dist[v]
    for i in range(base - 1, -1, -1):
        d += 1; state[path[i]] = 2; dist[path[i]] = d

spec = Counter(len(c) for c in cycles)
assert dict(spec) == {1: 313, 2: 32, 4: 20, 5: 8, 6: 60, 8: 20, 10: 8}, spec
assert len(cycles) == 461
assert sum(len(c) for c in cycles) == 1097
maxd = max(dist)
assert maxd == 21, maxd
assert sum(1 for d in dist if d == maxd) == 80

# traveler signatures
def shift(s, dx, dy):
    rows = [(s >> (4 * r)) & 15 for r in range(H)]
    out = 0
    for r in range(H):
        row = rows[(r - dy) % H]
        row = ((row << dx) | (row >> (W - dx))) & 15 if dx else row
        out |= row << (4 * r)
    return out

SHIFTS = [(dx, dy) for dx in range(W) for dy in range(H) if (dx, dy) != (0, 0)]

def signature(cyc):
    s = cyc[0]; p = len(cyc); v = s
    for t in range(1, p + 1):
        v = f[v]
        if v == s:
            return (t, 0, 0)
        for dx, dy in SHIFTS:
            if shift(s, dx, dy) == v:
                return (t, dx, dy)

sig = Counter((len(c),) + signature(c) for c in cycles)
expected_sig = {
    (1, 1, 0, 0): 313, (2, 1, 2, 0): 12, (2, 2, 0, 0): 20,
    (4, 4, 0, 0): 20, (5, 1, 0, 1): 4, (5, 1, 0, 4): 4,
    (6, 6, 0, 0): 60, (8, 8, 0, 0): 20,
    (10, 1, 2, 1): 2, (10, 1, 2, 4): 2, (10, 2, 0, 2): 2, (10, 2, 0, 3): 2,
}
assert dict(sig) == expected_sig, sig

# symmetry classes under 80-op group
def transform(s, dx, dy, fx, fy):
    out = 0
    for r in range(H):
        row = (s >> (4 * r)) & 15
        if not row:
            continue
        for c in range(W):
            if (row >> c) & 1:
                rr = (H - 1 - r) if fy else r
                cc = (W - 1 - c) if fx else c
                out |= 1 << (4 * ((rr + dy) % H) + ((cc + dx) % W))
    return out

OPS = [(dx, dy, fx, fy) for fx in (0, 1) for fy in (0, 1)
       for dx in range(W) for dy in range(H)]
assert len(OPS) == 80

def cyc_key(cyc):
    return min(min(transform(s, *op) for s in cyc) for op in OPS)

classes = defaultdict(list)
for i, cyc in enumerate(cycles):
    classes[(len(cyc), cyc_key(cyc))].append(i)

nclasses = Counter(p for (p, k) in classes)
assert dict(nclasses) == {1: 13, 2: 3, 4: 1, 5: 1, 6: 2, 8: 1, 10: 2}, nclasses
for (p, k), idxs in classes.items():
    assert 80 % len(idxs) == 0, (p, len(idxs))
p1sizes = Counter(len(idxs) for (p, k), idxs in classes.items() if p == 1)
assert dict(p1sizes) == {1: 1, 2: 1, 10: 1, 20: 7, 40: 2, 80: 1}, p1sizes

print("all checks passed")
sys.exit(0)
