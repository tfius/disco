import random, sys

W = H = 64
MASK = (1 << W) - 1

def rotl(v): return ((v << 1) | (v >> (W - 1))) & MASK
def rotr(v): return ((v >> 1) | (v << (W - 1))) & MASK

def step_rows(g):
    new = [0] * H
    for i in range(H):
        a, b, c = g[i - 1], g[i], g[(i + 1) % H]
        n1 = rotl(a); n3 = rotr(a)
        n4 = rotl(b); n5 = rotr(b)
        n6 = rotl(c); n8 = rotr(c)
        x1 = n1 ^ a ^ n3;  c1 = (n1 & a) | (n3 & (n1 ^ a))
        x2 = n4 ^ n5 ^ n6; c2 = (n4 & n5) | (n6 & (n4 ^ n5))
        x3 = c ^ n8;       c3 = c & n8
        ones = x1 ^ x2 ^ x3; cA = (x1 & x2) | (x3 & (x1 ^ x2))
        y1 = c1 ^ c2 ^ c3;   d1 = (c1 & c2) | (c3 & (c1 ^ c2))
        twos = y1 ^ cA;      d2 = y1 & cA
        new[i] = twos & ~(d1 | d2) & (ones | b) & MASK
    return new

def soup_rows(seed, p=0.5):
    rng = random.Random(seed)
    g = [0] * H
    for x in range(W):
        for y in range(H):
            if rng.random() < p:
                g[y] |= 1 << x
    return g

def pop(g): return sum(bin(r).count("1") for r in g)

densities = []
for seed in range(10):
    g = soup_rows(seed, 0.5)
    seen = {}
    gen, period, start = 0, None, None
    while gen < 5000:
        k = tuple(g)
        if k in seen:
            start = seen[k]
            period = gen - start
            break
        seen[k] = gen
        g = step_rows(g)
        gen += 1
    d = pop(g) / (W * H)
    densities.append(d)
    print(f"seed={seed} start={start} period={period} density={d:.4f}")
    if period != 2:
        print("FAIL: period != 2"); sys.exit(1)
    if start is None or start > 3700:
        print("FAIL: cycled too late"); sys.exit(1)
    if not (0.015 <= d <= 0.045):
        print("FAIL: density out of band"); sys.exit(1)

mean = sum(densities) / len(densities)
print(f"mean_density={mean:.4f}")
if not (0.0227 <= mean <= 0.0327):
    print("FAIL: mean density out of band"); sys.exit(1)
print("OK")
sys.exit(0)
