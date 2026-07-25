# AI Coding-Model Evaluation Study

A small, honest evaluation comparing two coding models on identical tasks. The design has
**three independent judgment sources** — objective unit tests, a blind LLM-judge, and a blind
human rater — and reports how well they agree.

**Subjects under evaluation:** Claude **Opus** (model A) vs Claude **Sonnet** (model B).
**LLM-judge:** Claude **Haiku** (independent of both subjects; also tests "can a lighter
model judge stronger ones?").
**Human rater:** the author, scoring blind — **designed and blind-ready, but not executed.**
`results/human_sheet.csv` is generated and shuffled, and every `human_score` cell is empty, so
**two** of the three sources are populated. Human-vs-judge inter-rater reliability is therefore
not reported.

**A κ *is* reported**, between the other two raters: **judge vs unit tests, κ = 0.793
(substantial)** over 56 solutions — 3 false passes, 0 false alarms. That statistic needs no
human. It is prevalence-dependent (this pool is deliberately enriched with seeded bad code) and
it is post-hoc rather than pre-registered; both caveats are stated wherever it appears. See
`FINDINGS.md`.

See `PROTOCOL.md` for the methodology and `rubric.md` for the locked scoring rubric.

## Why this design
- **Unit tests = objective ground truth.** No human needed for correctness.
- **LLM-judge = the scalable eval method** teams actually use.
- Comparing the judge against the tests surfaces **LLM-judge failure modes** (fluent-but-wrong
  code the judge rewards) — the headline finding.
- Runs entirely on Claude Code's own models: no API key, no cost.

## Layout
```
tasks/<id>/prompt.md          spec given to the models
tasks/<id>/test_solution.py   objective unit tests (TOTAL + run_tests(sol))
tasks/<id>/reference.py       correct solution, used only to validate the tests
solutions/<model>/<id>/solution.py   each subject's answer
solutions_blind/<opaque>/     shuffled, model-hidden copies for blind rating
results/                      objective.csv, judge.csv, human_sheet.csv, blind_key.csv, scores.csv
```

## Run order
1. **Validate test integrity:** `python run_tests.py --validate`  (every reference must pass)
2. **Generate solutions:** dispatch Opus and Sonnet to solve each `tasks/<id>/prompt.md`;
   save to `solutions/opus/<id>/solution.py` and `solutions/sonnet/<id>/solution.py`.
3. **Objective scores:** `python run_tests.py`  → `results/objective.csv`
4. **Blind set:** `python make_scoring_sheet.py`  → `solutions_blind/`, `results/human_sheet.csv`, `results/blind_key.csv`
5. **Judge:** give Haiku `judge_prompt.md` + each `solutions_blind/<id>/` (PROMPT.md + solution.py);
   save its JSON array to `results/judge_raw.json`; then `python ingest_judge.py` → `results/judge.csv`
6. **Human rating:** fill `human_score` (1-5) in `results/human_sheet.csv` by reviewing
   `solutions_blind/<id>/`. Do NOT open `blind_key.csv` until done.
7. **Merge:** `python merge_scores.py`  → `results/scores.csv`
8. **Report:** `python analyze.py results/scores.csv`  → `eval-report.md`

Steps 3, 7, 8 can run before human rating (step 6) for a partial report (winners + judge-vs-tests
contradictions); the human-vs-judge kappa fills in once you rate.

## Honesty guardrails
- Rubric is locked before scoring (`rubric.md`); don't tune it to a preferred winner.
- Same-provider subjects + a same-family judge = **self-preference risk**; disclose it and let the
  tests be the tie-breaker of record.
- Publish disagreements and limitations, not only the flattering numbers.
