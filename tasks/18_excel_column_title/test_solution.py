"""Unit tests for excel_column_title. Objective ground truth (no model judgment)."""

TOTAL = 8


def run_tests(sol):
    f = getattr(sol, "excel_column_title", None)
    if f is None:
        return 0, TOTAL
    cases = [
        (1, "A"),
        (26, "Z"),
        (27, "AA"),
        (28, "AB"),
        (52, "AZ"),
        (701, "ZY"),
        (702, "ZZ"),
        (703, "AAA"),
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
