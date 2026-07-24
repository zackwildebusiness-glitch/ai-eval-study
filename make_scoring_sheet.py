#!/usr/bin/env python3
"""
make_scoring_sheet.py - build the BLIND human-scoring sheet from generated solutions.

Reads solutions/<model>/<task>/solution.py, assigns a shuffled opaque id to each
(model, task) pair, copies each solution + its task PROMPT.md into
solutions_blind/<opaque>/ (so you review code without seeing which model wrote it),
and writes:
  results/human_sheet.csv  columns: opaque_id, task_id, dimension, human_score  <- YOU fill human_score
  results/blind_key.csv    columns: opaque_id, model, task_id                    <- de-blind key, do NOT peek while rating

The LLM-judge scores the SAME solutions_blind set by opaque id, so the blinding is shared
between you and the judge.

Usage: python make_scoring_sheet.py [--seed N]
"""

import csv
import os
import random
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
TASKS = os.path.join(ROOT, "tasks")
SOLUTIONS = os.path.join(ROOT, "solutions")
BLIND = os.path.join(ROOT, "solutions_blind")
RESULTS = os.path.join(ROOT, "results")
DIMENSIONS = ["correctness", "completeness", "code_quality", "instruction_adherence"]


def main(argv):
    seed = 1337
    if "--seed" in argv:
        seed = int(argv[argv.index("--seed") + 1])
    rng = random.Random(seed)

    pairs = []  # (model, task)
    for model in sorted(os.listdir(SOLUTIONS)) if os.path.isdir(SOLUTIONS) else []:
        mdir = os.path.join(SOLUTIONS, model)
        if not os.path.isdir(mdir):
            continue
        for task in sorted(os.listdir(mdir)):
            if os.path.exists(os.path.join(mdir, task, "solution.py")):
                pairs.append((model, task))
    if not pairs:
        print("No solutions found under solutions/<model>/<task>/solution.py. Generate solutions first.")
        return 1

    rng.shuffle(pairs)
    if os.path.isdir(BLIND):
        shutil.rmtree(BLIND)
    os.makedirs(BLIND, exist_ok=True)
    os.makedirs(RESULTS, exist_ok=True)

    key_rows = []
    sheet_rows = []
    for idx, (model, task) in enumerate(pairs, start=1):
        opaque = "S%02d" % idx
        dest = os.path.join(BLIND, opaque)
        os.makedirs(dest, exist_ok=True)
        shutil.copy(os.path.join(SOLUTIONS, model, task, "solution.py"),
                    os.path.join(dest, "solution.py"))
        prompt = os.path.join(TASKS, task, "prompt.md")
        if os.path.exists(prompt):
            shutil.copy(prompt, os.path.join(dest, "PROMPT.md"))
        key_rows.append((opaque, model, task))
        for dim in DIMENSIONS:
            sheet_rows.append((opaque, task, dim, ""))  # human_score blank

    with open(os.path.join(RESULTS, "human_sheet.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["opaque_id", "task_id", "dimension", "human_score"])
        w.writerows(sheet_rows)
    with open(os.path.join(RESULTS, "blind_key.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["opaque_id", "model", "task_id"])
        w.writerows(key_rows)

    print("Blinded %d solutions into solutions_blind/ (seed=%d)" % (len(pairs), seed))
    print("Fill human_score (1-5) in results/human_sheet.csv by reviewing solutions_blind/<id>/.")
    print("Do NOT open results/blind_key.csv until after you finish rating.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
