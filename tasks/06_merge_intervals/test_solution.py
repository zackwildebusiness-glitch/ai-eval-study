"""Unit tests for merge_intervals. Objective ground truth (no model judgment)."""

TOTAL = 7


def run_tests(sol):
    f = getattr(sol, "merge_intervals", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ([], []),
        ([[1, 3]], [[1, 3]]),
        ([[1, 3], [2, 6], [8, 10], [15, 18]], [[1, 6], [8, 10], [15, 18]]),
        ([[1, 4], [4, 5]], [[1, 5]]),
        ([[1, 4], [0, 4]], [[0, 4]]),
        ([[1, 4], [2, 3]], [[1, 4]]),
        ([[5, 6], [1, 2], [3, 4]], [[1, 2], [3, 4], [5, 6]]),
    ]
    passed = 0
    for intervals, expected in cases:
        try:
            r = f([list(iv) for iv in intervals])
            norm = sorted([list(iv) for iv in r])
            if norm == sorted(expected):
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
