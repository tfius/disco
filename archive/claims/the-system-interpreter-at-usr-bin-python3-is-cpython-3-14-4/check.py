import sys, sysconfig

ok = (
    sys.implementation.name == "cpython"
    and tuple(sys.version_info[:3]) == (3, 14, 4)
    and sys.version_info.releaselevel == "final"
    and sys.maxsize == 2**63 - 1
    and hasattr(sys, "_is_gil_enabled") and sys._is_gil_enabled() is True
    and sysconfig.get_config_var("Py_DEBUG") == 0
    and sysconfig.get_config_var("Py_GIL_DISABLED") == 0
    and sys.getsizeof(0) == 28
    and sys.getsizeof([]) == 56
)
sys.exit(0 if ok else 1)
