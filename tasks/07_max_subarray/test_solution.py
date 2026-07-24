"""Unit tests for max_subarray. Objective ground truth (no model judgment)."""

TOTAL = 7


def run_tests(sol):
    f = getattr(sol, "max_subarray", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6),
        ([1], 1),
        ([5, 4, -1, 7, 8], 23),
        ([-1], -1),
        ([-3, -2, -1], -1),
        ([0, 0, 0], 0),
        ([-2, -1], -1),
    ]
    passed = 0
    for nums, expected in cases:
        try:
            r = f(list(nums))
            if r == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
