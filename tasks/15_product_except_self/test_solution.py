"""Unit tests for product_except_self. Objective ground truth (no model judgment)."""

TOTAL = 6


def run_tests(sol):
    f = getattr(sol, "product_except_self", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ([1, 2, 3, 4], [24, 12, 8, 6]),
        ([-1, 1, 0, -3, 3], [0, 0, 9, 0, 0]),
        ([1, 2], [2, 1]),
        ([0, 0], [0, 0]),
        ([2, 3, 4, 5], [60, 40, 30, 24]),
        ([-2, -3, -4], [12, 8, 6]),
    ]
    passed = 0
    for nums, expected in cases:
        try:
            r = f(list(nums))
            if list(r) == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
