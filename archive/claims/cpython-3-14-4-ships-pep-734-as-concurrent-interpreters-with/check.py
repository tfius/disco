import sys
import concurrent.interpreters as ci

g = 1

def read_g():
    return g

def make_closure():
    cell = 7
    def inner():
        return cell
    return inner

lam = lambda: 42

def main():
    global g
    ok = True
    def chk(label, cond):
        nonlocal ok
        print(("PASS" if cond else "FAIL"), label)
        if not cond:
            ok = False

    # API surface
    for name in ("create", "Interpreter", "Queue", "create_queue",
                 "is_shareable", "NotShareableError", "ExecutionFailed"):
        chk(f"api:{name}", hasattr(ci, name))

    interp = ci.create()

    # isolation: exec cannot touch caller namespace
    x = "main"
    interp.exec("x = 'sub'")
    chk("isolation", x == "main")

    # exception wrapping
    try:
        interp.exec("raise ValueError('boom')")
        chk("ExecutionFailed raised", False)
    except ci.ExecutionFailed:
        chk("ExecutionFailed raised", True)

    # shareability matrix
    for v in (42, 3.14, "s", b"b", True, None, (1, "a")):
        chk(f"shareable:{type(v).__name__}", ci.is_shareable(v))
    for v in ([1], {"a": 1}, {1, 2}):
        chk(f"not-shareable:{type(v).__name__}", not ci.is_shareable(v))
    chk("fn-not-shareable-data", not ci.is_shareable(read_g))

    # __main__ re-exec footgun: mutate g AFTER defs, call sees fresh value 1
    g = 999
    chk("call-reexec-sees-fresh-global", interp.call(read_g) == 1)

    # stateless lambda works, returns value
    chk("call-stateless-lambda", interp.call(lam) == 42)

    # closure with cell rejected
    try:
        interp.call(make_closure())
        chk("closure-rejected", False)
    except ci.NotShareableError:
        chk("closure-rejected", True)

    interp.close()
    sys.exit(0 if ok else 1)

# Guard: when the subinterpreter re-executes this script for call(),
# stop after the defs above — only the main interpreter runs the checks.
if ci.get_current().id == ci.get_main().id:
    main()
