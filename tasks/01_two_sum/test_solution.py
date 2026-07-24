"""Unit tests for two_sum. Objective ground truth (no model judgment)."""

TOTAL = 6


def run_tests(sol):
    f = getattr(sol, "two_sum", None)
    if f is None:
        return 0, TOTAL
    cases = [
        (([2, 7, 11, 15], 9), [0, 1]),
        (([3, 2, 4], 6), [1, 2]),
        (([3, 3], 6), [0, 1]),
        (([1, 2, 3, 4, 5], 9), [3, 4]),
        (([0, 4, 3, 0], 0), [0, 3]),
        (([-1, -2, -3, -4, -5], -8), [2, 4]),
    ]
    passed = 0
    for (arr, target), expected in cases:
        try:
            r = f(list(arr), target)
            if r is not None and sorted(r) == sorted(expected):
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
