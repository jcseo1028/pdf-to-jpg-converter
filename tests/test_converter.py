from __future__ import annotations

from pathlib import Path

import fitz

from pdf_to_jpg_converter.converter import (
    _normalize_text_color,
    convert_pdf_to_jpg,
    read_page_count,
    render_preview,
    translate_pdf_to_korean,
)


def create_sample_pdf(pdf_path: Path, page_count: int = 2) -> None:
    document = fitz.open()
    try:
        for index in range(page_count):
            page = document.new_page()
            page.insert_text((72, 72), f"Sample page {index + 1}")
        document.save(pdf_path)
    finally:
        document.close()


def create_text_pdf(pdf_path: Path, text: str) -> None:
    document = fitz.open()
    try:
        page = document.new_page()
        text_area = fitz.Rect(48, 48, 560, 800)
        page.insert_textbox(text_area, text, fontsize=10)
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


def test_translate_pdf_to_korean_creates_translated_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "translate.pdf"
    output_pdf_path = tmp_path / "translate-ko.pdf"
    create_sample_pdf(pdf_path, page_count=2)

    result = translate_pdf_to_korean(
        pdf_path,
        output_pdf_path,
        translator=lambda text: f"[KO] {text}",
    )

    assert result.page_count == 2
    assert result.target_language == "ko"
    assert result.output_pdf_path == output_pdf_path
    assert output_pdf_path.exists()

    translated_document = fitz.open(output_pdf_path)
    try:
        first_page_text = translated_document.load_page(0).get_text("text")
        assert "[KO]" in first_page_text
    finally:
        translated_document.close()


def test_translate_pdf_to_korean_splits_long_text_and_retries(tmp_path: Path) -> None:
    pdf_path = tmp_path / "long-translate.pdf"
    output_pdf_path = tmp_path / "long-translate-ko.pdf"
    long_text = ("This is a long paragraph for translation. " * 120) + "\n\n" + ("More content. " * 120)
    create_text_pdf(pdf_path, long_text)

    captured_lengths: list[int] = []

    def length_limited_translator(text: str) -> str:
        captured_lengths.append(len(text))
        if len(text) > 100:
            raise ValueError("Text length need to be between 0 and 5000 characters")
        return f"[KO]{text}"

    result = translate_pdf_to_korean(
        pdf_path,
        output_pdf_path,
        translator=length_limited_translator,
        max_translation_chars=100,
    )

    assert result.page_count == 1
    assert output_pdf_path.exists()
    assert all(length <= 100 for length in captured_lengths if length > 0)


def test_translate_pdf_to_korean_handles_none_translation_result(tmp_path: Path) -> None:
    pdf_path = tmp_path / "none-translate.pdf"
    output_pdf_path = tmp_path / "none-translate-ko.pdf"
    create_text_pdf(pdf_path, "A - B")

    def translator_with_none(text: str) -> str | None:
        if text.strip() == "-":
            return None
        return f"[KO]{text}"

    result = translate_pdf_to_korean(
        pdf_path,
        output_pdf_path,
        translator=translator_with_none,
        max_translation_chars=100,
    )

    assert result.page_count == 1
    assert output_pdf_path.exists()


def test_normalize_text_color_converts_integer_rgb_to_float_tuple() -> None:
    assert _normalize_text_color(0x3366CC) == (51 / 255, 102 / 255, 204 / 255)


def test_normalize_text_color_clamps_tuple_values() -> None:
    assert _normalize_text_color((255, 128, -1)) == (1.0, 128 / 255, 0.0)


def test_translate_pdf_to_korean_reports_progress_callback(tmp_path: Path) -> None:
    pdf_path = tmp_path / "progress-translate.pdf"
    output_pdf_path = tmp_path / "progress-translate-ko.pdf"
    create_sample_pdf(pdf_path, page_count=2)

    progress_events: list[tuple[int, int]] = []

    translate_pdf_to_korean(
        pdf_path,
        output_pdf_path,
        translator=lambda text: f"[KO]{text}",
        progress_callback=lambda current, total: progress_events.append((current, total)),
    )

    assert progress_events
    assert all(total == 2 for _, total in progress_events)
    assert progress_events[-1][0] == 2