import sys
from fixpath import load
cyc = load("cyc")
decomp = load("decomp")
life = load("life")

W = H = 32
seeds = range(900000, 900020)

results = []
for seed in seeds:
    g0 = life.soup(seed, W, H, p=0.5)
    start, period = cyc.find_cycle(g0, W, H, cap=6000)
    g = g0
    for _ in range(start):
        g = life.step(g, W, H)
    states = decomp.cycle_states(g, period, W, H)
    frozen, everseen = decomp.frozen_mobile(states)
    total_live = sum(len(s) for s in states) / len(states)
    frac_frozen = len(frozen) / total_live if total_live > 0 else float('nan')
    results.append((seed, period, len(frozen)/(W*H), frac_frozen))

frozen_densities = [r[2] for r in results]
frac_frozens = [r[3] for r in results]
periods = sorted(set(r[1] for r in results))

mean_fd = sum(frozen_densities)/len(frozen_densities)
mean_ff = sum(frac_frozens)/len(frac_frozens)

assert 0.020 <= mean_fd <= 0.040, f"mean frozen density {mean_fd} out of range"
assert 0.75 <= mean_ff <= 0.95, f"mean frac_frozen {mean_ff} out of range"
assert all(f >= 0.5 for f in frac_frozens), f"some frac_frozen < 0.5: {frac_frozens}"
assert set(periods) == {1, 2, 128}, f"unexpected periods: {periods}"

print("OK: mean_fd=%.4f mean_ff=%.4f periods=%s" % (mean_fd, mean_ff, periods))
sys.exit(0)
