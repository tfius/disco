# Methodology v1

**Picking questions**
- Prefer narrow, falsifiable questions over broad ones: "does `sorted()` on mixed int/float preserve stability" beats "how does sorting work."
- Target one mechanism per claim. Compound questions ("does X and does Y") split into separate threads.
- Reuse prior archived claims as building blocks — ask what follows from what's already verified, not what's already known from general Python folklore.

**Designing experiments**
- Write the check.py assertion FIRST, before the exploratory code. If you can't state the pass/fail condition precisely, the question isn't ready.
- Make experiments self-contained: no reliance on ambient state, no hidden imports beyond stdlib + archive/tools.
- Print raw values, not just booleans, so surprise is diagnosable from output alone.
- Test the boundary, not the center: empty inputs, single-element, negative, zero, max-size — the interior usually behaves as predicted.

**When to keep digging**
- If the result contradicts prediction, don't immediately claim the opposite — vary one input at a time to isolate which assumption broke.
- If result matches prediction on first try, run one adversarial variant before archiving (different type, different scale, different platform-sensitive value) — cheap confidence check against lucky coincidence.
- Stop digging and claim once two independent variants agree; don't chase a third confirmation, that's budget waste.

**When to claim**
- Claim only what the check.py literally verifies — no generalizing beyond tested inputs in the claim text.
- State the claim as the narrowest true statement, not the broadest plausible one ("stable for equal-key floats" not "sorting is stable").
- If check.py needed a workaround (try/except, version guard) to pass, that workaround IS the finding — put it in the claim, don't hide it.

**Avoid**
- Avoid questions answerable from documentation alone with no runtime uncertainty — they waste a thread without discovering anything.
- Avoid re-deriving Python semantics already common knowledge; spend budget where behavior is implementation-specific or version-specific.
- Avoid multi-step experiments where failure could stem from step 1 OR step 3 — collapse to single-step tests when possible.
