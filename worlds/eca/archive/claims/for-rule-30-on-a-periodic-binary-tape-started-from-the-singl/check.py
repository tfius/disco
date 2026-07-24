import sys

def step(rule, bits):
    n = len(bits)
    table = [(rule >> i) & 1 for i in range(8)]
    out = [0]*n
    for i in range(n):
        l = bits[(i-1) % n]
        c = bits[i]
        r = bits[(i+1) % n]
        idx = (l << 2) | (c << 1) | r
        out[i] = table[idx]
    return out

def transient_len(rule, width, max_steps=200000):
    bits = [0]*width
    bits[0] = 1
    seen = {}
    state = tuple(bits)
    step_num = 0
    while state not in seen:
        seen[state] = step_num
        bits = step(rule, list(state))
        state = tuple(bits)
        step_num += 1
        if step_num > max_steps:
            raise RuntimeError("no cycle found within max_steps")
    return seen[state]

t11 = transient_len(30, 11)
t12 = transient_len(30, 12)

ok = (t11 == 23 and t11 > 11) and (t12 == 24 and t12 > 12)
print(f"width=11 transient={t11} (expect 23, >11)")
print(f"width=12 transient={t12} (expect 24, >12)")
sys.exit(0 if ok else 1)
