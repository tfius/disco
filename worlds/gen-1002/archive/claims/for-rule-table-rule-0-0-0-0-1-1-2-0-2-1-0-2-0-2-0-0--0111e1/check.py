import ca_fixedpoints as F

expected = {1:1, 2:3, 3:4, 4:7, 5:6, 6:12, 7:15, 8:23, 9:31, 10:48}

for w, exp in expected.items():
    brute = F.brute_fixed_points(w)
    mat = F.count_fixed_points(w)
    assert len(brute) == exp, f"w={w}: brute count {len(brute)} != expected {exp}"
    assert mat == exp, f"w={w}: matrix count {mat} != expected {exp}"
    assert len(brute) == mat, f"w={w}: brute {len(brute)} != mat {mat}"

print("All fixed-point counts verified for w=1..10:", expected)
