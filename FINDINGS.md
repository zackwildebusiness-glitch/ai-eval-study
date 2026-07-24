# Findings — Evaluating Two Frontier Coding Models, and the Judge That Rates Them

**Author:** Zack Wilde · **Date:** 2026-07-24 · Draft

## TL;DR (v2 — current)
Two studies. **v1** compared two frontier models and found complete correctness parity, with the LLM-judge clustering at the ceiling (89% identical perfect scores) — a result I could not distinguish from the code simply being uniformly good. **v2** settled it by planting 10 subtly-broken solutions into the blind pool: the same judge, on a byte-identical prompt, **caught 7 of 10 with zero false positives across 46 clean solutions**. So v1's ceiling was accuracy, not leniency — my own initial bias hypothesis was wrong, and is recorded as such. The sharper finding is *which* three it missed: every bug it caught was locally pattern-visible (a wrong operator, a missing bounds check), and every bug it missed required **simulating program state across iterations**. An LLM-judge reading code statically behaves like a strong linter, not a correctness oracle. Secondary: on bugs it *did* catch it still rated `code_quality` 4 — correctness and style scores came apart, so collapsing rubric dimensions into one number would erase the signal. Full v2 section below; v1 as originally published follows it.

## v1 TL;DR
I built a small evaluation designed to score coding-model output three independent ways — **objective unit tests, an LLM-as-judge, and a blind human rater**. Two of the three were populated in v1; the human pass was built and blind-ready but deliberately left unrun, because the judge's near-zero variance makes the human-vs-judge agreement statistic undefined regardless of how much rating is done (see §3). Two frontier models (Claude Opus and Claude Sonnet) came out at **complete correctness parity** (100% of unit tests each, across 23 tasks with independently-verified ground truth). The lightweight LLM-judge (Claude Haiku) **clustered at the ceiling**: 89% of 46 blind solutions got an identical perfect 5/5/5/5, even when explicitly instructed to differentiate. On uniformly-correct inputs this is *consistent with* saturation/leniency bias — but, honestly, it is **not distinguishable** from the code genuinely being uniformly good, which is exactly why the recommended next step feeds the judge known-bad code. The practical takeaway: **an LLM-judge cannot be validated without variance in the inputs**, and agreement metrics like Cohen's kappa are undefined when a rater doesn't discriminate.

## Why I built it
The daily question in AI evaluation is: *we can't fully trust a model's output — how do we measure whether it's good, and can we trust our measurement?* This project answers it directly by never relying on a single judgment source: deterministic tests are the ground truth, an LLM-judge is the scalable stand-in, and a human is the tiebreaker. The interesting comparisons are between them.

## Method
- **Subjects (models under test):** Claude Opus (A) vs Claude Sonnet (B). Each solved every task from the spec only, blind to the hidden tests.
- **Tasks:** 23 self-contained coding tasks — 15 standard (two-sum, fizzbuzz, binary search, …) and 8 edge-case-heavy (my_atoi 32-bit clamp, valid IPv4 with leading-zero rules, decode_string nesting, simplify_path, multiply_strings, …).
- **Three judgment sources per solution:**
  1. **Unit tests** — objective pass/total.
  2. **LLM-judge (Haiku)** — blind, 1–5 on four rubric dimensions.
  3. **Human rater** — blind, same rubric. *(status: see Limitations)*
- **Rubric (locked before scoring):** correctness, completeness, code quality, instruction adherence — each 1–5.
- **Blinding:** solutions were shuffled behind opaque ids (S01…S46); the judge and human never saw which model produced which.

## Ground-truth verification (the part most people skip)
A study is only as trustworthy as its answer key. Beyond checking that each reference solution passes its own tests, I wrote an **independent oracle verifier** (`oracle_check.py`) that re-derives expected outputs a *second, different way* and compares:
- `multiply_strings` vs Python big-integer arithmetic (400 random inputs)
- `simplify_path` vs `posixpath.normpath` (400 random paths)
- Excel column title ↔ number as **round-trip inverses** (10,000 values)
- `compare_version` vs integer-tuple comparison, and independent parsers for `decode_string`, `valid_ipv4`, `my_atoi`.

