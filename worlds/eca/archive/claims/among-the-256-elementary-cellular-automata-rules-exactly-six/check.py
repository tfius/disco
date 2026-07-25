def rule_table(rule):
    return [(rule >> i) & 1 for i in range(8)]

def apply_rule(state, n, tbl):
    out = 0
    for i in range(n):
        l = (state >> ((i-1) % n)) & 1
        c = (state >> i) & 1
        r = (state >> ((i+1) % n)) & 1
        idx = (l << 2) | (c << 1) | r
        out |= tbl[idx] << i
    return out

def is_bijective(rule, n):
    tbl = rule_table(rule)
    seen = set()
    for s in range(1 << n):
        img = apply_rule(s, n, tbl)
        if img in seen:
            return False
        seen.add(img)
    return True

Ns = list(range(4, 14))
always_bijective = []
for rule in range(256):
    if all(is_bijective(rule, n) for n in Ns):
        always_bijective.append(rule)

expected = [15, 51, 85, 170, 204, 240]
assert always_bijective == expected, f"got {always_bijective}, expected {expected}"
print("OK:", always_bijective)
