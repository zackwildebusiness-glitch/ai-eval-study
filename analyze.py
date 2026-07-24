#!/usr/bin/env python3
"""
analyze.py - analysis engine for a solo coding-model evaluation study.

Input: long-format CSV with columns
    task_id, model, dimension, human_score, judge_score, tests_passed, tests_total
Each row = one model's output on one task, scored on one rubric dimension by the
human and by an LLM-judge, plus that task's objective unit-test result.

Outputs (stdout + eval-report.md):
  1. Winner per source (human mean / judge mean / objective test pass-rate) per model
  2. Human-vs-judge quadratic-weighted Cohen's kappa (overall + per dimension) + exact-agreement %
  3. Judge-vs-tests contradictions (judge >= 4 but the output failed its tests)

Pure standard library. No sklearn / pandas / numpy required.

Usage:
    python analyze.py <scores.csv>
    python analyze.py --selftest
"""

import csv
import sys
from collections import defaultdict, OrderedDict

CATEGORIES = [1, 2, 3, 4, 5]  # ordinal rubric scale


# ---------------------------------------------------------------------------
# Weighted Cohen's kappa (quadratic weights), implemented from scratch.
# kappa = 1 - (sum w_ij * O_ij) / (sum w_ij * E_ij)
#   w_ij = (cat_i - cat_j)^2 / (k-1)^2   (quadratic; 0 on diagonal, 1 at extremes)
#   O_ij = observed joint proportion,  E_ij = product of marginals
# Returns None when kappa is undefined (no expected disagreement -> no variance).
# ---------------------------------------------------------------------------
def weighted_cohen_kappa(pairs, categories=CATEGORIES):
    n = len(pairs)
    if n == 0:
        return None
    idx = {c: i for i, c in enumerate(categories)}
    k = len(categories)
    denom = (k - 1) ** 2

    # weight matrix
    w = [[((categories[i] - categories[j]) ** 2) / denom for j in range(k)] for i in range(k)]

    # observed joint counts
    O = [[0.0] * k for _ in range(k)]
    row_marg = [0.0] * k
    col_marg = [0.0] * k
    for h, j in pairs:
        if h not in idx or j not in idx:
            raise ValueError("score %r/%r outside categories %r" % (h, j, categories))
        a, b = idx[h], idx[j]
        O[a][b] += 1.0
        row_marg[a] += 1.0
        col_marg[b] += 1.0

    # normalise to proportions
    for i in range(k):
        row_marg[i] /= n
        col_marg[i] /= n
        for j in range(k):
            O[i][j] /= n

    do = sum(w[i][j] * O[i][j] for i in range(k) for j in range(k))
    de = sum(w[i][j] * row_marg[i] * col_marg[j] for i in range(k) for j in range(k))

    if de == 0:
        return None  # undefined: raters put everything in one cell / no variance
    return 1.0 - do / de


def exact_agreement(pairs):
    if not pairs:
        return None
    same = sum(1 for h, j in pairs if h == j)
    return same / len(pairs)


def fmt_kappa(k):
    if k is None:
        return "undefined (no variance)"
    return "%.3f" % k


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------
REQUIRED = ["task_id", "model", "dimension", "human_score", "judge_score",
            "tests_passed", "tests_total"]


def _opt_int(v):
    """Parse an optional integer; blank/missing -> None (score not yet supplied)."""
    if v is None:
        return None
    v = str(v).strip()
    if v == "":
        return None
    return int(v)


def load_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError("CSV missing required columns: %s" % ", ".join(missing))
        for i, r in enumerate(reader, start=2):
            try:
                rows.append({
                    "task_id": r["task_id"].strip(),
                    "model": r["model"].strip(),
                    "dimension": r["dimension"].strip(),
                    "human_score": _opt_int(r["human_score"]),
                    "judge_score": _opt_int(r["judge_score"]),
                    "tests_passed": int(r["tests_passed"]),
                    "tests_total": int(r["tests_total"]),
                })
            except (ValueError, KeyError) as e:
                raise ValueError("bad data on CSV line %d: %s" % (i, e))
    if not rows:
        raise ValueError("no data rows in %s" % path)
    return rows


