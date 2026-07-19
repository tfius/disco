import sys
from collections import Counter
import fixpath
life = fixpath.load('life')

W = H = 8
CAP = 4096

def find_attractor(seed):
    g = life.soup(seed, W, H, 0.5)
    seen = {tuple(g): 0}
    t = 0
    while t < CAP:
        g = life.step(g, W, H)
        t += 1
        k = tuple(g)
        if k in seen:
            return g, t - seen[k]
        seen[k] = t
    return None, None

periods = Counter()
reps = {}
for s in range(300):
    g, per = find_attractor(508000 + s)
    assert per is not None, f"seed {s} did not resolve"
    periods[per] += 1
    reps.setdefault(per, []).append(g)

assert dict(periods) == {1: 256, 2: 21, 6: 5, 9: 1, 32: 11, 48: 3, 132: 3}, dict(periods)

def cells(g):
    return frozenset(life.to_set(g, W, H))

def translations(c0):
    return {frozenset(((x + dx) % W, (y + dy) % H) for x, y in c0): (dx, dy)
            for dx in range(W) for dy in range(H)}

# (i) every period-32 attractor: lone pop-5 glider, drift t=4, diagonal unit shift of order 8
for g0 in reps[32]:
    assert life.pop(g0) == 5, life.pop(g0)
    tr = translations(cells(g0))
    g = g0
    hit = None
    for t in range(1, 5):
        g = life.step(g, W, H)
        c = cells(g)
        if c in tr:
            hit = (t, tr[c])
            break
    assert hit is not None and hit[0] == 4, hit
    dx, dy = hit[1]
    assert dx in (1, 7) and dy in (1, 7), hit
    o, ax, ay = 1, dx, dy
    while (ax % W, ay % H) != (0, 0):
        ax += dx; ay += dy; o += 1
    assert o == 8, o

def d4_images(c):
    maps = [
        lambda x, y: (x, y),
        lambda x, y: (W - 1 - x, y),
        lambda x, y: (x, H - 1 - y),
        lambda x, y: (W - 1 - x, H - 1 - y),
        lambda x, y: (y, x),
        lambda x, y: (H - 1 - y, x),
        lambda x, y: (y, W - 1 - x),
        lambda x, y: (H - 1 - y, W - 1 - x),
    ]
    return [(pi, frozenset(m(x, y) for x, y in c)) for pi, m in enumerate(maps)]

# (ii)+(iii) p48 and p132: pure oscillators with half-period D4 symmetry, grid-scale
for per in (48, 132):
    g0 = reps[per][0]
    c0 = cells(g0)
    tr = translations(c0)
    trall = {}
    for pi, img in d4_images(c0):
        for k in translations(img):
            trall.setdefault(k, pi)
    g = g0
    ever = set(c0)
    pops = [len(c0)]
    half_ok = False
    for t in range(1, per):
        g = life.step(g, W, H)
        c = cells(g)
        ever |= c
        pops.append(len(c))
        assert c not in tr, f"p{per} drifts/recurs at t={t}"
        if t == per // 2:
            assert c in trall and trall[c] != 0, f"p{per}: no half-period D4 symmetry"
            half_ok = True
    assert half_ok
    assert max(pops) >= 2 * min(pops), (min(pops), max(pops))
    assert len(ever) > 32, len(ever)

print("OK")
sys.exit(0)
