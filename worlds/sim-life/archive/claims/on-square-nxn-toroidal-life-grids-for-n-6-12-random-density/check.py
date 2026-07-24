import sys
import cyc

def check():
    total_odd = 0
    total_trials = 0

    # Reproduce the N=6..12 sweep
    for N in range(6, 13):
        periods, _, fails = cyc.spectrum(range(810000, 810150), N, N, p=0.5, cap=8000)
        if fails:
            print(f"N={N}: {len(fails)} soups failed to converge within cap")
            return False
        for k, v in periods.items():
            total_trials += v
            if k % 2 == 1 and k > 1:
                total_odd += v
                print(f"N={N}: found odd period {k} x{v} occurrences")

    # Reproduce the original 9x9 / 13x13 sweep
    for (W, H) in [(9, 9), (13, 13)]:
        periods, _, fails = cyc.spectrum(range(800000, 800300), W, H, p=0.5, cap=6000)
        if fails:
            print(f"{W}x{H}: {len(fails)} soups failed to converge within cap")
            return False
        for k, v in periods.items():
            total_trials += v
            if k % 2 == 1 and k > 1:
                total_odd += v
                print(f"{W}x{H}: found odd period {k} x{v} occurrences")

    print(f"total trials={total_trials}, odd(>1) periods found={total_odd}")
    return total_odd == 0

if __name__ == "__main__":
    sys.exit(0 if check() else 1)
