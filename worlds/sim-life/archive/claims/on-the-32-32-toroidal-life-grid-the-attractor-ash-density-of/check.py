import sys
import life

W = H = 32
N = W * H
CAP = 4096

def settle(seed, p):
    g = life.soup(seed, W, H, p)
    seen = {}
    pops = []
    t = 0
    while t < CAP:
        key = tuple(g)
        if key in seen:
            s = seen[key]
            cyc = pops[s:]
            return t - s, sum(cyc) / len(cyc)   # period, mean cycle pop
        seen[key] = t
        pops.append(life.pop(g))
        g = life.step(g, W, H)
        t += 1
    return None, None                            # did not settle

fail = []

# (1) plateau: p in {0.35,0.45,0.55}, 20 seeds each
means = {}
for p in (0.35, 0.45, 0.55):
    dens = []
    for k in range(20):
        per, mp = settle(930000 + int(p * 100) * 100 + k, p)
        if per is None:
            fail.append(f"unsettled plateau run p={p} k={k}")
            continue
        dens.append(mp / N)
    m = sum(dens) / len(dens)
    means[p] = m
    if not (0.020 <= m <= 0.040):
        fail.append(f"plateau mean out of [0.020,0.040]: p={p} m={m:.4f}")
vals = list(means.values())
if max(vals) - min(vals) >= 0.008:
    fail.append(f"plateau spread too wide: {max(vals)-min(vals):.4f}")

# (2) death cliff: seeds 920000 + i*100 + k, p = i/50
def cliff(i):
    p = i / 50
    emp, dens = 0, []
    for k in range(20):
        per, mp = settle(920000 + i * 100 + k, p)
        if per is None:
            fail.append(f"unsettled cliff run p={p} k={k}")
            continue
        dens.append(mp / N)
        if mp == 0:
            emp += 1
    return emp / 20, sum(dens) / len(dens)

fe70, md70 = cliff(35)   # p=0.70
fe76, _ = cliff(38)      # p=0.76
fe78, _ = cliff(39)      # p=0.78
fe86, _ = cliff(43)      # p=0.86

if fe70 != 0.0:
    fail.append(f"p=0.70 frac_empty={fe70} (expected 0)")
if md70 <= 0.015:
    fail.append(f"p=0.70 mean density {md70:.4f} <= 0.015")
if fe76 >= 0.5:
    fail.append(f"p=0.76 frac_empty={fe76} (expected < 0.5)")
if fe78 < 0.5:
    fail.append(f"p=0.78 frac_empty={fe78} (expected >= 0.5)")
if fe86 != 1.0:
    fail.append(f"p=0.86 frac_empty={fe86} (expected 1.0)")

for f in fail:
    print("FAIL:", f)
print("checks passed" if not fail else f"{len(fail)} failures")
sys.exit(0 if not fail else 1)
