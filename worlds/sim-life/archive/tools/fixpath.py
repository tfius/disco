"""Demote the archive/tools directory to the END of sys.path so stdlib modules
(enum, re, fractions, ...) are not shadowed by same-named archived tools.
The archived tool enum.py otherwise breaks any stdlib import chain that touches
enum (re, fractions, dataclasses, ...). Import this FIRST:

    import fixpath

Tools stay importable afterwards (dir is still on sys.path, just last); a tool
whose name collides with stdlib can be loaded explicitly via fixpath.load(name).
"""
import sys, os, importlib.util

_d = os.path.dirname(os.path.abspath(__file__))
while _d in sys.path:
    sys.path.remove(_d)
sys.path.append(_d)

# purge an already-imported shadowed stdlib module if it came from the tools dir
for _name in ('enum',):
    _m = sys.modules.get(_name)
    if _m is not None and (getattr(_m, '__file__', '') or '').startswith(_d):
        del sys.modules[_name]

def load(name):
    """Import archived tool by explicit path, bypassing stdlib-name collisions."""
    spec = importlib.util.spec_from_file_location('tool_' + name, os.path.join(_d, name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
