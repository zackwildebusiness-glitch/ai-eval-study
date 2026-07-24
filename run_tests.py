#!/usr/bin/env python3
"""
run_tests.py - objective ground truth for the eval study.

Runs each subject's solution against each task's unit tests and writes
results/objective.csv  (columns: task_id, model, tests_passed, tests_total).

Task format (see tasks/01_two_sum/):
  tasks/<id>/prompt.md          - the spec handed to the models
  tasks/<id>/test_solution.py   - defines TOTAL:int and run_tests(sol_module)->(passed,total)
  tasks/<id>/reference.py       - a correct solution, used only to validate the tests

Subject solutions live at:
  solutions/<model>/<task_id>/solution.py

Usage:
  python run_tests.py             # score all solutions -> results/objective.csv
  python run_tests.py --validate  # run every task's reference.py; all must pass (test integrity)
"""

import csv
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(ROOT, "tasks")
SOLUTIONS = os.path.join(ROOT, "solutions")
RESULTS = os.path.join(ROOT, "results")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def task_ids():
    if not os.path.isdir(TASKS):
        return []
    return sorted(d for d in os.listdir(TASKS) if os.path.isdir(os.path.join(TASKS, d)))


def subjects():
    if not os.path.isdir(SOLUTIONS):
        return []
    return sorted(d for d in os.listdir(SOLUTIONS) if os.path.isdir(os.path.join(SOLUTIONS, d)))


def score(task, sol_path):
    """Return (passed, total). A crashing/broken solution scores 0/TOTAL, never raises."""
    tests = load_module(os.path.join(TASKS, task, "test_solution.py"), "t_" + task)
    total_declared = getattr(tests, "TOTAL", None)
    try:
        sol = load_module(sol_path, "s_" + task + "_" + os.path.basename(os.path.dirname(sol_path)))
        passed, total = tests.run_tests(sol)
        return passed, total
    except Exception:
        return 0, (total_declared if total_declared is not None else 1)


def validate():
    ok = True
    for task in task_ids():
        ref = os.path.join(TASKS, task, "reference.py")
        if not os.path.exists(ref):
            print("%-24s NO reference.py" % task)
            ok = False
            continue
        p, t = score(task, ref)
        good = (t > 0 and p == t)
        print("%-24s reference %d/%d  %s" % (task, p, t, "OK" if good else "FAIL"))
        ok &= good
    print("\nVALIDATE %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if "--validate" in argv:
        return validate()
    rows = []
    for subj in subjects():
        for task in task_ids():
            sol_path = os.path.join(SOLUTIONS, subj, task, "solution.py")
            if not os.path.exists(sol_path):
                continue
            p, t = score(task, sol_path)
            rows.append((task, subj, p, t))
            print("%-8s %-24s %d/%d" % (subj, task, p, t))
    if not rows:
        print("No solutions found under solutions/<model>/<task>/solution.py")
        return 0
    os.makedirs(RESULTS, exist_ok=True)
    out = os.path.join(RESULTS, "objective.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["task_id", "model", "tests_passed", "tests_total"])
        w.writerows(rows)
    print("\nwrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
