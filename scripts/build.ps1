param(
    [string]$PythonExe = "python"
)

& $PythonExe -m PyInstaller --noconfirm --clean --windowed --name "pdf-to-jpg-converter" --paths "src" "src/pdf_to_jpg_converter/app.py"