# python — full discovery program

## Where it stands

The archive is empty by reset, but the git history holds the earned first pass: the 3.14 census (interpreter identity, build flags — the version itself was the first surprise, since the model's priors are 3.13-flavored), incremental GC semantics via `gc.get_stats` deltas, PEP 649 deferred annotations (`__annotate__`, `annotationlib` formats), PEP 734 subinterpreters' two-tier object passing, and PEP 750 t-strings. Tools and claims are gone; the knowledge of *where the seams are* survives only as this program. The territory is CPython 3.14.4 (GCC 15.2.0, this machine) — every claim below is scoped to this build unless it states otherwise.

## Phase map

### Phase 1 — Re-census and instrument bootstrap
**Goal.** Rebuild the ground floor deliberately: one snapshot tool instead of five ad-hoc probes, plus the identity/interning map that every later phase leans on.
**Instruments.** `envprobe.py` (version, `sys.implementation`, build flags, `sysconfig.get_config_var("Py_GIL_DISABLED")`, `sys._is_gil_enabled()` if present, pointer size, `sys.int_info`/`float_info`, GC thresholds); `ident.py` (helpers: `same(a,b)`, refcount deltas, `is_interned` via `sys.intern` round-trip, immortality test via `sys.getrefcount` stability across binds).
**Predicted claims.**
- Small-int cache is exactly [-5, 256]: `a is b` for compile-time-independent constructions (e.g. `int("256") is 256`) holds at 256, fails at 257 [95].
- Small ints and single-char latin-1 strings are immortal: `sys.getrefcount(1)` returns the same sentinel value before and after binding 10,000 new references [80 that immortality is observable this way on this build].
- Identifier-like string literals within one code object are interned and mutually `is`-identical; a runtime `"".join` product of the same text is not, until passed through `sys.intern` [85].
- Compile-time constant folding produces shared constants: `x = 128 + 128; y = 256; x is y` is True inside one function, and `co_consts` shows the folded value [90].
- On this build `Py_GIL_DISABLED` is 0 and `sys._is_gil_enabled()` exists and returns True [75].
**How.** Everything through `is`, `sys.getrefcount`, `sys.getsizeof`, `co_consts` inspection — no timing. Interning claims phrased per-code-object, never globally.
**Traps.** REPL vs `exec` vs module compilation intern differently — checks must pin the compilation mode; refcount probes perturb what they measure (use deltas of deltas).
**Unlocks.** `envprobe` makes build-scoping one import; `ident` is the microscope for phases 2 and 4.

### Phase 2 — Specializing/adaptive interpreter forensics
**Goal.** Map the invisible tier: when bytecode specializes, to what, and what deoptimizes it — using `dis` as the only window.
**Instruments.** `speczoo.py`: run a function N times against controlled operand types, snapshot `dis.get_instructions(f, adaptive=True)` opnames after each call, return the (call_count → opname) transition table; a differ that reports first-specialization call index and deopt events.
**Predicted claims.**
- A two-int `a + b` function's `BINARY_OP` specializes to `BINARY_OP_ADD_INT` after a small fixed warm-up (predict exactly 2 calls; claim the measured constant) [70 on the phenomenon, 40 on my constant].
- Feeding the specialized function floats then strings triggers deopt back to the adaptive form, and re-specialization to `BINARY_OP_ADD_UNICODE` occurs after the same warm-up count [65].
- `BINARY_SUBSCR` no longer exists as an opcode in 3.14 — subscripting compiles to `BINARY_OP` with the subscript oparg; `dis.opmap` has no `"BINARY_SUBSCR"` key [60 — pure cross-version diff bait].
- `LOAD_ATTR` on instances specializes differently for slotted vs dict-backed classes (distinct specialized opnames), observable in the transition table [65].
- Specialization state is per-code-object, not per-function-object: two functions sharing `__code__` share warm-up [55].
**How.** Fixed operand scripts, no timing ever — specialization is claimed via opname strings, which are deterministic. Each claim's check re-runs the warm-up from a cold subprocess.
**Traps.** `dis` inspection itself can perturb counters; version-fragile opnames (scope claims to 3.14.x); tier-2/JIT presence on some builds changes the picture — `envprobe` must gate.
**Unlocks.** `speczoo` becomes the standard "what does the interpreter think of this code" probe; feeds phase 8's diff mining directly.

### Phase 3 — Incremental GC, deeper than the census
**Goal.** Move from "the stats moved" (old claims) to the mechanics: increment scheduling, what survives, finalizer and resurrection semantics.
**Instruments.** `gcprobe.py`: context manager freezing/restoring GC state; cycle factories (self-loop, 2-cycle, cycle-with-`__del__`, weakref'd cycle); collector that counts `gc.collect(generation)` returns per generation arg.
**Predicted claims.**
- `gc.get_threshold()` on this build returns a tuple whose meaning changed from 3.13 priors: second/third values no longer gate two older generations but scale increment size; claim the exact tuple and that `gc.set_threshold` round-trips it [70].
- `len(gc.get_stats()) == 2` on 3.14 versus the 3.13-prior 3 — the young/old restructuring is directly visible [55; if it is still 3, that failure maps the diff, which is the point].
- An unreachable self-referential cycle with no `__del__` is reclaimed by a single full `gc.collect()`: object count delta exactly N for N-object cycles [90].
- A cycle whose `__del__` resurrects `self` survives collection once, and the resurrected object is *not* re-finalized on the next collection (finalization-once rule) [75].
- Weakrefs into a collected cycle all go dead in the same collection that reclaims the cycle — no observable intermediate state from Python code [80].
**How.** Everything under `gc.disable()` + explicit `collect`, counting via `gc.get_count`, `len(gc.get_objects())` deltas on a tagged sentinel class. No allocation-pressure timing.
**Traps.** Background allocations by the harness pollute counts (filter by sentinel type); `__del__` ordering is explicitly unspecified — claim membership, not order.
**Unlocks.** `gcprobe`'s state-freezing pattern is reused by phase 6 (threads allocate) and gives clean baselines for phase 4's sizeof work.

### Phase 4 — Containers and the hash substrate
**Goal.** Exact laws of dict/set/hash: the guarantees, the growth schedules, the numeric identities.
**Instruments.** `hashlab.py` (modular-hash predictor implementing the documented `sys.hash_info.modulus` algorithm, to test prediction vs reality); `growth.py` (getsizeof-vs-len staircase extractor for dict/set/list).
**Predicted claims.**
- `hash(-1) == -2`, and `-1` is the only int whose hash differs from itself in [-5, 256] [95].
- For any `Fraction`-expressible number, `hash(x)` equals the inverse-modulus formula mod `2**61 - 1`: verified for 10,000 seeded int/float/Fraction triples with equal values hashing equal [90].
- `hash(float("nan"))` is identity-derived: two distinct NaN objects hash unequal, `hash(nan) == object.__hash__`-style value derived from `id`, and a NaN key can be *stored and retrieved* by identity from a dict [80].
- dict preserves insertion order under any interleaving of inserts/deletes/reinserts (reinsert goes to the end), and `popitem()` is LIFO — property-tested over 1,000 seeded random op sequences [95].
- dict `getsizeof` staircase: exact resize points (predict growth at 6th, then usable = 2/3 capacity, quadrupling small/doubling large — claim the measured table) [60 on my schedule, 90 that a clean staircase exists].
- Set iteration order for a fixed element multiset is a pure function of `PYTHONHASHSEED`: identical across 5 subprocess runs with seed pinned, differing across two chosen unequal seeds [85].
**How.** Subprocess pairs with `PYTHONHASHSEED` pinned/varied; property tests with `random.seed` stated in the claim; sizeof deltas, never timing.
**Traps.** The classic: claiming set order "random" (it's deterministic given seed) or dict order from hash (it isn't, since 3.7 compact dicts); key-sharing/inline-values makes instance-`__dict__` sizeof lie — measure plain dicts separately from instance dicts.
**Unlocks.** `hashlab` enables phase 5's `.pyc`-hash checks and phase 6's container-atomicity tests; the seeded-subprocess pattern becomes the world's determinism idiom.

### Phase 5 — Import machinery
**Goal.** The lifecycle of a module as observable protocol: finders, caches, bytecode files, partial-initialization states.
**Instruments.** `importlab.py`: builds throwaway package trees in a temp dir, imports them in sub-subprocesses, and reports `sys.modules` states, `__spec__` fields, and `__pycache__` byte-level contents; a `.pyc` header parser (magic, flags, source hash/mtime words).
**Predicted claims.**
- `importlib.util.MAGIC_NUMBER` is a constant for this build; a `.pyc` with one flipped magic byte is ignored and silently regenerated on import [90].
- The `.pyc` header is 16 bytes: magic + flags word + two words that are (mtime, size) when flags=0 and source-hash when compiled with `SOURCE_DATE_EPOCH`/hash-based invalidation; both modes demonstrable [80].
- During a circular import `a↔b`, the partially initialized module *is* present in `sys.modules`, and `from a import name` fails with `ImportError` whose message contains `"partially initialized module"` and `"circular import"` [85].
- Module-level `__getattr__` (PEP 562) is consulted only after normal attribute lookup misses, and `hasattr(mod, x)` triggers it exactly once per miss [85].
- A meta-path finder prepended to `sys.meta_path` intercepts even stdlib names not yet imported, but never names already in `sys.modules` — cache beats finders [90].
**How.** Every import experiment in a fresh subprocess with controlled `sys.path` and scrubbed `PYTHONPYCACHEPREFIX`; byte-level `.pyc` assertions via the parser.
**Traps.** Importing inside the harness process contaminates `sys.modules` for the whole experiment (subprocess-only rule); frozen/built-in modules follow a different path than the claims cover — scope to source imports.
**Unlocks.** Sub-subprocess orchestration + tempdir hygiene, needed for phase 6's multi-config runs and phase 8's version-flag sweeps.

### Phase 6 — Threads, GIL, and the free-threading boundary
**Goal.** What is actually atomic, when switches happen, and what of PEP 703/779 is visible from this GIL build.
**Instruments.** `racer.py`: N threads hammer a shared op for a fixed op-count (not wall-time), report lost updates; `switchprobe.py`: measures observed check-in granularity via a counter thread (results reported as distributions, claimed only as inequalities).
**Predicted claims.**
- `x += 1` on a shared int loses updates: 8 threads × 100k increments lands strictly below 800k in ≥1 of 3 trials at `sys.setswitchinterval(1e-6)` [85].
- `list.append` from 8 threads never loses an element: final length exactly 800k across 3 trials [90].
- `dict.setdefault` is atomic check-and-set: concurrent setdefault on one key yields exactly one winning value, all threads observing it [80].
- `sys.setswitchinterval` round-trips floats and accepts arbitrarily small positives but raises `ValueError` at 0 [70].
- On this build `concurrent.interpreters` imports, and passing a plain (non-shareable) object into an interpreter raises `NotShareableError`, while `int`/`str`/`tuple`-of-shareable crosses by value — re-earning the two-tier claim from git history against 3.14.4 [75].
**How.** Fixed op-counts, verdicts as counts and inequalities never durations; every racy claim's check runs 3 trials and claims the disjunction/conjunction explicitly.
**Traps.** The 30s timeout meets thread contention (budget op-counts down); "never loses" claims are ∀-shaped from ∃ evidence — phrase as "in 3×800k trials, zero losses observed" so verify re-samples honestly; free-threading claims are untestable on this build and must be parked, not claimed.
**Unlocks.** `racer` doubles as a stressor for GC (phase 3 revisit: does incremental GC ever run mid-`append` storm?); parks the open question that seeds any future `python-ft` (free-threaded build) world.

### Phase 7 — Exception machinery and frame forensics
**Goal.** Zero-cost exceptions, chaining rules, exception groups, and the 3.14-specific `finally` legislation — read through `dis`, tracebacks, and `sys.exception()`.
**Instruments.** `exclab.py`: raises through controlled nesting and reports `__context__`/`__cause__`/`__suppress_context__` graphs as dicts; `etable.py`: parses `dis`'s ExceptionTable output into (start, end, target, depth, lasti) tuples.
**Predicted claims.**
- A `try` body's non-exceptional path contains no setup opcode: `dis` of a try/except function shows no `SETUP_*` instruction, and the exception table (not bytecode) carries the handler range [85].
- `raise B from A` sets `__cause__` is A and `__suppress_context__` True, while a bare raise inside an except block sets `__context__` automatically; the full chain prints innermost-first with the exact "During handling of the above exception" separator [95].
- `except* ValueError` on `ExceptionGroup([ValueError, TypeError])` catches a *derived group* whose `.exceptions` is exactly the ValueError part, and the TypeError subgroup propagates [90].
- `return` inside `finally` compiles with a `SyntaxWarning` on 3.14 (PEP 765) — `warnings.catch_warnings` around `compile()` captures exactly one warning whose category is SyntaxWarning [70].
- A generator's frame after `.close()` has `gi_frame is None`, and `StopIteration` raised inside is replaced by `RuntimeError` (PEP 479 permanently) [90].
**How.** Structure-of-chain assertions via attribute walks, not string-matching whole tracebacks (message text is fragile — pin only load-bearing substrings); `etable` claims phrased on table structure, not offsets.
**Traps.** Traceback text drifts across micro-releases (checks pin substrings, never full text); `sys.exception()` vs `sys.exc_info()` aliasing confusions; warning claims need `-W` state controlled in the subprocess.
**Unlocks.** `etable` + `speczoo` together are a complete bytecode forensics kit — exactly the instrument set phase 8 sweeps with.

### Phase 8 — Cross-version diff mining: wrong priors as the map
**Goal.** Systematize the accident that produced this world's best surprises: the model's 3.13-flavored priors are a free diff engine against 3.14 reality. Predict *from prior*, run, and archive every stable divergence.
**Instruments.** `diffmine.py`: a battery runner — each battery is (probe fn, prior-expected value, observed value) triples over opcode maps, module attribute sets (`dir()` diffs of `sys`, `gc`, `typing`, `string`, `concurrent`), C-API-visible constants, error-message formats; results tabulated as PRIOR_HELD / PRIOR_BROKE.
**Predicted claims.**
- `dis.opmap` diff vs prior: at least `BINARY_SUBSCR` and `LOAD_ASSERTION_ERROR`-era names missing, new `LOAD_FAST_BORROW`-class or tail-call-era names present; claim the exact sorted symmetric-difference list for this build [55 on my examples, 85 that the list is nonempty and stable].
- `string.templatelib` exists with `Template` and `Interpolation`, and `t"..."` evaluates to a `Template` whose `.strings`/`.values` round-trip the parts exactly [90].
- `f(x annotations)`: `SomeClass.__annotations__` access triggers `__annotate__(1)` lazily — a counter in an annotation expression increments 0 times at class creation, exactly once at first `__annotations__` access, then caches [85].
- At least one error-message format claim breaks 3.13 priors (candidate: NameError/AttributeError suggestion wording, or the new multiline-expression carets); archive the surviving exact-substring claim [65].
- A capstone meta-claim: the battery's PRIOR_BROKE set is stable — running `diffmine` twice from cold subprocesses yields identical tables (the diff is real, not flaky) [80].
**How.** Prior values are committed in the prediction *before* the probe runs — this phase is the harness's own protocol turned recursive. Each divergence that replicates becomes its own scoped claim; the battery table itself is the claim artifact.
**Traps.** Prior contamination (once the agent has seen 3.14 reality, "priors" are no longer priors — batteries must be authored blind, from memory, before first execution and frozen); micro-release drift (scope to 3.14.4); mistaking machine-config for version diff (envprobe gates every battery).
**Unlocks.** The endgame: a reusable methodology for *any* future version bump — point `diffmine` at 3.15 and the world regenerates its frontier.

## Endgame

A completed archive is a behavioral specification of this build that a fresh 3.13-prior model would fail and this archive would correct: ~40–60 claims across identity/interning, specialization transition tables, GC increment semantics, container/hash laws, import protocol, concurrency atomicity tables, exception machinery, and the prior-diff table — each with a check that re-derives it from a cold subprocess. Stopping criteria: (1) three consecutive sessions where every surprise ≤2 (priors, now archive-informed, stop being wrong); (2) `audit` uplift plateaus — the archive already answers what a naive agent gets wrong; (3) remaining open questions all require what the harness cannot give: a free-threaded or JIT/tail-call build (parked for a sibling world), wall-clock performance laws (no timing oracle), or C-level state invisible from pure Python. The territory crosses into genuinely open ground at exactly those parks: free-threading's atomicity table is an open research surface even upstream; specialization *policy* (why these thresholds) is design intent, not behavior, and no experiment reaches it.

## Harness strain

- **30s timeout**: bites in phase 6 (contention runs) and phase 4 property sweeps; forces op-count budgeting, which is healthy discipline anyway.
- **Determinism**: hash randomization (pin `PYTHONHASHSEED` in subprocess env — claims are wrong if pinned only via `random`), GC nondeterminism from harness allocations, thread scheduling (claims must be count/inequality-shaped with trial counts stated).
- **Scoping**: the deepest strain — nearly every claim is per-build (3.14.4, GCC 15.2.0, GIL-enabled, 64-bit). `verify` on another machine would rightly cull unscoped claims; `envprobe` gating inside every check is the survival strategy, and claims that fail elsewhere are *doing their job* (they were about this build).
- **Self-observation**: the experiment process is made of the thing under study — `dis` perturbs specialization counters, refcount probes perturb refcounts, imports perturb `sys.modules`. The subprocess-per-measurement idiom is mandatory, and it spends the timeout budget.
- **∀-claims from ∃-evidence**: "never loses an element", "always interned" — the gate admits them if the check passes twice; only honest statistical phrasing keeps verify meaningful.

## Methodology attractor

Selection should converge on text enforcing: (1) *subprocess is the unit of measurement* — every probe cold, env pinned (`PYTHONHASHSEED`, `-W`, path); (2) *no timing, ever* — claim opnames, counts, exact values, inequalities; (3) *scope every claim to `envprobe`'s fingerprint* and let the check gate on it; (4) *predict from prior, loudly* — state the 3.13-flavored expectation before running, because broken priors are this world's richest vein; (5) *one mechanism per claim* — a dict-order claim must not smuggle a hash claim; (6) *park what needs another build* rather than weakening the claim to fit this one. The degenerate attractors to watch for: sizeof-staircase farming (endless cheap exact claims with no compression) and doc-echoing (claiming what the docs already state without an experiment that could have falsified it).
