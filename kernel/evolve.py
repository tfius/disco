"""Methodology evolution: champion/challenger selection over live threads.

The methodology (worlds/<w>/methodology.md) is self-authored strategy text injected
into the agent's prompt. The kernel never writes strategy content — it only runs the
selection: the model proposes a challenger from ledger evidence; champion and
challenger alternate threads; the frozen fitness below decides; the loser dies.
Evolving content, frozen judge — like everything else here.
"""
import json
import re

from . import config, ledger, llm, prompts

SCORES = {
    "claim_admitted": 3.0,
    "claim_rejected": -2.0,
    "culled": -3.0,  # delayed penalty: reality retracted an admitted claim

    "question": 1.0,        # honest parked surprise
    "question_parked": -0.5,  # premature claim the kernel had to park
    "noise": 0.0,
    "exhausted": 0.0,
    "parse-failure": -1.0,
    "syntax-failure": -1.0,
}
PROMOTE_MARGIN = 0.25


def _path(name):
    return config.WORLD_DIR / name


def _state() -> dict:
    f = _path("evolution.json")
    if f.exists():
        return json.loads(f.read_text())
    return {"generation": 1, "champion": [], "challenger": []}


def _save(state):
    _path("evolution.json").write_text(json.dumps(state, indent=2))


def champion_text() -> str:
    f = _path("methodology.md")
    return f.read_text().strip() if f.exists() else ""


def challenger_text():
    f = _path("methodology.challenger.md")
    return f.read_text().strip() if f.exists() else None


def current(on_event=print):
    """(variant, methodology_text) for the next thread. Keeps a live trial running."""
    if challenger_text() is None:
        propose(on_event)
    chal = challenger_text()
    if chal is None:  # proposal rejected — run the champion unopposed
        return "champion", champion_text()
    s = _state()
    if len(s["challenger"]) <= len(s["champion"]):
        return "challenger", chal
    return "champion", champion_text()


def score(outcome: dict) -> float:
    ending = outcome.get("ending", "")
    if ending == "claim":
        return SCORES["claim_admitted"] if outcome.get("admitted") else SCORES["claim_rejected"]
    if ending == "question":
        return SCORES["question_parked"] if outcome.get("parked") else SCORES["question"]
    return SCORES.get(ending, 0.0)


def note(outcome: dict, variant: str, on_event=print):
    """Record a finished thread against its variant; resolve the trial when full."""
    s = _state()
    s[variant].append({"thread": outcome.get("thread"), "ending": outcome.get("ending"),
                       "score": score(outcome)})
    # permanent attribution: which lineage made this thread — survives resolution,
    # so later culls can be charged to the variant that earned the false claim
    s.setdefault("attribution", {})[outcome.get("thread")] = {
        "gen": s["generation"], "variant": variant}
    _save(s)
    if challenger_text() is not None and \
            min(len(s["champion"]), len(s["challenger"])) >= config.TRIAL_THREADS:
        _resolve(s, on_event)


def _mean(rows):
    return sum(r["score"] for r in rows) / len(rows) if rows else 0.0


def _resolve(s, on_event):
    champ, chal = _mean(s["champion"]), _mean(s["challenger"])
    promoted = chal > champ + PROMOTE_MARGIN
    if promoted:
        old = champion_text()
        if old:
            hist = _path("methodology-history")
            hist.mkdir(exist_ok=True)
            (hist / f"gen-{s['generation']}.md").write_text(old + "\n")
        _path("methodology.md").write_text(challenger_text() + "\n")
    _path("methodology.challenger.md").unlink()
    ledger.log("evolution", event="promoted" if promoted else "discarded",
               generation=s["generation"], champion_score=round(champ, 2),
               challenger_score=round(chal, 2))
    on_event(f"  evolution gen {s['generation']}: challenger "
             f"{'PROMOTED' if promoted else 'discarded'} ({chal:.2f} vs {champ:.2f})")
    _save({"generation": s["generation"] + 1, "champion": [], "challenger": [],
           "attribution": s.get("attribution", {})})


def attribute_cull(thread: str, slug: str, on_event=print):
    """Delayed fitness: a culled claim is charged to the lineage that made it.
    If the thread belongs to the current unresolved trial, the penalty lands in
    the live scores; otherwise it is ledgered as lineage evidence for proposals."""
    s = _state()
    a = s.get("attribution", {}).get(thread)
    if not a:
        return
    if a["gen"] == s["generation"] and challenger_text() is not None:
        s[a["variant"]].append({"thread": thread, "ending": "culled",
                                "score": SCORES["culled"]})
        _save(s)
        on_event(f"  evolution: cull of {slug} charged to live {a['variant']} trial")
    ledger.log("evolution", event="cull-attributed", generation=a["gen"],
               variant=a["variant"], slug=slug)


def _evidence() -> str:
    parts = [ledger.tail(25)]
    if config.QUESTIONS.exists():
        demoted = [q.stem for q in config.QUESTIONS.glob("demoted-*.md")]
        if demoted:
            parts.append("claims culled by reality: " + ", ".join(demoted))
    return "\n".join(parts)


def propose(on_event=print):
    """One fresh model call authors a challenger methodology from the evidence."""
    text = llm.chat(
        [{"role": "user", "content": prompts.EVOLVE_PROPOSE.format(
            cap=config.METH_WORD_CAP,
            current=champion_text() or "(empty)",
            evidence=_evidence())}],
        temperature=0.9, max_tokens=1200,
    )
    text = re.sub(r"^```[a-z]*\s*$|^```\s*$", "", text.strip(), flags=re.M).strip()
    if not text or len(text.split()) > config.METH_WORD_CAP:
        ledger.log("evolution", event="proposal-rejected",
                   reason=f"empty or over {config.METH_WORD_CAP}-word cap")
        on_event("  evolution: proposal rejected (empty or over word cap)")
        return
    _path("methodology.challenger.md").write_text(text + "\n")
    ledger.log("evolution", event="proposed", generation=_state()["generation"])
    on_event(f"  evolution gen {_state()['generation']}: challenger methodology proposed")
