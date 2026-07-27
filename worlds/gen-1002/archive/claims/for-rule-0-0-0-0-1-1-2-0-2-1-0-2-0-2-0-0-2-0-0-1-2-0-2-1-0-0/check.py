from ca_rule import RULE, validate_rule, step

assert validate_rule(RULE)

def idx(l, c, r):
    return 9*l + 3*c + r

# 1. exact binary-neighborhood table check
expected = {
    (0,0,0): 0, (0,0,1): 0, (0,1,0): 0, (0,1,1): 1,
    (1,0,0): 1, (1,0,1): 0, (1,1,0): 0, (1,1,1): 2,
}
for nb, val in expected.items():
    l, c, r = nb
    assert RULE[idx(l,c,r)] == val, f"mismatch at {nb}: got {RULE[idx(l,c,r)]}, want {val}"

# 2. matches ECA rule24 on all binary neighborhoods except (1,1,1)
def rule24_val(l, c, r):
    nb = (l<<2)|(c<<1)|r
    return (24 >> nb) & 1

mismatches = []
for l in (0,1):
    for c in (0,1):
        for r in (0,1):
            rv = RULE[idx(l,c,r)]
            r24 = rule24_val(l,c,r)
            if rv != r24:
                mismatches.append((l,c,r,rv,r24))
assert mismatches == [(1,1,1,2,0)], f"unexpected mismatch set: {mismatches}"

# 3. closure iff no run of 3 consecutive 1s (cyclic) — direct dynamical check
def has_111(tape):
    L = len(tape)
    for i in range(L):
        if tape[i]==1 and tape[(i+1)%L]==1 and tape[(i+2)%L]==1:
            return True
    return False

def rule24_step(tape):
    L = len(tape)
    out = [0]*L
    for i in range(L):
        l = tape[i-1]; c = tape[i]; r = tape[(i+1)%L]
        out[i] = rule24_val(l,c,r)
    return out

import random
rng = random.Random(999)

# fresh instance: many random binary tapes, various L, check property for many independent draws
trials = 0
for L in [7, 13, 40, 97, 150]:
    for _ in range(30):
        tape = [rng.choice([0,1]) for _ in range(L)]
        pre_has_111 = has_111(tape)
        out = step(tape, RULE)
        out_is_binary = all(v in (0,1) for v in out)
        if not pre_has_111:
            # must stay binary AND match rule24 exactly
            assert out_is_binary, f"L={L} tape had no 111 but escaped: {tape} -> {out}"
            assert out == rule24_step(tape), f"L={L} no-111 tape didn't match rule24: {tape} -> {out} vs {rule24_step(tape)}"
        else:
            # must have escaped: at least one 2 must appear exactly where a 111 window sat
            assert not out_is_binary, f"L={L} tape had 111 but stayed binary: {tape} -> {out}"
        trials += 1

assert trials == 5*30

# also confirm the canonical all-1 -> all-2 escape (special case of the 111 rule, every window is 111)
for L in [1, 5, 50]:
    all1 = [1]*L
    assert step(all1, RULE) == [2]*L

print("OK", trials, "trials checked")
