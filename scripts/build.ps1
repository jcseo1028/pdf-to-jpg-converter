param(
    [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

& $PythonExe -m pip install -e ".[dev]"
& $PythonExe -m PyInstaller --noconfirm --clean --windowed --name "pdf-to-jpg-converter" --paths "src" --hidden-import deep_translator "src/pdf_to_jpg_converter/app.py"