This caught a real discrepancy — a POSIX leading-`//` edge where my *verifier* (not the reference) was wrong — which I fixed. Final: **0 mismatches across all oracle checks**, so the hardcoded expected values are independently confirmed correct.

## Results

### 1. Correctness: a dead heat
Both models passed **100%** of unit tests on **all 23 tasks** (Opus and Sonnet each). Even the edge-case-heavy tier produced no failures. On well-known algorithmic problems, these two frontier models are **indistinguishable on correctness** — a genuine parity result, and a caution against using standard coding benchmarks to separate frontier models.

### 2. LLM-judge behaviour: ceiling clustering
Across all **46 blind solutions**, the Haiku judge produced only **2 distinct score patterns**:

| Score pattern (corr/comp/quality/adher) | Count | Share |
|---|---|---|
| 5 / 5 / 5 / 5 | 41 | 89% |
| 5 / 5 / 4 / 5 | 5 | 11% |

Per-dimension means: correctness **5.00**, completeness **5.00**, instruction-adherence **5.00**, code-quality **4.89**. Three of the four dimensions had **zero variance** — every solution got a 5. This held **even though the judge was explicitly told to differentiate and warned that uniform top-marks are a judging failure**; in an earlier un-warned run it rated **all 30 items a flat 5/5/5/5**.

**Honest interpretation (this is the point):** ceiling-clustering like this is *consistent with* LLM-judge leniency/saturation bias — but on a pool where every solution genuinely passes all tests, it is **not distinguishable** from the judge correctly recognising uniformly-excellent code. You cannot tell bias from accuracy without feeding the judge code that is actually wrong. That ambiguity is the strongest argument for the next study (below), not a conclusion this one can draw.

