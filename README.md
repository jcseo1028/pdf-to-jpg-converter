# PDF to JPG Converter

Minimal Windows-oriented PDF to JPG converter built with Python.

## Current Scope

- Open a PDF file from a simple desktop GUI.
- Preview the first page of the selected PDF.
- Convert every page in the PDF into a separate JPG file.
- Package the application as a Windows executable without requiring a separate Python installation.

## Implementation Summary

- GUI: tkinter
- PDF rendering: PyMuPDF
- Image output: Pillow
- Packaging: PyInstaller
- Test runner: pytest

## Project Structure

- `src/pdf_to_jpg_converter/`: application code
- `tests/`: automated tests for conversion behavior
- `scripts/build.ps1`: Windows build script
- `.agents/`: repository rules, contracts, and change records

## Requirements

- Python 3.10 or newer for development
- Windows for executable packaging and end-user distribution

## Install Dependencies

```powershell
python -m pip install -e .[dev]
```

## Run the Application

```powershell
python -m pdf_to_jpg_converter.app
```

You can also run the installed console entry point:

```powershell
pdf-to-jpg-converter
```

## Run Tests

```powershell
pytest
```

## Build Windows Executable

```powershell
./scripts/build.ps1
```

The build output is created in:

- `dist/pdf-to-jpg-converter/`

This is a PyInstaller one-folder build. To distribute it, send the whole folder or a ZIP archive created from that folder.

## Output Behavior

- One JPG file is created per PDF page.
- Output filenames follow this pattern:

```text
<pdf-stem>-page-<page-number>.jpg
```

- JPG files are written atomically through a temporary file and then moved into place.

## Verified Behavior

- Page count reading works for generated sample PDFs.
- First-page preview rendering works.
- Conversion creates one JPG per page.
- Generated files have valid JPEG signatures.
- A Windows executable build is produced successfully.

## Out of Scope

- OCR
- PDF editing
- Merge, split, annotate, or compress features
- Cloud or network workflows
- Non-Windows packaging targets
