import sys

def step(word):
    first = word[0]
    rest = word[2:]
    prod = 'bb' if first == 'a' else 'a'
    return rest + prod, first

# Part 1: length semantics is exact arithmetic fact, verify on random/edge samples
import random
random.seed(1001)
for _ in range(2000):
    L = random.randint(2, 20)
    word = ''.join(random.choice('ab') for _ in range(L))
    new_word, first = step(word)
    if first == 'a':
        assert len(new_word) == len(word), f"a-read should preserve length: {word}"
    else:
        assert len(new_word) == len(word) - 1, f"b-read should decrease length by 1: {word}"

# Part 2: exhaustive halting + max halt-time formula for L=1..14
def simulate_certified(word, budget):
    seen = set()
    w = word
    for i in range(budget):
        if len(w) < 2:
            return ('HALT', i)
        if w in seen:
            return ('CYCLE', i)
        seen.add(w)
        w, _ = step(w)
    return ('EXCEEDED', budget)

for L in range(1, 15):
    budget = 4 * L + 50
    max_time = -1
    for mask in range(2**L):
        word = ''.join('a' if (mask >> k) & 1 else 'b' for k in range(L))
        status, t = simulate_certified(word, budget)
        if status != 'HALT':
            print(f"FAIL: L={L} word={word} status={status}")
            sys.exit(1)
        if t > max_time:
            max_time = t
    expected = 2 * L - 2 if L >= 2 else 0
    if max_time != expected:
        print(f"FAIL: L={L} max_time={max_time} expected={expected}")
        sys.exit(1)

print("All checks passed: length non-increasing, all words halt, max halt-time = 2L-2.")
sys.exit(0)
