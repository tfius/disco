import ca_rule as R
RULE = R.RULE
assert R.validate_rule(RULE)

L = 200

def make_tape(positions, val=1):
    t=[0]*L
    for p in positions: t[p]=val
    return t

def clusters(tape):
    cl=[]; cur=[]
    for v in tape:
        if v!=0: cur.append(v)
        else:
            if cur: cl.append(tuple(cur)); cur=[]
    if cur: cl.append(tuple(cur))
    return cl

# --- part 1: ballistic velocity +1 for single defect ---
t = make_tape([100])
cur = t[:]
positions = []
for step in range(120):
    nz = [i for i,v in enumerate(cur) if v!=0]
    assert len(nz) == 1, f"expected exactly one nonzero cell at step {step}, got {nz}"
    assert cur[nz[0]] == 1
    positions.append(nz[0])
    cur = R.step(cur, RULE)

for k in range(len(positions)):
    expected = (100 + k) % L
    assert positions[k] == expected, f"step {k}: expected pos {expected}, got {positions[k]}"

# --- part 2: gap-dependent merge behavior ---
T = 150
for gap in range(1, 8):
    t0 = make_tape([100, 100+gap])
    cur = t0[:]
    for _ in range(T):
        cur = R.step(cur, RULE)
    cl = clusters(cur)
    n_nonzero = sum(1 for v in cur if v != 0)
    if gap <= 2:
        assert n_nonzero < 2, f"gap={gap}: expected merge (fewer than 2 nonzero cells), got {cl}"
    else:
        assert n_nonzero == 2 and len(cl) == 2, f"gap={gap}: expected 2 separate defects, got {cl}"
        # check both still shape (1,) and relative spacing preserved
        idxs = sorted(i for i,v in enumerate(cur) if v != 0)
        d = (idxs[1]-idxs[0]) % L
        assert d == gap, f"gap={gap}: relative spacing changed to {d}"

# --- fresh instance: gap=3 tested over a longer horizon to confirm no eventual interaction ---
t0 = make_tape([50, 53])
cur = t0[:]
for _ in range(500):
    cur = R.step(cur, RULE)
cl = clusters(cur)
assert len(cl) == 2 and cl == [(1,), (1,)], f"gap=3 long-run: expected persistent separation, got {cl}"

print("OK: single defect ballistic v=+1, merge iff gap<=2, else permanent separation")
