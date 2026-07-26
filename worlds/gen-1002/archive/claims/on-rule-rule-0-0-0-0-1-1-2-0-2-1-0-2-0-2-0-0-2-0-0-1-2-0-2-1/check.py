import sys
from ca_rule import RULE, validate_rule, step

assert validate_rule(RULE)

def nz_positions(row):
    return [i for i,v in enumerate(row) if v != 0]

def run(tape, steps):
    hist = [tape[:]]
    t = tape[:]
    for _ in range(steps):
        t = step(t, RULE)
        hist.append(t[:])
    return hist

ok = True
fails = []

# (1) lone '1' moves right at velocity +1, forever, on several widths/positions
for W, a in [(61, 10), (121, 0), (151, 75), (97, 50)]:
    tape = [0]*W
    tape[a] = 1
    steps = W * 2  # run past a full wrap to be safe
    hist = run(tape, steps)
    for tt in range(steps+1):
        pos = nz_positions(hist[tt])
        if pos != [(a+tt) % W]:
            fails.append(f"1-particle W={W} a={a} t={tt} pos={pos} expected={[(a+tt)%W]}")
            ok = False
            break
        if hist[tt][(a+tt)%W] != 1:
            fails.append(f"1-particle value wrong W={W} a={a} t={tt}")
            ok = False
            break

# (2) lone '2' stays stationary forever
for W, b in [(61, 30), (121, 5), (151, 100)]:
    tape = [0]*W
    tape[b] = 2
    steps = W
    hist = run(tape, steps)
    for tt in range(steps+1):
        pos = nz_positions(hist[tt])
        if pos != [b] or hist[tt][b] != 2:
            fails.append(f"2-particle W={W} b={b} t={tt} pos={pos} val={hist[tt][b] if pos else None}")
            ok = False
            break

# (3) merge behavior: 1 at a, 2 at b, 0 < b-a < W, no wraparound issue (leave margin)
for W, a, b in [(121, 20, 100), (200, 10, 150), (150, 5, 120), (100, 0, 60)]:
    tape = [0]*W
    tape[a] = 1
    tape[b] = 2
    gap = b - a
    steps = gap + 30  # run well past merge
    hist = run(tape, steps)

    # just before merge: t = gap-1 -> two 2's at b-1, b
    t_pre = gap - 1
    pos_pre = nz_positions(hist[t_pre])
    if pos_pre != [b-1, b] or hist[t_pre][b-1] != 2 or hist[t_pre][b] != 2:
        fails.append(f"pre-merge W={W} a={a} b={b} t={t_pre} pos={pos_pre} vals={[hist[t_pre][p] for p in pos_pre]}")
        ok = False

    # at merge: t = gap -> single 2 at b-1
    t_merge = gap
    pos_m = nz_positions(hist[t_merge])
    if pos_m != [b-1] or hist[t_merge][b-1] != 2:
        fails.append(f"merge W={W} a={a} b={b} t={t_merge} pos={pos_m}")
        ok = False

    # after merge: permanently stationary single 2 at b-1
    for tt in range(t_merge, steps+1):
        pos = nz_positions(hist[tt])
        if pos != [b-1] or hist[tt][b-1] != 2:
            fails.append(f"post-merge W={W} a={a} b={b} t={tt} pos={pos}")
            ok = False
            break

if not ok:
    print("FAILURES:")
    for f in fails:
        print(" ", f)
    sys.exit(1)

print("All particle/merge behaviors confirmed.")
sys.exit(0)
