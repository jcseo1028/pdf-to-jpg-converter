# Change Specification

## Change Request Contract

```text
ChangeRequestContract {
  id: "pdf-to-jpg-windows-gui"
  scope: "Existing PDF-to-JPG conversion workflow plus additional PDF-to-PDF Korean translation save-as workflow in the Windows GUI."
  requested_change: "Keep the current Python-based PDF-to-JPG behavior unchanged, and add a new workflow where a user opens a PDF file, translates document text into Korean only, and saves the translated result as a new PDF file with a different name while preserving the source PDF."
  acceptance_checks: [
    "A user can select and open a PDF file through the GUI.",
    "Existing PDF-to-JPG conversion behavior remains available and unchanged.",
    "Each page of the selected PDF can still be converted into a separate JPG image.",
    "The application can process text content from the selected PDF for translation.",
    "The translated output is generated in Korean only.",
    "The user can save the translated result as a new PDF file using a different name.",
    "The original PDF file remains unchanged.",
    "During long translation runs, the GUI remains responsive and shows visible progress updates.",
    "The specification does not include features beyond existing PDF-to-JPG behavior and added Korean PDF-to-PDF translation save-as behavior."
  ]
}
```

## Goal

- Open a PDF file.
- Keep the existing page-by-page PDF to JPG conversion workflow.
- Translate the PDF text content into Korean.
- Save the translated result as a new PDF file with a different name.

## Constraints

- Use Python for implementation.
- Preserve existing PDF-to-JPG behavior without regression.
- Keep translation output language limited to Korean.
- Keep the added feature scope limited to PDF open, Korean translation, and translated PDF save-as.
- Preserve the original PDF file without in-place overwrite.
- Do not add unrelated features.

## Defined Scope

- Input: a PDF file selected by the user.
- Existing workflow: read the PDF and convert every page into an individual JPG image.
- Processing: extract translatable text from the selected PDF and generate Korean translations.
- Output: one JPG image per PDF page (existing workflow) and one newly generated translated PDF file (added workflow).
- Interface: a simple GUI that supports PDF selection, existing JPG conversion trigger, translation trigger, and save-as naming for the translated PDF.
- Save behavior: translated PDF is written to a user-selected location/name and does not overwrite the input PDF unless the user explicitly chooses the same path.

## Current Implementation State

- Current implementation supports PDF to JPG conversion and first-page preview in the GUI.
- Korean translation and translated PDF save-as behavior are implemented and integrated in the GUI.
- Existing conversion output naming for JPG files remains unchanged.
- Translation executes in a background worker thread so the GUI remains responsive.
- Translation progress is surfaced in the GUI via status updates and an active progress bar.
- Translation pipeline includes robustness handling for long text chunking, `None` translator responses, font fallback, and color normalization.
- Logging captures translation failures to support field diagnostics.

## Out of Scope

- Changes to the core existing PDF-to-JPG behavior beyond compatibility with the added feature.
- OCR, annotation, merging, splitting, or compression features unless separately requested.
- Cloud account features or collaboration workflows.
- Batch job orchestration across multiple PDFs in one action.

## Testable Checks

- A PDF file can be selected from the GUI and loaded by the application.
- Existing JPG conversion still runs, and the number of generated JPG files matches PDF page count.
- Existing JPG outputs are generated as JPG files with the current naming behavior.
- Translation processing produces Korean text output for translatable PDF content.
- The user can choose a different output filename/path for the translated PDF.
- Saving the translated PDF creates a new PDF file at the chosen location.
- The source PDF remains unchanged after translation and save.
- Translation does not freeze the GUI for long-running documents, and progress feedback is visible during execution.

## Session Notes

- Added per-page progress callback support from translation workflow to GUI status updates.
- Switched translation execution path in GUI from blocking call to background thread with main-thread UI updates.
- Hardened PDF text re-rendering against source fontname incompatibility by using fallback fonts.
- Normalized extracted PDF color values before text insertion to prevent invalid color component errors.
- Added fallback behavior for translator `None` return values to avoid string-join runtime failures.
