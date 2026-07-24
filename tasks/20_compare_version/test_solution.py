"""Unit tests for compare_version. Objective ground truth (no model judgment)."""

TOTAL = 7


def run_tests(sol):
    f = getattr(sol, "compare_version", None)
    if f is None:
        return 0, TOTAL
    cases = [
        (("1.01", "1.001"), 0),
        (("1.0", "1.0.0"), 0),
        (("0.1", "1.1"), -1),
        (("1.0.1", "1"), 1),
        (("7.5.2.4", "7.5.3"), -1),
        (("1", "1.0.0.1"), -1),
        (("2.0", "1.9.9"), 1),
    ]
    passed = 0
    for (v1, v2), expected in cases:
        try:
            r = f(v1, v2)
            if r == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
