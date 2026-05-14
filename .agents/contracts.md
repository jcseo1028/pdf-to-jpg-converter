# Contracts

## Contract Types

### Change Request Contract Schema

```text
ChangeRequestContract {
  id: string
  scope: string
  requested_change: string
  acceptance_checks: string[]
}
```

### Module Contract Schema

```text
ModuleContract {
  name: string
  responsibility: string
  inputs: string[]
  outputs: string[]
  dependencies: string[]
}
```

### Data Contract Schema

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

### GUI Module Contract

```text
ModuleContract {
  name: "GUI Module"
  responsibility: "Select a PDF file, show a first-page preview, trigger page-by-page JPG conversion, trigger Korean translation save-as to PDF, and present non-blocking translation progress in the UI."
  inputs: ["pdf_path", "output_directory", "output_pdf_path"]
  outputs: ["first_page_preview", "conversion_request", "conversion_result", "translation_request", "translation_progress_event", "translation_result"]
  dependencies: ["Conversion Module", "Translation Module"]
}
```

### Conversion Module Contract

```text
ModuleContract {
  name: "Conversion Module"
  responsibility: "Read a PDF file and write one JPG image per page using deterministic page-based filenames."
  inputs: ["pdf_path", "output_directory"]
  outputs: ["jpg_file_paths"]
  dependencies: []
}
```

### Translation Module Contract

```text
ModuleContract {
  name: "Translation Module"
  responsibility: "Read a PDF file, translate extracted text into Korean, write a new translated PDF file, and optionally emit per-page progress updates."
  inputs: ["pdf_path", "output_pdf_path", "progress_callback(optional)"]
  outputs: ["translation_progress_event(optional)", "translation_result"]
  dependencies: []
}
```

### ConversionRequest Data Contract

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

### ConversionResult Data Contract

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

### TranslationRequest Data Contract

```text
DataContract {
  name: "TranslationRequest"
  producer: "GUI Module"
  consumer: "Translation Module"
  fields: [
    { name: "pdf_path", type: "string", required: true },
    { name: "output_pdf_path", type: "string", required: true },
    { name: "target_language", type: "string", required: true },
    { name: "progress_callback", type: "callable|null", required: false }
  ]
}
```

### TranslationProgressEvent Data Contract

```text
DataContract {
  name: "TranslationProgressEvent"
  producer: "Translation Module"
  consumer: "GUI Module"
  fields: [
    { name: "current_page", type: "integer", required: true },
    { name: "total_pages", type: "integer", required: true }
  ]
}
```

### TranslationResult Data Contract

```text
DataContract {
  name: "TranslationResult"
  producer: "Translation Module"
  consumer: "GUI Module"
  fields: [
    { name: "page_count", type: "integer", required: true },
    { name: "output_pdf_path", type: "string", required: true },
    { name: "target_language", type: "string", required: true }
  ]
}
```

### GeneratedJpgFile Data Contract

```text
DataContract {
  name: "GeneratedJpgFile"
  producer: "Conversion Module"
  consumer: "End User"
  fields: [
    { name: "file_name_pattern", type: "string", required: true },
    { name: "format", type: "string", required: true }
  ]
}
```
