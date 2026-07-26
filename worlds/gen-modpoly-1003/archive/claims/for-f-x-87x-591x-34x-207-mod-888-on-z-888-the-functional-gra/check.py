def f(x):
    return 87*x**3 + 591*x**2 + 34*x + 207

def analyze(m):
    nxt = [f(x) % m for x in range(m)]
    tail = [None]*m
    cyc_id = [-1]*m
    cycles = []
    visited = [0]*m
    for start in range(m):
        if visited[start]:
            continue
        path=[]
        x=start
        while not visited[x]:
            visited[x]=1
            path.append(x)
            x=nxt[x]
        if cyc_id[x]==-1:
            idx=path.index(x)
            cyc=path[idx:]
            cid=len(cycles)
            cycles.append(cyc)
            for c in cyc:
                cyc_id[c]=cid
                tail[c]=0
        cid = cyc_id[x]
        for node in reversed(path):
            if tail[node] is not None:
                continue
            nx = nxt[node]
            tail[node] = tail[nx]+1
            cyc_id[node]=cid
    return nxt, cycles, cyc_id, tail

nxt8, cyc8, cid8, tail8 = analyze(8)
nxt37, cyc37, cid37, tail37 = analyze(37)
nxt3, cyc3, cid3, tail3 = analyze(3)

# mod3: all fixed points
assert cyc3 == [[0],[1],[2]] or sorted(len(c) for c in cyc3)==[1,1,1], "mod3 not all fixed points"
assert all(t==0 for t in tail3), "mod3 tails not all zero"

# mod8: single 4-cycle {7,5,3,1}, others tail 1
assert len(cyc8)==1 and sorted(cyc8[0])==[1,3,5,7], f"mod8 cycle structure wrong: {cyc8}"
for x in range(8):
    if x in cyc8[0]:
        assert tail8[x]==0
    else:
        assert tail8[x]==1, f"mod8 tail for {x} not 1: {tail8[x]}"

# mod37: single 4-cycle {4,12,32,15}
assert len(cyc37)==1 and sorted(cyc37[0])==[4,12,15,32], f"mod37 cycle structure wrong: {cyc37}"
assert max(tail37) == 7, f"mod37 max tail not 7: {max(tail37)}"
assert min(t for i,t in enumerate(tail37) if i not in cyc37[0]) >= 0

# full graph on Z_888
nxt888, cyc888, cid888, tail888 = analyze(888)
assert len(cyc888)==12, f"expected 12 cycles, got {len(cyc888)}"
assert all(len(c)==4 for c in cyc888), f"not all cycles length 4: {[len(c) for c in cyc888]}"
total_cyclic = sum(len(c) for c in cyc888)
assert total_cyclic == 48, f"expected 48 cyclic points, got {total_cyclic}"
assert max(tail888) == 7, f"expected max tail 7, got {max(tail888)}"

# max-formula check for every point
mismatches = 0
for x in range(888):
    predicted = max(tail8[x%8], tail37[x%37])
    if predicted != tail888[x]:
        mismatches += 1
assert mismatches == 0, f"{mismatches} mismatches in tail max-formula"

print("ALL CHECKS PASSED")
