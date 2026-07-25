"""Frozen kernel configuration. The agent never reads or writes this at runtime."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORLDS = ROOT / "worlds"

# "openai" (LM Studio & co.) or "claude" (shells out to `claude -p`)
BACKEND = os.environ.get("DISCO_BACKEND", "openai")
BASE_URL = os.environ.get("DISCO_BASE_URL", "http://localhost:1234/v1")
MODEL = os.environ.get("DISCO_MODEL", "qwen3.6-27b-med-slo@f16")
CLAUDE_MODEL = os.environ.get("DISCO_CLAUDE_MODEL", "")  # empty = CLI default

EXEC_TIMEOUT = int(os.environ.get("DISCO_EXEC_TIMEOUT", "30"))   # seconds per experiment
MAX_STEPS = int(os.environ.get("DISCO_MAX_STEPS", "8"))          # experiment steps per thread
MIN_CLAIM_EXPERIMENTS = int(os.environ.get("DISCO_MIN_CLAIM", "2"))  # replication gate
CULL_AFTER = int(os.environ.get("DISCO_CULL_AFTER", "2"))  # consecutive verify fails -> demoted
TRIAL_THREADS = int(os.environ.get("DISCO_TRIAL_THREADS", "4"))  # threads per variant per generation
METH_WORD_CAP = int(os.environ.get("DISCO_METH_CAP", "350"))  # methodology length limit
LLM_TIMEOUT = int(os.environ.get("DISCO_LLM_TIMEOUT", "900"))    # seconds per model call
AGENT_TEMPERATURE = float(os.environ.get("DISCO_TEMPERATURE", "0.8"))
JUDGE_TEMPERATURE = 0.1
MAX_TOKENS = int(os.environ.get("DISCO_MAX_TOKENS", "3000"))

DEFAULT_WORLD_TEXT = "Your world is the Python software environment of this machine."


def _point(world_dir: Path, name: str):
    global WORLD, WORLD_DIR, ARCHIVE, CLAIMS, TOOLS, QUESTIONS, RUNS, LEDGER
    WORLD = name
    WORLD_DIR = world_dir
    ARCHIVE = WORLD_DIR / "archive"
    CLAIMS = ARCHIVE / "claims"
    TOOLS = ARCHIVE / "tools"
    QUESTIONS = ARCHIVE / "open-questions"
    RUNS = WORLD_DIR / "runs"
    LEDGER = WORLD_DIR / "ledger.jsonl"


def set_world(name: str):
    """Point all state paths at worlds/<name>/. Kernel modules read these at call time."""
    _point(WORLDS / name, name)


def point_at(world_dir, name: str):
    """Point state paths at an arbitrary directory — rollout isolation copies."""
    _point(Path(world_dir), name)


set_world(os.environ.get("DISCO_WORLD", "python"))


def set_agent(name: str):
    """Agent identity for multi-agent science. 'solo' keeps legacy file names."""
    global AGENT
    AGENT = name


set_agent(os.environ.get("DISCO_AGENT", "solo"))


def world_description() -> str:
    """Territory text injected into the kernel prompt — the only domain-content file."""
    f = WORLD_DIR / "world.md"
    return f.read_text().strip() if f.exists() else DEFAULT_WORLD_TEXT


def ensure_dirs():
    for d in (CLAIMS, TOOLS, QUESTIONS, RUNS):
        d.mkdir(parents=True, exist_ok=True)
