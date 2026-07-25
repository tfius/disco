import math

def rule_table(rule):
    return [(rule >> p) & 1 for p in range(8)]

def step(state, N, table):
    out = 0
    for i in range(N):
        l = (state >> ((i-1) % N)) & 1
        c = (state >> i) & 1
        r = (state >> ((i+1) % N)) & 1
        idx = (l<<2)|(c<<1)|r
        out |= table[idx] << i
    return out

def perm_order(rule, N):
    table = rule_table(rule)
    size = 1 << N
    perm = [step(s, N, table) for s in range(size)]
    seen = [False]*size
    order = 1
    for s in range(size):
        if seen[s]:
            continue
        cyc = []
        cur = s
        while not seen[cur]:
            seen[cur] = True
            cyc.append(cur)
            cur = perm[cur]
        order = order * len(cyc) // math.gcd(order, len(cyc))
    return order

rules_shift = {170: 1, 204: 0, 240: -1}
rules_shiftc = {15: -1, 51: 0, 85: 1}

mismatches = []
for N in range(1, 15):
    for rule, s in rules_shift.items():
        d = math.gcd(N, abs(s)) if s != 0 else N
        m = N // d
        pred = m
        actual = perm_order(rule, N)
        if pred != actual:
            mismatches.append((rule, N, pred, actual))
    for rule, s in rules_shiftc.items():
        d = math.gcd(N, abs(s)) if s != 0 else N
        m = N // d
        pred = m if m % 2 == 0 else 2*m
        actual = perm_order(rule, N)
        if pred != actual:
            mismatches.append((rule, N, pred, actual))

if mismatches:
    print("MISMATCHES:", mismatches)
    raise SystemExit(1)
print("all match, N=1..14")
