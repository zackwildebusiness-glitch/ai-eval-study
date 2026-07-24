"""Unit tests for fizzbuzz. Objective ground truth (no model judgment)."""

TOTAL = 6


def run_tests(sol):
    f = getattr(sol, "fizzbuzz", None)
    if f is None:
        return 0, TOTAL
    cases = [
        (1, ["1"]),
        (3, ["1", "2", "Fizz"]),
        (5, ["1", "2", "Fizz", "4", "Buzz"]),
        (15, ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
              "11", "Fizz", "13", "14", "FizzBuzz"]),
        (16, ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
              "11", "Fizz", "13", "14", "FizzBuzz", "16"]),
        (2, ["1", "2"]),
    ]
    passed = 0
    for n, expected in cases:
        try:
            r = f(n)
            if r == expected:
                passed += 1
        except Exception:
            pass
    return passed, TOTAL
