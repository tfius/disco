"""Drift/spaceship census for exhaustive toroidal Life functional graphs.

translate(s, dr, dc, W, H) — translate bit-encoded state (bit = r*W+c).
find_cycles(f)             — all cycles of functional graph f (list of int).
drift_census(f, W, H)      — per drifting cycle: (period, first_k, shift_coset,
                             stabilizer, pop, rep, spans_rows, spans_cols).
A cycle is 'drifting' if some iterate of its representative is a nontrivial
translate. Shifts are only defined modulo the pattern's translation stabilizer,
so the full coset is returned. 'Localized' drifters (empty row AND empty
column) are true traveling objects, e.g. the speed-c pop-8 wave on 4x5.
"""

def translate(s, dr, dc, W, H):
    t = 0
    for r in range(H):
        nb = ((r + dr) % H) * W
        base = r * W
        for c in range(W):
            if (s >> (base + c)) & 1:
                t |= 1 << (nb + ((c + dc) % W))
    return t

def find_cycles(f):
    N = len(f)
    color = bytearray(N)
    cycles = []
    for s0 in range(N):
        if color[s0]:
            continue
        path = []
        s = s0
        while color[s] == 0:
            color[s] = 1
            path.append(s)
            s = f[s]
        if color[s] == 1:
            i = path.index(s)
            cycles.append(path[i:])
        for t in path:
            color[t] = 2
    return cycles

def drift_census(f, W, H):
    out = []
    for cyc in find_cycles(f):
        p = len(cyc)
        if p == 1:
            continue
        rep = min(cyc)
        stab = []
        trans = {}
        for dr in range(H):
            for dc in range(W):
                if (dr, dc) == (0, 0):
                    continue
                t = translate(rep, dr, dc, W, H)
                if t == rep:
                    stab.append((dr, dc))
                trans.setdefault(t, []).append((dr, dc))
        s = rep
        for k in range(1, p):
            s = f[s]
            if s in trans:
                rows = {r for r in range(H) for c in range(W)
                        if (rep >> (r*W+c)) & 1}
                cols = {c for r in range(H) for c in range(W)
                        if (rep >> (r*W+c)) & 1}
                out.append((p, k, tuple(sorted(trans[s])),
                            tuple(sorted(stab)), bin(rep).count("1"), rep,
                            len(rows) == H, len(cols) == W))
                break
    return out
