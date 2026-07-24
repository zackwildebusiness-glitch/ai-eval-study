"""Unit tests for valid_ipv4. Objective ground truth (no model judgment)."""

TOTAL = 9


def run_tests(sol):
    f = getattr(sol, "valid_ipv4", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ("1.1.1.1", True),
        ("0.0.0.0", True),
        ("255.255.255.255", True),
        ("256.1.1.1", False),
        ("1.1.1", False),
        ("01.1.1.1", False),
        ("1.1.1.1.", False),
        ("255.255.255.256", False),
        ("1.-1.1.1", False),
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
