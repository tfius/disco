import sys
sys.path.insert(0, 'archive/tools')
from life import soup, step

W, H = 6, 6

def find_period(g, W, H, max_iter=10000):
    seen = {}
    steps_taken = 0
    g_key = tuple(g)
    while g_key not in seen and steps_taken < max_iter:
        seen[g_key] = steps_taken
        g = step(g, W, H)
        g_key = tuple(g)
        steps_taken += 1
    
    if steps_taken >= max_iter:
        return None
    
    return steps_taken - seen[g_key]

# Test two independent seed ranges
period_data = []
for seed_base in [0, 800000]:
    periods = []
    for seed in range(seed_base, seed_base + 120):
        g = soup(seed, W, H, p=0.5)
        period = find_period(g, W, H)
        if period is not None:
            periods.append(period)
    period_data.append(periods)

# Both batches should show ~97% period <= 4
for batch_idx, periods in enumerate(period_data):
    at_most_4 = sum(1 for p in periods if p <= 4)
    pct = 100 * at_most_4 / len(periods)
    
    # Claim: >= 95% period <= 4
    if pct < 95:
        exit(1)
    
    # Claim: period-1 dominant (>= 70% of soups)
    p1_count = sum(1 for p in periods if p == 1)
    if 100 * p1_count / len(periods) < 70:
        exit(1)

exit(0)
