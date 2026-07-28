def tail_period(r, burn, x0=0.2, n=200):
    x = x0
    for _ in range(burn):
        x = r*x*(1-x)
    xs = []
    for _ in range(n):
        x = r*x*(1-x)
        xs.append(x)
    return xs

def is_period1(r, burn, tol=1e-7):
    xs = tail_period(r, burn)
    return all(abs(xs[i]-xs[0]) < tol for i in range(len(xs)))

def find_boundary1(burn, lo=2.9, hi=3.1, iters=40):
    assert is_period1(lo, burn) and not is_period1(hi, burn)
    for _ in range(iters):
        mid = (lo+hi)/2
        if is_period1(mid, burn):
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2

results = {}
for burn in [20000, 60000]:
    b = find_boundary1(burn)
    e = 3.0 - b
    prod = e * burn
    results[burn] = (b, e, prod)
    print(f"burn={burn} boundary1={b:.9f} error={e:.6e} prod={prod:.4f}")

b20, e20, p20 = results[20000]
b60, e60, p60 = results[60000]

# monotonic approach to 3
assert b60 > b20, f"boundary should move closer to 3 as burn grows: {b20} vs {b60}"
assert e60 < e20, "error must shrink with larger burn"

# error*burn stays in a bounded slowly-drifting band (Theta(1/burn), not const, not 1/burn^2)
assert 8.0 < p20 < 16.0, f"prod20={p20}"
assert 8.0 < p60 < 16.0, f"prod60={p60}"

# ratio check: consistent with ~1/burn scaling (ratio near 3x, generous band to allow log drift),
# and explicitly NOT consistent with 1/burn^2 (which would give ratio ~9x) or constant error (ratio ~1x)
ratio = e20 / e60
assert 2.0 < ratio < 4.5, f"ratio={ratio} not consistent with Theta(1/burn) scaling"

print("OK: critical slowing down near r=3 bifurcation confirmed, error ~ C/burn")
