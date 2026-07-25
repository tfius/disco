Methodology v1 — no threads run yet, starter rules from kernel design.

**Pick questions**
- Target concrete, checkable facts about Python env — not vague or philosophical ones.
- Prefer questions with clear pass/fail via a script (check.py must exit 0/nonzero deterministically).
- Avoid duplicate ground already in archive/claims/ — check first.
- Favor surprising or edge-case behavior over obvious stdlib facts (more info per claim).

**Design experiments**
- Predict outcome BEFORE writing/running code — predictions locked in ledger, no cheating.
- Keep check.py minimal: one assertion, one exit code. No hidden state, no external deps (stdlib only).
- Use archive/tools/ on PYTHONPATH if reusable helper needed — don't reinvent per-claim.
- Isolate variables: change one thing per experiment. If result ambiguous, narrow scope before rerunning.

**When to dig deeper**
- Result contradicts prediction → that's signal, not failure. Investigate why, don't discard.
- Result matches prediction but check.py flaky (nondeterministic) → fix determinism before claiming.
- Unexpected exception → capture exact error string, treat as data, not noise.

**When to claim**
- Only when check.py is deterministic and reproducible — run twice mentally, confirm same exit code.
- Claim narrow, precise fact over broad vague one. Narrow claims survive verify better.
- Don't claim speculation about "why" unless check.py actually tests the mechanism, not just the symptom.

**Avoid**
- No claims needing network, filesystem side effects outside sandbox, or timing-sensitive sleeps.
- No claims that only hold on this specific machine/version without checking version guard in check.py.
- Don't pass -I/-E to experiment interpreter — kills tool inheritance, breaks archive/tools/ imports.
- Don't write world-domain knowledge into kernel/ or prompts.py — irrelevant to methodology.md, but flagging since easy mistake.

Revise this file after first batch of threads — replace with rules grounded in actual admitted/rejected claim patterns once evidence exists.
