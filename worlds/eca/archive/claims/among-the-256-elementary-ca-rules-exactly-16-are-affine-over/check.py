def truth_table(rule):
    return [(rule >> p) & 1 for p in range(8)]  # index p = 4*a+2*b+c

def is_affine(rule):
    tt = truth_table(rule)
    f = tt[:]
    for i in range(3):
        bit = 1 << i
        for x in range(8):
            if x & bit:
                f[x] ^= f[x ^ bit]
    return all(f[m] == 0 for m in range(8) if bin(m).count('1') >= 2)

def affine_coeffs(rule):
    tt = truth_table(rule)
    def f(a,b,c): return tt[4*a+2*b+c]
    c0 = f(0,0,0)
    c1 = f(1,0,0) ^ c0
    c2 = f(0,1,0) ^ c0
    c3 = f(0,0,1) ^ c0
    ok = all(tt[4*a+2*b+c] == (c0 ^ (c1&a) ^ (c2&b) ^ (c3&c))
             for a in (0,1) for b in (0,1) for c in (0,1))
    return (c0,c1,c2,c3), ok

def step(rule, state, N):
    tt = truth_table(rule)
    out = 0
    for i in range(N):
        a = (state >> ((i-1)%N)) & 1
        b = (state >> i) & 1
        c = (state >> ((i+1)%N)) & 1
        out |= tt[4*a+2*b+c] << i
    return out

def is_bijective(rule, N):
    seen = set()
    for s in range(1<<N):
        o = step(rule, s, N)
        if o in seen:
            return False
        seen.add(o)
    return True

affine_rules = [r for r in range(256) if is_affine(r)]
expected_affine = [0,15,51,60,85,90,102,105,150,153,165,170,195,204,240,255]
assert affine_rules == expected_affine, affine_rules
assert len(affine_rules) == 16

decomp = {}
for r in affine_rules:
    coeffs, ok = affine_coeffs(r)
    assert ok
    decomp[r] = coeffs

linear_parts = {}
for r, (c0,c1,c2,c3) in decomp.items():
    linear_parts.setdefault((c1,c2,c3), []).append(r)

expected_parts = {
    (0,0,0):[0,255], (0,0,1):[85,170], (0,1,0):[51,204], (0,1,1):[102,153],
    (1,0,0):[15,240], (1,0,1):[90,165], (1,1,0):[60,195], (1,1,1):[105,150],
}
assert len(linear_parts) == 8
for lp, rules in expected_parts.items():
    assert sorted(linear_parts[lp]) == rules, (lp, linear_parts[lp])

monomial_parts = {(1,0,0),(0,1,0),(0,0,1)}
Ns = list(range(3,13))

bijective_all_N = sorted(r for r in affine_rules if all(is_bijective(r,N) for N in Ns))
predicted = sorted(r for lp,rules in linear_parts.items() if lp in monomial_parts for r in rules)
assert bijective_all_N == predicted == [15,51,85,170,204,240], bijective_all_N

# confirm the 5 non-monomial linear parts each fail bijectivity for some N in range
for lp, rules in linear_parts.items():
    if lp in monomial_parts:
        continue
    for r in rules:
        assert not all(is_bijective(r,N) for N in Ns), (r, "should fail some N")

print("OK")
