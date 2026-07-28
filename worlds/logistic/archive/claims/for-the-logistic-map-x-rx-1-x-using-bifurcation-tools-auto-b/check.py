import bifurcation_tools as bt

r1 = 3.0
r2 = 1 + 6**0.5  # exact known value, 3.449489742783178...

# recompute r3 (period4->8) from scratch
r3 = bt.auto_bisect_bifurcation(
    lo_period_r=3.5, lower_period=4,
    eps=0.0005, scan_step=0.0005,
    transient=8000, check=800, iters=60, r_max=3.56,
)

# recompute r4 (period8->16) from scratch
r4 = bt.auto_bisect_bifurcation(
    lo_period_r=3.55, lower_period=8,
    eps=0.0005, scan_step=0.0005,
    transient=8000, check=800, iters=60, r_max=3.6,
)

assert abs(r3 - 3.543953739944649) < 0.001, f"r3 mismatch: {r3}"
assert abs(r4 - 3.5643549192611363) < 0.001, f"r4 mismatch: {r4}"

delta1 = (r2 - r1) / (r3 - r2)
delta2 = (r3 - r2) / (r4 - r3)

assert abs(delta1 - 4.758318050154578) < 0.01, f"delta1 mismatch: {delta1}"
assert abs(delta2 - 4.630320419032261) < 0.01, f"delta2 mismatch: {delta2}"

FEIGENBAUM = 4.6692016091029906718532038204662
assert delta2 < delta1, "expected delta2 < delta1 (convergence)"
assert abs(delta2 - FEIGENBAUM) < abs(delta1 - FEIGENBAUM), "expected delta2 closer to true Feigenbaum constant"

# sanity: period transitions confirmed
p_below3 = bt.get_period(r3 - 0.001, tol=1e-5, x0=0.5, transient=8000, check=800)
p_above3 = bt.get_period(r3 + 0.001, tol=1e-5, x0=0.5, transient=8000, check=800)
assert p_below3 == 4 and p_above3 == 8, f"r3 period transition wrong: {p_below3}->{p_above3}"

p_below4 = bt.get_period(r4 - 0.001, tol=1e-5, x0=0.5, transient=8000, check=800)
p_above4 = bt.get_period(r4 + 0.001, tol=1e-5, x0=0.5, transient=8000, check=800)
assert p_below4 == 8 and p_above4 == 16, f"r4 period transition wrong: {p_below4}->{p_above4}"

print("CLAIM VERIFIED")
print(f"r3={r3}, r4={r4}, delta1={delta1}, delta2={delta2}")
