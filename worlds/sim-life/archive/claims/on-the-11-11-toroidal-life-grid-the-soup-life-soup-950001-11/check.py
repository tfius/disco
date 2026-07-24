import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
import life, cyc

W = H = 11
seed = 950001
p = 0.5

g0 = life.soup(seed, W, H, p)
start, period = cyc.find_cycle(g0, W, H, cap=6000)

assert start == 73, f"expected start=73, got {start}"
assert period == 429, f"expected period=429, got {period}"
assert period % 2 == 1, "period should be odd"

g = g0
for _ in range(start):
    g = life.step(g, W, H)
cyc_start_state = tuple(g)

pops = []
gg = g
for i in range(period):
    pops.append(sum(bin(row).count("1") for row in gg))
    gg = life.step(gg, W, H)

assert min(pops) == 7, f"expected min pop 7, got {min(pops)}"
assert max(pops) == 42, f"expected max pop 42, got {max(pops)}"
assert len(set(pops)) == 23, f"expected 23 distinct pops, got {len(set(pops))}"

gg2 = list(cyc_start_state)
for _ in range(period):
    gg2 = life.step(gg2, W, H)
assert tuple(gg2) == cyc_start_state, "did not return to start state after 'period' steps"

print("OK: seed 950001 on 11x11 -> transient 73, period 429 (odd), pop range 7-42, verified full-state cycle")
sys.exit(0)
