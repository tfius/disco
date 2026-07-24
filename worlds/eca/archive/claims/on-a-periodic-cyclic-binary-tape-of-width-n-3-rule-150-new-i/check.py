import sys

def kernel_dim(n):
    rows = []
    for i in range(n):
        row = 0
        row |= 1 << ((i-1) % n)
        row |= 1 << i
        row |= 1 << ((i+1) % n)
        rows.append(row)
    rank = 0
    work = rows[:]
    for col in range(n):
        piv = None
        for r in range(rank, len(work)):
            if (work[r] >> col) & 1:
                piv = r
                break
        if piv is None:
            continue
        work[rank], work[piv] = work[piv], work[rank]
        for r in range(len(work)):
            if r != rank and (work[r] >> col) & 1:
                work[r] ^= work[rank]
        rank += 1
    return n - rank

def rule150_step(state, n):
    new = 0
    for i in range(n):
        l = (state >> ((i-1) % n)) & 1
        c = (state >> i) & 1
        r = (state >> ((i+1) % n)) & 1
        bit = l ^ c ^ r
        new |= (bit << i)
    return new

import random
for n in [4, 7, 10, 13]:
    if rule150_step(0, n) != 0:
        sys.exit(1)
    for _ in range(20):
        s = random.getrandbits(n)
        t = random.getrandbits(n)
        if rule150_step(s ^ t, n) != (rule150_step(s, n) ^ rule150_step(t, n)):
            sys.exit(1)

for n in range(3, 101):
    kdim = kernel_dim(n)
    expected_singular = (n % 3 == 0)
    actual_singular = kdim > 0
    if expected_singular != actual_singular:
        sys.exit(1)
    if actual_singular and kdim != 2:
        sys.exit(1)

sys.exit(0)
