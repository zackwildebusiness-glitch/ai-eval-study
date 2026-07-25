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


def kappa_label(k):
    """Landis & Koch style band. Reported alongside the number so a reader is
    not left to guess whether 0.79 is good; the bands are conventional, not a
    property of this data."""
    if k is None:
        return "undefined"
    if k < 0:
        return "worse than chance"
    if k < 0.2:
        return "slight"
    if k < 0.4:
        return "fair"
    if k < 0.6:
        return "moderate"
    if k < 0.8:
        return "substantial"
    return "near-perfect"


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
# Arms that are seeded controls, not models under test. Their solutions carry
# deliberate known bugs, so including them in the model comparison would be
# meaningless (they are engineered to fail). They ARE included in the agreement
# and contradiction analyses -- that is the whole reason they exist: they supply
# the quality variance that makes weighted kappa computable and gives the judge
# something it can be caught missing.
CONTROL_ARMS = frozenset({"planted"})


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

    arms = sorted(set(r["model"] for r in rows))
    models = [m for m in arms if m not in CONTROL_ARMS]
    controls = [m for m in arms if m in CONTROL_ARMS]
    out = OrderedDict()
    for m in arms:
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
    return out, models, controls


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


JUDGE_CORRECT_MIN = 4   # judge correctness >= this == "the judge says this is correct"


def judge_vs_tests_kappa(rows):
    """Cohen's kappa between the LLM judge and the unit tests.

    The two raters are the judge and the test suite, both answering one binary
    question: is this solution correct? The judge says yes at correctness >= 4;
    the tests say yes when every test passes.

    This needs NO human rater, which is the point -- it was computable from data
    already collected. Returns (kappa, cells, po, pe) with cells as a dict of
    the 2x2, or (None, cells, po, None) when kappa is undefined (a rater with no
    variance drives expected agreement to 1).

    CAVEAT, and it must travel with the number: kappa is prevalence-dependent
    and this pool is deliberately enriched with seeded bad solutions, so the
    result describes agreement ON THIS POOL, not on naturally occurring code.
    """
    pairs = []
    for r in rows:
        if r["dimension"] != "correctness" or r["judge_score"] is None:
            continue
        if r["tests_total"] is None or r["tests_total"] <= 0:
            continue
        judge_ok = 1 if r["judge_score"] >= JUDGE_CORRECT_MIN else 0
        tests_ok = 1 if r["tests_passed"] == r["tests_total"] else 0
        pairs.append((judge_ok, tests_ok))

    n = len(pairs)
    cells = {
        "both_correct": sum(1 for j, t in pairs if j == 1 and t == 1),
        "false_pass": sum(1 for j, t in pairs if j == 1 and t == 0),
        "false_alarm": sum(1 for j, t in pairs if j == 0 and t == 1),
        "both_broken": sum(1 for j, t in pairs if j == 0 and t == 0),
        "n": n,
    }
    if n == 0:
        return None, cells, None, None

    po = (cells["both_correct"] + cells["both_broken"]) / n
    p_judge = (cells["both_correct"] + cells["false_pass"]) / n
    p_tests = (cells["both_correct"] + cells["false_alarm"]) / n
    pe = p_judge * p_tests + (1 - p_judge) * (1 - p_tests)
    if abs(1 - pe) < 1e-12:
        return None, cells, po, pe
    return (po - pe) / (1 - pe), cells, po, pe


