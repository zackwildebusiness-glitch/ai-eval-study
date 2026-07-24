"""Unit tests for excel_column_number. Objective ground truth (no model judgment)."""

TOTAL = 8


def run_tests(sol):
    f = getattr(sol, "excel_column_number", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ("A", 1),
        ("Z", 26),
        ("AA", 27),
        ("AB", 28),
        ("AZ", 52),
        ("ZY", 701),
        ("ZZ", 702),
        ("AAA", 703),
    ]
    passed = 0
    for s, expected in cases:
        try:
            r = f(s)
            if r == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
