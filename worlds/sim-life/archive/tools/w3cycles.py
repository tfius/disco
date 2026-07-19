"""Width-3 toroidal Life cycle structure via the reduced row-population automaton.

rule22(bits)          -- one step of elementary CA Rule 22 on a ring (the exact
                         dynamics of all-full/all-empty-row states on 3xH Life).
reduced_cycles(H)     -- all cycles of the reduced automaton on {0..3}^H;
                         returns list of cycles, each a list of pop-tuples.
lift(pops, H)         -- lift a row-pop state to a 3xH Life grid (first p cols live).
cycles_of(f, N)       -- generic cycle finder for an explicit function on range(N).
"""

def rule22(s):
    H = len(s)
    return tuple(
        1 if ((s[i] and not s[i-1] and not s[(i+1) % H]) or
              (not s[i] and s[i-1] + s[(i+1) % H] == 1)) else 0
        for i in range(H))

def _nxt_pop(a, p, b):
    surv = 1 if (a + b + p - 1) in (2, 3) else 0
    born = 1 if (a + b + p) == 3 else 0
    return p * surv + (3 - p) * born

_TBL = {(a, p, b): _nxt_pop(a, p, b)
        for a in range(4) for p in range(4) for b in range(4)}

def cycles_of(f, N):
    """All cycles of f: range(N)->range(N). Returns list of lists of states."""
    status = bytearray(N)
    out = []
    for s in range(N):
        if status[s]:
            continue
        path, pos = [], {}
        x = s
        while status[x] == 0 and x not in pos:
            pos[x] = len(path); path.append(x); x = f[x]
        if status[x] == 0:
            k = pos[x]
            out.append(path[k:])
            for y in path[k:]: status[y] = 1
            for y in path[:k]: status[y] = 2
        else:
            for y in path: status[y] = 2
    return out

def reduced_cycles(H):
    """Cycles of the width-3 reduced automaton; each cycle is a list of
    H-tuples of row populations (0..3)."""
    N = 4 ** H
    pw = [4 ** i for i in range(H)]
    f = [0] * N
    for s in range(N):
        d = [(s // pw[i]) % 4 for i in range(H)]
        f[s] = sum(_TBL[(d[(i-1) % H], d[i], d[(i+1) % H])] * pw[i]
                   for i in range(H))
    out = []
    for cyc in cycles_of(f, N):
        out.append([tuple((s // pw[i]) % 4 for i in range(H)) for s in cyc])
    return out

def lift(pops, H):
    """Row-pop state -> 3xH Life grid with the first p cells of each row live."""
    import life
    return life.from_set({(x, r) for r, p in enumerate(pops)
                          for x in range(p)}, H)
