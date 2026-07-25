"""
Exact fixed-point counting for the radius-1, 3-state CA rule (ca_rule.RULE),
via a 9-state pair-transition matrix M on states (a,b) in {0,1,2}^2, with
edge (a,b)->(b,c) iff RULE[9a+3b+c]==b (i.e. center cell unchanged).

Number of fixed points on a cyclic tape of width w == trace(M^w).
Verified equal to direct brute-force enumeration for w=3..8 (counts:
4,7,6,12,15,23). Use this instead of ad-hoc trajectory/cycle-finding loops,
which are easy to get wrong (a prior bug double-counted fixed points reached
via multiple distinct predecessor trajectories).

Functions:
  build_pair_matrix(rule=RULE) -> (M, idx_of, pairs)
  mat_mult(A,B), mat_pow(A,p)
  count_fixed_points(w, rule=RULE) -> int   # trace(M^w)
  brute_fixed_points(w, rule=RULE) -> list of fixed-point tapes (tuples)
"""
import itertools
from ca_rule import RULE, step

def build_pair_matrix(rule=RULE):
    pairs = list(itertools.product(range(3), repeat=2))
    idx_of = {p: i for i, p in enumerate(pairs)}
    n = len(pairs)
    M = [[0]*n for _ in range(n)]
    for (a, b) in pairs:
        for c in range(3):
            if rule[9*a+3*b+c] == b:
                M[idx_of[(a,b)]][idx_of[(b,c)]] += 1
    return M, idx_of, pairs

def mat_mult(A, B):
    n = len(A)
    C = [[0]*n for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        for k in range(n):
            if Ai[k] == 0:
                continue
            aik = Ai[k]
            Bk = B[k]
            for j in range(n):
                C[i][j] += aik * Bk[j]
    return C

def mat_pow(A, p):
    n = len(A)
    R = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    base = [row[:] for row in A]
    while p > 0:
        if p & 1:
            R = mat_mult(R, base)
        base = mat_mult(base, base)
        p >>= 1
    return R

def count_fixed_points(w, rule=RULE):
    M, _, _ = build_pair_matrix(rule)
    Mp = mat_pow(M, w)
    return sum(Mp[i][i] for i in range(len(M)))

def brute_fixed_points(w, rule=RULE):
    out = []
    for tape in itertools.product(range(3), repeat=w):
        if tuple(step(list(tape), rule)) == tape:
            out.append(tape)
    return out
