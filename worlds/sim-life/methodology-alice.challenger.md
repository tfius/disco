Discovery methodology — toroidal Game of Life world

1. Pick questions with concrete, checkable structure: fixed grid sizes/ranges, named patterns (LWSS, glider), explicit densities. Vague "does X ever happen" questions burn steps before convergence — narrow scope in the prediction itself.

2. Run 3 steps per question, watch surprise trend. Pattern seen: 9-6-0, 10-8-2, 10-8-2 — surprise decays fast once mechanism is pinned down. Stop and claim at step 3 when surprise hits 0-2; don't push a 4th step, diminishing returns.

3. Odd-oscillation / rare-event questions (surprise 2/10 first try) are weak — either reframe with concrete bound (grid size range, density value) or drop. First attempt (soup 950001) barely cleared; second attempt with size range 6-12 and explicit density scored 10-8-2 and admitted clean. Concreteness > cleverness.

4. Glider-collision / open-ended combinatorial questions plateau mid-surprise (5-6-2) — still admits, but weaker signal than parametrized single-object questions (LWSS, density convergence). Prefer one-object-one-property questions over multi-object interaction questions unless collision outcome space is enumerable.

5. Density-convergence questions (comparing to known asymptotic constants) score highest early surprise (10-8) — good territory, keep mining: other known Life constants (still-life density, glider density in random soups) likely equally rich.

6. Abandon fast: two "noise abandoned" entries after weak steps — don't rescue a dying thread, redirect budget to next question.

7. Tools: archive reusable pattern-detection code (lwss.py pattern) per claim — build a small library of verified detectors (spaceship-survives, oscillator-period, density-converges) to reuse across questions instead of rewriting from scratch each thread.

8. Don't hand-tune methodology via evolution loop — gen 2 variant lost (1.0 vs 1.25); trust champion/challenger scoring, don't second-guess a discarded variant.

9. Every batch: confirm VERIFY stays 24/24 — if a claim check ever regresses, stop and fix the tool before adding new claims; don't build new territory on a cracked foundation.
