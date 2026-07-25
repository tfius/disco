import math
from collections import Counter

def f_mod(x, m):
    return (66*x**3 + 181*x**2 + 6*x + 5) % m

def tail_and_cycle(x0, m):
    seen = {}
    x = x0
    i = 0
    while x not in seen:
        seen[x] = i
        x = f_mod(x, m)
        i += 1
    return seen[x], i - seen[x]

primes = [2,3,5,7]
comp = {p: {x: tail_and_cycle(x, p) for x in range(p)} for p in primes}
comp_indeg = {}
for p in primes:
    counts = [0]*p
    for z in range(p):
        counts[f_mod(z,p)] += 1
    comp_indeg[p] = counts

full_counts = [0]*210
tails_full = {}
cyc_full = {}
for x in range(210):
    t, c = tail_and_cycle(x, 210)
    tails_full[x] = t
    cyc_full[x] = c
for z in range(210):
    full_counts[f_mod(z,210)] += 1

mism_tc = []
mism_indeg = []
for x in range(210):
    pred_tail = max(comp[p][x % p][0] for p in primes)
    pred_cyc = 1
    for p in primes:
        cp = comp[p][x % p][1]
        pred_cyc = pred_cyc * cp // math.gcd(pred_cyc, cp)
    if (tails_full[x], cyc_full[x]) != (pred_tail, pred_cyc):
        mism_tc.append(x)
    pred_indeg = 1
    for p in primes:
        pred_indeg *= comp_indeg[p][x % p]
    if pred_indeg != full_counts[x]:
        mism_indeg.append(x)

assert len(mism_tc) == 0, f"tail/cycle mismatches: {mism_tc[:5]}"
assert len(mism_indeg) == 0, f"indeg mismatches: {mism_indeg[:5]}"

tail_dist = Counter(tails_full.values())
cyc_dist = Counter(cyc_full.values())
indeg_dist = Counter(full_counts)

assert cyc_dist == Counter({2: 210}), f"cycle dist mismatch: {cyc_dist}"
assert tail_dist == Counter({1: 96, 2: 90, 0: 24}), f"tail dist mismatch: {tail_dist}"
assert indeg_dist == Counter({0:150, 1:16, 2:16, 3:12, 6:12, 9:2, 18:2}), f"indeg dist mismatch: {indeg_dist}"

print("OK: CRT decomposition exact for tail/cycle and in-degree factorization")
