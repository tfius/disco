import bifurcation_tools as bt

r1 = 3.0
r2 = bt.bisect_bifurcation(3.0, 3.5, lower_period=2)
assert abs(r2 - 3.449138848659235) < 1e-9, r2

# bracket-find hi for r3 (period 4->8) by scanning, exactly as in experiment
hi8 = None
r = 3.55
while r <= 3.565:
    if bt.get_period(r) == 8:
        hi8 = r
        break
    r += 0.001
assert hi8 is not None
r3 = bt.bisect_bifurcation(3.50, hi8, lower_period=4)
assert abs(r3 - 3.543953739944649) < 1e-9, r3

# bracket-find hi for r4 (period 8->16)
eps = 0.0005
lo4 = r3 + eps
assert bt.get_period(lo4) == 8
hi16 = None
r = r3 + 0.001
while r <= 3.568:
    if bt.get_period(r) == 16:
        hi16 = r
        break
    r += 0.0005
assert hi16 is not None
r4 = bt.bisect_bifurcation(lo4, hi16, lower_period=8)
assert abs(r4 - 3.564354919261117) < 1e-9, r4

delta1 = (r2 - r1) / (r3 - r2)
delta2 = (r3 - r2) / (r4 - r3)
assert abs(delta1 - 4.737007473933891) < 1e-9, delta1
assert abs(delta2 - 4.647520117078646) < 1e-9, delta2

feig = 4.6692016091
assert abs(delta2 - feig) < abs(delta1 - feig)
