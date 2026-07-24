"""Unit tests for climb_stairs. Objective ground truth (no model judgment)."""

TOTAL = 6


def run_tests(sol):
    f = getattr(sol, "climb_stairs", None)
    if f is None:
        return 0, TOTAL
    cases = [
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 5),
        (5, 8),
        (10, 89),
    ]
    passed = 0
    for n, expected in cases:
        try:
            r = f(n)
            if r == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
