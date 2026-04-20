# Contracts

## Contract Types

### Change Request Contract
```text
ChangeRequestContract {
  id: string
  scope: string
  requested_change: string
  acceptance_checks: string[]
}
```

### Module Contract
```text
ModuleContract {
  name: string
  responsibility: string
  inputs: string[]
  outputs: string[]
  dependencies: string[]
}
```

### Data Contract
```text
DataContract {
  name: string
  producer: string
  consumer: string
  fields: { name: string, type: string, required: boolean }[]
}
```

## Contract Rules
- Keep every contract explicit, small, and self-contained.
- Use the same field names and terms across all documents.
- Prefer additive changes over breaking changes.
- Update the relevant contract before changing implementation behavior, interfaces, or data structures.
- Do not introduce fields, interfaces, or workflows without a stated need in the change request.
