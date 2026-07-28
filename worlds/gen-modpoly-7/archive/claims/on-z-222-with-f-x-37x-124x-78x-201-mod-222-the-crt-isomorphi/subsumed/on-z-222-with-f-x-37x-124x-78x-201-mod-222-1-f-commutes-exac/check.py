def f(x, m=222):
    return (37*x**3 + 124*x**2 + 78*x + 201) % m

def fm(a, m):
    return (37*a**3 + 124*a**2 + 78*a + 201) % m

moduli = [2, 3, 37]

def analyze(m):
    tail = {}
    cyc_len = {}
    cycles_found = []
    for start in range(m):
        seen = {}
        x = start
        path = []
        while x not in seen:
            seen[x] = len(path)
            path.append(x)
            x = fm(x, m)
        tail_len = seen[x]
        cyc = path[tail_len:]
        tail[start] = tail_len
        cyc_len[start] = len(cyc)
    return tail, cyc_len

tails = {}
cycs = {}
for m in moduli:
    t, c = analyze(m)
    tails[m] = t
    cycs[m] = c

# component checks
assert all(tails[2][a] == 0 for a in range(2)), "f2 should have zero tails"
assert all(cycs[2][a] == 2 for a in range(2)), "f2 should be single 2-cycle"

assert tails[3] == {0: 0, 1: 2, 2: 1}, f"f3 tails mismatch: {tails[3]}"
assert all(cycs[3][a] == 1 for a in range(3)), "f3 should collapse to fixed point"

expected_tail37 = {0: 6, 1: 4, 2: 0, 3: 9, 4: 4, 5: 10, 6: 5, 7: 6, 8: 2, 9: 7, 10: 7,
                    11: 11, 12: 0, 13: 3, 14: 5, 15: 5, 16: 5, 17: 5, 18: 3, 19: 1,
                    20: 11, 21: 7, 22: 7, 23: 2, 24: 6, 25: 5, 26: 10, 27: 4, 28: 9,
                    29: 1, 30: 4, 31: 6, 32: 6, 33: 3, 34: 8, 35: 3, 36: 6}
assert tails[37] == expected_tail37, f"f37 tails mismatch: {tails[37]}"
assert all(cycs[37][a] == 1 for a in range(37)), "f37 should be all fixed-point-feeding"
fixed37 = [a for a in range(37) if fm(a,37) == a]
assert sorted(fixed37) == [2, 12], f"f37 fixed points mismatch: {fixed37}"

# full graph: CRT product structure, mismatch count 0
import math
def crt(a2, a3, a37):
    M = 222
    mods = [2,3,37]
    vals = [a2,a3,a37]
    x = 0
    for mi, ai in zip(mods, vals):
        Mi = M // mi
        inv = pow(Mi, -1, mi)
        x += ai * Mi * inv
    return x % M

def tail_and_cycle_full(x):
    seen = {}
    path = []
    cur = x
    while cur not in seen:
        seen[cur] = len(path)
        path.append(cur)
        cur = f(cur)
    tlen = seen[cur]
    clen = len(path) - tlen
    return tlen, clen

mismatches = 0
tail_lengths_all = {}
for x in range(222):
    a2, a3, a37 = x % 2, x % 3, x % 37
    pred_tail = max(tails[2][a2], tails[3][a3], tails[37][a37])
    l = cycs[2][a2]
    l = l * cycs[3][a3] // math.gcd(l, cycs[3][a3])
    l = l * cycs[37][a37] // math.gcd(l, cycs[37][a37])
    pred_cycle = l
    actual_tail, actual_cycle = tail_and_cycle_full(x)
    tail_lengths_all[x] = actual_tail
    if actual_tail != pred_tail or actual_cycle != pred_cycle:
        mismatches += 1

assert mismatches == 0, f"CRT product structure violated: {mismatches} mismatches"

# full cycle structure
seen_global = {}
cycles = []
for start in range(222):
    path = []
    seenlocal = {}
    x = start
    while x not in seenlocal:
        seenlocal[x] = len(path)
        path.append(x)
        x = f(x)
    tail_len = seenlocal[x]
    cyc = path[tail_len:]
    key = frozenset(cyc)
    if key not in seen_global:
        seen_global[key] = cyc
        cycles.append(cyc)

cycle_sets = sorted([sorted(c) for c in cycles])
expected_cycles = sorted([[39,150],[12,123]])
assert cycle_sets == expected_cycles, f"cycle structure mismatch: {cycle_sets}"

total_cyc_pts = sum(len(c) for c in cycles)
assert total_cyc_pts == 4, f"expected 4 cyclic points, got {total_cyc_pts}"

# tail length distribution
from collections import Counter
tl_counter = dict(Counter(tail_lengths_all.values()))
expected_dist = {0: 4, 1: 12, 2: 20, 3: 24, 4: 24, 5: 36, 6: 36, 7: 24, 8: 6, 9: 12, 10: 12, 11: 12}
assert tl_counter == expected_dist, f"tail length distribution mismatch: {tl_counter}"
assert max(tail_lengths_all.values()) == 11

print("ALL CHECKS PASSED")
