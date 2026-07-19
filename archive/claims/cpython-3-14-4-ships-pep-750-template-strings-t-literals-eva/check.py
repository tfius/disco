import sys

def fail(msg):
    print("FAIL:", msg); sys.exit(1)

try:
    from string import templatelib
except ImportError:
    fail("no string.templatelib")

pub = {n for n in dir(templatelib) if not n.startswith('_')}
if pub != {'Template', 'Interpolation', 'convert'}:
    fail(f"module surface {pub}")

t = eval('t"x={1+1}"')
if type(t) is not templatelib.Template:
    fail("not Template")
if t.strings != ('x=', ''):
    fail(f"strings {t.strings}")
if len(t.strings) != len(t.interpolations) + 1:
    fail("strings/interpolations length invariant")
i = t.interpolations[0]
if (i.value, i.expression, i.conversion, i.format_spec) != (2, '1+1', None, ''):
    fail(f"interp {i}")
if t.values != (2,):
    fail(f"values {t.values}")

# iteration skips empty static strings
parts = list(t)
if parts[0] != 'x=' or len(parts) != 2 or not isinstance(parts[1], templatelib.Interpolation):
    fail(f"iter {parts}")

# eager evaluation
try:
    eval('t"{no_such_name_xyz}"')
    fail("lazy evaluation: no NameError")
except NameError:
    pass

# conversion / format_spec
c = eval('t"{42!r:>5}"').interpolations[0]
if (c.conversion, c.format_spec) != ('r', '>5'):
    fail(f"conv/spec {c.conversion!r} {c.format_spec!r}")

# concatenation rules
t2 = eval('t"y={3}"')
cat = t + t2
if cat.strings != ('x=', 'y=', '') or [ip.value for ip in cat.interpolations] != [2, 3]:
    fail(f"T+T {cat.strings}")
for expr in ('t + "s"', '"s" + t'):
    try:
        eval(expr)
        fail(f"{expr} did not raise")
    except TypeError:
        pass

# implicit concat merges; str/f-string mixing is SyntaxError
if eval('t"a" t"b{1}"').strings != ('ab', ''):
    fail("implicit t t concat")
for src in ('f"a" t"b{1}"', '"a" t"b{1}"'):
    try:
        eval(src)
        fail(f"{src} compiled")
    except SyntaxError:
        pass

# str() does not render values
if str(t) == 'x=2':
    fail("str(t) rendered values")
if 'Template' not in str(t):
    fail(f"str(t) unexpected: {str(t)[:60]}")

print("OK")
sys.exit(0)
