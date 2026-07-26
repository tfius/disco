import sys
from ca_rule import run, RULE, validate_rule

validate_rule(RULE)

def nz_positions(t):
    return [i for i,v in enumerate(t) if v != 0]

for W in [5, 7, 11, 21, 61, 101]:
    c = W // 2

    # Case A: single 1 -> rigid right mover, period W
    tapeA = [0]*W
    tapeA[c] = 1
    histA = run(tapeA, W, RULE)
    for t in range(W+1):
        pos = nz_positions(histA[t])
        assert pos == [(c+t) % W], f"W={W} t={t} case A pos={pos} expected {[(c+t)%W]}"
        assert histA[t][pos[0]] == 1, f"W={W} t={t} case A value != 1"

    # Case B: single 2 -> stationary, hold for 150 steps
    tapeB = [0]*W
    tapeB[c] = 2
    histB = run(tapeB, 150, RULE)
    for t in range(151):
        pos = nz_positions(histB[t])
        assert pos == [c], f"W={W} t={t} case B pos={pos} expected [{c}]"
        assert histB[t][c] == 2, f"W={W} t={t} case B value != 2"

print("all widths OK")
sys.exit(0)
