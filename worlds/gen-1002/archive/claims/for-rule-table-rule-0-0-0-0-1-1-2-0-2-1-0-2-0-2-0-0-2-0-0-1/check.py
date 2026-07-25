RULE = [0, 0, 0, 0, 1, 1, 2, 0, 2, 1, 0, 2, 0, 2, 0, 0, 2, 0, 0, 1, 2, 0, 2, 1, 0, 0, 1]

def step(tape, rule=RULE):
    n = len(tape)
    out = [0]*n
    for i in range(n):
        l = tape[(i-1) % n]
        c = tape[i]
        r = tape[(i+1) % n]
        idx = l*9 + c*3 + r
        out[i] = rule[idx]
    return out

def nz(tape):
    return [(i,v) for i,v in enumerate(tape) if v != 0]

# (1) all-0 fixed point
for N in (10, 41):
    t = [0]*N
    for _ in range(20):
        t = step(t)
        assert t == [0]*N, "all-0 tape not fixed"

# (2) single-1 glider moves right at speed 1, shape preserved, until near wraparound
N = 41
start = 5
t = [0]*N
t[start] = 1
for k in range(1, 30):
    t = step(t)
    expected_pos = (start + k) % N
    assert nz(t) == [(expected_pos, 1)], f"glider mismatch at step {k}: {nz(t)}"

# (3) single-2 defect is static fixed point
N = 41
t = [0]*N
t[20] = 2
for k in range(30):
    t = step(t)
    assert nz(t) == [(20, 2)], f"2-defect not static at step {k}: {nz(t)}"

# (4) glider annihilation at obstacle, general over gaps and widths
for N in (41, 61, 81):
    for glider_pos, obstacle_pos in [(5, 8), (5, 12), (5, 20), (10, 25), (0, 3)]:
        gap = (obstacle_pos - glider_pos) % N
        if gap < 3:
            continue
        t = [0]*N
        t[glider_pos] = 1
        t[obstacle_pos] = 2
        settled = False
        final_expected = (obstacle_pos - 1) % N
        for k in range(N + 5):
            t = step(t)
            cur = nz(t)
            if cur == [(final_expected, 2)]:
                settled = True
                # confirm it stays stable for extra steps
                for _ in range(10):
                    t = step(t)
                    assert nz(t) == [(final_expected, 2)], "not stable after settling"
                break
        assert settled, f"never settled: N={N} glider={glider_pos} obstacle={obstacle_pos} final={nz(t)}"

print("ALL CHECKS PASSED")
