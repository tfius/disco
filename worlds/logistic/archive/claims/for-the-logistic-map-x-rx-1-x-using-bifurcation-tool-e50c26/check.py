import subprocess, sys

code = '''
from bifurcation_tools import auto_bisect_bifurcation
r1 = 3.0
r2 = auto_bisect_bifurcation(r1, 2)
r3 = auto_bisect_bifurcation(r2, 4)
r4 = auto_bisect_bifurcation(r3, 8)
delta1 = (r2 - r1) / (r3 - r2)
delta2 = (r3 - r2) / (r4 - r3)
print(f"{r2:.6f} {r3:.6f} {r4:.6f} {delta1:.6f} {delta2:.6f}")
'''

result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
assert result.returncode == 0, result.stderr
vals = result.stdout.split()
r2, r3, r4, delta1, delta2 = map(float, vals)

assert abs(r2 - 3.449139) < 1e-5, r2
assert abs(r3 - 3.543954) < 1e-5, r3
assert abs(r4 - 3.564355) < 1e-5, r4
assert abs(delta1 - 4.737007) < 1e-5, delta1
assert abs(delta2 - 4.647520) < 1e-5, delta2

assert delta2 < delta1, (delta1, delta2)
assert 4.6 <= delta1 <= 4.8, delta1
assert 4.6 <= delta2 <= 4.8, delta2
