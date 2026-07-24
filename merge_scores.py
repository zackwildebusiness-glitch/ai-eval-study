#!/usr/bin/env python3
"""
merge_scores.py - join objective + judge + human into results/scores.csv for analyze.py.

Reads:
  results/objective.csv     task_id, model, tests_passed, tests_total          (from run_tests.py)
  results/judge.csv         task_id, model, dimension, judge_score             (from ingest_judge.py)
  results/human_sheet.csv   opaque_id, task_id, dimension, human_score         (you fill; optional)
  results/blind_key.csv     opaque_id, model, task_id                          (to de-blind human rows)

Writes results/scores.csv (long format):
  task_id, model, dimension, human_score, judge_score, tests_passed, tests_total
One row per (task, model, dimension). human_score / judge_score left blank if absent
(analyze.py treats blanks as "not yet supplied").

Usage: python merge_scores.py
"""

import csv
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "results")
DIMENSIONS = ["correctness", "completeness", "code_quality", "instruction_adherence"]


def read_csv(name):
    path = os.path.join(RESULTS, name)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main():
    objective = {}
    for r in read_csv("objective.csv"):
        objective[(r["task_id"], r["model"])] = (r["tests_passed"], r["tests_total"])
    if not objective:
        print("results/objective.csv missing/empty - run run_tests.py first.")
        return 1

    judge = {}
    for r in read_csv("judge.csv"):
        judge[(r["task_id"], r["model"], r["dimension"])] = r["judge_score"]

    # human: de-blind via key
    key = {r["opaque_id"]: (r["model"], r["task_id"]) for r in read_csv("blind_key.csv")}
    human = {}
    for r in read_csv("human_sheet.csv"):
        hs = (r.get("human_score") or "").strip()
        if hs == "":
            continue
        if r["opaque_id"] not in key:
            continue
        model, task = key[r["opaque_id"]]
        human[(task, model, r["dimension"])] = hs

    rows = []
    for (task, model), (tp, tt) in sorted(objective.items()):
        for dim in DIMENSIONS:
            rows.append((
                task, model, dim,
                human.get((task, model, dim), ""),
                judge.get((task, model, dim), ""),
                tp, tt,
            ))

    out = os.path.join(RESULTS, "scores.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["task_id", "model", "dimension", "human_score", "judge_score",
                    "tests_passed", "tests_total"])
        w.writerows(rows)
    n_human = sum(1 for r in rows if r[3] != "")
    n_judge = sum(1 for r in rows if r[4] != "")
    print("wrote %s  (%d rows; %d human-scored, %d judge-scored)" % (out, len(rows), n_human, n_judge))
    return 0


if __name__ == "__main__":
    sys.exit(main())
