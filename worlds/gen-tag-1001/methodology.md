Predict narrow, falsifiable claims about actual runtime behavior — version quirks, stdlib edge cases, type coercion, error messages — not vague generalities. Vague claim = hard to design check.py for.

Before running: write prediction specific enough that check.py just asserts one condition. If prediction needs multiple asserts, split into multiple claims.

Design experiment to isolate one variable. Change one thing from baseline, not several. Multi-variable script = surprise ambiguous, hard to compress to clean claim.

Prefer cheap experiments (single print, single import, single call) over elaborate scripts. Fast iteration > thoroughness per round early on.

When result matches prediction exactly: still worth archiving if fact nonobvious (undocumented behavior, version-specific, easy to get wrong). Skip claiming truisms (well-documented stdlib behavior everyone knows).

When result surprises: dig one level deeper before claiming — rerun with adjacent input to confirm it's a real boundary, not a fluke (typo, wrong assumption about environment). One confirm run, not five.

Write check.py to test the *mechanism*, not the specific numbers from one run. E.g., check "raises TypeError," not "prints exactly this string" unless string itself is the discovery.

Avoid claims that depend on external state (files, network, timing, randomness without seed) — nondeterministic checks get rejected on rerun.

If prediction was wrong: don't force a claim from wreckage. Either reformulate as a claim about *why* it was wrong (if that's the real discovery), or drop and move to next question — don't pad archive with weak claims.

Watch ledger tail for prior claims before repeating similar experiments — build on what's archived, don't rediscover same fact different phrasing.

Stop digging into a topic after 2 dead-end experiments in a row (no signal, no surprise) — switch questions. Sunk cost isn't a good reason to keep going.

Keep claim text short: state the fact plainly, mechanism if relevant, no narrative padding.