# ---------------------------------------------------------------------------
# Analyses
# ---------------------------------------------------------------------------
def winners_per_source(rows):
    by_model_human = defaultdict(list)
    by_model_judge = defaultdict(list)
    # dedupe test results to one per (task, model) so repeated dimension rows
    # don't multi-count the same unit-test run
    test_by_task_model = {}
    for r in rows:
        if r["human_score"] is not None:
            by_model_human[r["model"]].append(r["human_score"])
        if r["judge_score"] is not None:
            by_model_judge[r["model"]].append(r["judge_score"])
        key = (r["task_id"], r["model"])
        if key not in test_by_task_model:
            test_by_task_model[key] = (r["tests_passed"], r["tests_total"])

    models = sorted(set(r["model"] for r in rows))
    out = OrderedDict()
    for m in models:
        hp = by_model_human[m]
        jp = by_model_judge[m]
        passed = sum(p for (t, mm), (p, tot) in test_by_task_model.items() if mm == m)
        total = sum(tot for (t, mm), (p, tot) in test_by_task_model.items() if mm == m)
        out[m] = {
            "human_mean": sum(hp) / len(hp) if hp else None,
            "judge_mean": sum(jp) / len(jp) if jp else None,
            "test_pass_rate": (passed / total) if total else None,
            "tests_passed": passed,
            "tests_total": total,
        }
    return out, models


def _winner(stats, models, key, higher_better=True):
    vals = [(m, stats[m][key]) for m in models if stats[m][key] is not None]
    if len(vals) < 2:
        return None, None
    vals.sort(key=lambda x: x[1], reverse=higher_better)
    top, second = vals[0], vals[1]
    if abs(top[1] - second[1]) < 1e-12:
        return "tie", 0.0
    return top[0], top[1] - second[1]


def agreement_analysis(rows):
    def both(r):
        return r["human_score"] is not None and r["judge_score"] is not None

    overall = [(r["human_score"], r["judge_score"]) for r in rows if both(r)]
    by_dim = defaultdict(list)
    for r in rows:
        if both(r):
            by_dim[r["dimension"]].append((r["human_score"], r["judge_score"]))
    result = {
        "overall_kappa": weighted_cohen_kappa(overall),
        "overall_exact": exact_agreement(overall),
        "n": len(overall),
        "per_dimension": OrderedDict(),
    }
    for dim in sorted(by_dim):
        pairs = by_dim[dim]
        result["per_dimension"][dim] = {
            "kappa": weighted_cohen_kappa(pairs),
            "exact": exact_agreement(pairs),
            "n": len(pairs),
        }
    return result


def contradictions(rows):
    """Judge rated the output highly (>=4) but it objectively failed its tests."""
    out = []
    for r in rows:
        if r["judge_score"] is not None and r["judge_score"] >= 4 and r["tests_passed"] < r["tests_total"]:
            out.append(r)
    return out


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def build_report(rows):
    stats, models = winners_per_source(rows)
    agree = agreement_analysis(rows)
    contra = contradictions(rows)

    lines = []
    p = lines.append
    p("# Evaluation Report\n")
    p("Rows scored: %d  |  Models: %s\n" % (len(rows), ", ".join(models)))

    p("## 1. Winner per judgment source\n")
    p("| Model | Human mean | Judge mean | Test pass-rate |")
    p("|---|---|---|---|")
    for m in models:
        s = stats[m]
        p("| %s | %s | %s | %s (%d/%d) |" % (
            m,
            "%.2f" % s["human_mean"] if s["human_mean"] is not None else "-",
            "%.2f" % s["judge_mean"] if s["judge_mean"] is not None else "-",
            "%.1f%%" % (100 * s["test_pass_rate"]) if s["test_pass_rate"] is not None else "-",
            s["tests_passed"], s["tests_total"],
        ))
    p("")
    for label, key, hb in [("Human", "human_mean", True),
                           ("Judge", "judge_mean", True),
                           ("Tests", "test_pass_rate", True)]:
        win, margin = _winner(stats, models, key, hb)
        if win is None:
            p("- **%s:** not enough models to compare." % label)
        elif win == "tie":
            p("- **%s:** tie." % label)
        else:
            p("- **%s winner:** %s (margin %.3f)" % (label, win, margin))
    p("")

    p("## 2. Human vs LLM-judge agreement\n")
    if agree["n"] == 0:
        p("_Pending: no human ratings supplied yet. Fill `results/human_sheet.csv`, "
          "re-run `merge_scores.py`, then re-run this report to get human-vs-judge kappa._\n")
    p("Quadratic-weighted Cohen's kappa (corrects for chance); exact = identical score.\n")
    p("- **Overall:** kappa = %s, exact agreement = %s  (n=%d)" % (
        fmt_kappa(agree["overall_kappa"]),
        "%.1f%%" % (100 * agree["overall_exact"]) if agree["overall_exact"] is not None else "-",
        agree["n"],
    ))
    p("")
    p("| Dimension | n | Weighted kappa | Exact agreement |")
    p("|---|---|---|---|")
    for dim, d in agree["per_dimension"].items():
        p("| %s | %d | %s | %s |" % (
            dim, d["n"], fmt_kappa(d["kappa"]),
            "%.1f%%" % (100 * d["exact"]) if d["exact"] is not None else "-",
        ))
    p("\n_Kappa guide: <0 worse than chance, 0-.2 slight, .2-.4 fair, .4-.6 moderate, .6-.8 substantial, .8-1 near-perfect._\n")

    p("## 3. Judge-vs-tests contradictions (the headline finding)\n")
    if not contra:
        p("None: the judge never rated a test-failing output >= 4. (Either strong judge, or few failing outputs.)\n")
    else:
        p("Cases where the LLM-judge scored an output >= 4 while its unit tests objectively failed:\n")
        p("| Task | Model | Dimension | Judge score | Tests |")
        p("|---|---|---|---|---|")
        for r in contra:
            p("| %s | %s | %s | %d | %d/%d |" % (
                r["task_id"], r["model"], r["dimension"],
                r["judge_score"], r["tests_passed"], r["tests_total"],
            ))
        p("\n**%d contradiction rows** - each is direct evidence of an LLM-judge failure mode "
          "(fluent-but-wrong code the judge rewarded). This is the finding eval teams care about most.\n"
          % len(contra))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-test: constructed dataset with a hand-verified weighted kappa.
