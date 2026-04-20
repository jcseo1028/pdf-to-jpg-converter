from __future__ import annotations

from pathlib import Path

import fitz

from pdf_to_jpg_converter.converter import convert_pdf_to_jpg, read_page_count, render_preview


def create_sample_pdf(pdf_path: Path, page_count: int = 2) -> None:
    document = fitz.open()
    try:
        for index in range(page_count):
            page = document.new_page()
            page.insert_text((72, 72), f"Sample page {index + 1}")
        document.save(pdf_path)
    finally:
        document.close()


def test_read_page_count_returns_document_page_count(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    create_sample_pdf(pdf_path, page_count=3)

    assert read_page_count(pdf_path) == 3


def test_render_preview_returns_non_empty_image(tmp_path: Path) -> None:
    pdf_path = tmp_path / "preview.pdf"
    create_sample_pdf(pdf_path, page_count=1)

    preview_image = render_preview(pdf_path)

    assert preview_image.width > 0
    assert preview_image.height > 0


def test_convert_pdf_to_jpg_creates_one_jpg_per_page(tmp_path: Path) -> None:
    pdf_path = tmp_path / "convert.pdf"
    output_directory = tmp_path / "output"
    create_sample_pdf(pdf_path, page_count=2)

    result = convert_pdf_to_jpg(pdf_path, output_directory)

    assert result.page_count == 2
    assert len(result.jpg_file_paths) == 2
    assert all(path.exists() for path in result.jpg_file_paths)
    assert all(path.suffix.lower() == ".jpg" for path in result.jpg_file_paths)
    assert all(path.read_bytes().startswith(b"\xff\xd8\xff") for path in result.jpg_file_paths)