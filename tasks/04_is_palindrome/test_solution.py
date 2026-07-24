"""Unit tests for is_palindrome. Objective ground truth (no model judgment)."""

TOTAL = 7


def run_tests(sol):
    f = getattr(sol, "is_palindrome", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ("", True),
        ("a", True),
        ("A man, a plan, a canal: Panama", True),
        ("race a car", False),
        ("Was it a car or a cat I saw?", True),
        ("0P", False),
        ("ab_a", True),
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
