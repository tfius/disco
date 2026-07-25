import sys

RULE = [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1,
        0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1]

def step(tape):
    n = len(tape)
    out = [0]*n
    for i in range(n):
        idx = 0
        for k in range(-2,3):
            idx = (idx<<1) | tape[(i+k) % n]
        out[i] = RULE[idx]
    return out

# check table fidelity on width-5 cyclic tape
for idx in range(32):
    bits = [(idx>>k)&1 for k in range(4,-1,-1)]
    nxt = step(bits)
    if nxt[2] != RULE[idx]:
        print(f"table mismatch at idx={idx}")
        sys.exit(1)

# check fixed points for widths 1..30
for width in range(1, 31):
    zero_tape = [0]*width
    one_tape = [1]*width
    t = zero_tape[:]
    for _ in range(20):
        t = step(t)
        if t != zero_tape:
            print(f"zero tape not fixed at width={width}")
            sys.exit(1)
    t = one_tape[:]
    for _ in range(20):
        t = step(t)
        if t != one_tape:
            print(f"one tape not fixed at width={width}")
            sys.exit(1)

print("OK")
sys.exit(0)
