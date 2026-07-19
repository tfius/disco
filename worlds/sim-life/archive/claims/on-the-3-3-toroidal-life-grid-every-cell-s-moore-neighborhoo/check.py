import sys
import fixpath
w3 = fixpath.load('w3census')
t4 = fixpath.load('torus4')

fail = []
def req(cond, msg):
    if not cond:
        fail.append(msg)

T = w3.build_table()

# --- 3x3 exact image structure ---
N = 512
f = [w3.step_int(s, 3, T) for s in range(N)]
full = N - 1
img = set(f)
pred = {0, full} | {s for s in range(N) if bin(s).count('1') == 4}
req(img == pred, "3x3 image != {empty, all-alive} u pop4")
req(len(img) == 128, f"3x3 image size {len(img)} != 128")
req(N - len(img) == 384, f"3x3 GoE count {N-len(img)} != 384")
req(sum(1 for s in range(N) if bin(s).count('1') == 4) == 126, "pop4 count != 126")
req(all(f[s] == s for s in range(N) if bin(s).count('1') == 4), "not all pop4 are fixed points")
p3 = [s for s in range(N) if bin(s).count('1') == 3]
req(len(p3) == 84 and all(f[s] == full for s in p3), "pop3 states do not all map to all-alive")
req(f[full] == 0, "all-alive does not map to empty")
req(sum(1 for s in range(N) if bin(s).count('1') == 1 and s not in img) == 9,
    "3x3 pop-1 GoE count != 9")

# --- 3xH preimages of all-alive: exactly one live cell per row ---
for H in (4, 5):
    NH = 1 << (3 * H)
    fullH = NH - 1
    pre = set(s for s in range(NH) if w3.step_int(s, H, T) == fullH)
    onerow = set(s for s in range(NH)
                 if all(bin((s >> (3 * r)) & 7).count('1') == 1 for r in range(H)))
    req(pre == onerow, f"3x{H} preimage(all-alive) != one-live-cell-per-row set")
    req(len(pre) == 3 ** H, f"3x{H} preimage count {len(pre)} != {3**H}")

# --- 4x4: all-alive unreachable; pop-2 GoEs are exactly the diagonal pairs ---
f4 = t4.build_f(4)
N4 = len(f4)
req(N4 == 65536, f"torus4.build_f(4) size {N4} != 65536")
img4 = bytearray(N4)
for s in range(N4):
    img4[f4[s]] = 1
req(not img4[N4 - 1], "4x4 all-alive is reachable")

def disp(s):
    b = [i for i in range(16) if (s >> i) & 1]
    (r0, c0), (r1, c1) = ((x // 4, x % 4) for x in b)
    d = ((r1 - r0) % 4, (c1 - c0) % 4)
    return min(d, ((-d[0]) % 4, (-d[1]) % 4))

goe2, reach2 = {}, {}
for s in range(N4):
    if bin(s).count('1') != 2:
        continue
    d = disp(s)
    tgt = reach2 if img4[s] else goe2
    tgt[d] = tgt.get(d, 0) + 1
req(goe2 == {(1, 1): 16, (1, 3): 16}, f"4x4 pop-2 GoE classes {sorted(goe2.items())} != diagonals 16+16")
req(sum(goe2.values()) == 32, "4x4 pop-2 GoE count != 32")
req(all(bin(s).count('1') > 2 for s in range(N4) if not img4[s] and bin(s).count('1') < 2),
    "4x4 has a GoE of population < 2")
req(min((bin(s).count('1') for s in range(N4) if not img4[s]), default=99) == 2,
    "4x4 minimum GoE population != 2")
req((1, 1) not in reach2 and (1, 3) not in reach2, "some diagonal pop-2 pair is reachable")
req(sum(reach2.values()) == 120 - 32, f"4x4 reachable pop-2 count {sum(reach2.values())} != 88")

if fail:
    for m in fail:
        print("FAIL:", m)
    sys.exit(1)
print("OK: 3x3 image=128/GoE=384, 3x4/3x5 all-alive preimages = 3^H one-per-row, 4x4 pop-2 GoEs = 32 diagonals")
sys.exit(0)
