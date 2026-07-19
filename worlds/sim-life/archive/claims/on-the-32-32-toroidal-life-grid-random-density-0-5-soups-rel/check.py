import sys
import life
from collections import Counter

W = H = 32
CAP = 6000

def analyze(seed):
    g = life.soup(seed, W, H, 0.5)
    if isinstance(g, list):
        g = tuple(g)
    seen = {g: 0}
    for t in range(1, CAP + 1):
        g = life.step(g, W, H)
        if isinstance(g, list):
            g = tuple(g)
        if g in seen:
            return seen[g], t - seen[g]
        seen[g] = t
    return None, None

def batch(lo, hi):
    periods = Counter()
    transients = []
    for s in range(lo, hi):
        tr, p = analyze(s)
        if p is None:
            print("FAIL: seed %d did not converge within %d" % (s, CAP))
            sys.exit(1)
        periods[p] += 1
        transients.append(tr)
    return periods, transients

p1, t1 = batch(910000, 910100)
p2, t2 = batch(920000, 920100)

if dict(p1) != {1: 21, 2: 78, 128: 1}:
    print("FAIL batch1 spectrum:", dict(sorted(p1.items())))
    sys.exit(1)
if dict(p2) != {1: 22, 2: 77, 128: 1}:
    print("FAIL batch2 spectrum:", dict(sorted(p2.items())))
    sys.exit(1)
if max(t1) != 2224 or max(t2) != 1471:
    print("FAIL max transients:", max(t1), max(t2))
    sys.exit(1)
if abs(sum(t1) / len(t1) - 516.0) > 0.05 or abs(sum(t2) / len(t2) - 444.5) > 0.05:
    print("FAIL transient means: %.2f %.2f" % (sum(t1) / len(t1), sum(t2) / len(t2)))
    sys.exit(1)
for p in list(p1) + list(p2):
    if p not in (1, 2) and p != 128:
        print("FAIL unexpected period", p)
        sys.exit(1)
print("OK: spectra {1:21,2:78,128:1} and {1:22,2:77,128:1}, no periods in 3..127, long period exactly 128")
sys.exit(0)
