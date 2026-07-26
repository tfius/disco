import itertools

def step(w):
    if len(w) < 2:
        return None
    c = w[0]
    rest = w[2:]
    prod = 'bb' if c == 'a' else 'a'
    return rest + prod

def run(w, budget=5000):
    seen = {}
    seen[w] = 0
    cur = w
    for i in range(1, budget+1):
        nxt = step(cur)
        if nxt is None:
            return ('halt', i)
        if nxt in seen:
            return ('cycle', i - seen[nxt])
        seen[nxt] = i
        cur = nxt
    return ('unknown', budget)

max_len = 18
for L in range(1, max_len+1):
    max_steps = 0
    max_word = None
    for bits in itertools.product('ab', repeat=L):
        w = ''.join(bits)
        outcome, val = run(w)
        assert outcome == 'halt', f"non-halt found: {w} -> {outcome}"
        if val > max_steps:
            max_steps = val
            max_word = w
    expected = 2*L - 1
    all_a = 'a'*L
    assert max_steps == expected, f"L={L}: max_steps={max_steps} != expected {expected}"
    assert max_word == all_a, f"L={L}: max achiever {max_word} != all-a word {all_a}"

print("verified: max_steps(L) = 2L-1, achieved by a^L, for L=1..18")
