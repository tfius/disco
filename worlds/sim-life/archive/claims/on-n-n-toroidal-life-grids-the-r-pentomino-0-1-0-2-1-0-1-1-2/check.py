import sys, fixpath
life = fixpath.load("life")

R = [(0,1),(0,2),(1,0),(1,1),(2,1)]
GLIDER = [108,110,112,116,125,145]
PLAIN  = [100,113,120,141,150]

def make(N):
    rows=[0]*N; o=N//2-1
    for (r,c) in R: rows[(r+o)%N] |= 1<<((c+o)%N)
    return rows

def run(N, cap=8000):
    g=make(N); seen={}; hist=[]
    for t in range(cap):
        k=tuple(g)
        if k in seen:
            s=seen[k]; return t-s, hist[s]
        seen[k]=t; hist.append(g); g=life.step(g,N,N)
    return None, None

def cells(g,N):
    out=set()
    for r in range(N):
        x=g[r]; c=0
        while x:
            if x&1: out.add((r,c))
            x>>=1; c+=1
    return out

def clusters(cs,N):
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

def analyze(g0,N):
    g=g0; snaps=[]
    for _ in range(5):
        snaps.append(cells(g,N)); g=life.step(g,N,N)
    gl=[]
    for c in clusters(snaps[0],N):
        if len(c)!=5: continue
        for (dr,dc) in ((1,1),(1,-1),(-1,1),(-1,-1)):
            if set(((r+dr)%N,(cc+dc)%N) for (r,cc) in c) <= snaps[4]:
                gl.append(c); break
    allg=set().union(*gl) if gl else set()
    def near(p):
        for (r,c) in allg:
            dr=min((p[0]-r)%N,(r-p[0])%N); dc=min((p[1]-c)%N,(c-p[1])%N)
            if max(dr,dc)<=3: return True
        return False
    a={p for p in snaps[0] if not near(p)}
    b={p for p in snaps[2] if not near(p)}
    return len(gl), a==b

fail=[]
for N in GLIDER+PLAIN:
    per,g0 = run(N)
    if per is None:
        fail.append((N,"nocycle")); continue
    k,bg = analyze(g0,N)
    if (per>2) != (k>=1):
        fail.append((N,"biconditional",per,k))
    if k>=1 and per != 4*N:
        fail.append((N,"period!=4N",per))
    if k>=1 and not bg:
        fail.append((N,"bg not period<=2"))
    if N in GLIDER and k<1:
        fail.append((N,"expected glider",per,k))
    if N in PLAIN and (k!=0 or per>2):
        fail.append((N,"expected plain",per,k))

if fail:
    print("FAIL:", fail); sys.exit(1)
print("OK: glider<=>period==4N verified on", GLIDER+PLAIN)
sys.exit(0)
