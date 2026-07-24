"""Unit tests for spiral_order. Objective ground truth (no model judgment)."""

TOTAL = 6


def run_tests(sol):
    f = getattr(sol, "spiral_order", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ([], []),
        ([[1]], [1]),
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [1, 2, 3, 6, 9, 8, 7, 4, 5]),
        ([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
         [1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]),
        ([[1], [2], [3]], [1, 2, 3]),
        ([[1, 2, 3]], [1, 2, 3]),
    ]
    passed = 0
    for matrix, expected in cases:
        try:
            r = f([list(row) for row in matrix])
            if list(r) == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
