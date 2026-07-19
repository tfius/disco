"""Width-W strip/torus machinery for Life image analysis.

- next_row_table(W): tbl[(a<<2W)|(b<<W)|c] = successor of middle row b given
  rows a above and c below, toroidal columns. Rows are W-bit ints.
- image_size(W, H, tbl): exact number of one-step-reachable states on the W-by-H
  torus (feasible up to ~2^27 total states in ~20s).
- build_dfa(W): follower-set DFA of the image sofic shift on the width-W strip,
  via subset construction over the row-pair NFA. Returns edge list
  edges[state] = [successor, ...] (one per admissible output letter).
  Sizes: W=2 -> 690 states, W=3 -> 533, W=4 blows past 50k.
- word_counts(edges, nmax): [a_1..a_nmax], a_n = number of distinct length-n
  output words (paths from the full-set start state). Growth ratio -> lambda_W
  (lambda_2 = 3.250988, lambda_3 = 4.544950), always < 2^W: GoE fraction -> 1.

NOTE: import fixpath first in experiments that also need stdlib fractions/re.
"""
from itertools import product

def next_row_table(W):
    M = 1 << W
    tbl = [0] * (M * M * M)
    for a in range(M):
        for b in range(M):
            base = (a << (2 * W)) | (b << W)
            for c in range(M):
                nr = 0
                for j in range(W):
                    l = (j - 1) % W
                    r = (j + 1) % W
                    cnt = (((a >> l) & 1) + ((a >> j) & 1) + ((a >> r) & 1)
                         + ((b >> l) & 1) + ((b >> r) & 1)
                         + ((c >> l) & 1) + ((c >> j) & 1) + ((c >> r) & 1))
                    if cnt == 3 or (((b >> j) & 1) and cnt == 2):
                        nr |= 1 << j
                tbl[base | c] = nr
    return tbl

def image_size(W, H, tbl=None):
    if tbl is None:
        tbl = next_row_table(W)
    M = 1 << W
    s2 = 2 * W
    seen = bytearray(1 << (W * H))
    cs2 = [c << s2 for c in range(M)]
    cw = [c << W for c in range(M)]
    sh0 = W * (H - 1)
    for head in product(range(M), repeat=H - 1):
        P = 0
        for i in range(1, H - 2):
            P = (P << W) | tbl[(head[i - 1] << s2) | (head[i] << W) | head[i + 1]]
        P2 = P << s2
        k0 = (head[0] << W) | head[1]
        km = (head[H - 3] << s2) | (head[H - 2] << W)
        kl = (head[H - 2] << s2) | head[0]
        for c in range(M):
            seen[(tbl[cs2[c] | k0] << sh0) | P2 | (tbl[km | c] << W) | tbl[kl | cw[c]]] = 1
    return seen.count(1)

def build_dfa(W, cap_states=200000):
    M = 1 << W
    M2 = M * M
    tbl = next_row_table(W)
    trans = [[0] * M for _ in range(M2)]
    for a in range(M):
        for b in range(M):
            s = a * M + b
            for c in range(M):
                o = tbl[(a << (2 * W)) | (b << W) | c]
                trans[s][o] |= 1 << (b * M + c)
    full = (1 << M2) - 1
    idx = {full: 0}
    order = [full]
    edges = []
    i = 0
    while i < len(order):
        S = order[i]
        row = []
        for o in range(M):
            T = 0
            X = S
            while X:
                lb = X & -X
                T |= trans[lb.bit_length() - 1][o]
                X ^= lb
            if T:
                j = idx.get(T)
                if j is None:
                    j = len(order)
                    idx[T] = j
                    order.append(T)
                row.append(j)
        edges.append(row)
        i += 1
        if len(order) > cap_states:
            raise RuntimeError(f"DFA blew past {cap_states} states")
    return edges

def word_counts(edges, nmax):
    v = [0] * len(edges)
    v[0] = 1
    out = []
    for n in range(nmax):
        nv = [0] * len(edges)
        for s, row in enumerate(edges):
            c = v[s]
            if c:
                for t in row:
                    nv[t] += c
        v = nv
        out.append(sum(v))
    return out
