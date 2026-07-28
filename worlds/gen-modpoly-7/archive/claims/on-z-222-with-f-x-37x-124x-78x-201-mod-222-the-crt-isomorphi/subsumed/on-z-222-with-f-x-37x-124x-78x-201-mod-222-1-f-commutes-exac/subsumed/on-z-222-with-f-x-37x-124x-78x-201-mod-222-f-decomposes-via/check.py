def f(x):
    return (37*x**3 + 124*x**2 + 78*x + 201) % 222

N = 222

# --- brute force full graph stats ---
from collections import Counter
img = [f(x) for x in range(N)]
indeg = Counter(img)
image_size = len(indeg)
indeg_dist = Counter(indeg.values())
fixed = [x for x in range(N) if f(x) == x]

state = [0]*N
cycles = []
for start in range(N):
    if state[start] != 0:
        continue
    path = []
    seen = {}
    x = start
    while state[x] == 0:
        seen[x] = len(path)
        path.append(x)
        state[x] = 1
        x = f(x)
    if state[x] == 1:
        idx = seen[x]
        cycles.append(frozenset(path[idx:]))
    for node in path:
        state[node] = 2
cycles = set(cycles)

assert image_size == 76, image_size
assert dict(indeg_dist) == {1:2, 2:38, 4:36}, dict(indeg_dist)
assert N - image_size == 146
assert len(fixed) == 0
assert cycles == {frozenset({150,39}), frozenset({12,123})}, cycles
assert all(len(c) == 2 for c in cycles)

# --- CRT decomposition check ---
def f2(a): return (a+1) % 2
def f3(b): return (b*b + b) % 3
def f37(c): return (13*c*c + 4*c + 16) % 37

for x in range(N):
    assert f(x) % 2 == f2(x % 2)
    assert f(x) % 3 == f3(x % 3)
    assert f(x) % 37 == f37(x % 37)

# f2 bijection, single 2-cycle
assert sorted(f2(a) for a in range(2)) == [0,1]
assert f2(0) == 1 and f2(1) == 0

# f3: unique fixed point 0, rest reach it
assert [b for b in range(3) if f3(b)==b] == [0]
assert f3(1) == 2 and f3(2) == 0

# f37: exactly fixed points {2,12}, image size 19, indeg dist {1:1,2:18}
fixed37 = [c for c in range(37) if f37(c) == c]
assert fixed37 == [2, 12], fixed37
img37 = [f37(c) for c in range(37)]
indeg37 = Counter(img37)
assert len(indeg37) == 19
assert dict(Counter(indeg37.values())) == {1:1, 2:18}

# every point of f37 eventually reaches 2 or 12
for start in range(37):
    x = start
    for _ in range(50):
        x = f37(x)
    assert x in (2, 12)

# in-degree formula: indeg(y) = indeg3(y%3) * indeg37(y%37)
indeg3 = Counter(f3(b) for b in range(3))
for y in range(N):
    pred = indeg3.get(y % 3, 0) * indeg37.get(y % 37, 0)
    assert pred == indeg.get(y, 0), (y, pred, indeg.get(y,0))

print("ALL CHECKS PASSED")
