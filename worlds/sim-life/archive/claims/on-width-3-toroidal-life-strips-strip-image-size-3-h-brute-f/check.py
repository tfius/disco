import sys
from fixpath import load
strip = load("strip")

sizes = {}
for H in range(3, 9):
    sizes[H] = strip.image_size(3, H)

ratios = {H: sizes[H]/sizes[H-1] for H in range(4, 9)}

# ratio must be strictly below 8 for all computed H
for H, r in ratios.items():
    if not (r < 8):
        print(f"FAIL: ratio at H={H} is {r}, not < 8")
        sys.exit(1)

# monotonic decrease for H=6,7,8
seq = [ratios[6], ratios[7], ratios[8]]
if not (seq[0] > seq[1] > seq[2]):
    print(f"FAIL: ratios not monotonically decreasing: {seq}")
    sys.exit(1)

# ratios should be in a reasonable band around the claimed ~4.6-5.0
for H in (6, 7, 8):
    if not (4.4 <= ratios[H] <= 5.1):
        print(f"FAIL: ratio at H={H} = {ratios[H]} outside [4.4,5.1]")
        sys.exit(1)

print("OK", ratios)
sys.exit(0)
