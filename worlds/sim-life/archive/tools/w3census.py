"""Exhaustive cycle census for width-3 toroidal Life (3xH grids).

State encoding: bit = r*3 + c. Cross-checked against life.step.
  build_table()            -> 512-entry row-triple table T[a<<6|r<<3|b] = next middle row
  step_int(s, H, T=None)   -> next int-encoded state
  census(H, T=None)        -> (spectrum dict {period: n_cycles}, list of cycles with period>1)
  translate(s, dx, dy, H)  -> torus-translated state
"""

def build_table():
    T = [0] * 512
    for a in range(8):
        for r in range(8):
            for b in range(8):
                new = 0
                for c in range(3):
                    n = 0
                    for row in (a, r, b):
                        for dc in (-1, 0, 1):
                            n += (row >> ((c + dc) % 3)) & 1
                    self = (r >> c) & 1
                    n -= self
                    if n == 3 or (self and n == 2):
                        new |= 1 << c
                T[a << 6 | r << 3 | b] = new
    return T

_T = build_table()

def step_int(s, H, T=None):
    T = T or _T
    rows = [(s >> (3 * r)) & 7 for r in range(H)]
    out = 0
    for i in range(H):
        out |= T[rows[i - 1] << 6 | rows[i] << 3 | rows[(i + 1) % H]] << (3 * i)
    return out

def translate(s, dx, dy, H):
    out = 0
    for r in range(H):
        row = (s >> (3 * r)) & 7
        nr = ((row << dx) | (row >> (3 - dx))) & 7 if dx else row
        out |= nr << (3 * ((r + dy) % H))
    return out

def census(H, T=None):
    """Exhaustive functional-graph cycle census over all 2^(3H) states."""
    T = T or _T
    N = 1 << (3 * H)
    f = [step_int(s, H, T) for s in range(N)]
    color = bytearray(N)
    spec = {}
    cycles = []
    for s in range(N):
        if color[s]:
            continue
        path, pos, x = [], {}, s
        while color[x] == 0 and x not in pos:
            pos[x] = len(path)
            path.append(x)
            x = f[x]
        if color[x] == 0:
            cyc = tuple(path[pos[x]:])
            spec[len(cyc)] = spec.get(len(cyc), 0) + 1
            if len(cyc) > 1:
                cycles.append(cyc)
        for y in path:
            color[y] = 2
    return spec, cycles
