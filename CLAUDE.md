# disco — discovery harness

An LLM agent discovers verified facts about the Python environment via
predict → run → surprise → compress → archive. Design rationale in README.md.

## Commands

- `python3 selftest.py` — offline end-to-end test, no endpoint needed. Run after any kernel change.
- `python3 disco.py run -n 1` — live discovery thread (needs a backend, below)
- `python3 disco.py status` / `audit` / `verify` / `worlds` / `seed` / `reset`
- `python3 disco.py newworld <name> "<territory>"` then `-w <name>` on any command —
  worlds live in `worlds/<name>/` with their own archive/runs/ledger
- `python3 disco.py export` — world threads → training episodes (exports/, gitignored)
- `python3 disco.py genworld <seed> [--family ca|modpoly|tag]` — contamination-free random world
- `python3 disco.py stats` / `deps` — discovery metrics, claim→tool dependency graph
- `python3 disco.py grind <seeds...> -n T` — batch: generate worlds + run + export
- `python3 disco.py run --agents a,b` / `calib` / `coevolve` — multi-agent science, calibration, POET loop

## Backends

- `DISCO_BACKEND=openai` (default): OpenAI-compatible endpoint, `DISCO_BASE_URL` + `DISCO_MODEL` (LM Studio)
- `DISCO_BACKEND=claude`: shells out to `claude -p` per call; `DISCO_CLAUDE_MODEL` optional

## Invariants — do not break

- `kernel/` is frozen machinery and must contain **zero domain knowledge**. Never add
  hints, examples, or workflow advice to `prompts.py` — protocol mechanics only.
  The agent is supposed to discover everything else itself.
- Domain content lives in exactly one place: `worlds/<name>/world.md`. Steering goes
  through `seed` (open questions) or world.md — never through kernel code or prompts.
- `worlds/<name>/methodology.md` is AGENT-authored strategy, evolved by
  champion/challenger selection (kernel/evolve.py). Neither humans nor kernel code
  write its content; the kernel only scores trials with the frozen fitness in
  evolve.py. Do not "improve" the methodology by hand.
- Predictions are committed before execution; only the kernel writes each world's
  `ledger.jsonl` and `archive/`.
- A claim enters the world's `archive/claims/` only if its `check.py` exits 0.
- The agent-facing ledger tail (`ledger.tail(for_agent=True)`) must never show
  audit/verify entries — the fast loop must not see its own audit metric.
- Experiments run with the world's `archive/tools/` on `PYTHONPATH`; never pass `-I`/`-E` to the
  experiment interpreter (kills tool inheritance).
- Stdlib only. No third-party dependencies.
