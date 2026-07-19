import sys, time
T0 = time.time()
import fixpath
life = fixpath.load('life')

def FS(cells, W, H):
    try: return life.from_set(cells, H)
    except TypeError: return life.from_set(cells, W, H)

def detect_order():
    cells = {(1,3)}
    try:
        g = FS(cells,4,2)
        if life.to_set(g,4,2) == cells: return 'rc'
    except Exception: pass
    return 'xy'
ORDER = detect_order()

def is_still(cells_rc, W, H):
    enc = cells_rc if ORDER=='rc' else {(c,r) for (r,c) in cells_rc}
    g = FS(enc, W, H)
    return life.to_set(life.step(g,W,H),W,H) == enc

# 1. stripe constructions attain floor(WH/2)
for W in range(2,17):
    for H in range(2,17,2):
        if not is_still({(r,c) for r in range(0,H,2) for c in range(W)}, W, H):
            print(f'FAIL: row stripes not still on {W}x{H}'); sys.exit(1)
for W in range(2,17,2):
    for H in range(3,16,2):
        if not is_still({(r,c) for c in range(0,W,2) for r in range(H)}, W, H):
            print(f'FAIL: col stripes not still on {W}x{H}'); sys.exit(1)

# 2. transfer DP: S(W,H) == floor(WH/2) for W=2..5, H=3..12
def dp_width(W, Hmax):
    S=1<<W
    wc=[[((r>>((x-1)%W))&1)+((r>>x)&1)+((r>>((x+1)%W))&1) for x in range(W)] for r in range(S)]
    POP=[bin(r).count('1') for r in range(S)]
    succ={}
    for a in range(S):
        wa=wc[a]
        for b in range(S):
            wb=wc[b]
            lst=[]
            for c in range(S):
                wcc=wc[c]; ok=True
                for x in range(W):
                    own=(b>>x)&1
                    n=wa[x]+wcc[x]+wb[x]-own
                    if (1 if (n==3 or (own and n==2)) else 0)!=own: ok=False; break
                if ok: lst.append(c)
            if lst: succ[(a,b)]=lst
    while True:
        has_in=set()
        for s,lst in succ.items():
            for c in lst: has_in.add((s[1],c))
        ns={}; changed=False
        for s,lst in succ.items():
            if s not in has_in: changed=True; continue
            l2=[c for c in lst if (s[1],c) in succ]
            if len(l2)!=len(lst): changed=True
            if l2: ns[s]=l2
            else: changed=True
        succ=ns
        if not changed: break
    res={}
    for s0 in list(succ):
        best={s0:0}
        for h in range(1,Hmax+1):
            nb={}
            for s,w in best.items():
                nw=w+POP[s[1]]
                for c in succ.get(s,()):
                    t=(s[1],c)
                    if nb.get(t,-1)<nw: nb[t]=nw
            best=nb
            if not best: break
            if h>=3 and s0 in best and res.get(h,-1)<best[s0]: res[h]=best[s0]
    return res

for W in range(2,6):
    res=dp_width(W,12)
    for H in range(3,13):
        v=res.get(H)
        if v != (W*H)//2:
            print(f'FAIL: S({W},{H})={v} != {(W*H)//2}'); sys.exit(1)

# 3. brute-force cross-check on tiny toruses (incl. H=2 where DP is invalid)
from itertools import combinations
def brute_max(W,H):
    N=W*H
    for p in range(N,0,-1):
        for comb in combinations(range(N),p):
            if is_still({(i//W,i%W) for i in comb},W,H): return p
    return 0
for (W,H) in [(2,2),(3,2),(3,3),(2,4),(3,4)]:
    if brute_max(W,H) != (W*H)//2:
        print(f'FAIL: brute S({W},{H}) != floor(WH/2)'); sys.exit(1)

print(f'OK: max still-life population = floor(WH/2) on all checked toruses ({time.time()-T0:.1f}s)')
sys.exit(0)
