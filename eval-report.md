# Evaluation Report

Rows scored: 224  |  Models under test: opus, sonnet  |  Control arms: planted

## 1. Winner per judgment source

| Model | Human mean | Judge mean | Test pass-rate |
|---|---|---|---|
| opus | - | 5.00 | 100.0% (161/161) |
| sonnet | - | 5.00 | 100.0% (161/161) |

- **Human:** not enough models to compare.
- **Judge:** tie.
- **Tests:** tie.

### Control arm (seeded known-bad code -- NOT a competitor)

| Arm | Judge mean | Test pass-rate |
|---|---|---|
| planted | 3.40 | 81.9% (59/72) |

These solutions carry deliberate, documented bugs (see `planted_bugs.csv`) and are excluded from the winner comparison above. Their purpose is to create genuine quality variance: they give the judge something it can be caught missing, and they are what makes the agreement statistics below meaningful. **A high judge mean on this arm is itself the finding** -- it means the judge rewarded code that objectively fails its tests.

## 2. Judge vs unit tests -- Cohen's kappa

Two raters, one binary question: is this solution correct? The judge says yes at correctness >= 4; the tests say yes when every test passes. **No human rater is needed for this statistic.**

| | tests say correct | tests say broken |
|---|---|---|
| **judge says correct** | 46 | **3** |
| **judge says broken** | 0 | 7 |

- Observed agreement **94.6%**, chance agreement **74.1%** -> **kappa = 0.793** (substantial). n=56
- **3 false passes** (judge cleared code its tests fail) and **0 false alarms** (judge doubted code that passes).
- The asymmetry is the finding: this judge is **conservative in the dangerous direction** -- it waves broken code through rather than raising false alarms.

> **Two caveats that must travel with this number.** (1) kappa is *prevalence-dependent* and this pool is deliberately enriched with seeded bad solutions, so it describes agreement **on this pool**, not on naturally occurring code. (2) This analysis was **not pre-registered** -- `PROTOCOL.md` specified a human-vs-judge kappa; this judge-vs-tests kappa is post-hoc.

## 3. Human vs LLM-judge agreement

_Pending: no human ratings supplied yet. Fill `results/human_sheet.csv`, re-run `merge_scores.py`, then re-run this report to get human-vs-judge kappa._

Quadratic-weighted Cohen's kappa (corrects for chance); exact = identical score.

- **Overall:** kappa = undefined (no variance), exact agreement = -  (n=0)

| Dimension | n | Weighted kappa | Exact agreement |
|---|---|---|---|

_Kappa guide: <0 worse than chance, 0-.2 slight, .2-.4 fair, .4-.6 moderate, .6-.8 substantial, .8-1 near-perfect._

## 4. Judge-vs-tests contradictions (the headline finding)

Cases where the LLM-judge scored an output >= 4 while its unit tests objectively failed:

| Task | Model | Dimension | Judge score | Tests |
|---|---|---|---|---|
| 06_merge_intervals | planted | code_quality | 4 | 6/7 |
| 09_binary_search | planted | code_quality | 4 | 6/7 |
| 12_spiral_order | planted | correctness | 5 | 5/6 |
| 12_spiral_order | planted | completeness | 5 | 5/6 |
| 12_spiral_order | planted | code_quality | 4 | 5/6 |
| 12_spiral_order | planted | instruction_adherence | 5 | 5/6 |
| 14_length_of_longest_substring | planted | correctness | 5 | 6/7 |
| 14_length_of_longest_substring | planted | completeness | 5 | 6/7 |
| 14_length_of_longest_substring | planted | code_quality | 5 | 6/7 |
| 14_length_of_longest_substring | planted | instruction_adherence | 5 | 6/7 |
| 16_multiply_strings | planted | correctness | 5 | 5/7 |
| 16_multiply_strings | planted | completeness | 5 | 5/7 |
| 16_multiply_strings | planted | code_quality | 5 | 5/7 |
| 16_multiply_strings | planted | instruction_adherence | 5 | 5/7 |
| 17_simplify_path | planted | code_quality | 4 | 5/7 |
| 20_compare_version | planted | code_quality | 4 | 5/7 |
| 22_valid_ipv4 | planted | code_quality | 4 | 8/9 |
| 23_my_atoi | planted | code_quality | 4 | 8/9 |

**18 contradiction rows** - each is direct evidence of an LLM-judge failure mode (fluent-but-wrong code the judge rewarded). This is the finding eval teams care about most.
- 18 on seeded control code (deliberate known bugs).
- 0 on genuine model output (an unprompted judge miss).

## 5. Planted-bug detection rate (judge sensitivity)

Each row is one seeded solution with a documented deliberate bug that fails its unit tests. 'Caught' = the judge gave correctness <= 3. 'Missed' = the judge gave >= 4 to code it should have doubted.

**Judge caught 7 of 10 (70%); missed 3 (30%).**

| Task | Judge correctness | Tests | Verdict |
|---|---|---|---|
| 06_merge_intervals | 2 | 6/7 | caught |
| 09_binary_search | 2 | 6/7 | caught |
| 12_spiral_order | 5 | 5/6 | **MISSED** |
| 14_length_of_longest_substring | 5 | 6/7 | **MISSED** |
| 16_multiply_strings | 5 | 5/7 | **MISSED** |
| 17_simplify_path | 2 | 5/7 | caught |
| 20_compare_version | 2 | 5/7 | caught |
| 21_decode_string | 2 | 5/6 | caught |
| 22_valid_ipv4 | 2 | 8/9 | caught |
| 23_my_atoi | 2 | 8/9 | caught |

Unlike the ceiling-clustering result, this number is unambiguous: the ground truth is known by construction, so a miss cannot be explained away as the code genuinely being good.

