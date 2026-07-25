import math

def f(x, m=210):
    return (66*x**3 + 181*x**2 + 6*x + 5) % m

def analyze(m):
    fmap = [ (66*x**3+181*x**2+6*x+5)%m for x in range(m) ]
    tail = [None]*m
    cyclen = [None]*m
    for start in range(m):
        if tail[start] is not None:
            continue
        path = []
        pos = {}
        x = start
        while tail[x] is None and x not in pos:
            pos[x] = len(path)
            path.append(x)
            x = fmap[x]
        if tail[x] is not None:
            base_tail = tail[x]
            base_cyc = cyclen[x]
            for i, node in enumerate(reversed(path)):
                d = i+1
                tail[node] = base_tail + d
                cyclen[node] = base_cyc
        else:
            idx = pos[x]
            clen = len(path) - idx
            for i, node in enumerate(path):
                if i >= idx:
                    tail[node] = 0
                    cyclen[node] = clen
                else:
                    tail[node] = idx - i
                    cyclen[node] = clen
    return tail, cyclen

primes = [2,3,5,7]
comp = {p: analyze(p) for p in primes}
full_tail, full_cyc = analyze(210)

# check CRT commutation
for x in range(210):
    fx = f(x)
    for p in primes:
        assert fx % p == (66*(x%p)**3+181*(x%p)**2+6*(x%p)+5) % p, f"commutation fail at x={x}, p={p}"

# check tail/cycle formula
for x in range(210):
    residues = [x % p for p in primes]
    pred_tail = max(comp[p][0][r] for p, r in zip(primes, residues))
    pred_cyc = 1
    for p, r in zip(primes, residues):
        c = comp[p][1][r]
        pred_cyc = pred_cyc * c // math.gcd(pred_cyc, c)
    assert pred_tail == full_tail[x], f"tail mismatch at x={x}"
    assert pred_cyc == full_cyc[x], f"cyclen mismatch at x={x}"

print("CLAIM VERIFIED: CRT decomposition holds exactly for all 210 points")
