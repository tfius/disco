"""R-pentomino / glider-census machinery for square toroidal Life grids.

run(N, cap) -> (transient, period, cycle_state)
gliders(g, N) -> list of 5-cell clusters translating (+-1,+-1) per 4 gens
census(Ns, cap) -> [(N, transient, period, k, bg_ok), ...]
"""
import fixpath
life = fixpath.load("life")

R_PENT = [(0,1),(0,2),(1,0),(1,1),(2,1)]

def place(pat, N, off=None):
    """Place a cell-list on an NxN torus; default offset = center-ish."""
    if off is None: off = (N//2-1, N//2-1)
    rows=[0]*N
    for (r,c) in pat: rows[(r+off[0])%N] |= 1<<((c+off[1])%N)
    return rows

def run(N, cap=8000, g0=None):
    """Iterate to first repeated state. Returns (transient, period, cycle_state)."""
    g = g0 if g0 is not None else place(R_PENT, N)
    seen={}; hist=[]
    for t in range(cap):
        k=tuple(g)
        if k in seen:
            s=seen[k]; return s, t-s, hist[s]
        seen[k]=t; hist.append(g); g=life.step(g,N,N)
    return None, None, None

def cells(g, N):
    out=set()
    for r in range(N):
        x=g[r]; c=0
        while x:
            if x&1: out.add((r,c))
            x>>=1; c+=1
    return out

def clusters(cs, N):
    """8-connected components on the torus."""
    cs=set(cs); out=[]
    while cs:
        s=cs.pop(); comp={s}; st=[s]
        while st:
            r,c=st.pop()
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    q=((r+dr)%N,(c+dc)%N)
                    if q in cs:
                        cs.discard(q); comp.add(q); st.append(q)
        out.append(comp)
    return out

def gliders(g, N):
    """5-cell clusters that reappear translated (+-1,+-1) after exactly 4 gens."""
    x=g; snaps=[]
    for _ in range(5):
        snaps.append(cells(x,N)); x=life.step(x,N,N)
    found=[]
    for c in clusters(snaps[0],N):
        if len(c)!=5: continue
        for (dr,dc) in ((1,1),(1,-1),(-1,1),(-1,-1)):
            if set(((r+dr)%N,(cc+dc)%N) for (r,cc) in c) <= snaps[4]:
                found.append(c); break
    return found

def background_period2(g, N, gl=None, halo=3):
    """True iff the non-glider background is unchanged after 2 gens."""
    if gl is None: gl = gliders(g,N)
    allg=set().union(*gl) if gl else set()
    x=g; snaps=[]
    for _ in range(3):
        snaps.append(cells(x,N)); x=life.step(x,N,N)
    def near(p):
        for (r,c) in allg:
            dr=min((p[0]-r)%N,(r-p[0])%N); dc=min((p[1]-c)%N,(c-p[1])%N)
            if max(dr,dc)<=halo: return True
        return False
    a={p for p in snaps[0] if not near(p)}
    b={p for p in snaps[2] if not near(p)}
    return a==b

def census(Ns, cap=8000):
    """[(N, transient, period, glider_count, background_period2_ok), ...]"""
    out=[]
    for N in Ns:
        tr,per,g0 = run(N,cap)
        if tr is None:
            out.append((N,None,None,None,None)); continue
        gl = gliders(g0,N)
        out.append((N,tr,per,len(gl),background_period2(g0,N,gl)))
    return out
