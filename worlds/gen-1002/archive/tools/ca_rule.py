"""Reusable CA rule-101002 engine (radius-1, 3-state, cyclic tapes).

RULE is a length-27 list indexed by 9*left + 3*center + right (base-3,
leftmost neighbor most significant), values in {0,1,2}.
"""

RULE = [0, 0, 0, 0, 1, 1, 2, 0, 2, 1, 0, 2, 0, 2, 0, 0, 2, 0, 0, 1, 2, 0, 2, 1, 0, 0, 1]

def validate_rule(rule=RULE):
    assert len(rule) == 27
    for v in rule:
        assert v in (0, 1, 2)
    return True

def step(tape, rule=RULE):
    """One synchronous update of a cyclic tape."""
    n = len(tape)
    out = [0] * n
    for i in range(n):
        l = tape[(i - 1) % n]
        c = tape[i]
        r = tape[(i + 1) % n]
        idx = l * 9 + c * 3 + r
        out[i] = rule[idx]
    return out

def run(tape, steps, rule=RULE):
    """Return list of tapes, seq[0]=initial, seq[k]=after k steps."""
    seq = [tape]
    cur = tape
    for _ in range(steps):
        cur = step(cur, rule)
        seq.append(cur)
    return seq

def nz(tape):
    """Nonzero (index, value) pairs — useful for sparse-defect tracing."""
    return [(i, v) for i, v in enumerate(tape) if v != 0]
