import sys
import life
from collections import Counter

W = H = 16
CAP = 3000

def run(seed):
    g = life.soup(seed, W, H, 0.5)
    seen = {}
    t = 0
    while t <= CAP:
        key = tuple(g)
        if key in seen:
            return seen[key], t - seen[key], g
        seen[key] = t
        g = life.step(g, W, H)
        t += 1
    return None, None, g

def cycle_states(g, period):
    states = [tuple(g)]
    cur = list(g)
    for _ in range(period - 1):
        cur = life.step(cur, W, H)
        states.append(tuple(cur))
    return states

def glider_plus_ash(g, period):
    states = cycle_states(g, period)
    static = set()
    for y in range(H):
        for x in range(W):
            series = [(states[t][y] >> x) & 1 for t in range(period)]
            if all(series[t] == series[(t + 2) % period] for t in range(period)):
                static.add((x, y))
    def movset(t):
        return frozenset((x, y) for y in range(H) for x in range(W)
                         if (states[t][y] >> x) & 1 and (x, y) not in static)
    if any(len(movset(t)) != 5 for t in range(period)):
        return False
    m0, m4 = movset(0), movset(4)
    shift = None
    for dy in (1, H - 1):
        for dx in (1, W - 1):
            if frozenset(((x + dx) % W, (y + dy) % H) for x, y in m0) == m4:
                shift = (dx, dy)
    if shift is None:
        return False
    return all(
        frozenset(((x + shift[0]) % W, (y + shift[1]) % H) for x, y in movset(t)) == movset(t + 4)
        for t in range(0, period - 4, 4))

hist = Counter()
ratios_ok = True
p64_states = []
for base in (700000, 710000):
    bh = Counter()
    for s in range(150):
        tr, per, g = run(base + s)
        if per is None or tr > 3000:
            sys.exit(1)          # must resolve within cap
        bh[per] += 1
        if per == 64:
            p64_states.append(g)
    if not bh[1] > bh[2]:
        ratios_ok = False        # fixed points beat period-2 in each batch
    hist += bh

if dict(hist) != {1: 183, 2: 107, 64: 9, 32: 1}:
    sys.exit(2)                  # exact period spectrum
if not ratios_ok:
    sys.exit(3)
if not all(glider_plus_ash(tuple(g), 64) for g in p64_states):
    sys.exit(4)                  # every period-64 = glider + static ash
sys.exit(0)
