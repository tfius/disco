import gc, sys
from collections import Counter

fails = []
def ck(name, cond):
    if not cond:
        fails.append(name)
        print("FAIL:", name)
    else:
        print("ok:", name)

# 1. incremental-GC default thresholds
ck("threshold-(2000,10,0)", gc.get_threshold() == (2000, 10, 0))

# 2. net count: alloc-kept raises count, del lowers it back
gc.collect()
base = gc.get_count()[0]
held = [[i] for i in range(1000)]
up = gc.get_count()[0] - base
del held
down = gc.get_count()[0] - base
ck("count-net-up~1000", 900 <= up <= 1100)
ck("count-net-restored", down <= 50)

# 3. alloc-then-free churn -> zero automatic collections
events = []
def cb(phase, info):
    if phase == "stop":
        events.append(dict(info))
gc.collect()
gc.callbacks.append(cb)
for i in range(60_000):
    x = ([i], {i: (i,)})
    del x
gc.callbacks.remove(cb)
ck("churn-no-auto-collections", len(events) == 0)

# 4-6. kept-alive allocs + dropped cycles -> gen-1 increments that reap cycles
events = []
gc.collect()
stats_before = [s["collections"] for s in gc.get_stats()]
gc.callbacks.append(cb)
holder = []
for i in range(60_000):
    holder.append([i])
    a = []; a.append(a)
    del a
gc.callbacks.remove(cb)
stats_after = [s["collections"] for s in gc.get_stats()]
gens = Counter(e["generation"] for e in events)
d0, d1, d2 = (a - b for a, b in zip(stats_after, stats_before))
ck("auto-collections-happened", len(events) >= 10)
ck("all-events-gen1", set(gens) == {1})
ck("stats0-never-advances", d0 == 0)
ck("stats1-ticks-fewer-than-events", 0 < d1 < len(events))
ck("stats2-untouched-by-auto", d2 == 0)
ck("increments-reap-cycles", sum(e["collected"] for e in events) > 10_000)
del holder

# 7. explicit collect(g): callback tagged g; stats attribution for 0 and 2
for gen, slot in ((0, 0), (2, 2)):
    ev = []
    def cb2(phase, info, ev=ev):
        if phase == "stop":
            ev.append(dict(info))
    before = [s["collections"] for s in gc.get_stats()]
    gc.callbacks.append(cb2)
    gc.collect(gen)
    gc.callbacks.remove(cb2)
    after = [s["collections"] for s in gc.get_stats()]
    delta = [a - b for a, b in zip(after, before)]
    ck(f"collect({gen})-cb-tagged", len(ev) == 1 and ev[0]["generation"] == gen)
    expected = [0, 0, 0]; expected[slot] = 1
    ck(f"collect({gen})-stats-delta", delta == expected)

sys.exit(1 if fails else 0)
