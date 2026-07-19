"""Exhaustive functional-graph machinery for width-4 toroidal Life grids (4xH).

build_f(H)            -> full successor list f of length 2^(4H), via 4096-entry row-triple table
all_cycles(f)         -> list of cycles (each a list of states, in orbit order)
decompose(f)          -> (cycles, dist) where dist[s] = transient length to cycle
shift(s, dx, dy, H)   -> translate packed state by (dx cols, dy rows)
signature(cyc, f, H)  -> (t_min, dx, dy): minimal t>=1 with f^t(s)=shift(s,dx,dy); (p,0,0) for oscillators
transform(s, dx, dy, fx, fy, H) -> apply translation + optional h/v flip
sym_classes(cycles, H)-> dict (period, canonical_key) -> list of cycle indices, under 80|group| = 20*4 ops
States are packed 4 bits per row, row r at bits 4r..4r+3, column c = bit c.
"""

W = 4
_TCACHE = {}

def _newrow(a, r, b):
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

def _table():
    if 'T' not in _TCACHE:
        T = [0] * 4096
        for a in range(16):
            for r in range(16):
                base = (a << 8) | (r << 4)
                for b in range(16):
                    T[base | b] = _newrow(a, r, b)
        _TCACHE['T'] = T
    return _TCACHE['T']

def build_f(H):
    T = _table()
    N = 1 << (4 * H)
    f = [0] * N
    for s in range(N):
        rows = [(s >> (4 * r)) & 15 for r in range(H)]
        out = 0
        for r in range(H):
            out |= T[(rows[(r - 1) % H] << 8) | (rows[r] << 4) | rows[(r + 1) % H]] << (4 * r)
        f[s] = out
    return f

def decompose(f):
    N = len(f)
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
    return cycles, dist

def all_cycles(f):
    return decompose(f)[0]

def shift(s, dx, dy, H):
    rows = [(s >> (4 * r)) & 15 for r in range(H)]
    out = 0
    for r in range(H):
        row = rows[(r - dy) % H]
        row = ((row << dx) | (row >> (W - dx))) & 15 if dx else row
        out |= row << (4 * r)
    return out

def signature(cyc, f, H):
    """Scan shifts dx-major (dx 0..3 outer, dy 0..H-1 inner), excluding identity."""
    shifts = [(dx, dy) for dx in range(W) for dy in range(H) if (dx, dy) != (0, 0)]
    s = cyc[0]; p = len(cyc); v = s
    for t in range(1, p + 1):
        v = f[v]
        if v == s:
            return (t, 0, 0)
        for dx, dy in shifts:
            if shift(s, dx, dy, H) == v:
                return (t, dx, dy)

def transform(s, dx, dy, fx, fy, H):
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

def sym_classes(cycles, H):
    from collections import defaultdict
    ops = [(dx, dy, fx, fy) for fx in (0, 1) for fy in (0, 1)
           for dx in range(W) for dy in range(H)]
    classes = defaultdict(list)
    for i, cyc in enumerate(cycles):
        key = min(min(transform(s, *op, H) for s in cyc) for op in ops)
        classes[(len(cyc), key)].append(i)
    return dict(classes)
