# Copilot Instructions

## Source of Truth
- Treat `.agents/` as the primary source of repository guidance.
- Use `.agents/contracts.md` before changing behavior, interfaces, or data structures.
- If guidance conflicts, apply this order: `rules.md` -> `contracts.md` -> `modules.md` -> `pipeline.md` -> `system.md`.

## Scope Control
- Limit work to the files required by the active change request.
- Do not scan the full repository by default.
- Expand search scope only when the active change request cannot be resolved from the immediately affected area.
- Do not infer features, workflows, or constraints that are not explicitly stated.

## Change Strategy
- Make incremental, testable changes.
- Follow contract-first updates before implementation changes.
- Keep edits small, local, and reversible.
- Do not perform broad restructuring, renaming, reformatting, or cleanup unless the change request explicitly requires it.

## Validation
- Validate only the directly affected behavior or files.
- Do not introduce unrelated fixes or opportunistic refactors.
- If a relevant contract is missing, add the minimal contract needed before implementation changes.
