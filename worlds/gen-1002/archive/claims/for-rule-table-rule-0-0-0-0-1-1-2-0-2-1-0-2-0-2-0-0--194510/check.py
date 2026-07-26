import sys
from ca_rule import RULE, validate_rule, step

assert validate_rule(RULE)

# Structural guarantee: homogeneous neighborhoods give width-independent lookups
assert RULE[0] == 0, f"RULE[0]={RULE[0]}, expected 0 (all-0 fixed point)"
assert RULE[13] == 2, f"RULE[13]={RULE[13]}, expected 2 (all-1 -> all-2)"
assert RULE[26] == 1, f"RULE[26]={RULE[26]}, expected 1 (all-2 -> all-1)"

ok = True
for n in range(1, 61):
    t0 = [0]*n
    if step(t0, RULE) != t0:
        ok = False
        print(f"FAIL n={n}: all-0 not fixed")

    t1 = [1]*n
    t2 = [2]*n
    n1 = step(t1, RULE)
    n2 = step(n1, RULE)
    if n1 != t2:
        ok = False
        print(f"FAIL n={n}: all-1 did not map to all-2")
    if n2 != t1:
        ok = False
        print(f"FAIL n={n}: all-2 did not map back to all-1")
    if n1 == t1:
        ok = False
        print(f"FAIL n={n}: period collapsed to 1")

sys.exit(0 if ok else 1)
