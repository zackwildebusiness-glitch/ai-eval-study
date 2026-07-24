# Evaluation Report

Rows scored: 184  |  Models under test: opus, sonnet

## 1. Winner per judgment source

| Model | Human mean | Judge mean | Test pass-rate |
|---|---|---|---|
| opus | - | 4.99 | 100.0% (161/161) |
| sonnet | - | 4.96 | 100.0% (161/161) |

- **Human:** not enough models to compare.
- **Judge winner:** opus (margin 0.033)
- **Tests:** tie.

## 2. Human vs LLM-judge agreement

_Pending: no human ratings supplied yet. Fill `results/human_sheet.csv`, re-run `merge_scores.py`, then re-run this report to get human-vs-judge kappa._

Quadratic-weighted Cohen's kappa (corrects for chance); exact = identical score.

- **Overall:** kappa = undefined (no variance), exact agreement = -  (n=0)

| Dimension | n | Weighted kappa | Exact agreement |
|---|---|---|---|

_Kappa guide: <0 worse than chance, 0-.2 slight, .2-.4 fair, .4-.6 moderate, .6-.8 substantial, .8-1 near-perfect._

## 3. Judge-vs-tests contradictions (the headline finding)

None: the judge never rated a test-failing output >= 4. (Either strong judge, or few failing outputs.)

