import math
from collections import Counter

def f_full(x):
    return (66*x**3 + 181*x**2 + 6*x + 5) % 210

def f_p(y, p):
    return (66*y**3 + 181*y**2 + 6*y + 5) % p

def tail_cyc(m, fmap):
    tail = [0]*m
    cyc = [0]*m
    for x in range(m):
        seq = [x]
        cur = x
        for _ in range(m+2):
            cur = fmap(cur)
            seq.append(cur)
        seen = {}
        for i, v in enumerate(seq):
            if v in seen:
                cstart = seen[v]
                clen = i - cstart
                tail[x] = cstart
                cyc[x] = clen
                break
            seen[v] = i
    return tail, cyc

def lcm(a,b): return a*b//math.gcd(a,b)

tail_full, cyc_full = tail_cyc(210, f_full)

primes = [2,3,5,7]
per_prime = {}
for p in primes:
    per_prime[p] = tail_cyc(p, lambda y, p=p: f_p(y,p))

expected_tails = {2:[0,0], 3:[0,1,0], 5:[0,2,1,1,0], 7:[0,2,0,2,1,0,1]}
expected_cycs  = {2:[2,2], 3:[2,2,2], 5:[1,1,1,1,1], 7:[2,1,1,1,1,2,1]}
for p in primes:
    t,c = per_prime[p]
    assert t == expected_tails[p], f"tail mismatch p={p}: {t}"
    assert c == expected_cycs[p], f"cyc mismatch p={p}: {c}"

mismatches = 0
for x in range(210):
    tp=[]; cp=[]
    for p in primes:
        y = x % p
        t,c = per_prime[p]
        tp.append(t[y]); cp.append(c[y])
    pt = max(tp)
    pc = 1
    for cc in cp: pc = lcm(pc,cc)
    if pt != tail_full[x] or pc != cyc_full[x]:
        mismatches += 1

assert mismatches == 0, f"{mismatches} mismatches found"

tail_hist = Counter(tail_full)
assert dict(tail_hist) == {0:24, 1:96, 2:90}, f"tail hist {dict(tail_hist)}"

cyc_hist = Counter(cyc_full[x] for x in range(210) if tail_full[x]==0)
assert dict(cyc_hist) == {2:24}, f"cyc hist {dict(cyc_hist)}"

num_cycles = sum(v//k for k,v in cyc_hist.items())
assert num_cycles == 12, f"num cycles {num_cycles}"

print("OK")
