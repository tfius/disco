import strip
import life

W = 4
tbl = strip.next_row_table(W)

def pack(g, W, H):
    s = 0
    for y in range(H):
        s = (s << W) | g[y]
    return s

def brute_image(W, H):
    N = W * H
    total = 1 << N
    seen = set()
    for st in range(total):
        live = [(i % W, i // W) for i in range(N) if (st >> i) & 1]
        g = life.from_set(live, H)
        g2 = life.step(g, W, H)
        seen.add(pack(g2, W, H))
    return len(seen)

# H < 3 must raise IndexError
try:
    strip.image_size(W, 2, tbl)
    raise SystemExit("expected IndexError for H=2, got none")
except IndexError:
    pass

expected = {3: 340, 4: 17879, 5: 279165}
for H, exp in expected.items():
    f = strip.image_size(W, H, tbl)
    assert f == exp, f"H={H}: strip.image_size={f} != expected {exp}"
    if H <= 4:
        b = brute_image(W, H)
        assert b == f, f"H={H}: brute={b} != fast={f}"

print("OK: all checks passed")
