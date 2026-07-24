def gf2_rank(rows, ncols):
    """Rank of a list of int-bitmask rows over GF(2), each row < 2**ncols."""
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

def rule90_matrix_rows(n):
    """Circulant transition matrix rows for Rule 90 on a cyclic tape of width n."""
    return [(1 << ((i - 1) % n)) | (1 << ((i + 1) % n)) for i in range(n)]

def rule90_step(state, n):
    """Apply Rule 90 once to bitmask state on a cyclic tape of width n."""
    left = ((state << 1) | (state >> (n - 1))) & ((1 << n) - 1)
    right = ((state >> 1) | (state << (n - 1))) & ((1 << n) - 1)
    return left ^ right
