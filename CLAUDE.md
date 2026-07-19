# disco — discovery harness

An LLM agent discovers verified facts about the Python environment via
predict → run → surprise → compress → archive. Design rationale in README.md.

## Commands

- `python3 selftest.py` — offline end-to-end test, no endpoint needed. Run after any kernel change.
- `python3 disco.py run -n 1` — live discovery thread (needs a backend, below)
- `python3 disco.py status` / `audit` / `verify`

## Backends

- `DISCO_BACKEND=openai` (default): OpenAI-compatible endpoint, `DISCO_BASE_URL` + `DISCO_MODEL` (LM Studio)
- `DISCO_BACKEND=claude`: shells out to `claude -p` per call; `DISCO_CLAUDE_MODEL` optional

## Invariants — do not break

- `kernel/` is frozen machinery and must contain **zero domain knowledge**. Never add
  hints, examples, or workflow advice to `prompts.py` — protocol mechanics only.
  The agent is supposed to discover everything else itself.
- Predictions are committed before execution; only the kernel writes `ledger.jsonl` and `archive/`.
- A claim enters `archive/claims/` only if its `check.py` exits 0.
- The agent-facing ledger tail (`ledger.tail(for_agent=True)`) must never show
  audit/verify entries — the fast loop must not see its own audit metric.
- Experiments run with `archive/tools/` on `PYTHONPATH`; never pass `-I`/`-E` to the
  experiment interpreter (kills tool inheritance).
- Stdlib only. No third-party dependencies.
