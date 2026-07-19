import sys, math, life

def pc(x): return bin(x).count("1")
C3 = [1,3,3,1]

def rownext(a_pop, row, b_pop):
    S = a_pop + pc(row) + b_pop
    if S == 3: return 7
    if S == 4: return row
    return 0

# (0) row-population automaton == life.step on width-3 toruses
for s in range(20):
    H = 10
    g = life.soup(9900+s, 3, H)
    for _ in range(3):
        cells = life.to_set(g, 3, H)
        rows = [0]*H
        for (x,y) in cells: rows[y] |= 1<<x
        g = life.step(g, 3, H)
        cells2 = life.to_set(g, 3, H)
        rows2 = [0]*H
        for (x,y) in cells2: rows2[y] |= 1<<x
        pred = [rownext(pc(rows[y-1]), rows[y], pc(rows[(y+1)%H])) for y in range(H)]
        assert pred == rows2, "row automaton mismatch"

# (a) 3x3: still lifes = empty + all pop-4 patterns = 127
n33 = 0
for s in range(512):
    cells = {(x,y) for y in range(3) for x in range(3) if (s>>(3*y+x))&1}
    still = life.to_set(life.step(life.from_set(cells,3),3,3),3,3) == cells
    p = len(cells)
    assert still == (p in (0,4)), "3x3 characterization fails"
    n33 += still
assert n33 == 127, n33

# (b) transfer matrix trace == brute-force census
def valid(a,p,b):
    S = a+p+b
    if p == 0: return a+b != 3
    if p == 3: return S in (3,4)
    return S == 4

M = [[0]*16 for _ in range(16)]
for a in range(4):
    for p in range(4):
        for b in range(4):
            if valid(a,p,b):
                M[4*a+p][4*p+b] += C3[b]

def matmul(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(16) if A[i][k]) for j in range(16)] for i in range(16)]

N = {}
Mp = M
for H in range(2, 49):
    Mp = matmul(Mp, M)
    N[H] = sum(Mp[i][i] for i in range(16))

def brute(H):
    n = 0
    for s in range(1 << (3*H)):
        cells = {(x,y) for y in range(H) for x in range(3) if (s>>(3*y+x))&1}
        if life.to_set(life.step(life.from_set(cells,H),3,H),3,H) == cells: n += 1
    return n

for H in (3,4,5):
    assert N[H] == brute(H), f"transfer != brute at H={H}"
assert (N[3],N[4],N[5],N[6],N[16]) == (127,39,121,2595,8112423), "known counts fail"

# (c) growth structure
r3  = [N[H]/N[H-3] for H in (18,24,30,36,42,48)]
assert all(x < y for x,y in zip(r3, r3[1:])), "3|H ratios not increasing"
assert all(x < 27 for x in r3), "3|H ratio exceeds 27"
assert 26.9 < r3[-1] < 27.0, r3[-1]
for H in (43,44,46,47):
    assert abs(N[H]/N[H-3] - 19.7625) < 1e-3, f"non-mult ratio off at H={H}"
assert abs(math.log2(N[47])/141 - 0.4783) < 5e-4
e48 = math.log2(N[48])/144
assert math.log2(3)/3 < e48 < 0.540, e48

print("OK")
sys.exit(0)
