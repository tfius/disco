"""Width-3 toroidal Life reduced dynamics: row-population automaton + still-life transfer matrix.

Width 3 means every cell's neighborhood spans all three columns, so dynamics
factor through row populations: next(row y) = 111 if S==3, row y if S==4, else 0,
where S = pop(y-1)+pop(y)+pop(y+1).

rownext(a_pop, row, b_pop)  -> next row bitmask (row is 3-bit int)
transfer_matrix()           -> 16x16 int matrix M on (prev_pop, pop) pairs
still_counts(Hmax)          -> dict H -> N(3,H) = trace(M^H), exact ints
"""

def _pc(x): return bin(x).count("1")

def rownext(a_pop, row, b_pop):
    S = a_pop + _pc(row) + b_pop
    if S == 3: return 7
    if S == 4: return row
    return 0

def _valid(a, p, b):
    S = a + p + b
    if p == 0: return a + b != 3
    if p == 3: return S in (3, 4)
    return S == 4

_C3 = [1, 3, 3, 1]

def transfer_matrix():
    M = [[0]*16 for _ in range(16)]
    for a in range(4):
        for p in range(4):
            for b in range(4):
                if _valid(a, p, b):
                    M[4*a+p][4*p+b] += _C3[b]
    return M

def _matmul(A, B):
    return [[sum(A[i][k]*B[k][j] for k in range(16) if A[i][k]) for j in range(16)]
            for i in range(16)]

def still_counts(Hmax):
    M = transfer_matrix()
    N = {}
    Mp = M
    for H in range(2, Hmax+1):
        Mp = _matmul(Mp, M)
        N[H] = sum(Mp[i][i] for i in range(16))
    return N
