"""The oracle. Executes agent code in a subprocess; only source of ground truth.

NOT a security sandbox — code runs as your user with network access.
Run disco inside a VM or container if that matters to you.
"""
import subprocess
import sys
from pathlib import Path

from . import config


def run_python(code: str, workdir: Path, timeout: int = None) -> dict:
    workdir.mkdir(parents=True, exist_ok=True)
    script = workdir / "experiment.py"
    script.write_text(code)
    env = {
        "PYTHONPATH": str(config.TOOLS),  # archived tools are importable — reuse is real
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": str(workdir),
    }
    try:
        # no -I: isolated mode would ignore PYTHONPATH and break tool inheritance
        p = subprocess.run(
            [sys.executable, str(script)],
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout or config.EXEC_TIMEOUT,
            env=env,
        )
        return {"exit": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "timeout": False}
    except subprocess.TimeoutExpired as e:
        return {"exit": None,
                "stdout": e.stdout if isinstance(e.stdout, str) else "",
                "stderr": e.stderr if isinstance(e.stderr, str) else "",
                "timeout": True}


def format_result(result: dict) -> str:
    parts = [f"exit: {'TIMEOUT' if result['timeout'] else result['exit']}"]
    if result["stdout"]:
        parts.append(f"stdout:\n{result['stdout']}")
    if result["stderr"]:
        parts.append(f"stderr:\n{result['stderr']}")
    if not result["stdout"] and not result["stderr"]:
        parts.append("(no output)")
    return "\n".join(parts)
