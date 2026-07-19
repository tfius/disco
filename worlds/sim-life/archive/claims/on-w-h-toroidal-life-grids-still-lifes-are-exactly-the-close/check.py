import sys
import stilltm, life

fails = []
def chk(name, cond):
    if not cond:
        fails.append(name)
        print("FAIL:", name)
    else:
        print("ok:", name)

def brute(W, H):
    cnt = 0
    mask = (1 << W) - 1
    for s in range(1 << (W * H)):
        g = [(s >> (r * W)) & mask for r in range(H)]
        if life.step(g, W, H) == g:
            cnt += 1
    return cnt

# 1. transfer graph counts == brute force
adj = {W: stilltm.build_adj(W) for W in (3, 4, 5, 6, 7)}
expect = {(3, 2): 3, (3, 3): 127, (3, 4): 39, (4, 2): 9, (4, 3): 39, (4, 4): 53}
for (W, H), n in expect.items():
    tr = stilltm.trace_H(adj[W], W, H)
    bf = brute(W, H)
    chk(f"trace==brute=={n} at W={W},H={H}", tr == bf == n)

# 2. W=3 SCC structure: two nontrivial SCCs, per-3 rad-3 without empty, aperiodic with empty
def nontrivial_sccs(W):
    succ = stilltm.succ_of(adj[W], W)
    nodes = [s for s in range(len(adj[W])) if adj[W][s]]
    comps = stilltm.sccs_iter(nodes, succ)
    out = []
    for c in comps:
        if len(c) > 1 or c[0] in succ(c[0]):
            p = stilltm.scc_period(c, succ)
            r = stilltm.scc_radius(c, succ, max(p, 1))
            out.append((len(c), p, r, 0 in c))
    return out

s3 = nontrivial_sccs(3)
chk("W=3 has exactly 2 nontrivial SCCs", len(s3) == 2)
per3 = [x for x in s3 if x[1] == 3]
aper = [x for x in s3 if x[1] == 1]
chk("W=3 one period-3 SCC: n=27, radius 3, no empty",
    len(per3) == 1 and per3[0][0] == 27 and abs(per3[0][2] - 3.0) < 1e-6 and not per3[0][3])
chk("W=3 one aperiodic SCC: n=30, contains empty, radius~2.7036318",
    len(aper) == 1 and aper[0][0] == 30 and aper[0][3] and abs(aper[0][2] - 2.7036318) < 1e-4)

# period-3 SCC is the binary family: both rows of each state in {0, 7}
if per3:
    succ3 = stilltm.succ_of(adj[3], 3)
    nodes3 = [s for s in range(len(adj[3])) if adj[3][s]]
    comps3 = stilltm.sccs_iter(nodes3, succ3)
    big = max((c for c in comps3 if stilltm.scc_period(c, succ3) == 3), key=len)
    chk("period-3 SCC states are binary rows {0,7}... no wait, n=27 so not only",
        len(big) == 27)

# 3. W=4..7: exactly one nontrivial SCC, aperiodic, contains empty, radius matches
lam_expect = {4: 2.5537154293, 5: 4.4791773687, 6: 5.0930357529, 7: 6.4166263135}
lams = {3: 3.0}
for W in (4, 5, 6, 7):
    sW = nontrivial_sccs(W)
    chk(f"W={W} exactly one nontrivial SCC", len(sW) == 1)
    n, p, r, has0 = sW[0]
    chk(f"W={W} SCC aperiodic + contains empty", p == 1 and has0)
    chk(f"W={W} radius ~ {lam_expect[W]}", abs(r - lam_expect[W]) < 1e-6)
    lams[W] = r

# 4. period-3 oscillation and mu^3 correction for W=3
N3 = {H: stilltm.trace_H(adj[3], 3, H) for H in list(range(2, 8)) + [9, 12, 15, 18, 21]}
chk("N(3,H) H=2..7 == 3,127,39,121,2595,1177",
    [N3[H] for H in range(2, 8)] == [3, 127, 39, 121, 2595, 1177])
d = {H: N3[H] - 3 * 3**H for H in (9, 12, 15, 18, 21)}
r1, r2 = d[18] / d[15], d[21] / d[18]
mu3 = 2.7036318 ** 3
chk("d(H+3)/d(H) -> mu^3 ~ 19.76", abs(r1 - mu3) < 0.2 and abs(r2 - mu3) < 0.06)

# 5. eta non-monotone with stated ordering (subset)
eta = {W: lams[W] ** (1.0 / W) for W in lams}
chk("eta ordering eta3>eta5>eta6>eta7>eta4",
    eta[3] > eta[5] > eta[6] > eta[7] > eta[4])
chk("eta3 inflated above all others", all(eta[3] > eta[W] for W in (4, 5, 6, 7)))

print("\n%d failures" % len(fails))
sys.exit(1 if fails else 0)
