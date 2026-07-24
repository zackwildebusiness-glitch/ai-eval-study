# Solo AI-Eval Study — Protocol (draft v0.1)

**Author:** Zack Wilde · **Status:** v1 executed (see `FINDINGS.md`) · **Requires:** no API key and no paid raters — as run, all three models (two subjects, one judge) were driven through Claude Code, and the human rater is the author.

## Goal
Publish an evaluation study that demonstrates real methodology — objective ground truth + LLM-as-judge validation + human rating with reported agreement — and turns "builds eval-shaped tooling" into "has *run* a rigorous evaluation." Zero second human required.

## Research questions
1. On N coding tasks, which model (A vs B) produces better output?
2. How well does an automated **LLM-judge agree with a human rater**? (inter-rater reliability, human-vs-machine)
3. Where does the LLM-judge **disagree with objective ground truth** (unit tests)? (judge failure modes — the headline finding)

## Design
- **Tasks:** 15–20 self-contained coding tasks. Each has (a) a written spec and (b) hidden unit tests that define objective correctness wherever possible.
- **Models:** two, labelled **A / B** and blinded during rating. Recommended: two Claude models on the existing key (e.g. Opus vs Haiku).
- **Inputs:** hash-identical prompt to both models.

## Three independent judgment sources per output
1. **Deterministic harness (objective):** compiles? unit tests pass (count/total)? spec constraints met? → objective score. *This is the strongest "rater" and needs no human.*
2. **Human rater (you):** blind, on a locked 1–5 rubric across the dimensions below.
3. **LLM-as-judge:** a model scoring blind on the **same** rubric.

## Rubric (LOCK before scoring; ordinal 1–5, with anchored 1/3/5 descriptions)
- **Correctness** — does it actually perform the task
- **Completeness** — edge cases, error handling
- **Code quality / readability**
- **Instruction adherence** — followed the spec's constraints
- *(optional)* **Robustness / safety**

## Procedure
1. **Pilot** 2–3 tasks → calibrate rubric wording → **LOCK** rubric.
2. Generate outputs for all tasks × 2 models.
3. Run deterministic harness → objective scores.
4. **Blind human rating** — outputs shuffled, model identity hidden (A/B key stored separately).
5. **LLM-judge rating** — blind, same rubric.
6. *(optional, adds rigor)* **Test–retest:** re-rate a shuffled ~30% subset ≥48h later → intra-rater reliability.

## Analysis (see `analyze.py`)
- Winner per source (human / tests / judge) + margin.
- **Human-vs-judge quadratic-weighted Cohen's kappa** (per dimension + overall) + raw % agreement.
- **Judge-vs-tests contradiction table** (judge ≥4 but tests fail) — the money finding.
- Test–retest kappa (if step 6 done).

## Deliverable (public GitHub repo + short blog post)
Methodology · task specs · both models' raw outputs · all three score sets · kappa tables · disagreement analysis · honest limitations. Blog summary links the repo. Add to resume: "Ran and published an N-task LLM evaluation with LLM-as-judge validation (weighted κ = …) and ground-truth contradiction analysis."

## Cost & dependencies
Two Claude models + one judge model on the existing Anthropic key ≈ a few cents–$2 of tokens. No paid humans, no new accounts.

## Honesty guardrails
- Lock the rubric before seeing outputs (no post-hoc tuning to a preferred winner).
- Report κ, not just % agreement (κ corrects for chance).
- Publish disagreements and limitations, not just the flattering numbers.

---

# v2 Addendum — Planted-Bug Judge-Sensitivity Study (pre-registered)

**Status:** analysis plan fixed **before** any v2 result existed. Written after the planted
solutions were commissioned but before the judge scored them, so the metrics below could not
be chosen to flatter an outcome. Git history is the timestamp.

## Why v2 exists
v1 produced a measurement dead-zone. Both subject models passed 100% of unit tests on all 23
tasks, so the judge had nothing it could be caught missing; it clustered at the ceiling (89%
identical 5/5/5/5) and weighted κ was **mathematically undefined** — you cannot compute
agreement against a rater that does not vary. v1's ceiling-clustering is *consistent with*
judge leniency but **indistinguishable** from the code genuinely being uniformly good.

The only way to break that ambiguity is to feed the judge code that is **known** to be wrong.

## Intervention
A third arm, `planted`, is added to the subject pool: 10 solutions derived from real model
output with exactly one subtle, documented defect each, recorded in `planted_bugs.csv`.

Bug admissibility criteria, fixed in advance:
- Must fail **at least one** hidden test but pass the **majority** (roughly 60–95% passing).
  A solution scoring 0/TOTAL is rejected — total failure is trivially detectable and would
  inflate the judge's apparent sensitivity.
- Must read as clean, confident, idiomatic code: no comments hinting at the defect, no dead
  code, no anomalous constructs.
- Bug classes are spread (off-by-one, missing empty-input guard, wrong tie-break, missing
  clamp, incorrect early return, wrong comparison operator, dropped final element, …) so the
  result is not an artifact of one defect type.

## Variables held constant (this is the point)
- **`judge_prompt.md` is byte-identical to v1.** v1's ceiling-clustering occurred *with* that
  prompt, including its explicit "be calibrated, use the middle" instruction. Changing the
  prompt and the input pool together would confound the two; any change in judge behaviour
  must be attributable to the pool alone.
- **`rubric.md` unchanged.** Same four dimensions, same 1–5 scale.
- **Tasks, hidden tests, and both subject models' v1 solutions unchanged.** v1's exact state is
  preserved at git tag `v1-findings`.
- The whole pool is re-judged in one pass, not just the new items — opaque ids reshuffle when
  the pool grows, and the judge must see a single uniform blind set.

## Pre-registered analysis
1. **Planted-bug detection rate** (primary): of the 10 seeded solutions, the share the judge
   gave `correctness` ≤ 3. **Caught = ≤3, Missed = ≥4.** These thresholds are fixed now.
   A "miss" is a judge scoring code ≥4 on correctness that objectively fails its own tests.
2. **Judge-vs-tests contradictions**, split into *seeded* (deliberate) and *organic* (an
   unprompted miss on genuine model output).
3. **Weighted Cohen's κ (human vs judge)** — expected to become computable for the first time,
   because the seeded arm supplies score variance. If the judge *still* shows near-zero
   variance, κ remains undefined and **that will be reported as the result**, not worked around.
4. The `planted` arm is excluded from the model-vs-model winner comparison (it is a control,
   engineered to fail) but included in agreement and contradiction analysis. Enforced in code
   by `CONTROL_ARMS` in `analyze.py`, with self-tests E and F.

## Pre-committed interpretation rules
- A **high** detection rate means the judge is usable as a correctness screen on this task
  class — and it retroactively strengthens the v1 reading that the code really was uniformly
  good, rather than the judge being blind.
- A **low** detection rate is the headline judge-failure finding: fluent-but-wrong code scored
  highly, quantified against known ground truth.
- Either outcome is publishable. Neither will be reframed after the fact.
- n = 10 seeded items is small. The detection rate will be reported with that caveat attached
  and **no confidence interval implying more precision than 10 items support.**
