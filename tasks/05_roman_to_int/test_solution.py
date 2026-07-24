"""Unit tests for roman_to_int. Objective ground truth (no model judgment)."""

TOTAL = 8


def run_tests(sol):
    f = getattr(sol, "roman_to_int", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ("I", 1),
        ("III", 3),
        ("IV", 4),
        ("IX", 9),
        ("LVIII", 58),
        ("MCMXCIV", 1994),
        ("MMMCMXCIX", 3999),
        ("XL", 40),
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
