Toroidal Life grids — methodology

Pattern in evidence: threads that stay on one concrete, bounded question (fixed grid sizes, fixed density, named phenomenon) run 3-4 steps and land a CLAIM. Threads chasing vague/open questions ("do soups ever settle into genuine odd oscillati...") burn steps at high surprise then get abandoned as noise. Surprise decays fast within a thread (10→8→2, 10→6→6→2) — that decay is the signal to stop, not push further.

Rules:

1. Pick questions with a fixed, checkable scope: specific grid size or size range (n=6-12, 32-64), specific density (0.5), specific object (glider, ash, attractor). Avoid "do X ever happen" / "genuine" / open-ended existence questions — they don't converge to a checkable claim.
2. Reuse prior admitted claims' territory as stepping stones: toroidal 6-12 → 32-48-64 → 32×32 specifically. Narrowing an already-successful territory converges faster than opening new territory cold (glider-collision thread: fresh territory, surprise 5/6/2, no claim).
3. Watch surprise trajectory per thread. Step 1 surprise 8-10 is normal (novelty). If step 2 still ≥6, run step 3. Once surprise drops to ≤2, stop digging — claim what's solid or abandon; forcing more steps wastes the thread (seen twice: 10/8/2 pattern each time claim came right after the ≤2 step, not after more probing).
4. Build/archive a reusable tool (ash.py) per territory instead of ad-hoc scripts each thread — attractor/ash measurement is the recurring primitive across grid-size, density, and collision questions; a shared tool cuts setup steps and raises signal-to-noise on later threads.
5. Don't resurrect noise-abandoned questions verbatim — the two blank/empty noise entries suggest malformed or under-specified questions got dropped immediately. Precheck: question must name grid size, density, and the specific measured quantity before committing.
6. Methodology mutations: only keep a generation if it beats prior fitness (gen 2 discarded 1.0 vs 1.25) — don't hand-tune, let evolve.py's champion/challenger comparison decide.
7. Prefer claims scoped to exact parameter sets you actually ran (e.g. "n=32,48,64" not "n≥32") — matches the admitted-claim naming pattern and keeps check.py verifiable.
