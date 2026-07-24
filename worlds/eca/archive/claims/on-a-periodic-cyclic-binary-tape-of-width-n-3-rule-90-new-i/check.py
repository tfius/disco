import sys

def gf2_rank(rows, ncols):
    rows = rows[:]
    rank = 0
    for col in range(ncols):
        pivot = None
        for r in range(rank, len(rows)):
            if (rows[r] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for r in range(len(rows)):
            if r != rank and (rows[r] >> col) & 1:
                rows[r] ^= rows[rank]
        rank += 1
    return rank

def kernel_dim(n):
    rows = [(1 << ((i - 1) % n)) | (1 << ((i + 1) % n)) for i in range(n)]
    return n - gf2_rank(rows, n)

for n in range(3, 97):
    expected = 1 if n % 2 == 1 else 2
    actual = kernel_dim(n)
    if actual != expected:
        print(f"FAIL N={n} kernel_dim={actual} expected={expected}")
        sys.exit(1)

print("all N=3..96 match parity rule")
sys.exit(0)
