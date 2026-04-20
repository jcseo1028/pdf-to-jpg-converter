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

## Repository Contracts

### Module Contract
```text
ModuleContract {
  name: "GUI Module"
  responsibility: "Select a PDF file, show a preview, and trigger page-by-page JPG conversion."
  inputs: ["pdf_path", "output_directory"]
  outputs: ["preview_image", "conversion_request"]
  dependencies: ["Conversion Module"]
}
```

### Module Contract
```text
ModuleContract {
  name: "Conversion Module"
  responsibility: "Read a PDF file and write one JPG image per page."
  inputs: ["pdf_path", "output_directory"]
  outputs: ["jpg_file_paths"]
  dependencies: []
}
```

### Data Contract
```text
DataContract {
  name: "ConversionRequest"
  producer: "GUI Module"
  consumer: "Conversion Module"
  fields: [
    { name: "pdf_path", type: "string", required: true },
    { name: "output_directory", type: "string", required: true }
  ]
}
```

### Data Contract
```text
DataContract {
  name: "ConversionResult"
  producer: "Conversion Module"
  consumer: "GUI Module"
  fields: [
    { name: "page_count", type: "integer", required: true },
    { name: "jpg_file_paths", type: "string[]", required: true }
  ]
}
```
