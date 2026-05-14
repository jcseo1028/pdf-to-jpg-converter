from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import re

import fitz
from PIL import Image


_WINDOWS_KOREAN_FONT_PATH = Path("C:/Windows/Fonts/malgun.ttf")


@dataclass(frozen=True)
class ConversionResult:
    page_count: int
    jpg_file_paths: list[Path]


@dataclass(frozen=True)
class TranslationResult:
    page_count: int
    output_pdf_path: Path
    target_language: str


def _build_default_korean_translator() -> Callable[[str], str]:
    try:
        from deep_translator import GoogleTranslator
    except ImportError as error:
        raise RuntimeError(
            "Korean translation requires the 'deep-translator' package. Install project dependencies first."
        ) from error

    translator = GoogleTranslator(source="auto", target="ko")

    def translate_text(text: str) -> str:
        if not text.strip():
            return ""
        translated = translator.translate(text)
        if translated is None:
            return text
        return translated

    return translate_text


def _split_text_by_max_length(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    pieces: list[str] = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + max_chars, text_length)
        if end < text_length:
            newline_index = text.rfind("\n", start, end)
            space_index = text.rfind(" ", start, end)
            split_index = max(newline_index, space_index)
            if split_index > start:
                end = split_index + 1
        pieces.append(text[start:end])
        start = end
    return pieces


def _translate_chunk_with_retry(chunk: str, translate_text: Callable[[str], str], max_chars: int) -> str:
    try:
        translated = translate_text(chunk)
        if translated is None:
            # Some translators return None for punctuation-only input.
            return chunk
        return translated
    except Exception as error:
        error_message = str(error).lower()
        is_length_error = "5000" in error_message or "text length" in error_message
        if is_length_error and len(chunk) > 1:
            split_chunks = _split_text_by_max_length(chunk, max(1, len(chunk) // 2))
            translated_parts = [
                _translate_chunk_with_retry(part, translate_text, max_chars)
                for part in split_chunks
                if part
            ]
            return "".join(translated_parts)
        raise


def _translate_text_preserving_paragraphs(text: str, translate_text: Callable[[str], str], max_chars: int) -> str:
    if not text.strip():
        return ""

    translated_blocks: list[str] = []
    blocks = re.split(r"(\n\s*\n)", text)
    for block in blocks:
        if not block:
            continue
        if re.fullmatch(r"\n\s*\n", block):
            translated_blocks.append(block)
            continue

        chunks = _split_text_by_max_length(block, max_chars)
        translated_chunks = [
            _translate_chunk_with_retry(chunk, translate_text, max_chars)
            for chunk in chunks
            if chunk.strip()
        ]
        translated_blocks.append("".join(translated_chunks))

    return "".join(translated_blocks)


def _normalize_text_color(color: object) -> tuple[float, float, float]:
    if isinstance(color, int):
        red = (color >> 16) & 0xFF
        green = (color >> 8) & 0xFF
        blue = color & 0xFF
        return (red / 255.0, green / 255.0, blue / 255.0)

    if isinstance(color, (tuple, list)):
        numeric_values = [float(value) for value in color if isinstance(value, (int, float))]
        if len(numeric_values) == 1:
            value = numeric_values[0]
            if value > 1:
                value = value / 255.0
            value = min(max(value, 0.0), 1.0)
            return (value, value, value)
        if len(numeric_values) >= 3:
            rgb = numeric_values[:3]
            if any(component > 1 for component in rgb):
                rgb = [component / 255.0 for component in rgb]
            return tuple(min(max(component, 0.0), 1.0) for component in rgb)

    return (0.0, 0.0, 0.0)


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


def translate_pdf_to_korean(
    pdf_path: str | Path,
    output_pdf_path: str | Path,
    translator: Callable[[str], str] | None = None,
    max_translation_chars: int = 4500,
    progress_callback: Callable[[int, int], None] | None = None,
) -> TranslationResult:
    pdf_file = Path(pdf_path)
    translated_pdf_file = Path(output_pdf_path)
    translated_pdf_file.parent.mkdir(parents=True, exist_ok=True)

    translate_text = translator or _build_default_korean_translator()

    source_document = fitz.open(pdf_file)
    translated_document = fitz.open()
    page_count = source_document.page_count
    try:
        for page_index in range(page_count):
            source_page = source_document.load_page(page_index)
            text_blocks = source_page.get_text("dict")

            target_page = translated_document.new_page(
                width=source_page.rect.width, height=source_page.rect.height
            )

            # Copy images from the source page
            for image in source_page.get_images(full=True):
                xref = image[0]
                pix = fitz.Pixmap(source_document, xref)
                target_page.insert_image(source_page.rect, pixmap=pix)

            # Translate and insert text blocks
            page_had_text = False
            for block in text_blocks.get("blocks", []):
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if text:
                            page_had_text = True
                            try:
                                translated_text = _translate_text_preserving_paragraphs(
                                    text, translate_text, max_translation_chars
                                )
                            except Exception as error:
                                raise RuntimeError(
                                    f"Translation failed on page {page_index + 1}: {error}"
                                ) from error

                            # Insert translated text with original style
                            insert_point = fitz.Point(span["bbox"][0], span["bbox"][1])
                            font_size = span.get("size", 11)
                            source_font_name = span.get("font", "helv")
                            color = _normalize_text_color(span.get("color", 0))

                            try:
                                target_page.insert_text(
                                    insert_point,
                                    translated_text,
                                    fontsize=font_size,
                                    fontname=source_font_name,
                                    color=color,
                                )
                            except Exception:
                                # Some source PDF fonts are embedded-only names or contain unsupported characters.

                                if _WINDOWS_KOREAN_FONT_PATH.exists():
                                    try:
                                        target_page.insert_text(
                                            insert_point,
                                            translated_text,
                                            fontsize=font_size,
                                            fontname="malgun",
                                            fontfile=str(_WINDOWS_KOREAN_FONT_PATH),
                                            color=color,
                                        )
                                        continue
                                    except Exception:
                                        pass

                                target_page.insert_text(
                                    insert_point,
                                    translated_text,
                                    fontsize=font_size,
                                    fontname="helv",
                                    color=color,
                                )

                            if progress_callback is not None:
                                progress_callback(page_index + 1, page_count)

            if progress_callback is not None and not page_had_text:
                progress_callback(page_index + 1, page_count)

        temporary_output_path = translated_pdf_file.with_suffix(".tmp.pdf")
        translated_document.save(temporary_output_path)
        temporary_output_path.replace(translated_pdf_file)
    finally:
        translated_document.close()
        source_document.close()

    return TranslationResult(
        page_count=page_count,
        output_pdf_path=translated_pdf_file,
        target_language="ko",
    )