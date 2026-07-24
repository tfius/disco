def rule150_step(state, n):
    new = 0
    for i in range(n):
        l = (state >> ((i-1) % n)) & 1
        c = (state >> i) & 1
        r = (state >> ((i+1) % n)) & 1
        bit = l ^ c ^ r
        new |= (bit << i)
    return new

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
