from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import ImageTk

from .converter import convert_pdf_to_jpg, read_page_count, render_preview


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
        except Exception as error:
            self.preview_label.config(image="", text="Failed to load preview.")
            self.info_label.config(text="")
            self.status_label.config(text="Failed to load PDF.")
            self.convert_button.state(["disabled"])
            messagebox.showerror("Open PDF", str(error))

    def convert_pdf(self) -> None:
        if self.pdf_path is None:
            return

        output_directory = filedialog.askdirectory(title="Select output folder")
        if not output_directory:
            return

        try:
            self.status_label.config(text="Converting PDF pages to JPG...")
            self.root.update_idletasks()
            result = convert_pdf_to_jpg(self.pdf_path, output_directory)
            self.status_label.config(text=f"Created {result.page_count} JPG files.")
            messagebox.showinfo("Convert to JPG", f"Created {result.page_count} JPG files.")
        except Exception as error:
            self.status_label.config(text="Conversion failed.")
            messagebox.showerror("Convert to JPG", str(error))


def build_app() -> tk.Tk:
    root = tk.Tk()
    PdfToJpgApp(root)
    return root