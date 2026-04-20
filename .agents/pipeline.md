# Pipeline

## Change Flow
1. Receive a scoped change request.
2. Identify the affected module or modules.
3. Read the applicable rules before making changes.
4. Read the relevant contracts before changing behavior, interfaces, or data.
5. Update or add contracts if the change request modifies behavior, interfaces, or data structures.
6. Apply the smallest change set required to satisfy the change request.
7. Validate only the directly affected behavior or files.
8. Persist session decisions in `.agents/changes/` before finalizing the session.

## Flow Rules
- The sequence is mandatory unless a higher-priority rule requires otherwise.
- Contract changes precede implementation changes.
- Validation follows the implemented change and stays within the affected scope.
