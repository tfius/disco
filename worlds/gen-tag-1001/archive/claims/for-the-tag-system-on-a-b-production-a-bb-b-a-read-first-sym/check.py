import itertools

def step(word):
    if len(word) < 2:
        return None
    c = word[0]
    rest = word[2:]
    prod = 'bb' if c == 'a' else 'a'
    return rest + prod

def run(word, budget=200):
    seen = {}
    w = word
    for i in range(budget):
        seen[w] = i
        w2 = step(w)
        if w2 is None:
            return ('HALT', i + 1)
        if w2 in seen:
            return ('CYCLE', i + 1)
        w = w2
    return ('UNKNOWN', budget)

max_steps = 0
total = 0
for n in range(1, 17):
    for bits in itertools.product('ab', repeat=n):
        word = ''.join(bits)
        kind, steps = run(word)
        total += 1
        assert kind == 'HALT', f"non-halt found: {word!r} -> {kind}"
        if steps > max_steps:
            max_steps = steps

assert total == 2**17 - 2, f"expected {2**17-2} words, got {total}"
assert max_steps == 31, f"expected max_steps=31, got {max_steps}"
print("OK: all", total, "words length 1-16 halt, max_steps =", max_steps)
