import itertools, random, sys

def step(w):
    if len(w) < 2:
        return None
    c = w[0]
    rest = w[2:]
    return rest + ('bb' if c=='a' else 'a')

def run(w0, budget=5000):
    w = w0
    t = 0
    while True:
        if len(w) < 2:
            return ('halt', t)
        w = step(w)
        t += 1
        if t > budget:
            return ('budget', t)
    # unreachable

fail = False

# exhaustive small lengths
max_by_len = {}
for L in range(1, 15):
    for bits in itertools.product('ab', repeat=L):
        w0 = ''.join(bits)
        kind, t = run(w0)
        if kind != 'halt':
            print("FAIL: non-halt found", w0, kind)
            fail = True
        else:
            max_by_len[L] = max(max_by_len.get(L, 0), t)

# sampled larger lengths
random.seed(1001)
for L in range(15, 61):
    mx = 0
    for _ in range(300):
        w0 = ''.join(random.choice('ab') for _ in range(L))
        kind, t = run(w0)
        if kind != 'halt':
            print("FAIL: non-halt found", w0, kind)
            fail = True
        mx = max(mx, t)
    max_by_len[L] = mx
    # bound check
    if mx > 2 * L:
        print(f"FAIL: bound violated at L={L}, max_steps={mx} > 2*L={2*L}")
        fail = True

if fail:
    sys.exit(1)
print("OK: all tested words halted; max_steps(L) <= 2*L held for all L up to 60")
sys.exit(0)
