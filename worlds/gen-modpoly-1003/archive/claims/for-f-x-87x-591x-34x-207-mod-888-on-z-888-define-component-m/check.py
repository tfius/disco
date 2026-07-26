def f_mod(x, m):
    return (87*x**3 + 591*x**2 + 34*x + 207) % m

def build_indeg_mod(m):
    cnt = [0]*m
    for x in range(m):
        cnt[f_mod(x, m)] += 1
    return cnt

cnt8 = build_indeg_mod(8)
cnt3 = build_indeg_mod(3)
cnt37 = build_indeg_mod(37)
cnt888 = build_indeg_mod(888)

# per-point factorization holds exactly
for y in range(888):
    pred = cnt8[y % 8] * cnt3[y % 3] * cnt37[y % 37]
    assert pred == cnt888[y], f"mismatch at y={y}: {cnt888[y]} vs {pred}"

nz8 = sum(1 for v in cnt8 if v > 0)
nz3 = sum(1 for v in cnt3 if v > 0)
nz37 = sum(1 for v in cnt37 if v > 0)

assert nz8 == 4
assert nz3 == 3
assert nz37 == 25
assert nz8 * nz3 * nz37 == 300

zero_count = sum(1 for v in cnt888 if v == 0)
assert zero_count == 588

# f_3 is a full bijection: every residue has in-degree exactly 1
assert all(v == 1 for v in cnt3)

print("OK: in-degree factorization exact, image size 300, zero-count 588, f_3 bijective")
