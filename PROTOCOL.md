# Solo AI-Eval Study — Protocol (draft v0.1)

**Author:** Zack Wilde · **Status:** draft for review · **Requires:** one Anthropic API key. No second human, no paid raters.

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
