"""Unit tests for multiply_strings. Objective ground truth (no model judgment)."""

TOTAL = 7


def run_tests(sol):
    f = getattr(sol, "multiply_strings", None)
    if f is None:
        return 0, TOTAL
    cases = [
        (("2", "3"), "6"),
        (("123", "456"), "56088"),
        (("0", "99999"), "0"),
        (("99", "99"), "9801"),
        (("123456789", "987654321"), "121932631112635269"),
        (("0", "0"), "0"),
        (("1", "1"), "1"),
    ]
    passed = 0
    for (num1, num2), expected in cases:
        try:
            r = f(num1, num2)
            if r == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
