"""Frozen kernel configuration. The agent never reads or writes this at runtime."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# "openai" (LM Studio & co.) or "claude" (shells out to `claude -p`)
BACKEND = os.environ.get("DISCO_BACKEND", "openai")
BASE_URL = os.environ.get("DISCO_BASE_URL", "http://localhost:1234/v1")
MODEL = os.environ.get("DISCO_MODEL", "qwen3.6-27b-med-slo@f16")
CLAUDE_MODEL = os.environ.get("DISCO_CLAUDE_MODEL", "")  # empty = CLI default

ARCHIVE = ROOT / "archive"
CLAIMS = ARCHIVE / "claims"
TOOLS = ARCHIVE / "tools"
QUESTIONS = ARCHIVE / "open-questions"
RUNS = ROOT / "runs"
LEDGER = ROOT / "ledger.jsonl"

EXEC_TIMEOUT = int(os.environ.get("DISCO_EXEC_TIMEOUT", "30"))   # seconds per experiment
MAX_STEPS = int(os.environ.get("DISCO_MAX_STEPS", "8"))          # experiment steps per thread
MIN_CLAIM_EXPERIMENTS = int(os.environ.get("DISCO_MIN_CLAIM", "2"))  # replication gate
LLM_TIMEOUT = int(os.environ.get("DISCO_LLM_TIMEOUT", "900"))    # seconds per model call
AGENT_TEMPERATURE = float(os.environ.get("DISCO_TEMPERATURE", "0.8"))
JUDGE_TEMPERATURE = 0.1
MAX_TOKENS = int(os.environ.get("DISCO_MAX_TOKENS", "3000"))


def ensure_dirs():
    for d in (CLAIMS, TOOLS, QUESTIONS, RUNS):
        d.mkdir(parents=True, exist_ok=True)
