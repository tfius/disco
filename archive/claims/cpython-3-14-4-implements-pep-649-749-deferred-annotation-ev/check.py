import sys
assert sys.version_info[:3] >= (3, 14, 0), "wrong interpreter"

import annotationlib
from annotationlib import Format, get_annotations

# Format enum: exactly these four members with these values
assert {m.name: m.value for m in Format} == {
    "VALUE": 1, "VALUE_WITH_FAKE_GLOBALS": 2, "FORWARDREF": 3, "STRING": 4
}, "Format members changed"

def f(x: Undef) -> Undef: pass

# deferred: __annotate__ exists and is callable; nothing evaluated yet
assert callable(f.__annotate__), "no __annotate__"

# access before binding raises NameError
try:
    f.__annotations__
    raise SystemExit("expected NameError on unbound annotation name")
except NameError:
    pass

# FORWARDREF: ForwardRef objects with owner, no raise
fw = get_annotations(f, format=Format.FORWARDREF)
assert type(fw["x"]).__name__ == "ForwardRef", fw
assert fw["x"].__forward_arg__ == "Undef"
assert fw["x"].__owner__ is f, "ForwardRef missing owner"

# STRING: plain source strings
st = get_annotations(f, format=Format.STRING)
assert st == {"x": "Undef", "return": "Undef"}, st
assert all(type(v) is str for v in st.values())

# failed access did not poison: binding the name makes access succeed
Undef = int
assert f.__annotations__ == {"x": int, "return": int}, "retry after NameError failed"

# first successful evaluation is cached: rebind does not change result
Undef = str
assert f.__annotations__ == {"x": int, "return": int}, "cache not stable under rebind"

# class-body self-reference resolves lazily to the class object
class C:
    x: C
assert C.__annotations__ == {"x": C}, C.__annotations__

sys.exit(0)
