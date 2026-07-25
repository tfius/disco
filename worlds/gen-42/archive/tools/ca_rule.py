"""CA rule implementation for radius-2, 2-state cellular automaton.

RULE table indexed by 5-bit neighborhood (leftmost cell = MSB, rightmost = LSB).
Cyclic boundary conditions.
"""

RULE = [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1,
        0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1]

def step(tape):
    """Advance a cyclic tape (list of 0/1) by one CA step."""
    n = len(tape)
    out = [0]*n
    for i in range(n):
        idx = 0
        for k in range(-2, 3):
            idx = (idx << 1) | tape[(i+k) % n]
        out[i] = RULE[idx]
    return out

def run(tape, steps):
    """Run `steps` iterations, return list of tapes including initial (len steps+1)."""
    history = [tape[:]]
    t = tape[:]
    for _ in range(steps):
        t = step(t)
        history.append(t[:])
    return history

def neighborhood_index(bits):
    """Convert a 5-bit list (MSB..LSB) to the RULE index."""
    idx = 0
    for b in bits:
        idx = (idx << 1) | b
    return idx
