"""Exhaustive state-space enumeration for small toroidal Life grids.
image_map(W, H) -> (n_reachable, fixed_set, reachable_set_or_None, succ_dict)
State encoding: bit y*W+x set iff cell (x,y) live. reachable_set and succ
are only populated when W*H <= 20 (memory guard); succ maps state -> successor."""
from life import step, from_set, to_set

def image_map(W, H):
    N = W * H
    total = 1 << N
    reachable = bytearray(total)
    fixed = set()
    succ = {}
    keep = N <= 20
    for idx in range(total):
        live = {(b % W, b // W) for b in range(N) if (idx >> b) & 1}
        g = step(from_set(live, H), W, H)
        idx2 = 0
        for (x, y) in to_set(g, W, H):
            idx2 |= 1 << (y * W + x)
        reachable[idx2] = 1
        if idx2 == idx:
            fixed.add(idx)
        if keep:
            succ[idx] = idx2
    reach_set = {i for i in range(total) if reachable[i]} if keep else None
    return sum(reachable), fixed, reach_set, succ
