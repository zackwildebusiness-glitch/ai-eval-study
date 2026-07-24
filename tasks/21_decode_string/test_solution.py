"""Unit tests for decode_string. Objective ground truth (no model judgment)."""

TOTAL = 6


def run_tests(sol):
    f = getattr(sol, "decode_string", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ("3[a]2[bc]", "aaabcbc"),
        ("3[a2[c]]", "accaccacc"),
        ("2[abc]3[cd]ef", "abcabccdcdcdef"),
        ("abc", "abc"),
        ("10[a]", "aaaaaaaaaa"),
        ("2[2[2[a]]]", "aaaaaaaa"),
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
