"""Reusable bifurcation-hunting routines for the logistic map x -> r*x*(1-x)."""

def get_period(r, tol=1e-5, x0=0.5, transient=8000, check=400, maxp=128):
    x = x0
    for _ in range(transient):
        x = r*x*(1-x)
    seq = []
    for _ in range(check):
        x = r*x*(1-x)
        seq.append(x)
    for p in range(1, maxp+1):
        ok = True
        for i in range(len(seq)-p):
            if abs(seq[i+p]-seq[i]) > tol:
                ok = False
                break
        if ok:
            return p
    return None

def bisect_bifurcation(lo, hi, lower_period, transient=8000, check=400, iters=50):
    p_lo = get_period(lo, transient=transient, check=check)
    p_hi = get_period(hi, transient=transient, check=check)
    assert p_lo == lower_period, f"bad lo bracket: expected {lower_period}, got {p_lo} at r={lo}"
    assert p_hi == lower_period*2, f"bad hi bracket: expected {lower_period*2}, got {p_hi} at r={hi}"
    for _ in range(iters):
        mid = (lo+hi)/2
        p = get_period(mid, transient=transient, check=check)
        if p is None or p <= lower_period:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2

def find_hi_bracket(r_start, target_period, r_max=4.0, step=0.001):
    """Scan forward from r_start until get_period(r) == target_period. Returns r or None.
    Useful because near a bifurcation the period right at/just past the boundary is
    often ambiguous (returns the lower period) due to finite transient/check windows;
    scanning finds a point solidly inside the higher-period window."""
    r = r_start
    while r <= r_max:
        if get_period(r) == target_period:
            return r
        r += step
    return None

def auto_bisect_bifurcation(lo_period_r, lower_period, eps=0.0005, scan_step=0.001,
                             transient=8000, check=400, iters=50, r_max=4.0):
    """Robust wrapper: given a point lo_period_r known to have period==lower_period,
    scans forward to find a hi bracket with period==2*lower_period, then bisects.
    Nudges the lo bracket by +eps to dodge boundary ambiguity where get_period right
    at the found bifurcation still reports the lower period."""
    target = lower_period * 2
    hi = find_hi_bracket(lo_period_r, target, r_max=r_max, step=scan_step)
    assert hi is not None, f"could not find r with period {target} scanning from {lo_period_r}"
    lo = lo_period_r
    if get_period(lo, transient=transient, check=check) != lower_period:
        lo = lo_period_r + eps
    return bisect_bifurcation(lo, hi, lower_period, transient=transient, check=check, iters=iters)
