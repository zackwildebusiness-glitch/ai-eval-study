"""Unit tests for length_of_longest_substring. Objective ground truth (no model judgment)."""

TOTAL = 7


def run_tests(sol):
    f = getattr(sol, "length_of_longest_substring", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ("", 0),
        ("a", 1),
        ("abcabcbb", 3),
        ("bbbbb", 1),
        ("pwwkew", 3),
        ("dvdf", 3),
        ("abba", 2),
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
