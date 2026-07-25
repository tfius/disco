"""Reusable functional-graph analysis for maps on Z_m.

analyze(m, fmap=None, poly=None) -> (tail, cyclen)
  tail[x]   = number of steps from x until entering its eventual cycle
  cyclen[x] = length of the eventual cycle reached from x

Provide either fmap (list of length m, fmap[x]=f(x)) or poly=(a,b,c,d,mod_formula)
where f(x) = (66*x**3+181*x**2+6*x+5) % m is the default system's map.
"""
import math

def default_f(x, m):
    return (66*x**3 + 181*x**2 + 6*x + 5) % m

def analyze(m, fmap=None):
    if fmap is None:
        fmap = [default_f(x, m) for x in range(m)]
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

def crt_predict(m, primes, comp=None):
    """Given full modulus m and its prime factors, and component (tail,cyclen)
    dicts keyed by prime (each analyze(p) output), predict full tail/cyclen
    per x via max-tail / lcm-cycle rule. Returns (pred_tail, pred_cyc) lists."""
    if comp is None:
        comp = {p: analyze(p) for p in primes}
    pred_tail = [None]*m
    pred_cyc = [None]*m
    for x in range(m):
        residues = [x % p for p in primes]
        pred_tail[x] = max(comp[p][0][r] for p, r in zip(primes, residues))
        c_lcm = 1
        for p, r in zip(primes, residues):
            c = comp[p][1][r]
            c_lcm = c_lcm * c // math.gcd(c_lcm, c)
        pred_cyc[x] = c_lcm
    return pred_tail, pred_cyc
