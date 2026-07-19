"""envprobe — one-call snapshot of interpreter facts for baseline comparisons."""
import sys, sysconfig, platform

def probe():
    return {
        "impl": sys.implementation.name,
        "version": tuple(sys.version_info),
        "executable": sys.executable,
        "gil_enabled": sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else None,
        "maxsize": sys.maxsize,
        "sizeof_int0": sys.getsizeof(0),
        "sizeof_emptylist": sys.getsizeof([]),
        "recursion_limit": sys.getrecursionlimit(),
        "hash_randomization": sys.flags.hash_randomization,
        "platform": platform.platform(),
        "compiler": platform.python_compiler(),
        "py_debug": sysconfig.get_config_var("Py_DEBUG"),
        "gil_disabled_build": sysconfig.get_config_var("Py_GIL_DISABLED"),
    }

if __name__ == "__main__":
    for k, v in probe().items():
        print(f"{k}: {v}")
