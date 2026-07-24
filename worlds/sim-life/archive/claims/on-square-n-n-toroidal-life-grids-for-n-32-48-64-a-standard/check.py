import sys

def step(rows, W, H):
    new = [0]*H
    for r in range(H):
        above = rows[(r-1) % H]
        cur = rows[r]
        below = rows[(r+1) % H]
        newrow = 0
        for c in range(W):
            cm1 = (c-1) % W
            cp1 = (c+1) % W
            cnt = (
                ((above >> cm1) & 1) + ((above >> c) & 1) + ((above >> cp1) & 1) +
                ((cur   >> cm1) & 1) +                       ((cur   >> cp1) & 1) +
                ((below >> cm1) & 1) + ((below >> c) & 1) + ((below >> cp1) & 1)
            )
            alive = (cur >> c) & 1
            if alive and cnt in (2, 3):
                newrow |= (1 << c)
            elif (not alive) and cnt == 3:
                newrow |= (1 << c)
        new[r] = newrow
    return tuple(new)

def pop(rows):
    return sum(bin(r).count("1") for r in rows)

def place(cells, W, H, base_rows=None):
    rows = list(base_rows) if base_rows else [0]*H
    for (r, c) in cells:
        rows[r % H] |= (1 << (c % W))
    return rows

STEPS = 400
glider_A = [(0,1),(1,2),(2,0),(2,1),(2,2)]
glider_B = [(0,1),(1,0),(2,0),(2,1),(2,2)]

def run(N, d):
    g = tuple(place(
        [(r,c+d) for (r,c) in glider_B],
        N, N,
        place(glider_A, N, N, [0]*N)
    ))
    states = [g]
    for t in range(STEPS):
        g = step(g, N, N)
        states.append(g)
    final_pop = pop(states[-1])
    base_t = 360
    period = None
    for p in range(1, 33):
        if states[base_t] == states[base_t + p]:
            period = p
            break
    return final_pop, period

EXPECT_EVEN = (8, 1)
EXPECT_ODD = (18, 2)

ok = True
for N in (32, 48, 64):
    for d in range(4, 14):
        fp, per = run(N, d)
        expect = EXPECT_EVEN if d % 2 == 0 else EXPECT_ODD
        if (fp, per) != expect:
            print(f"MISMATCH N={N} d={d}: got {(fp, per)}, expected {expect}")
            ok = False

if ok:
    print("all N,d combinations match parity-only prediction")
    sys.exit(0)
else:
    sys.exit(1)
