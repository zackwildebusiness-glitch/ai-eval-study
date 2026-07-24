# Scoring Rubric (LOCKED)

Four dimensions, ordinal **1–5**. Lock this before any scoring; do not tune it to a preferred winner.
The same rubric is used by the human rater and the LLM-judge. Unit tests are a **separate, objective**
signal and are NOT one of these dimensions.

## 1. Correctness
Does the code actually solve the task as specified?
- **1** — wrong approach or does not run.
- **3** — mostly right; fails some inputs / has a clear bug.
- **5** — correct on the full input domain described in the spec.

## 2. Completeness
Edge cases, empty/degenerate inputs, and error handling.
- **1** — ignores edge cases; crashes on empty/boundary input.
- **3** — handles the common cases; misses one or two edges.
- **5** — handles empty, boundary, and invalid inputs sensibly.

## 3. Code quality
Readability, naming, structure — would you accept it in review?
- **1** — unreadable, no structure, misleading names.
- **3** — readable but clunky or repetitive.
- **5** — clean, idiomatic, well-named, appropriately concise.

## 4. Instruction adherence
Did it follow the spec's explicit constraints (signature, return type, "do X not Y")?
- **1** — ignored the required signature/return contract.
- **3** — followed the gist; deviated on a detail.
- **5** — followed every stated constraint exactly.

_Scores are per (task, model, dimension). Ground-truth unit-test pass rate is recorded separately._
