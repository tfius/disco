from funcgraph_analyze import analyze, crt_predict
import math

primes = [2,3,5,7]
comp = {p: analyze(p) for p in primes}

# check per-prime facts
tail2,cyc2 = comp[2]
assert cyc2 == [2,2], f"mod2 cyc {cyc2}"
assert tail2 == [0,0], f"mod2 tail {tail2}"

tail3,cyc3 = comp[3]
assert cyc3 == [2,2,2], f"mod3 cyc {cyc3}"
assert tail3 == [0,1,0], f"mod3 tail {tail3}"

tail5,cyc5 = comp[5]
assert cyc5 == [1,1,1,1,1], f"mod5 cyc {cyc5}"
assert tail5 == [0,2,1,1,0], f"mod5 tail {tail5}"

tail7,cyc7 = comp[7]
assert cyc7 == [2,1,1,1,1,2,1], f"mod7 cyc {cyc7}"
assert tail7 == [0,2,0,2,1,0,1], f"mod7 tail {tail7}"

# full graph vs CRT prediction
full_tail, full_cyc = analyze(210)
pred_tail, pred_cyc = crt_predict(210, primes, comp)

assert full_tail == pred_tail, "tail mismatch"
assert full_cyc == pred_cyc, "cyc mismatch"

# derived global facts
assert set(full_cyc) == {2}, f"expected only cycle length 2, got {set(full_cyc)}"
assert max(full_tail) == 2, f"expected max tail 2, got {max(full_tail)}"

print("OK: CRT product structure confirmed, unique cycle length 2, max tail 2")
