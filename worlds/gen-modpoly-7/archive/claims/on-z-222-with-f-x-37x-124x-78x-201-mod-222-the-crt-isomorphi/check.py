def f_mod(m):
    def f(x):
        return (37*x**3 + 124*x**2 + 78*x + 201) % m
    return f

f222 = f_mod(222)
f2, f3, f37 = f_mod(2), f_mod(3), f_mod(37)

# 1. commuting law
for x in range(222):
    assert f222(x) % 2 == f2(x % 2)
    assert f222(x) % 3 == f3(x % 3)
    assert f222(x) % 37 == f37(x % 37)

# 2. CRT bijection check
seen = set()
for x in range(222):
    key = (x % 2, x % 3, x % 37)
    assert key not in seen
    seen.add(key)
assert len(seen) == 222

def preimage_table(m, fm):
    pre = {y: [] for y in range(m)}
    for z in range(m):
        pre[fm(z)].append(z)
    return pre

pre222 = preimage_table(222, f222)
pre2 = preimage_table(2, f2)
pre3 = preimage_table(3, f3)
pre37 = preimage_table(37, f37)

def crt(z2, z3, z37):
    for z in range(222):
        if z % 2 == z2 and z % 3 == z3 and z % 37 == z37:
            return z
    raise ValueError

# 3. exact preimage set equality for ALL x (full sweep, fresh full verification)
for x in range(222):
    x2, x3, x37 = x % 2, x % 3, x % 37
    predicted = set()
    for z2 in pre2[x2]:
        for z3 in pre3[x3]:
            for z37 in pre37[x37]:
                predicted.add(crt(z2, z3, z37))
    actual = set(pre222[x])
    assert predicted == actual, f"mismatch at x={x}"

# 4. indegree factorization law, fresh check via direct counting (not reusing preimage sets)
indeg222 = [0]*222
for z in range(222):
    indeg222[f222(z)] += 1
indeg2 = [0]*2
for z in range(2):
    indeg2[f2(z)] += 1
indeg3 = [0]*3
for z in range(3):
    indeg3[f3(z)] += 1
indeg37 = [0]*37
for z in range(37):
    indeg37[f37(z)] += 1

for x in range(222):
    assert indeg222[x] == indeg2[x%2]*indeg3[x%3]*indeg37[x%37]

# 5. fresh instance: cycle structure of f_222 restricted to CRT-fixed-point-compatible residues
# check that x is a fixed point of f222 iff (x%2,x%3,x%37) are simultaneously fixed points of f2,f3,f37
fixed2 = {z for z in range(2) if f2(z) == z}
fixed3 = {z for z in range(3) if f3(z) == z}
fixed37 = {z for z in range(37) if f37(z) == z}
for x in range(222):
    is_fixed_222 = (f222(x) == x)
    is_fixed_components = (x%2 in fixed2) and (x%3 in fixed3) and (x%37 in fixed37)
    assert is_fixed_222 == is_fixed_components, f"fixed point mismatch at x={x}"

print("LAW VERIFIED: full CRT factorization of f on Z_222 into Z_2 x Z_3 x Z_37 components")
