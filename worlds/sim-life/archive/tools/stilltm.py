"""Still-life transfer-operator machinery for W x H toroidal Life.

States are (prev_row, cur_row) pairs encoded a*R+p with R=2^W, rows W-bit ints.
Edge (a,p) -> (p,b) iff row p is stable (Life rule fixes every cell of p)
given row a above and row b below. Number of still lifes on the W x H torus
= number of closed walks of length H = trace(M^H). Validated against brute
force for (W,H) in {3,4}x{2,3,4}.

build_adj(W)            -> adj list, adj[a*R+p] = sorted list of b
succ_of(adj, W)         -> successor function s -> [t]
trace_H(adj, W, H)      -> exact still-life count on W x H torus (int)
trim_core(adj, W)       -> set of states on some biinfinite path (recurrent core)
sccs_iter(nodes, succ)  -> list of SCCs (iterative Tarjan)
scc_period(comp, succ)  -> period (gcd of cycle lengths) of an SCC
scc_radius(comp, succ, p) -> spectral radius via p-step power iteration
"""
from math import gcd

def tables(W):
    R = 1 << W
    t3, t2 = [], []
    for r in range(R):
        r3, r2 = [], []
        for c in range(W):
            l, rt = (c-1) % W, (c+1) % W
            bl, bc, br = (r >> l) & 1, (r >> c) & 1, (r >> rt) & 1
            r3.append(bl + bc + br); r2.append(bl + br)
        t3.append(r3); t2.append(r2)
    return t3, t2

def build_adj(W):
    R = 1 << W
    t3, t2 = tables(W)
    amask = [[[0, 0] for _ in range(6)] for _ in range(W)]
    for c in range(W):
        for b in range(R):
            v = t3[b][c]
            for s in range(6):
                n = s + v
                if 2 <= n <= 3: amask[c][s][1] |= 1 << b
                if n != 3:      amask[c][s][0] |= 1 << b
    FULL = (1 << R) - 1
    adj = [None] * (R * R)
    for a in range(R):
        ta = t3[a]
        for p in range(R):
            tp = t2[p]
            m = FULL
            for c in range(W):
                m &= amask[c][ta[c] + tp[c]][(p >> c) & 1]
                if not m: break
            lst = []
            while m:
                lb = m & -m
                lst.append(lb.bit_length() - 1)
                m ^= lb
            adj[a * R + p] = lst
    return adj

def succ_of(adj, W):
    R = 1 << W
    def succ(s):
        base = (s % R) * R
        return [base + b for b in adj[s]]
    return succ

def trace_H(adj, W, H):
    R = 1 << W
    total = 0
    for s in range(R * R):
        if not adj[s]: continue
        v = {s: 1}
        for _ in range(H):
            nv = {}
            for st, cnt in v.items():
                base = (st % R) * R
                for b in adj[st]:
                    k = base + b
                    nv[k] = nv.get(k, 0) + cnt
            v = nv
            if not v: break
        total += v.get(s, 0)
    return total

def trim_core(adj, W):
    R = 1 << W
    alive = set(s for s in range(R * R) if adj[s])
    while True:
        has_in = set()
        for s in alive:
            base = (s % R) * R
            for b in adj[s]:
                t = base + b
                if t in alive: has_in.add(t)
        new_alive = set()
        for s in alive:
            if s not in has_in: continue
            base = (s % R) * R
            if any((base + b) in alive for b in adj[s]):
                new_alive.add(s)
        if new_alive == alive: break
        alive = new_alive
    return alive

def sccs_iter(nodes, succ):
    index = {}; low = {}; onstk = set(); stk = []; out = []
    cnt = [0]
    for root in nodes:
        if root in index: continue
        work = [(root, iter(succ(root)))]
        index[root] = low[root] = cnt[0]; cnt[0] += 1
        stk.append(root); onstk.add(root)
        while work:
            v, it = work[-1]
            adv = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = cnt[0]; cnt[0] += 1
                    stk.append(w); onstk.add(w)
                    work.append((w, iter(succ(w))))
                    adv = True; break
                elif w in onstk:
                    if index[w] < low[v]: low[v] = index[w]
            if adv: continue
            work.pop()
            if work:
                u = work[-1][0]
                if low[v] < low[u]: low[u] = low[v]
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stk.pop(); onstk.discard(w); comp.append(w)
                    if w == v: break
                out.append(comp)
    return out

def scc_period(comp, succ):
    cs = set(comp)
    root = comp[0]
    lvl = {root: 0}; q = [root]; g = 0
    while q:
        nq = []
        for u in q:
            for w in succ(u):
                if w not in cs: continue
                if w in lvl:
                    g = gcd(g, lvl[u] + 1 - lvl[w])
                else:
                    lvl[w] = lvl[u] + 1; nq.append(w)
        q = nq
    return abs(g) if g else 0

def scc_radius(comp, succ, p, iters=400):
    cs = {s: i for i, s in enumerate(comp)}
    nbrs = [[cs[w] for w in succ(s) if w in cs] for s in comp]
    n = len(comp)
    v = [1.0] * n
    lam = 0.0
    for it in range(iters):
        tot0 = sum(v)
        for _ in range(max(p, 1)):
            nv = [0.0] * n
            for i in range(n):
                x = v[i]
                if x:
                    for j in nbrs[i]:
                        nv[j] += x
            v = nv
        tot1 = sum(v)
        if tot1 == 0: return 0.0
        newlam = (tot1 / tot0) ** (1.0 / max(p, 1))
        v = [x / tot1 for x in v]
        if it > 3 and abs(newlam - lam) < 1e-12: return newlam
        lam = newlam
    return lam
