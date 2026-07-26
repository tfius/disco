def f(x):
    return (66*x**3 + 181*x**2 + 6*x + 5) % 210

def fp(y, p):
    return (66*y**3 + 181*y**2 + 6*y + 5) % p

primes = [2,3,5,7]

preimg_full = {x: set() for x in range(210)}
for y in range(210):
    preimg_full[f(y)].add(y)

preimg_p = {}
for p in primes:
    d = {r: set() for r in range(p)}
    for y in range(p):
        d[fp(y,p)].add(y)
    preimg_p[p] = d

mismatches = 0
for x in range(210):
    predicted = set()
    for y in range(210):
        ok = True
        for p in primes:
            if (y % p) not in preimg_p[p][x % p]:
                ok = False
                break
        if ok:
            predicted.add(y)
    if predicted != preimg_full[x]:
        mismatches += 1

assert mismatches == 0, f"{mismatches} mismatches found"
print("OK: 0 mismatches, set-level CRT factorization confirmed")
