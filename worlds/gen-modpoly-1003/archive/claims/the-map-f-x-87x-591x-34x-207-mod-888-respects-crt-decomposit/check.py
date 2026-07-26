import sys

N = 888
def f(x):
    return (87*x**3 + 591*x**2 + 34*x + 207) % N

def find_cycles(fn, size):
    color = [0]*size
    cycles = []
    for start in range(size):
        if color[start] != 0:
            continue
        path = []
        x = start
        while color[x] == 0:
            color[x] = 1
            path.append(x)
            x = fn(x)
        if color[x] == 1:
            idx = path.index(x)
            cycles.append(tuple(path[idx:]))
        for p in path:
            color[p] = 2
    return cycles

# 1. mod-3 identity check
for x in range(N):
    assert f(x) % 3 == x % 3, f"f({x}) mod3 != x mod3"

# 2. induced maps well-defined on Z_8 and Z_37
def induced(modulus):
    table = {}
    for x in range(N):
        r = x % modulus
        val = f(x) % modulus
        if r in table:
            assert table[r] == val, f"induced map mod {modulus} not well-defined at {r}"
        else:
            table[r] = val
    return lambda r: table[r]

f8 = induced(8)
f37 = induced(37)

cyc8 = find_cycles(f8, 8)
cyc37 = find_cycles(f37, 37)

assert len(cyc8) == 1 and len(cyc8[0]) == 4, f"expected single 4-cycle in Z_8, got {cyc8}"
assert set(cyc8[0]) == {1,3,5,7}, f"Z_8 cycle mismatch: {cyc8[0]}"

assert len(cyc37) == 1 and len(cyc37[0]) == 4, f"expected single 4-cycle in Z_37, got {cyc37}"
assert set(cyc37[0]) == {4,12,32,15}, f"Z_37 cycle mismatch: {cyc37[0]}"

# 3. full graph cycle structure
cycles_full = find_cycles(f, N)
lengths = sorted(len(c) for c in cycles_full)
assert len(cycles_full) == 12, f"expected 12 cycles, got {len(cycles_full)}"
assert lengths == [4]*12, f"expected all cycles length 4, got {lengths}"

total_cycle_nodes = sum(len(c) for c in cycles_full)
assert total_cycle_nodes == 48 == 4*4*3, f"expected 48 cycle nodes, got {total_cycle_nodes}"

print("OK: CRT decomposition confirmed, 12 four-cycles, 48 cycle nodes, mod-3 identity.")
sys.exit(0)