# ---------------------------------------------------------------------------
def _selftest():
    ok = True

    # Test A: perfect agreement (with variance) -> kappa = 1.0
    perfect = [(1, 1), (5, 5), (3, 3), (1, 1), (5, 5)]
    ka = weighted_cohen_kappa(perfect)
    print("  perfect-agreement kappa = %s (expect 1.000)" % fmt_kappa(ka))
    ok &= (ka is not None and abs(ka - 1.0) < 1e-9)

    # Test B: hand-computed case. Ratings in {1,5} only, so quadratic weight
    # between them = (4^2)/(4^2) = 1, reducing to a 2-category problem.
    #   both=1: 4,  both=5: 4,  (h1,j5): 1,  (h5,j1): 1   (N=10)
    #   marginals all 0.5 -> Do = 0.2, De = 0.5 -> kappa = 1 - 0.4 = 0.600
    hand = ([(1, 1)] * 4) + ([(5, 5)] * 4) + [(1, 5)] + [(5, 1)]
    kb = weighted_cohen_kappa(hand)
    print("  hand-computed kappa     = %s (expect 0.600)" % fmt_kappa(kb))
    ok &= (kb is not None and abs(kb - 0.600) < 0.01)

    # Test C: no variance (all identical) -> undefined, must not crash/NaN
    flat = [(3, 3)] * 6
    kc = weighted_cohen_kappa(flat)
    print("  no-variance kappa       = %s (expect undefined)" % fmt_kappa(kc))
    ok &= (kc is None)

    # Test D: contradiction detection
    rows = [
        {"task_id": "t1", "model": "A", "dimension": "correctness",
         "human_score": 2, "judge_score": 5, "tests_passed": 3, "tests_total": 5},
        {"task_id": "t2", "model": "B", "dimension": "correctness",
         "human_score": 5, "judge_score": 5, "tests_passed": 5, "tests_total": 5},
    ]
    c = contradictions(rows)
    print("  contradictions found    = %d (expect 1)" % len(c))
    ok &= (len(c) == 1 and c[0]["task_id"] == "t1")

    print("\nSELFTEST %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def _write_sample(path):
    rows = [
        # task, model, dimension, human, judge, tp, tt
        ("t1", "A", "correctness", 5, 5, 5, 5),
        ("t1", "A", "completeness", 4, 4, 5, 5),
        ("t1", "B", "correctness", 2, 4, 2, 5),   # judge liked it, tests failed
        ("t1", "B", "completeness", 2, 3, 2, 5),
        ("t2", "A", "correctness", 4, 3, 4, 4),
        ("t2", "A", "completeness", 4, 4, 4, 4),
        ("t2", "B", "correctness", 5, 5, 4, 4),
        ("t2", "B", "completeness", 3, 4, 4, 4),
        ("t3", "A", "correctness", 3, 2, 3, 4),
        ("t3", "A", "completeness", 3, 3, 3, 4),
        ("t3", "B", "correctness", 5, 5, 4, 4),
        ("t3", "B", "completeness", 4, 5, 4, 4),
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(REQUIRED)
        for r in rows:
            wr.writerow(r)


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[1] == "--selftest":
        print("Running self-test...")
        return _selftest()
    if argv[1] == "--make-sample":
        _write_sample("sample_scores.csv")
        print("wrote sample_scores.csv")
        return 0

    path = argv[1]
    rows = load_rows(path)
    report = build_report(rows)
    print(report)
    with open("eval-report.md", "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print("\n[wrote eval-report.md]")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
