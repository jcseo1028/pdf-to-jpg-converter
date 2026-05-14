from __future__ import annotations

import logging
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import ImageTk

from .converter import convert_pdf_to_jpg, read_page_count, render_preview, translate_pdf_to_korean


class PdfToJpgApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF to JPG Converter")
        self.root.geometry("900x700")

        self.pdf_path: Path | None = None
        self.preview_photo: ImageTk.PhotoImage | None = None

        container = ttk.Frame(root, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        controls = ttk.Frame(container)
        controls.pack(fill=tk.X)

        self.open_button = ttk.Button(controls, text="Open PDF", command=self.open_pdf)
        self.open_button.pack(side=tk.LEFT)

        self.convert_button = ttk.Button(controls, text="Convert to JPG", command=self.convert_pdf)
        self.convert_button.pack(side=tk.LEFT, padx=(12, 0))
        self.convert_button.state(["disabled"])

        self.translate_button = ttk.Button(
            controls,
            text="Translate to Korean PDF",
            command=self.translate_pdf,
        )
        self.translate_button.pack(side=tk.LEFT, padx=(12, 0))
        self.translate_button.state(["disabled"])

        self.file_label = ttk.Label(container, text="No PDF selected.")
        self.file_label.pack(anchor=tk.W, pady=(12, 0))

        self.info_label = ttk.Label(container, text="")
        self.info_label.pack(anchor=tk.W, pady=(4, 12))

        preview_frame = ttk.LabelFrame(container, text="Preview", padding=12)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        self.preview_label = ttk.Label(preview_frame, text="Open a PDF to preview the first page.", anchor=tk.CENTER)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        self.status_label = ttk.Label(container, text="Ready.")
        self.status_label.pack(anchor=tk.W, pady=(12, 0))

        self.progress_bar = ttk.Progressbar(container, mode="indeterminate", length=300)
        self.progress_bar.pack(fill=tk.X, pady=(8, 0))
        self.progress_bar.pack_forget()

    def _set_busy(self, is_busy: bool) -> None:
        if is_busy:
            self.open_button.state(["disabled"])
            self.convert_button.state(["disabled"])
            self.translate_button.state(["disabled"])
        else:
            self.open_button.state(["!disabled"])
            if self.pdf_path is None:
                self.convert_button.state(["disabled"])
                self.translate_button.state(["disabled"])
            else:
                self.convert_button.state(["!disabled"])
                self.translate_button.state(["!disabled"])

    def _show_progress(self) -> None:
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(8, 0))
        self.progress_bar.start(12)
        self.root.update_idletasks()

    def _hide_progress(self) -> None:
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.root.update_idletasks()

    def _on_translation_progress(self, current_page: int, total_pages: int) -> None:
        self.progress_bar.step(2)
        self.status_label.config(text=f"Translating PDF to Korean... (page {current_page}/{total_pages})")
        self.root.update_idletasks()

    def _on_translation_completed(self, output_path: Path) -> None:
        self.status_label.config(text=f"Saved translated PDF: {output_path}")
        self._hide_progress()
        self._set_busy(False)
        messagebox.showinfo("Translate to Korean PDF", f"Saved: {output_path}")

    def _on_translation_failed(self, error: Exception) -> None:
        logging.exception("Translate to Korean PDF failed", exc_info=error)
        self.status_label.config(text="Translation failed.")
        self._hide_progress()
        self._set_busy(False)
        messagebox.showerror(
            "Translate to Korean PDF",
            f"{error}\n\nAutomatic text-chunk retry was attempted. Please try a shorter document or split pages and retry.",
        )

    def open_pdf(self) -> None:
        selected_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf")],
        )
        if not selected_path:
            return

        self.pdf_path = Path(selected_path)
        self.file_label.config(text=str(self.pdf_path))

        try:
            page_count = read_page_count(self.pdf_path)
            preview_image = render_preview(self.pdf_path, zoom=1.2)
            preview_image.thumbnail((820, 560))
            self.preview_photo = ImageTk.PhotoImage(preview_image)
            self.preview_label.config(image=self.preview_photo, text="")
            self.info_label.config(text=f"Pages: {page_count}")
            self.status_label.config(text="PDF loaded.")
            self.convert_button.state(["!disabled"])
            self.translate_button.state(["!disabled"])
        except Exception as error:
            self.preview_label.config(image="", text="Failed to load preview.")
            self.info_label.config(text="")
            self.status_label.config(text="Failed to load PDF.")
            self.convert_button.state(["disabled"])
            self.translate_button.state(["disabled"])
            messagebox.showerror("Open PDF", str(error))

    def convert_pdf(self) -> None:
        if self.pdf_path is None:
            return

        output_directory = filedialog.askdirectory(title="Select output folder")
        if not output_directory:
            return

        try:
            self._set_busy(True)
            self._show_progress()
            self.status_label.config(text="Converting PDF pages to JPG...")
            self.root.update_idletasks()
            result = convert_pdf_to_jpg(self.pdf_path, output_directory)
            self.status_label.config(text=f"Created {result.page_count} JPG files.")
            messagebox.showinfo("Convert to JPG", f"Created {result.page_count} JPG files.")
        except Exception as error:
            self.status_label.config(text="Conversion failed.")
            messagebox.showerror("Convert to JPG", str(error))
        finally:
            self._hide_progress()
            self._set_busy(False)

    def translate_pdf(self) -> None:
        if self.pdf_path is None:
            return

        translated_pdf_path = filedialog.asksaveasfilename(
            title="Save translated PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"{self.pdf_path.stem}-ko.pdf",
        )
        if not translated_pdf_path:
            return

        selected_output_path = Path(translated_pdf_path)
        if selected_output_path.resolve() == self.pdf_path.resolve():
            overwrite_confirmed = messagebox.askyesno(
                "Overwrite source PDF",
                "You selected the same file as the source PDF. Overwrite it?",
            )
            if not overwrite_confirmed:
                self.status_label.config(text="Translation canceled.")
                return

        self._set_busy(True)
        self._show_progress()
        self.status_label.config(text="Translating PDF to Korean... (starting)")
        self.root.update_idletasks()

        def worker() -> None:
            try:
                result = translate_pdf_to_korean(
                    self.pdf_path,
                    selected_output_path,
                    progress_callback=lambda current, total: self.root.after(
                        0,
                        self._on_translation_progress,
                        current,
                        total,
                    ),
                )
                self.root.after(0, self._on_translation_completed, result.output_pdf_path)
            except Exception as error:
                self.root.after(0, self._on_translation_failed, error)

        threading.Thread(target=worker, daemon=True).start()


def build_app() -> tk.Tk:
    root = tk.Tk()
    PdfToJpgApp(root)
    return root