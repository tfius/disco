def step(word):
    s = word[0]
    rest = word[2:]
    prod = 'bb' if s == 'a' else 'a'
    return rest + prod

def run(word, budget):
    w = word
    for t in range(budget):
        if len(w) < 2:
            return (t, w)
        w = step(w)
    return (None, w)

for n in range(1, 501):
    w = 'a'*n
    budget = 2*n + 10
    t, final = run(w, budget)
    expected_t = 2*(n-1)
    assert t == expected_t, f"n={n}: expected halt at t={expected_t}, got t={t}"
    assert final == 'a', f"n={n}: expected final word 'a', got {final!r}"

print("OK: all n=1..500 halt at t=2(n-1) with final word 'a'")
