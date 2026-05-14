# PDF to JPG Converter

Minimal Windows-oriented PDF to JPG converter built with Python.

## Current Scope

- Open a PDF file from a simple desktop GUI.
- Preview the first page of the selected PDF.
- Convert every page in the PDF into a separate JPG file.
- Translate PDF text into Korean and save it as a new PDF file.
- Show translation progress while keeping the GUI responsive during long-running translation.
- Package the application as a Windows executable without requiring a separate Python installation.

## Implementation Summary

- GUI: tkinter
- PDF rendering: PyMuPDF
- Image output: Pillow
- Translation backend: deep-translator (Google Translator)
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

To build a single-file executable instead:

```powershell
python -m PyInstaller --onefile --distpath dist/pdf-to-jpg-converter --name pdf-to-jpg-converter src/pdf_to_jpg_converter/app.py
```

Single-file output path:

- `dist/pdf-to-jpg-converter/pdf-to-jpg-converter.exe`

## Output Behavior

- One JPG file is created per PDF page.
- One translated PDF file can be created from the selected source PDF.
- Output filenames follow this pattern:

```text
<pdf-stem>-page-<page-number>.jpg
```

- The translated PDF default filename in the GUI is:

```text
<pdf-stem>-ko.pdf
```

- JPG files are written atomically through a temporary file and then moved into place.
- Translated PDF files are written atomically through a temporary file and then moved into place.
- During translation, the GUI shows an active progress indicator and page-based status text.

## Translation Reliability Notes

- Long text is translated in retryable chunks to tolerate API size limits.
- If translator responses include `None`, the original text chunk is preserved instead of failing.
- PDF span colors are normalized before text insertion to satisfy PyMuPDF color requirements.
- If source font names are incompatible, the renderer falls back to safe fonts for output generation.

## Verified Behavior

- Page count reading works for generated sample PDFs.
- First-page preview rendering works.
- Conversion creates one JPG per page.
- Generated files have valid JPEG signatures.
- Translated PDF generation works through automated tests.
- Translation handles `None` translator responses without crashing.
- Translation emits progress callback events used by the GUI progress display.
- A Windows executable build is produced successfully.

## Out of Scope

- OCR
- PDF editing
- Merge, split, annotate, or compress features
- Cloud or network workflows
- Non-Windows packaging targets
