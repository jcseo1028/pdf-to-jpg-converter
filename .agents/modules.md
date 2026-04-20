# Modules

## Module Definitions

### System Module
- Responsibility: define repository-level purpose, boundaries, and outcomes.
- Inputs: change request context.
- Outputs: allowed operating space.
- Dependencies: none.

### Rules Module
- Responsibility: define mandatory change constraints and session finalization requirements.
- Inputs: proposed change set.
- Outputs: allowed change strategy.
- Dependencies: none.

### Contracts Module
- Responsibility: define explicit task, module, and data contracts.
- Inputs: requested behavior, interface, or data changes.
- Outputs: stable contract definitions.
- Dependencies: none.

### Pipeline Module
- Responsibility: define the ordered flow for handling a change request.
- Inputs: scoped change request.
- Outputs: ordered execution steps.
- Dependencies: System Module, Rules Module, Contracts Module.

## Independence Rules
- Each module is complete within its own responsibility.
- A module may be updated without changing another module unless its declared dependency or owned contract changes.
- Shared terms must keep the same meaning across all modules.
- Cross-module updates must be explicit and minimal.
