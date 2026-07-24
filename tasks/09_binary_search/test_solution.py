"""Unit tests for binary_search. Objective ground truth (no model judgment)."""

TOTAL = 7


def run_tests(sol):
    f = getattr(sol, "binary_search", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ([], 5, [-1]),
        ([1], 1, [0]),
        ([1], 2, [-1]),
        ([-5, -3, 0, 2, 7, 11], 7, [4]),
        ([-5, -3, 0, 2, 7, 11], -5, [0]),
        ([-5, -3, 0, 2, 7, 11], 5, [-1]),
        ([1, 2, 2, 2, 3], 2, [1, 2, 3]),  # duplicates: any matching index is fine
    ]
    passed = 0
    for arr, target, acceptable in cases:
        try:
            r = f(list(arr), target)
            if r in acceptable:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
