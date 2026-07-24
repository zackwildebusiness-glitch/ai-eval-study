"""Unit tests for simplify_path. Objective ground truth (no model judgment)."""

TOTAL = 7


def run_tests(sol):
    f = getattr(sol, "simplify_path", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ("/home/", "/home"),
        ("/../", "/"),
        ("/home//foo/", "/home/foo"),
        ("/a/./b/../../c/", "/c"),
        ("/a/../../b/../c//.//", "/c"),
        ("/", "/"),
        ("/...", "/..."),
    ]
    passed = 0
    for path, expected in cases:
        try:
            r = f(path)
            if r == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
