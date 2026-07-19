import sys
from itertools import combinations
from life import step, from_set, to_set

def image_map(W, H):
    N = W * H
    total = 1 << N
    reachable = bytearray(total)
    fixed = set()
    succ = {}
    small = N <= 9
    for idx in range(total):
        live = {(b % W, b // W) for b in range(N) if (idx >> b) & 1}
        g = step(from_set(live, H), W, H)
        idx2 = 0
        for (x, y) in to_set(g, W, H):
            idx2 |= 1 << (y * W + x)
        reachable[idx2] = 1
        if idx2 == idx:
            fixed.add(idx)
        if small:
            succ[idx] = idx2
    reach_set = {i for i in range(total) if reachable[i]} if small else None
    return sum(reachable), fixed, reach_set, succ

# 2x2: image = {empty} + dominoes, all fixed, 11 GoE
r, fx, rs, _ = image_map(2, 2)
dominoes = {0b0011, 0b1100, 0b0101, 0b1010}
assert rs == {0} | dominoes, "2x2 image wrong"
assert rs == fx, "2x2 image != fixed points"
assert 16 - r == 11, "2x2 GoE count wrong"

# 3x3: image = {empty, full} + pop4; fixed = {empty} + pop4; pop3->full->empty
r, fx, rs, succ = image_map(3, 3)
full = (1 << 9) - 1
pop4 = {sum(1 << b for b in c) for c in combinations(range(9), 4)}
assert rs == {0, full} | pop4, "3x3 image wrong"
assert fx == {0} | pop4, "3x3 fixed points wrong"
assert all(succ[sum(1 << b for b in c)] == full for c in combinations(range(9), 3)), "3x3 pop-3 -> full fails"
assert succ[full] == 0, "3x3 full -> empty fails"

# 4x4 and 4x5 exact counts, monotone decrease at generic sizes
r44, fx44, _, _ = image_map(4, 4)
assert r44 == 17879 and len(fx44) == 53, "4x4 counts wrong"
r45, fx45, _, _ = image_map(4, 5)
assert r45 == 279165 and len(fx45) == 313, "4x5 counts wrong"
assert r44 / 65536 > r45 / 1048576, "generic monotone decrease fails"

print("OK")
sys.exit(0)
