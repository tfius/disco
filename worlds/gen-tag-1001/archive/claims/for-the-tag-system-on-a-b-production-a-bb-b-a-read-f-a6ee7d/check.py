import random, sys

def step(w):
    if len(w) < 2:
        return None
    c, rest = w[0], w[2:]
    prod = 'bb' if c == 'a' else 'a'
    return rest + prod

def classify(w, budget=3000):
    seen = {}
    cur = w
    t = 0
    while True:
        if len(cur) < 2:
            return 'halt'
        if cur in seen:
            return 'cycle'
        seen[cur] = t
        cur = step(cur)
        t += 1
        if t > budget:
            return 'unknown'

random.seed(12345)
bad = []
for L in [15, 20, 30, 50, 80, 120, 200]:
    for _ in range(500):
        w = ''.join(random.choice('ab') for _ in range(L))
        kind = classify(w)
        if kind != 'halt':
            bad.append((L, w, kind))

if bad:
    print("FOUND NON-HALTING:", bad[:5])
    sys.exit(1)

print("all sampled words halted, 0 cycles, 0 unknowns")
sys.exit(0)
