"""Unit tests for valid_parentheses. Objective ground truth (no model judgment)."""

TOTAL = 8


def run_tests(sol):
    f = getattr(sol, "valid_parentheses", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ("", True),
        ("()", True),
        ("()[]{}", True),
        ("(]", False),
        ("([)]", False),
        ("{[]}", True),
        ("(", False),
        ("((()))", True),
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
