#!/usr/bin/env python3
"""
ingest_judge.py - de-blind the LLM-judge's scores into results/judge.csv.

Input : results/judge_raw.json  - a JSON array the judge produced, one object per blind id:
          {"id":"S03","correctness":4,"completeness":3,"code_quality":5,"instruction_adherence":4}
Uses  : results/blind_key.csv    - maps opaque_id -> (model, task_id)
Output: results/judge.csv        - long format: task_id, model, dimension, judge_score

Usage: python ingest_judge.py
"""

import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(ROOT, "results")
DIMENSIONS = ["correctness", "completeness", "code_quality", "instruction_adherence"]


def main():
    key = {}
    with open(os.path.join(RESULTS, "blind_key.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            key[r["opaque_id"]] = (r["model"], r["task_id"])

    with open(os.path.join(RESULTS, "judge_raw.json"), encoding="utf-8") as f:
        judged = json.load(f)

    rows = []
    seen = set()
    for obj in judged:
        oid = obj["id"]
        if oid not in key:
            print("WARNING: judge id %r not in blind_key, skipping" % oid)
            continue
        model, task = key[oid]
        seen.add(oid)
        for dim in DIMENSIONS:
            if dim not in obj:
                print("WARNING: %s missing dimension %r" % (oid, dim))
                continue
            rows.append((task, model, dim, int(obj[dim])))

    missing = set(key) - seen
    if missing:
        print("WARNING: judge did not score these blind ids: %s" % ", ".join(sorted(missing)))

    with open(os.path.join(RESULTS, "judge.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["task_id", "model", "dimension", "judge_score"])
        w.writerows(rows)
    print("wrote results/judge.csv (%d rows from %d judged items)" % (len(rows), len(seen)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
