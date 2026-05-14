from __future__ import annotations

import logging

# Configure logging
logging.basicConfig(
    filename="application.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

from pdf_to_jpg_converter.gui import build_app


def main() -> None:
    app = build_app()
    app.mainloop()


if __name__ == "__main__":
    main()