### 3. Agreement
- **Judge vs unit tests:** both sit at the ceiling (tests 100% pass; judge means ≈ 4.99/5) and therefore "agree" — but the agreement is **uninformative**: with no failing solutions, there is nothing for the judge to be caught missing, and **zero judge-vs-tests contradictions** arose.
- **Human vs judge (weighted Cohen's kappa):** not computed. And critically — it *cannot* be meaningfully computed on this pool even with human ratings, because the judge has **near-zero variance** (only code-quality moved, and only 4↔5). Weighted kappa is undefined when a rater doesn't discriminate. **A real κ requires a pool with a genuine quality spread — i.e. the planted-bug study below.**
- **Methodology lesson:** you cannot measure agreement against a rater that doesn't vary. Uniformly-strong subjects produce a measurement dead-zone; the fix is to introduce known-bad cases, not to collect more ratings on uniformly-good ones.

## What I'd do next (and why it's the more valuable study)
The ceiling effect here is the finding *and* the limitation: frontier models don't fail on famous problems, so there's nothing for the judge to be caught missing. The natural next iteration is a **judge-sensitivity study**: plant solutions with subtle, known bugs (that fail the hidden tests) into the blind pool and measure whether the judge catches them. Every case where the judge rates a test-failing solution highly is a quantified judge failure mode — the result that actually tells you whether an automated judge can be trusted in production.

*(That study was then run. See v2 below.)*

---

# v2 — Planted-Bug Judge-Sensitivity Study

**The analysis plan for this section was pre-registered in `PROTOCOL.md` before any v2 score existed** — detection thresholds, bug admissibility, and the interpretation rules for both a high and a low detection rate. Git history is the timestamp. Nothing below was chosen after seeing the outcome.

## Method
Ten solutions derived from real model output, each carrying exactly one subtle documented defect (`planted_bugs.csv`), were mixed blind into the pool as a third arm. Each was verified to fail at least one hidden test while passing the majority — **71–89% of tests still passing**, so no seeded item was detectable by simply crashing. Bug classes were spread across ten kinds (boundary operator, off-by-one loop bound, missing edge guard, stale-index window, wrong iteration direction, stack guard, `zip` truncation, single-digit accumulation, boundary comparison, half-applied integer clamp) so the result is not an artifact of one defect type.

The pool grew 46 → 56 and was **re-judged in a single pass**. `judge_prompt.md` and `rubric.md` were held **byte-identical to v1**, so the input pool is the only variable.

## Result: the judge caught 7 of 10, with zero false positives

| | |
|---|---|
| Seeded bugs detected (correctness ≤ 3) | **7 / 10** |
| Seeded bugs missed (correctness ≥ 4 on failing code) | **3 / 10** |
| False positives (clean solutions wrongly flagged) | **0 / 46** |
| Judge mean, control arm | **3.40** |
| Judge mean, both subject models | **5.00** |

The judge separated seeded from clean code cleanly, and did not smear suspicion across the pool to get there.

## This resolves v1's central ambiguity — against my own initial hypothesis
v1 could not tell judge leniency apart from the code genuinely being uniformly good. v2 answers it: **the same judge, on the same prompt, discriminates sharply the moment there is something to find.** So v1's ceiling-clustering was *not* saturation bias — it was a correct read of genuinely uniform code. The leniency hypothesis I raised in v1 is not supported, and I am recording that rather than quietly dropping it.

## The more interesting result: *which* three it missed

| Missed | The defect | What catching it requires |
|---|---|---|
| `12_spiral_order` | unguarded final column traversal | tracing boundary state around a 1-column matrix |
| `14_length_of_longest_substring` | window start rewound by a stale index | tracing window state across iterations on `"abba"` |
| `16_multiply_strings` | outer loop iterates the wrong direction | tracing place-value accumulation through carries |

All seven **caught** bugs are *local and pattern-visible* — a single operator (`<` vs `<=`, `>= 255` vs `> 255`), a single wrong constant (`len(stack) > 1`), a known idiom pitfall (`zip` silently truncating), a missing bounds check. All three **missed** bugs require **simulating program state across iterations** to see the defect at all.

**The hypothesis this supports:** an LLM-judge reading code statically behaves like a strong linter — excellent at recognising defect *patterns*, blind to defects that only appear when you execute the code in your head. That is a much sharper and more actionable claim than "LLM judges are lenient," and it maps directly onto when an automated judge is safe to deploy: use it to screen for known defect shapes, do not trust it as a correctness oracle for stateful logic.

**Bounding this honestly:** n = 10 seeded items, one judge model, one task family. Three misses is enough to notice a pattern and not enough to prove one — the local-vs-stateful split is a hypothesis consistent with all ten cases, not an established law. Testing it properly means a purpose-built set with the two bug categories balanced and larger n. No confidence interval is quoted, because 10 items do not support one.

## Secondary finding: correctness and quality came apart
On the seven bugs it caught, the judge still awarded **code_quality = 4** — it docked correctness but kept calling the broken code well-written. That produces **18 judge-vs-tests contradiction rows, all on seeded code and none on genuine model output**. The judge is not scoring one blurred impression of "goodness": it downgrades correctness while style scores stay high. Anyone aggregating rubric dimensions into a single quality number would erase exactly the signal that matters.

## What v2 still does not deliver
- **Weighted Cohen's κ is still not computed** — the human rating pass remains unpopulated (all 224 cells in `results/human_sheet.csv` are empty). The seeded arm now supplies the score variance that makes κ *computable*, which it was not in v1; the missing input is human rating time, not a statistical obstacle. The selection rule for that pass is pre-registered in `PROTOCOL.md`.
- **Judge and subjects still share a provider** (all Claude). Unchanged from v1.
- **The seeded bugs are mine**, so they reflect what I thought would be subtle. An adversary optimising against this specific judge would likely do better than 3/10.

## Limitations (read these)
- **Subjects share a provider** (both Claude); this is not a cross-vendor comparison.
- **Judge is same-family** (Haiku) → possible self-preference; disclosed, and the tests are the anchor of record.
- **Tasks are well-known algorithms** → high ceiling; they don't probe novel or ambiguous specs where models diverge.
- **No naturally-failing solutions** → no judge-vs-tests contradictions to surface (see Next).
- **Human ratings:** optional in this version; the blind sheet (`results/human_sheet.csv`) is generated and ready if a human-vs-judge agreement number is wanted.

## Reproducibility
Everything is in this repo. `python run_tests.py --validate` (ground truth) · `python oracle_check.py` (independent verification) · `python run_tests.py` → `make_scoring_sheet.py` → judge → `ingest_judge.py` → `merge_scores.py` → `python analyze.py results/scores.csv`. See `README.md` and `PROTOCOL.md`.
