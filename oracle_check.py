#!/usr/bin/env python3
"""
oracle_check.py - INDEPENDENT ground-truth verification for the hard-tier tasks.

`run_tests.py --validate` only proves a reference passes its OWN test cases (reference and
test could be consistently wrong together). This script proves the references are actually
correct by comparing each against a SEPARATELY-IMPLEMENTED oracle over many inputs:

  16 multiply_strings   vs  Python bignum (str(int*int))
  17 simplify_path       vs  posixpath.normpath (stdlib, independent)
  18/19 excel title<->number  round-trip inverse over 1..10000
  20 compare_version     vs  int-tuple comparison
  21 decode_string       vs  independent recursive parser
  22 valid_ipv4          vs  independent validator
  23 my_atoi             vs  independent parser + clamp

If a reference matches its independent oracle everywhere, then the hardcoded expected values
in test_solution.py (which the reference passes) are correct. Exit 0 = all ground truth verified.
"""

import importlib.util
import os
import posixpath
import random
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(ROOT, "tasks")


def ref(task):
    path = os.path.join(TASKS, task, "reference.py")
    spec = importlib.util.spec_from_file_location("ref_" + task, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---- independent oracles ----
def orc_compare_version(v1, v2):
    a = [int(x) for x in v1.split(".")]
    b = [int(x) for x in v2.split(".")]
    n = max(len(a), len(b))
    a += [0] * (n - len(a))
    b += [0] * (n - len(b))
    return (a > b) - (a < b)


def orc_decode(s):
    i = 0

    def parse():
        nonlocal i
        out = []
        while i < len(s) and s[i] != "]":
            if s[i].isdigit():
                k = 0
                while s[i].isdigit():
                    k = k * 10 + int(s[i]); i += 1
                i += 1  # skip '['
                inner = parse()
                i += 1  # skip ']'
                out.append(inner * k)
            else:
                out.append(s[i]); i += 1
        return "".join(out)

    return parse()


def orc_valid_ipv4(s):
    parts = s.split(".")
    if len(parts) != 4:
        return False
    for p in parts:
        if not p.isdigit():
            return False
        if len(p) > 1 and p[0] == "0":
            return False
        if int(p) > 255:
            return False
    return True


def orc_my_atoi(s):
    lo, hi = -2147483648, 2147483647
    i, n = 0, len(s)
    while i < n and s[i] == " ":
        i += 1
    sign = 1
    if i < n and s[i] in "+-":
        sign = -1 if s[i] == "-" else 1
        i += 1
    num = 0
    got = False
    while i < n and s[i].isdigit():
        num = num * 10 + int(s[i]); i += 1; got = True
    if not got:
        return 0
    num *= sign
    return max(lo, min(hi, num))


def check(name, fn, cases):
    bad = []
    for inp, expected in cases:
        try:
            got = fn(*inp) if isinstance(inp, tuple) else fn(inp)
        except Exception as e:
            got = "EXC:%s" % e
        if got != expected:
            bad.append((inp, expected, got))
    status = "OK" if not bad else "FAIL"
    print("  %-22s %s  (%d checks, %d mismatches)" % (name, status, len(cases), len(bad)))
    for inp, exp, got in bad[:5]:
        print("      %r -> oracle %r but reference %r" % (inp, exp, got))
    return not bad


def main():
    rng = random.Random(42)
    ok = True

    # 16 multiply_strings vs bignum
    m = ref("16_multiply_strings").multiply_strings
    cases = []
    for _ in range(400):
        a = rng.randint(0, 10 ** rng.randint(1, 15))
        b = rng.randint(0, 10 ** rng.randint(1, 15))
        cases.append(((str(a), str(b)), str(a * b)))
    ok &= check("16 multiply_strings", m, cases)

    # 17 simplify_path vs posixpath.normpath (single leading slash only)
    sp = ref("17_simplify_path").simplify_path
    segs = ["a", "b", "c", ".", "..", ""]
    cases = []
    for _ in range(400):
        k = rng.randint(1, 8)
        path = "/" + "/".join(rng.choice(segs) for _ in range(k))
        exp = posixpath.normpath(path)
        # POSIX normpath preserves a leading "//" (implementation-defined); the task spec
        # collapses all leading slashes to a single "/". Align the oracle to the spec.
        if exp.startswith("//"):
            exp = "/" + exp.lstrip("/")
        cases.append((path, exp))
    ok &= check("17 simplify_path", sp, cases)

    # 18/19 excel round-trip inverse
    title = ref("18_excel_column_title").excel_column_title
    number = ref("19_excel_column_number").excel_column_number
    cases = [((n,), n) for n in range(1, 10001)]
    ok &= check("18/19 excel round-trip", lambda n: number(title(n)), cases)

    # 20 compare_version vs int-tuple oracle
    cv = ref("20_compare_version").compare_version
    cases = []
    for _ in range(400):
        def ver():
            return ".".join(str(rng.randint(0, 20)) for _ in range(rng.randint(1, 4)))
        v1, v2 = ver(), ver()
        cases.append(((v1, v2), orc_compare_version(v1, v2)))
    ok &= check("20 compare_version", cv, cases)

    # 21 decode_string vs independent parser
    ds = ref("21_decode_string").decode_string
    curated = ["3[a]2[bc]", "3[a2[c]]", "2[abc]3[cd]ef", "abc", "10[a]",
               "2[2[2[a]]]", "", "a", "1[x]", "5[ab]"]
    cases = [(c, orc_decode(c)) for c in curated]
    ok &= check("21 decode_string", ds, cases)

    # 22 valid_ipv4 vs independent validator
    vip = ref("22_valid_ipv4").valid_ipv4
    curated = ["1.1.1.1", "0.0.0.0", "255.255.255.255", "256.1.1.1", "1.1.1",
               "01.1.1.1", "1.1.1.1.", "255.255.255.256", "1.-1.1.1",
               "00.0.0.0", "10.0.0.1", "999.1.1.1", "1.2.3", "1.2.3.4.5"]
    cases = [(c, orc_valid_ipv4(c)) for c in curated]
    ok &= check("22 valid_ipv4", vip, cases)

    # 23 my_atoi vs independent parser
    ma = ref("23_my_atoi").my_atoi
    curated = ["42", "   -42", "4193 with words", "words and 987", "-91283472332",
               "2147483648", "+1", "", "  +0 123", "-2147483648", "2147483647",
               "  -000123abc", "+-12", "   ", "3.14"]
    cases = [(c, orc_my_atoi(c)) for c in curated]
    ok &= check("23 my_atoi", ma, cases)

    print("\nORACLE CHECK %s" % ("PASS - ground truth independently verified" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
