import sys
from ca_rule import step

def int_to_tape(x, W):
    return [(x >> (W-1-i)) & 1 for i in range(W)]

def tape_to_int(t):
    v = 0
    for b in t:
        v = (v << 1) | b
    return v

def fixed_points(W):
    N = 1 << W
    fps = []
    for x in range(N):
        t = int_to_tape(x, W)
        if tape_to_int(step(t)) == x:
            fps.append(x)
    return fps

for W in range(2, 15):
    fps = set(fixed_points(W))
    all0 = 0
    all1 = (1 << W) - 1
    expected = {all0, all1}
    if W % 2 == 0:
        alt1 = int('01'*(W//2), 2)
        alt2 = int('10'*(W//2), 2)
        expected |= {alt1, alt2}
    if fps != expected:
        print(f"MISMATCH at W={W}: got {sorted(fps)} expected {sorted(expected)}")
        sys.exit(1)

print("All widths W=2..14 match parity rule for fixed points.")
sys.exit(0)
