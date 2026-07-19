import os
import sys
from concurrent import interpreters

GLOBAL_VAL = 42
REEXEC = os.environ.get("DISCO_CHECK_734_REEXEC") is not None


def stateless(x):
    return x + 1


def reads_global():
    return GLOBAL_VAL


def make_closure():
    z = 10
    def inner(x):
        return x + z
    return inner


if not REEXEC:
    # Guard against the fake-__main__ re-import triggered by pickling reads_global.
    os.environ["DISCO_CHECK_734_REEXEC"] = "1"
    failures = []

    # 1. is_shareable partition (tuple containing a list IS shareable)
    cases = [
        ("s", True), (b"b", True), (1, True), (1.5, True), (True, True),
        (None, True), ((1, "a"), True), ((1, [2]), True),
        (memoryview(b"m"), True),
        ([1], False), ({"a": 1}, False), ({1}, False), (stateless, False),
    ]
    for obj, expect in cases:
        got = interpreters.is_shareable(obj)
        if got != expect:
            failures.append(f"is_shareable({obj!r}) = {got}, expected {expect}")

    q = interpreters.create_queue()
    if not interpreters.is_shareable(q):
        failures.append("Queue not shareable")

    # 2. unbounditems param exists on create_queue (pickle-fallback surface)
    import inspect
    if "unbounditems" not in inspect.signature(interpreters.create_queue).parameters:
        failures.append("create_queue has no unbounditems param")

    # 3. pickle fallback: __reduce__ fires for unshareable, not for shareable
    calls = []
    class Traced:
        def __reduce__(self):
            calls.append(1)
            return (str, ())
    q.put(Traced()); q.get()
    if not calls:
        failures.append("__reduce__ not called for unshareable put")
    q.put("plain"); q.get()
    if len(calls) != 1:
        failures.append("__reduce__ called for shareable str")

    # 4. memoryview shares the buffer
    ba = bytearray(b"AAAA")
    q.put(memoryview(ba))
    ba[:] = b"ZZZZ"
    if bytes(q.get()) != b"ZZZZ":
        failures.append("memoryview put/get did not share buffer")

    # 5. call semantics
    interp = interpreters.create()
    if interp.call(stateless, 1) != 2:
        failures.append("stateless call failed")
    if interp.call(lambda x: x * 2, 5) != 10:
        failures.append("stateless lambda call failed")

    GLOBAL_VAL = 99  # callee must see re-import snapshot (42), not this
    r = interp.call(reads_global)
    if r != 42:
        failures.append(f"reads_global returned {r!r}, expected snapshot 42")

    try:
        interp.call(make_closure(), 1)
        failures.append("closure call did not raise")
    except interpreters.NotShareableError:
        pass
    except Exception as e:
        failures.append(f"closure raised {type(e).__name__}, not NotShareableError")

    interp.close()

    for f in failures:
        print("FAIL:", f)
    sys.exit(1 if failures else 0)
# else: we are the fake __main__ re-import inside the subinterpreter — do nothing.
