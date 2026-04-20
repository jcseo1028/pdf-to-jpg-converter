from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz
from PIL import Image


@dataclass(frozen=True)
class ConversionResult:
    page_count: int
    jpg_file_paths: list[Path]


def read_page_count(pdf_path: str | Path) -> int:
    pdf_file = Path(pdf_path)
    document = fitz.open(pdf_file)
    try:
        return document.page_count
    finally:
        document.close()


def render_preview(pdf_path: str | Path, page_index: int = 0, zoom: float = 1.0) -> Image.Image:
    pdf_file = Path(pdf_path)
    document = fitz.open(pdf_file)
    try:
        page = document.load_page(page_index)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        return Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
    finally:
        document.close()


def convert_pdf_to_jpg(pdf_path: str | Path, output_directory: str | Path, zoom: float = 2.0) -> ConversionResult:
    pdf_file = Path(pdf_path)
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    document = fitz.open(pdf_file)
    jpg_file_paths: list[Path] = []
    try:
        for page_number in range(document.page_count):
            page = document.load_page(page_number)
            pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            output_path = output_dir / f"{pdf_file.stem}-page-{page_number + 1}.jpg"
            temporary_output_path = output_path.with_suffix(".tmp")
            try:
                image.save(temporary_output_path, format="JPEG", quality=95)
            finally:
                image.close()
            temporary_output_path.replace(output_path)
            jpg_file_paths.append(output_path)
    finally:
        document.close()

    return ConversionResult(page_count=len(jpg_file_paths), jpg_file_paths=jpg_file_paths)