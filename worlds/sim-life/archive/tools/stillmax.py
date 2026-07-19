"""Maximum still-life population on W x H toroidal Life grids.

Row-pair transfer DP over cyclic row configurations. Valid for H >= 3
(H=2 wraps vertically so each row is its own double neighbor -- use brute force there).
Verified law: max_still_pop(W)[H] == (W*H)//2 for all W<=7 tested.

  succ_graph(W)          -> dict {(rowA,rowB): [rowC,...]} of locally-stable triples, trimmed to its recurrent core
  max_still_pop(W, Hmax) -> dict {H: max population of a still life on W x H torus}, H in 3..Hmax
  stripes(W, H)          -> a floor(WH/2)-population still life as a set of (row,col), when W or H is even
"""

def succ_graph(W):
    S = 1 << W
    wc = [[((r >> ((x-1) % W)) & 1) + ((r >> x) & 1) + ((r >> ((x+1) % W)) & 1)
           for x in range(W)] for r in range(S)]
    succ = {}
    for a in range(S):
        wa = wc[a]
        for b in range(S):
            wb = wc[b]
            lst = []
            for c in range(S):
                wcc = wc[c]; ok = True
                for x in range(W):
                    own = (b >> x) & 1
                    n = wa[x] + wcc[x] + wb[x] - own
                    if (1 if (n == 3 or (own and n == 2)) else 0) != own:
                        ok = False; break
                if ok: lst.append(c)
            if lst: succ[(a, b)] = lst
    # trim to recurrent core: states with both in- and out-edges, to fixpoint
    while True:
        has_in = set()
        for s, lst in succ.items():
            for c in lst: has_in.add((s[1], c))
        ns = {}; changed = False
        for s, lst in succ.items():
            if s not in has_in: changed = True; continue
            l2 = [c for c in lst if (s[1], c) in succ]
            if len(l2) != len(lst): changed = True
            if l2: ns[s] = l2
            else: changed = True
        succ = ns
        if not changed: break
    return succ

def max_still_pop(W, Hmax):
    succ = succ_graph(W)
    POP = [bin(r).count('1') for r in range(1 << W)]
    res = {}
    for s0 in list(succ):
        best = {s0: 0}
        for h in range(1, Hmax + 1):
            nb = {}
            for s, w in best.items():
                nw = w + POP[s[1]]
                for c in succ.get(s, ()):
                    t = (s[1], c)
                    if nb.get(t, -1) < nw: nb[t] = nw
            best = nb
            if not best: break
            if h >= 3 and s0 in best and res.get(h, -1) < best[s0]:
                res[h] = best[s0]
    return res

def stripes(W, H):
    """A floor(WH/2)-cell still life as {(row,col)}. Requires W or H even."""
    if H % 2 == 0:
        return {(r, c) for r in range(0, H, 2) for c in range(W)}
    if W % 2 == 0:
        return {(r, c) for c in range(0, W, 2) for r in range(H)}
    raise ValueError("odd x odd torus: floor(WH/2) needs a non-stripe pattern")
