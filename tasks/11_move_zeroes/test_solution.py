"""Unit tests for move_zeroes. Objective ground truth (no model judgment)."""

TOTAL = 6


def run_tests(sol):
    f = getattr(sol, "move_zeroes", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ([0, 1, 0, 3, 12], [1, 3, 12, 0, 0]),
        ([0], [0]),
        ([], []),
        ([1, 2, 3], [1, 2, 3]),
        ([0, 0, 0], [0, 0, 0]),
        ([4, 0, 5, 0, 0, 6], [4, 5, 6, 0, 0, 0]),
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
