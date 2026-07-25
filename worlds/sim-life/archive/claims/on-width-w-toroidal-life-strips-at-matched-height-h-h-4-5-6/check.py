import sys
sys.path.insert(0, "archive/tools")
import strip

expected = {
    3: {4: 340, 5: 1622, 6: 8008},
    4: {4: 17879, 5: 279165, 6: 3050114},
}

fracs = {}
for W, hs in expected.items():
    tbl = strip.next_row_table(W)
    fracs[W] = {}
    for H, exp_img in hs.items():
        img = strip.image_size(W, H, tbl)
        assert img == exp_img, f"W={W} H={H}: image={img} expected {exp_img}"
        total = 2**(W*H)
        fracs[W][H] = 1 - img/total

for H in (4,5,6):
    assert fracs[3][H] > fracs[4][H], f"H={H}: W=3 frac {fracs[3][H]} not > W=4 frac {fracs[4][H]}"

print("OK", fracs)
