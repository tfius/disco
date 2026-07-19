import fixpath, sys
strip = fixpath.load('strip')
life = fixpath.load('life')

EXPECT = {(2,3):10,(2,4):89,(2,5):293,(2,6):862,(2,7):3251,(2,8):10961,(2,9):36058,
          (3,3):128,(3,4):340,(3,5):1622,(3,6):8008,(3,7):38012,(3,8):178072,
          (4,4):17879,(4,5):279165,(4,6):3050114,(5,5):8520996}
tbls = {}
def tbl(W):
    if W not in tbls: tbls[W] = strip.next_row_table(W)
    return tbls[W]
for (W,H),v in sorted(EXPECT.items()):
    n = strip.image_size(W,H,tbl(W))
    assert n == v, f"image({W},{H})={n} expected {v}"

# transpose symmetry
assert strip.image_size(5,4,tbl(5)) == EXPECT[(4,5)]
assert strip.image_size(4,3,tbl(4)) == EXPECT[(3,4)]
assert strip.image_size(6,4,tbl(6)) == EXPECT[(4,6)]

# H=2 unsupported: raises IndexError
try:
    strip.image_size(4,2,tbl(4)); assert False, "H=2 should raise"
except IndexError:
    pass

# brute-force cross-check on 3x4
imgs = set()
for s in range(1 << 12):
    live = {(x,y) for y in range(4) for x in range(3) if (s>>(y*3+x))&1}
    g = life.step(life.from_set(live,4), 3, 4)
    imgs.add(frozenset(life.to_set(g,3,4)))
assert len(imgs) == EXPECT[(3,4)]

# non-monotonicity of per-cell ratio
r = lambda W,H: EXPECT[(W,H)]**(1.0/(W*H))
assert r(3,8) < r(2,9) < r(4,5), "width-3 anomaly: W=3 below W=2 below W=4"
assert r(4,6) < r(4,5), "H-dip at 4x6"
assert all(r(W,H) < 2 for (W,H) in EXPECT)
sys.exit(0)
