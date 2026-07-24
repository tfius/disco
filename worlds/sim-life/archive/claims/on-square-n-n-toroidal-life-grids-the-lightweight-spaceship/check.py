import sys
import life

def lwss_cells(r0, c0):
    base = [(0,1),(0,4),(1,0),(2,0),(2,4),(3,0),(3,1),(3,2),(3,3)]
    return {(r0+r, c0+c) for r, c in base}

def match_translation(orig, cells, N):
    orig = list(orig)
    for dr in range(N):
        for dc in range(N):
            translated = {((r+dr) % N, (c+dc) % N) for r, c in orig}
            if translated == cells:
                return (dr, dc)
    return None

def test_N(N, periods=10):
    orig = lwss_cells(0, 0)
    g = life.from_set(orig, N)
    base_off = None
    for k in range(1, periods+1):
        for _ in range(4):
            g = life.step(g, N, N)
        cells = life.to_set(g, N, N)
        off = match_translation(orig, cells, N)
        if off is None or off == (0, 0):
            return False, base_off
        if base_off is None:
            base_off = off
        else:
            expected = ((base_off[0]*k) % N, (base_off[1]*k) % N)
            if off != expected:
                return False, base_off
    return True, base_off

def predicted_pass(N):
    if N >= 21:
        return True
    if N >= 11 and N % 2 == 1:
        return True
    return False

fail_band_evens = {12, 14, 16, 18, 20}
errors = []

for N in range(5, 51):
    ok, base_off = test_N(N)
    expected = predicted_pass(N)
    if ok != expected:
        errors.append(f"N={N}: expected pass={expected}, got {ok}")
        continue
    if ok and base_off != (0, N - 2):
        errors.append(f"N={N}: passed but base_off={base_off}, expected (0,{N-2})")

if errors:
    print("MISMATCHES:")
    for e in errors:
        print(" ", e)
    sys.exit(1)

print("All N in 5..50 match predicted pass/fail pattern and base_off=(0,N-2) where passing.")
sys.exit(0)