def planted_detection(rows):
    """How often did the judge catch a seeded known-bad solution?

    Counts one item per (task, control-arm) pair, using the judge's `correctness`
    score. 'Caught' means correctness <= 3 -- the judge signalled doubt. 'Missed'
    means correctness >= 4 on code that is known to fail its own unit tests.
    Returns (caught, missed, items) where items is a list of per-task detail.
    """
    items = []
    for r in rows:
        if r["model"] not in CONTROL_ARMS or r["dimension"] != "correctness":
            continue
        if r["judge_score"] is None:
            continue
        items.append({
            "task_id": r["task_id"],
            "arm": r["model"],
            "judge_correctness": r["judge_score"],
            "tests_passed": r["tests_passed"],
            "tests_total": r["tests_total"],
            "caught": r["judge_score"] <= 3,
        })
    items.sort(key=lambda d: d["task_id"])
    caught = sum(1 for d in items if d["caught"])
    return caught, len(items) - caught, items


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def build_report(rows):
    stats, models, controls = winners_per_source(rows)
    agree = agreement_analysis(rows)
    contra = contradictions(rows)

    lines = []
    p = lines.append
    p("# Evaluation Report\n")
    p("Rows scored: %d  |  Models under test: %s%s\n" % (
        len(rows),
        ", ".join(models) if models else "(none)",
        "  |  Control arms: %s" % ", ".join(controls) if controls else "",
    ))

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

    if controls:
        p("### Control arm (seeded known-bad code -- NOT a competitor)\n")
        p("| Arm | Judge mean | Test pass-rate |")
        p("|---|---|---|")
        for c in controls:
            s = stats[c]
            p("| %s | %s | %s (%d/%d) |" % (
                c,
                "%.2f" % s["judge_mean"] if s["judge_mean"] is not None else "-",
                "%.1f%%" % (100 * s["test_pass_rate"]) if s["test_pass_rate"] is not None else "-",
                s["tests_passed"], s["tests_total"],
            ))
        p("\nThese solutions carry deliberate, documented bugs (see `planted_bugs.csv`) and are "
          "excluded from the winner comparison above. Their purpose is to create genuine quality "
          "variance: they give the judge something it can be caught missing, and they are what "
          "makes the agreement statistics below meaningful. **A high judge mean on this arm is "
          "itself the finding** -- it means the judge rewarded code that objectively fails its tests.\n")

    jk, jcells, jpo, jpe = judge_vs_tests_kappa(rows)
    if jcells["n"] > 0:
        p("## 2. Judge vs unit tests -- Cohen's kappa\n")
        p("Two raters, one binary question: is this solution correct? The judge says yes at "
          "correctness >= %d; the tests say yes when every test passes. **No human rater is "
          "needed for this statistic.**\n" % JUDGE_CORRECT_MIN)
        p("| | tests say correct | tests say broken |")
        p("|---|---|---|")
        p("| **judge says correct** | %d | **%d** |" % (jcells["both_correct"], jcells["false_pass"]))
        p("| **judge says broken** | %d | %d |" % (jcells["false_alarm"], jcells["both_broken"]))
        p("")
        if jk is None:
            p("- kappa = undefined (a rater showed no variance). n=%d\n" % jcells["n"])
        else:
            p("- Observed agreement **%.1f%%**, chance agreement **%.1f%%** -> **kappa = %.3f** (%s). n=%d"
              % (100 * jpo, 100 * jpe, jk, kappa_label(jk), jcells["n"]))
            p("- **%d false passes** (judge cleared code its tests fail) and **%d false alarms** "
              "(judge doubted code that passes)." % (jcells["false_pass"], jcells["false_alarm"]))
            if jcells["false_alarm"] == 0 and jcells["false_pass"] > 0:
                p("- The asymmetry is the finding: this judge is **conservative in the dangerous "
                  "direction** -- it waves broken code through rather than raising false alarms.")
        p("\n> **Two caveats that must travel with this number.** (1) kappa is *prevalence-dependent* "
          "and this pool is deliberately enriched with seeded bad solutions, so it describes "
          "agreement **on this pool**, not on naturally occurring code. (2) This analysis was "
          "**not pre-registered** -- `PROTOCOL.md` specified a human-vs-judge kappa; this "
          "judge-vs-tests kappa is post-hoc.\n")

    p("## 3. Human vs LLM-judge agreement\n")
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
        seeded = [r for r in contra if r["model"] in CONTROL_ARMS]
        organic = [r for r in contra if r["model"] not in CONTROL_ARMS]
        p("\n**%d contradiction rows** - each is direct evidence of an LLM-judge failure mode "
          "(fluent-but-wrong code the judge rewarded). This is the finding eval teams care about most."
          % len(contra))
        p("- %d on seeded control code (deliberate known bugs)." % len(seeded))
        p("- %d on genuine model output (an unprompted judge miss)." % len(organic))
        p("")

    caught, missed, items = planted_detection(rows)
    if items:
        p("## 4. Planted-bug detection rate (judge sensitivity)\n")
        p("Each row is one seeded solution with a documented deliberate bug that fails its unit "
          "tests. 'Caught' = the judge gave correctness <= 3. 'Missed' = the judge gave >= 4 to "
          "code it should have doubted.\n")
        p("**Judge caught %d of %d (%.0f%%); missed %d (%.0f%%).**\n" % (
            caught, len(items), 100.0 * caught / len(items),
            missed, 100.0 * missed / len(items),
        ))
        p("| Task | Judge correctness | Tests | Verdict |")
        p("|---|---|---|---|")
        for d in items:
            p("| %s | %d | %d/%d | %s |" % (
                d["task_id"], d["judge_correctness"],
                d["tests_passed"], d["tests_total"],
                "caught" if d["caught"] else "**MISSED**",
            ))
        p("\nUnlike the ceiling-clustering result, this number is unambiguous: the ground truth is "
          "known by construction, so a miss cannot be explained away as the code genuinely being "
          "good.\n")

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

    # Test E: control arms are excluded from the model comparison but still
    # counted in contradictions. A control arm must never be crowned "winner",
    # and must not suppress a real tie between the two models under test.
    ctrl_rows = [
        {"task_id": "t1", "model": "opus", "dimension": "correctness",
         "human_score": None, "judge_score": 5, "tests_passed": 5, "tests_total": 5},
        {"task_id": "t1", "model": "sonnet", "dimension": "correctness",
         "human_score": None, "judge_score": 5, "tests_passed": 5, "tests_total": 5},
        {"task_id": "t1", "model": "planted", "dimension": "correctness",
         "human_score": None, "judge_score": 5, "tests_passed": 3, "tests_total": 5},
    ]
    stats, models, controls = winners_per_source(ctrl_rows)
    print("  comparison models       = %s (expect ['opus', 'sonnet'])" % models)
    ok &= (models == ["opus", "sonnet"] and controls == ["planted"])
    win, _ = _winner(stats, models, "test_pass_rate", True)
    print("  winner w/ control arm   = %s (expect tie)" % win)
    ok &= (win == "tie")
    ok &= ("planted" in stats)  # control stats still computed, just reported apart

    # Test F: planted detection counts a >=4 correctness score on failing code
    # as MISSED, and a <=3 score as caught.
    det_rows = ctrl_rows + [
        {"task_id": "t2", "model": "planted", "dimension": "correctness",
         "human_score": None, "judge_score": 2, "tests_passed": 1, "tests_total": 4},
        {"task_id": "t2", "model": "planted", "dimension": "code_quality",
         "human_score": None, "judge_score": 5, "tests_passed": 1, "tests_total": 4},
    ]
    caught, missed, items = planted_detection(det_rows)
    print("  planted caught/missed   = %d/%d (expect 1/1 over 2 items)" % (caught, missed))
    ok &= (caught == 1 and missed == 1 and len(items) == 2)

    # Test G: judge-vs-tests kappa, hand-computed.
    #   2x2: both_correct=46, false_pass=3, false_alarm=0, both_broken=7 (n=56)
    #   Po = 53/56 = .946429
    #   p_judge = 49/56 = .875 ; p_tests = 46/56 = .821429
    #   Pe = .875*.821429 + .125*.178571 = .718750 + .022321 = .741071
    #   k  = (.946429 - .741071) / (1 - .741071) = .205357/.258929 = .793103
    g_rows = []
    def _row(dim, judge, tp, tt):
        return {"task_id": "t", "model": "m", "dimension": dim,
                "human_score": None, "judge_score": judge,
                "tests_passed": tp, "tests_total": tt}
    g_rows += [_row("correctness", 5, 5, 5) for _ in range(46)]   # judge ok, tests ok
    g_rows += [_row("correctness", 5, 3, 5) for _ in range(3)]    # judge ok, tests fail
    g_rows += [_row("correctness", 2, 1, 5) for _ in range(7)]    # judge doubts, tests fail
    # a non-correctness row must be ignored entirely
    g_rows += [_row("code_quality", 5, 1, 5)]
    kg, cells, po, pe = judge_vs_tests_kappa(g_rows)
    print("  judge-vs-tests kappa    = %s (expect 0.793)" % fmt_kappa(kg))
    ok &= (kg is not None and abs(kg - 0.793103) < 0.0005)
    print("  2x2 n / false_pass      = %d / %d (expect 56 / 3)" % (cells["n"], cells["false_pass"]))
    ok &= (cells["n"] == 56 and cells["false_pass"] == 3 and cells["false_alarm"] == 0)

    # Test H: a judge with no variance makes this kappa undefined, not 0.
    flat_rows = [_row("correctness", 5, 5, 5) for _ in range(10)]
    kh, _, _, _ = judge_vs_tests_kappa(flat_rows)
    print("  no-variance judge kappa = %s (expect undefined)" % fmt_kappa(kh))
    ok &= (kh is None)

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
