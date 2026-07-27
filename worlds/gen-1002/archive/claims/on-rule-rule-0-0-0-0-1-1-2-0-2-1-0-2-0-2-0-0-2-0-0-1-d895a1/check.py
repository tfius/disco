import sys

RULE = [0,0,0,0,1,1,2,0,2,1,0,2,0,2,0,0,2,0,0,1,2,0,2,1,0,0,1]

def step(tape):
    n = len(tape)
    new = [0]*n
    for i in range(n):
        l = tape[(i-1) % n]
        c = tape[i]
        r = tape[(i+1) % n]
        idx = 9*l + 3*c + r
        new[i] = RULE[idx]
    return new

def rotate_right1(t):
    n = len(t)
    return [t[(i-1) % n] for i in range(n)]

ok = True

for p in range(3, 31):
    for pos in range(p):  # test every starting position, not just 0
        # single '2' defect: must be exact fixed point
        t2 = [0]*p
        t2[pos] = 2
        s2 = step(t2)
        if s2 != t2:
            print(f"FAIL single2 p={p} pos={pos}: step={s2} orig={t2}")
            ok = False

        # single '1' defect: must equal rigid right-shift by 1
        t1 = [0]*p
        t1[pos] = 1
        s1 = step(t1)
        expected = rotate_right1(t1)
        if s1 != expected:
            print(f"FAIL single1 p={p} pos={pos}: step={s1} expected={expected}")
            ok = False

    # full-cycle period check for one representative position per p
    t1 = [0]*p
    t1[0] = 1
    cur = t1[:]
    period_found = None
    for k in range(1, p+2):
        cur = step(cur)
        if cur == t1:
            period_found = k
            break
    if period_found != p:
        print(f"FAIL period p={p}: found {period_found}")
        ok = False

    # mass conservation check across p steps for single1
    cur = t1[:]
    for k in range(p):
        cur = step(cur)
        if sum(1 for x in cur if x != 0) != 1:
            print(f"FAIL mass conservation p={p} step={k}: {cur}")
            ok = False

sys.exit(0 if ok else 1)
