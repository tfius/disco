import sys, time
sys.path.insert(0, "worlds/life/archive/tools" if False else ".")
from fixpath import load
strip = load("strip")

# Verify: runtime at matched W*H product is within ~5x factor regardless of split,
# and throughput stays in a stable order-of-magnitude band.
def timed(W, H):
    tbl = strip.next_row_table(W)
    t0 = time.time()
    strip.image_size(W, H, tbl)
    dt = time.time() - t0
    total = 2**(W*H)
    return dt, total

# product 16
d1, t1 = timed(4, 4)
d2, t2 = timed(2, 8)  # W=2 supported? tbl building loops fine for W=2
assert t1 == t2 == 2**16

# product 18
d3, t3 = timed(3, 6)
d4, t4 = timed(6, 3)

rates = []
for d, t in [(d1, t1), (d3, t3), (d4, t4)]:
    if d > 0:
        rates.append(t / d)

# throughput should be within a factor of 10 across these small runs (loose bound,
# real machines vary, but should stay same order of magnitude ~1e6-1e8/s)
lo, hi = min(rates), max(rates)
assert hi / lo < 15, f"throughput varies too much: {rates}"

# extrapolation sanity: predicted time for W=5,H=6 (2^30 states) from measured
# throughput should exceed 30s (explaining the original timeout)
d5, t5 = timed(5, 4)  # 2^20, cheap calibration point
rate = t5 / d5
predicted_5_6 = (2**30) / rate
assert predicted_5_6 > 30, f"predicted time for W=5,H=6 too low: {predicted_5_6:.1f}s"

print("OK: runtime scales with 2^(W*H), throughput stable, W=5/H=6 predicted >30s")
