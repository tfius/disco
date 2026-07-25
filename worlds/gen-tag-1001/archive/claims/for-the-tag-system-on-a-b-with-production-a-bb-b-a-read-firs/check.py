import sys
from itertools import product

def step(word):
    if len(word) < 2:
        return None
    first = word[0]
    rest = word[2:]
    prod = 'bb' if first == 'a' else 'a'
    return rest + prod

def run(word, budget=5000):
    seen = {}
    w = word
    for i in range(budget):
        if len(w) < 2:
            return ('halt', i, w)
        if w in seen:
            return ('cycle', i - seen[w], w)
        seen[w] = i
        w = step(w)
    return ('budget_exceeded', budget, w)

for L in range(1, 21):
    max_steps = 0
    for bits in product('ab', repeat=L):
        word = ''.join(bits)
        outcome, info, final = run(word)
        if outcome != 'halt':
            print(f"FAIL: word {word!r} outcome={outcome} info={info}")
            sys.exit(1)
        if info > 2*L - 2:
            print(f"FAIL: word {word!r} halted in {info} steps > bound {2*L-2}")
            sys.exit(1)
        max_steps = max(max_steps, info)
    predicted = 2*L - 2
    if max_steps != predicted:
        print(f"FAIL: L={L} max_steps={max_steps} != predicted={predicted}")
        sys.exit(1)

print("All checks passed for L=1..20: 100% halt, max steps == 2L-2")
sys.exit(0)
