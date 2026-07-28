"""Medium loop: naive-agent uplift.

Does the archive make a fresh agent better at predicting this world?
Sample past experiments; a fresh model predicts each output twice — with and
without the claims digest. Uplift = mean(with) - mean(without), judge-scored.
The fast loop never optimizes this number; it is telemetry for the human.
"""
import json
import random

from . import archive, config, ledger, llm, prompts


def _judge_accuracy(predicted: str, actual: str) -> int:
    raw = llm.chat(
        [
            {"role": "system", "content": prompts.AUDIT_JUDGE_SYSTEM},
            {"role": "user", "content": prompts.AUDIT_JUDGE_USER.format(
                predicted=predicted, actual=actual)},
        ],
        temperature=config.JUDGE_TEMPERATURE,
        max_tokens=200,
    )
    return llm.json_score(raw, "accuracy", default=0)[0]


def _samples(k: int):
    steps = []
    if config.RUNS.exists():
        for step_dir in config.RUNS.glob("*/step-*"):
            code_f, result_f = step_dir / "experiment.py", step_dir / "result.json"
            if code_f.exists() and result_f.exists():
                result = json.loads(result_f.read_text())
                if not result["timeout"] and result["stdout"].strip():
                    steps.append((code_f.read_text(), result["stdout"]))
    random.shuffle(steps)
    return steps[:k]


def run(k: int = 8, on_event=print) -> dict:
    samples = _samples(k)
    if not samples:
        on_event("audit: no completed experiments with output yet")
        return {}
    knowledge = prompts.AUDIT_KNOWLEDGE.format(claims=archive.claims_digest())
    with_scores, without_scores = [], []
    for i, (code, actual) in enumerate(samples, 1):
        for scores, kn in ((without_scores, ""), (with_scores, knowledge)):
            predicted = llm.chat(
                [{"role": "user", "content": prompts.AUDIT_PREDICT.format(knowledge=kn, code=code)}],
                temperature=0.2, max_tokens=1000,
            )
            scores.append(_judge_accuracy(predicted, actual))
        on_event(f"  sample {i}/{len(samples)}: with {with_scores[-1]}/10, without {without_scores[-1]}/10")
    w = round(sum(with_scores) / len(with_scores), 2)
    wo = round(sum(without_scores) / len(without_scores), 2)
    entry = {"uplift": round(w - wo, 2), "with_archive": w, "without_archive": wo,
             "samples": len(samples)}
    ledger.log("audit", **entry)
    on_event(f"audit: uplift {entry['uplift']} (with {w} vs without {wo}, n={len(samples)})")
    return entry
