def f_mod(y, p):
    return (66*y**3 + 181*y**2 + 6*y + 5) % p

def f(x, m=210):
    return (66*x**3 + 181*x**2 + 6*x + 5) % m

def component_tail_lengths(p):
    img = [f_mod(y,p) for y in range(p)]
    visited=[False]*p
    on_cycle=set()
    for start in range(p):
        if visited[start]: continue
        path=[]; pos={}
        x=start
        while not visited[x] and x not in pos:
            pos[x]=len(path); path.append(x); x=img[x]
        if x in pos:
            for n in path[pos[x]:]:
                on_cycle.add(n)
        for n in path: visited[n]=True
    tail = {}
    for y in range(p):
        steps=0
        x=y
        while x not in on_cycle:
            x=img[x]
            steps+=1
        tail[y]=steps
    return tail

primes=[2,3,5,7]
tails = {p: component_tail_lengths(p) for p in primes}

m=210
img=[f(x,m) for x in range(m)]
visited=[False]*m
on_cycle=set()
for start in range(m):
    if visited[start]: continue
    path=[]; pos={}
    x=start
    while not visited[x] and x not in pos:
        pos[x]=len(path); path.append(x); x=img[x]
    if x in pos:
        for n in path[pos[x]:]:
            on_cycle.add(n)
    for n in path: visited[n]=True

def brute_tail(y):
    steps=0
    x=y
    while x not in on_cycle:
        x=img[x]
        steps+=1
    return steps

for x in range(m):
    predicted = max(tails[p][x % p] for p in primes)
    actual = brute_tail(x)
    assert predicted == actual, f"mismatch at x={x}: predicted {predicted}, actual {actual}"

print("OK: all 210 tail lengths match max-of-component-tails formula")
