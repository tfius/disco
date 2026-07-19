"""Chat client for any OpenAI-compatible endpoint (LM Studio)."""
import json
import re
import time
import urllib.error
import urllib.request

from . import config

THINK_RE = re.compile(r"<think>.*?</think>", re.S)


def strip_think(text: str) -> str:
    text = THINK_RE.sub("", text)
    # unclosed <think> or orphan closer: keep only what follows the last </think>
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1]
    return text.strip()


def chat(messages, temperature=None, max_tokens=None, retries=2):
    if config.BACKEND == "claude":
        return _chat_claude(messages, retries)
    body = {
        "model": config.MODEL,
        "messages": messages,
        "temperature": config.AGENT_TEMPERATURE if temperature is None else temperature,
        "max_tokens": config.MAX_TOKENS if max_tokens is None else max_tokens,
    }
    req = urllib.request.Request(
        config.BASE_URL + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    last_err = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=config.LLM_TIMEOUT) as r:
                data = json.load(r)
            return strip_think(data["choices"][0]["message"]["content"])
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:300]
            last_err = f"{e} — {body}"
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as e:
            last_err = e
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"LLM call failed after {retries + 1} attempts: {last_err}")


def _chat_claude(messages, retries=2):
    """Backend: `claude -p` in pure text mode. Stateless — the transcript is flattened
    into one prompt per call; disco's kernel remains the only writer of state.
    temperature/max_tokens are not controllable through the CLI and are ignored."""
    import subprocess
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    convo = "\n\n".join(
        f"[{m['role'].upper()}]\n{m['content']}" for m in messages if m["role"] != "system"
    ) + "\n\n[ASSISTANT]"
    cmd = ["claude", "-p", "--output-format", "text", "--max-turns", "1"]
    if system:
        cmd += ["--append-system-prompt", system]
    if config.CLAUDE_MODEL:
        cmd += ["--model", config.CLAUDE_MODEL]
    last_err = None
    for attempt in range(retries + 1):
        try:
            p = subprocess.run(cmd, input=convo, capture_output=True, text=True,
                               timeout=config.LLM_TIMEOUT)
            if p.returncode == 0 and p.stdout.strip():
                return strip_think(p.stdout)
            last_err = f"exit {p.returncode}: {p.stderr.strip()[:300]}"
        except (subprocess.TimeoutExpired, OSError) as e:
            last_err = e
        if attempt < retries:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"claude -p failed after {retries + 1} attempts: {last_err}")


def json_score(raw: str, key: str, default: int) -> tuple[int, str]:
    """Parse a judge reply: first {...} block, clamp key to 0-10, return (score, note)."""
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        data = json.loads(m.group()) if m else {}
        return (max(0, min(10, int(data.get(key, default)))),
                str(data.get("note", ""))[:200])
    except (json.JSONDecodeError, ValueError, TypeError):
        return default, f"judge unparseable: {raw[:80]}"
