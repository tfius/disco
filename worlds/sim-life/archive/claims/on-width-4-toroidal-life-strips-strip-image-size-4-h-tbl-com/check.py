import time
import strip

tbl = strip.next_row_table(4)
expected = {3: 340, 4: 17879, 5: 279165, 6: 3050114}

t0 = time.time()
for H, exp_img in expected.items():
    img = strip.image_size(4, H, tbl)
    assert img == exp_img, f"H={H}: expected image {exp_img}, got {img}"

fracs = {H: 1 - expected[H] / (2 ** (4 * H)) for H in expected}
# non-monotonic dip at H=4 relative to H=3, then rising through H=6
assert fracs[4] < fracs[3], f"expected dip at H=4: {fracs[4]} !< {fracs[3]}"
assert fracs[5] > fracs[4], f"expected rise H=4->5: {fracs[5]} !> {fracs[4]}"
assert fracs[6] > fracs[5], f"expected rise H=5->6: {fracs[6]} !> {fracs[5]}"

print("All exact image sizes and non-monotonic pattern confirmed.")
print("fracs:", fracs)
print(f"elapsed {time.time()-t0:.2f}s")
