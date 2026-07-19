import sys
import fixpath
from collections import Counter
torus4 = fixpath.load("torus4")
tr = fixpath.load("transient")

EXPECT = {
    2: dict(maxd=4, die_basin=216, die_max=4, srv_max=1,
            gtips=16, gorbits=[16], srv_hist={0: 20, 1: 20}),
    3: dict(maxd=4, die_basin=3754, die_max=4, srv_max=1,
            gtips=72, gorbits=[48, 24], srv_hist={0: 42, 1: 300}),
    4: dict(maxd=9, die_basin=49116, die_max=8, srv_max=9,
            gtips=128, gorbits=[128], tip_ashpop=4),
    5: dict(maxd=21, die_basin=884500, die_max=21, srv_max=16,
            gtips=80, gorbits=[80], srv_tips=240, srv_orbits=[80, 80, 80],
            srv_ashpop=6),
}

def orbits_of(states, gens):
    stateset = set(states)
    seen = set()
    sizes = []
    for t in states:
        if t in seen:
            continue
        orb = {t}
        frontier = [t]
        while frontier:
            u = frontier.pop()
            for m in gens.values():
                v = tr.apply_perm(u, m)
                if v not in orb:
                    orb.add(v)
                    frontier.append(v)
        assert orb <= stateset, "orbit leaves state set"
        seen |= orb
        sizes.append(len(orb))
    return sorted(sizes, reverse=True)

for H, E in EXPECT.items():
    N = 1 << (4 * H)
    f = torus4.build_f(H)
    dist, oncycle, order = tr.depths(f)
    dies = tr.dies_mask(f, dist, order)
    gens = tr.grid_gens(4, H)

    maxd = max(dist)
    assert maxd == E["maxd"], (H, "maxd", maxd)
    assert sum(dies) == E["die_basin"], (H, "die_basin", sum(dies))

    die_max = max(dist[s] for s in range(N) if dies[s])
    srv_max = max(dist[s] for s in range(N) if not dies[s])
    assert die_max == E["die_max"], (H, "die_max", die_max)
    assert srv_max == E["srv_max"], (H, "srv_max", srv_max)

    gtips = [s for s in range(N) if dist[s] == maxd]
    assert len(gtips) == E["gtips"], (H, "gtips", len(gtips))
    assert orbits_of(gtips, gens) == E["gorbits"], (H, "gorbits")

    # group order sanity: 32, 48, 128, 80 — free orbit iff orbit size == order
    if H in (2, 3):
        hist = dict(Counter(dist[s] for s in range(N) if not dies[s]))
        assert hist == E["srv_hist"], (H, "srv_hist", hist)
        # global tips all die (diehards)
        assert all(dies[s] for s in gtips), (H, "gtips not all diehards")

    if H == 4:
        # global max survives: all 128 tips land on pop-4 still lifes
        for t in gtips:
            per, land = tr.period_of(f, t, maxd)
            assert per == 1 and bin(land).count("1") == E["tip_ashpop"], (H, "tip ash")
        assert not any(dies[s] for s in gtips), (H, "4x4 tips must survive")

    if H == 5:
        assert all(dies[s] for s in gtips), (H, "4x5 gtips not all diehards")
        stips = [s for s in range(N) if not dies[s] and dist[s] == srv_max]
        assert len(stips) == E["srv_tips"], (H, "srv_tips", len(stips))
        assert orbits_of(stips, gens) == E["srv_orbits"], (H, "srv_orbits")
        for t in stips:
            per, land = tr.period_of(f, t, srv_max)
            assert per == 1 and bin(land).count("1") == E["srv_ashpop"], (H, "srv ash")

print("all checks passed")
sys.exit(0)
