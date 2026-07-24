"""Unit tests for my_atoi. Objective ground truth (no model judgment)."""

TOTAL = 9


def run_tests(sol):
    f = getattr(sol, "my_atoi", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ("42", 42),
        ("   -42", -42),
        ("4193 with words", 4193),
        ("words and 987", 0),
        ("-91283472332", -2147483648),
        ("2147483648", 2147483647),
        ("+1", 1),
        ("", 0),
        ("  +0 123", 0),
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
