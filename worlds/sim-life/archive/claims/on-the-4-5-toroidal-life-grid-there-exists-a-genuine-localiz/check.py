import sys
import fixpath
from collections import Counter
import torus4

W = 4

def translate(s, dr, dc, H):
    t = 0
    for r in range(H):
        nb = ((r + dr) % H) * 4
        base = r * 4
        for c in range(4):
            if (s >> (base + c)) & 1:
                t |= 1 << (nb + ((c + dc) % 4))
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

def cells_of(s, H):
    return {(r, c) for r in range(H) for c in range(4) if (s >> (r*4+c)) & 1}

def localized(s, H):
    rows = {r for r in range(H) for c in range(4) if (s >> (r*4+c)) & 1}
    cols = {c for r in range(H) for c in range(4) if (s >> (r*4+c)) & 1}
    return len(rows) < H and len(cols) < 4

def drifting(cyc, f, H):
    rep = min(cyc)
    p = len(cyc)
    trans = {translate(rep, dr, dc, H) for dr in range(H) for dc in range(4)
             if (dr, dc) != (0, 0)}
    s = rep
    for _ in range(1, p):
        s = f[s]
        if s in trans:
            return True
    return False

def naive_step(cells, W, H):
    cnt = Counter()
    for (r, c) in cells:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr or dc:
                    cnt[((r+dr) % H, (c+dc) % W)] += 1
    return {cell for cell, n in cnt.items()
            if n == 3 or (n == 2 and cell in cells)}

# --- 4x5: exactly 8 localized drifting cycles, p=5, pop=8, f = T(+-1,0) ---
H = 5
f = torus4.build_f(H)
loc = []
for cyc in find_cycles(f):
    if len(cyc) > 1 and localized(min(cyc), H) and drifting(cyc, f, H):
        loc.append(cyc)
assert len(loc) == 8, f"expected 8 localized drifting cycles, got {len(loc)}"
assert 7082 in {min(c) for c in loc} or any(7082 in c for c in loc), "rep 7082 missing"
for cyc in loc:
    rep = min(cyc)
    assert len(cyc) == 5, f"period {len(cyc)} != 5"
    assert bin(rep).count("1") == 8, "pop != 8"
    assert f[rep] in (translate(rep, 1, 0, H), translate(rep, 4, 0, H)), \
        f"f(rep) not a (+-1,0) translate for {rep}"
    s = rep
    for _ in range(5):
        s = f[s]
    assert s == rep, "does not return after 5 gens"

# --- the 40 cycle states are one symmetry orbit ---
cycle_states = set()
for cyc in loc:
    cycle_states.update(cyc)
assert len(cycle_states) == 40
base = cells_of(min(loc[0]), H)
orbit = set()
for fr in (False, True):
    for fc in (False, True):
        fl = {((H-1-r) if fr else r, (3-c) if fc else c) for r, c in base}
        for dr in range(H):
            for dc in range(4):
                cells = {((r+dr) % H, (c+dc) % 4) for r, c in fl}
                t = 0
                for r, c in cells:
                    t |= 1 << (r*4+c)
                orbit.add(t)
assert orbit == cycle_states, "cycle states != one symmetry orbit"

# --- wraps essential: same cells on 4x6 and 5x5 are not one-step translates ---
c0 = cells_of(7082, 5)
for (WW, HH) in ((4, 6), (5, 5)):
    c1 = naive_step(c0, WW, HH)
    ok = any(c1 == {((r+dr) % HH, (c+dc) % WW) for r, c in c0}
             for dr in range(HH) for dc in range(WW))
    assert not ok, f"unexpected translate on {WW}x{HH}"

# --- no localized drifting cycles on 4x2, 4x3, 4x4 ---
for HH in (2, 3, 4):
    fh = torus4.build_f(HH)
    for cyc in find_cycles(fh):
        if len(cyc) > 1 and localized(min(cyc), HH) and drifting(cyc, fh, HH):
            print(f"unexpected localized drifter on 4x{HH}")
            sys.exit(1)

print("OK")
sys.exit(0)
