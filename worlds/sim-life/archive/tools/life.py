"""Conway's Game of Life on a toroidal grid — bit-parallel engine.

Grid representation: list of H ints, one per row; bit x of g[y] is cell (x, y).
Validated against a naive set-based engine for 200 generations (step 2 of the
soup-ash thread) and against blinker/glider laws (step 1).
"""
import random

def step(g, W, H):
    """One Life generation on a W x H torus. g: list of H row-bitmask ints."""
    MASK = (1 << W) - 1
    s = W - 1
    new = [0] * H
    for i in range(H):
        a, b, c = g[i - 1], g[i], g[(i + 1) % H]
        n1 = ((a << 1) | (a >> s)) & MASK; n3 = ((a >> 1) | (a << s)) & MASK
        n4 = ((b << 1) | (b >> s)) & MASK; n5 = ((b >> 1) | (b << s)) & MASK
        n6 = ((c << 1) | (c >> s)) & MASK; n8 = ((c >> 1) | (c << s)) & MASK
        x1 = n1 ^ a ^ n3;  c1 = (n1 & a) | (n3 & (n1 ^ a))
        x2 = n4 ^ n5 ^ n6; c2 = (n4 & n5) | (n6 & (n4 ^ n5))
        x3 = c ^ n8;       c3 = c & n8
        ones = x1 ^ x2 ^ x3; cA = (x1 & x2) | (x3 & (x1 ^ x2))
        y1 = c1 ^ c2 ^ c3;   d1 = (c1 & c2) | (c3 & (c1 ^ c2))
        twos = y1 ^ cA;      d2 = y1 & cA
        new[i] = twos & ~(d1 | d2) & (ones | b) & MASK
    return new

def from_set(live, H):
    """Set of (x, y) tuples -> row-bitmask grid."""
    g = [0] * H
    for (x, y) in live:
        g[y] |= 1 << x
    return g

def to_set(g, W, H):
    """Row-bitmask grid -> set of (x, y) tuples."""
    return {(x, y) for y in range(H) for x in range(W) if (g[y] >> x) & 1}

def soup(seed, W, H, p=0.5):
    """Random soup grid; column-major x-then-y fill order, random.Random(seed)."""
    rng = random.Random(seed)
    g = [0] * H
    for x in range(W):
        for y in range(H):
            if rng.random() < p:
                g[y] |= 1 << x
    return g

def pop(g):
    """Live-cell count."""
    return sum(bin(r).count("1") for r in g)

def run_to_cycle(g, W, H, max_gens):
    """Advance until the exact grid state repeats or max_gens is hit.

    Returns (gen_stopped, period_or_None, cycle_start_or_None, final_grid).
    """
    seen = {}
    gen = 0
    while gen < max_gens:
        k = tuple(g)
        if k in seen:
            start = seen[k]
            return gen, gen - start, start, g
        seen[k] = gen
        g = step(g, W, H)
        gen += 1
    return gen, None, None, g
