"""Reusable core routines for exploring the logistic map x -> r*x*(1-x)."""

def logistic_iter(r, x0, n):
    """Return list of n iterates starting from x0 (x0 itself not included)."""
    x = x0
    xs = []
    for _ in range(n):
        x = r * x * (1 - x)
        xs.append(x)
    return xs

def tail_period(r, burn, x0=0.2, n=200):
    """Iterate burn warmup steps then return next n steps (for period/convergence checks)."""
    x = x0
    for _ in range(burn):
        x = r * x * (1 - x)
    xs = []
    for _ in range(n):
        x = r * x * (1 - x)
        xs.append(x)
    return xs

def is_close(a, b, tol):
    return abs(a - b) < tol

def is_period1(r, burn, x0=0.2, n=200, tol=1e-7):
    xs = tail_period(r, burn, x0, n)
    return all(is_close(v, xs[0], tol) for v in xs)

def is_period_le2(r, burn, x0=0.2, n=200, tol=1e-7):
    xs = tail_period(r, burn, x0, n)
    return all(is_close(xs[i], xs[i % 2], tol) for i in range(len(xs)))

def fixed_point(r):
    """Analytic nontrivial fixed point 1-1/r (valid target for r>1)."""
    return 1 - 1 / r

def multiplier_at_fixed_point(r):
    """Derivative of f at the nontrivial fixed point: f'(x*) = 2 - r."""
    return 2 - r

def bisect_boundary(pred_lo_true, lo, hi, iters=40):
    """Generic bisection: pred_lo_true(mid) True means still on 'lo' side.
    Requires pred_lo_true(lo)==True and pred_lo_true(hi)==False."""
    assert pred_lo_true(lo) and not pred_lo_true(hi)
    for _ in range(iters):
        mid = (lo + hi) / 2
        if pred_lo_true(mid):
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
