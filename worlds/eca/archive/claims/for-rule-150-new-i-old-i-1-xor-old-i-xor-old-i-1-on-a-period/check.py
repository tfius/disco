from eca_rule150_gf2 import kernel_dim

bad = []
for n in range(3, 101):
    d = kernel_dim(n)
    expected = 2 if n % 3 == 0 else 0
    if d != expected:
        bad.append((n, d, expected))

if bad:
    print("FAIL mismatches:", bad)
    raise SystemExit(1)

print("OK: kernel_dim(n)==2 iff 3|n, else 0, for n=3..100")
raise SystemExit(0)
