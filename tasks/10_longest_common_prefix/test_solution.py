"""Unit tests for longest_common_prefix. Objective ground truth (no model judgment)."""

TOTAL = 7


def run_tests(sol):
    f = getattr(sol, "longest_common_prefix", None)
    if f is None:
        return 0, TOTAL
    cases = [
        ([], ""),
        (["flower", "flow", "flight"], "fl"),
        (["dog", "racecar", "car"], ""),
        ([""], ""),
        (["a"], "a"),
        (["", "b"], ""),
        (["interspecies", "interstellar", "interstate"], "inters"),
    ]
    passed = 0
    for strs, expected in cases:
        try:
            r = f(list(strs))
            if r == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
