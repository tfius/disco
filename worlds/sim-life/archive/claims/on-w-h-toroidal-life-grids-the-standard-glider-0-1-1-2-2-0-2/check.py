import sys
import life
from math import lcm

GLIDER = {(0,1),(1,2),(2,0),(2,1),(2,2)}

def shifted(s, dr, dc, W, H):
    return {((a+dr) % H, (b+dc) % W) for (a, b) in s}

def run(W, H, cap=6000):
    g = life.from_set(GLIDER, H)
    seen, hist, t = {}, [], 0
    key = tuple(g)
    while key not in seen and t < cap:
        seen[key] = t
        hist.append(g)
        g = life.step(g, W, H)
        key = tuple(g)
        t += 1
    tr = seen[key]
    return tr, t - tr, hist

fail = []

# Above threshold: spaceship + exact period 4*lcm(W,H)
for (W, H) in [(5,5),(5,6),(5,16),(6,6),(6,9),(7,7),(7,16),(8,8),(8,15),(6,13)]:
    tr, per, hist = run(W, H)
    s0 = life.to_set(hist[tr], W, H)
    g4 = hist[tr]
    for _ in range(4):
        g4 = life.step(g4, W, H)
    s4 = life.to_set(g4, W, H)
    if not (tr == 0 and len(s0) == 5 and s4 == shifted(s0, 1, 1, W, H)):
        fail.append(("ship", W, H))
    if per != 4 * lcm(W, H):
        fail.append(("period", W, H, per))

# Below threshold: never a translate of the glider anywhere in the cycle
glider_translates = set()
for (W, H) in [(3,h) for h in range(3,17)] + [(4,h) for h in range(4,17)]:
    tr, per, hist = run(W, H)
    g = hist[tr]
    ok = True
    for _ in range(per):
        s = life.to_set(g, W, H)
        if len(s) == 5:
            for dr in range(H):
                for dc in range(W):
                    if shifted(GLIDER, dr, dc, W, H) == s:
                        ok = False
        g = life.step(g, W, H)
    if not ok:
        fail.append(("subthreshold-translate", W, H))

# Specific anatomy facts
tr, per, hist = run(4, 4)
if not (per == 8 and tr == 3):
    fail.append(("4x4", tr, per))
pops = []
g = hist[tr]
for _ in range(per):
    pops.append(life.pop(g))
    g = life.step(g, 4, 4)
if sorted(pops) != [4, 4, 5, 5, 5, 5, 5, 5]:
    fail.append(("4x4-pops", pops))
for (W, H) in [(4,6),(4,10),(4,16)]:
    tr, per, hist = run(W, H)
    if not (per == 1 and life.pop(hist[tr]) == 0):
        fail.append(("4xH-death", W, H, tr, per))
tr, per, hist = run(3, 16)
if per != 14:
    fail.append(("3x16", per))

if fail:
    print("FAIL:", fail)
    sys.exit(1)
print("OK")
sys.exit(0)
