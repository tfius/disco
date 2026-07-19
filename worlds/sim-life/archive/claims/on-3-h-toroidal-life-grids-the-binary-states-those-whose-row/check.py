import sys
from collections import Counter
import life

def rule22(s):
    H = len(s)
    return tuple(
        1 if ((s[i] and not s[i-1] and not s[(i+1) % H]) or
              (not s[i] and s[i-1] + s[(i+1) % H] == 1)) else 0
        for i in range(H))

def fail(msg):
    print("FAIL:", msg); sys.exit(1)

# --- 1. Exhaustive: binary states closed + evolve as Rule 22, H=3..10 ---
for H in range(3, 11):
    for m in range(2 ** H):
        bits = tuple((m >> r) & 1 for r in range(H))
        cells = {(x, r) for r in range(H) if bits[r] for x in range(3)}
        g2 = life.step(life.from_set(cells, H), 3, H)
        pred = rule22(bits)
        want = {(x, r) for r in range(H) if pred[r] for x in range(3)}
        if life.to_set(g2, 3, H) != want:
            fail(f"rule22 mismatch H={H} state={bits}")
print("1) binary subsystem == Rule 22 ring, exhaustive H=3..10: OK")

# --- reduced row-population automaton machinery ---
def nxt_pop(a, p, b):
    surv = 1 if (a + b + p - 1) in (2, 3) else 0
    born = 1 if (a + b + p) == 3 else 0
    return p * surv + (3 - p) * born

TBL = {(a, p, b): nxt_pop(a, p, b) for a in range(4) for p in range(4) for b in range(4)}

def cycles_of(f, N):
    status = bytearray(N); out = []
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
    N = 4 ** H
    pw = [4 ** i for i in range(H)]
    f = [0] * N
    for s in range(N):
        d = [(s // pw[i]) % 4 for i in range(H)]
        f[s] = sum(TBL[(d[(i-1) % H], d[i], d[(i+1) % H])] * pw[i] for i in range(H))
    return cycles_of(f, N), pw

def r22_spectrum(H):
    N = 2 ** H
    f = [0] * N
    for s in range(N):
        bits = tuple((s >> i) & 1 for i in range(H))
        f[s] = sum(b << i for i, b in enumerate(rule22(bits)))
    return Counter(len(c) for c in cycles_of(f, N))

# --- 2. spectra match + long periods exist + 3. all cycles lift with equal period ---
EXPECT_LONG = {7: {4, 7}, 8: {4, 6}, 9: {4}, 10: {4, 6}}
for H in range(4, 11):
    cycs, pw = reduced_cycles(H)
    binspec = Counter()
    reps = []
    for cyc in cycs:
        pops_all = [[(s // pw[i]) % 4 for i in range(H)] for s in cyc]
        if all(v in (0, 3) for st in pops_all for v in st):
            binspec[len(cyc)] += 1
        reps.append((len(cyc), pops_all[0]))
    if binspec != r22_spectrum(H):
        fail(f"H={H} binary spectrum != rule22 spectrum: {binspec}")
    periods = {p for p, _ in reps}
    if H in EXPECT_LONG and not EXPECT_LONG[H] <= periods:
        fail(f"H={H} missing long periods: have {periods}, want >= {EXPECT_LONG[H]}")
    for per, pops in reps:
        cells = {(x, r) for r, p in enumerate(pops) for x in range(p)}
        g0 = life.from_set(cells, H)
        g = g0; truep = None
        for t in range(1, 6 * per + 5):
            g = life.step(g, 3, H)
            if g == g0:
                truep = t; break
        if truep != per:
            fail(f"H={H} lift period {truep} != reduced {per} pops={pops}")
    print(f"2/3) H={H}: spectrum match, {len(reps)} cycles all lift with equal period: OK")

# --- 4. the H=7 period-7 wave is a rigid +3-row shift per step ---
H = 7
cells = {(x, r) for r in (0, 2, 6) for x in range(3)}
g1 = life.step(life.from_set(cells, H), 3, H)
if life.to_set(g1, 3, H) != {(x, (r + 3) % H) for (x, r) in cells}:
    fail("H=7 wave is not a +3-row shift")
print("4) H=7 wave shifts +3 rows/step: OK")
print("ALL CHECKS PASSED")
sys.exit(0)
