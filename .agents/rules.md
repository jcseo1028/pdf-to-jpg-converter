# Rules

## Minimal Change Rules
- Apply the smallest possible change set that satisfies the change request.
- Do not edit files outside the affected scope unless a contract or validation requirement makes the edit necessary.
- Do not perform refactoring, renaming, reformatting, or file moves unless the change request explicitly requires them.
- Do not reorganize unrelated files, modules, or document structure.
- Keep each change incremental and independently verifiable.

## Contract-First Rules
- Update the relevant contract before changing behavior, interfaces, or data structures.
- If no relevant contract exists, add the minimal contract needed before implementation changes.
- Do not implement behavior that is not represented by an explicit contract when a contract is required.

## Scope Rules
- Operate only within the stated scope of the change request.
- Do not assume missing requirements, hidden dependencies, or future features.
- Do not add implementation code unless explicitly requested.

## Session Finalization
- Before ending a work session, persist key decisions, assumptions, and contract changes into `.agents/changes/`.
- Each session record must be concise and specific to the completed change request.
