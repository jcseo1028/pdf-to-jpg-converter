from __future__ import annotations

from pdf_to_jpg_converter.gui import build_app


def main() -> None:
    app = build_app()
    app.mainloop()


if __name__ == "__main__":
    main()