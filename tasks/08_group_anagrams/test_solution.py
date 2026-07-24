"""Unit tests for group_anagrams. Objective ground truth (no model judgment)."""

TOTAL = 6


def normalize(groups):
    # sort within each group, then sort the list of groups, so order never matters.
    return sorted(sorted(g) for g in groups)


def run_tests(sol):
    f = getattr(sol, "group_anagrams", None)
    if f is None:
        return 0, TOTAL
    cases = [
        (["eat", "tea", "tan", "ate", "nat", "bat"],
         [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]),
        ([""], [[""]]),
        (["a"], [["a"]]),
        ([], []),
        (["abc", "cba", "bac", "xyz"], [["abc", "cba", "bac"], ["xyz"]]),
        (["ab", "ba", "ab"], [["ab", "ba", "ab"]]),
    ]
    passed = 0
    for words, expected in cases:
        try:
            r = f(list(words))
            if normalize(r) == normalize(expected):
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
