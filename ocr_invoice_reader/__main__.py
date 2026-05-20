"""Entry point so `python -m ocr_invoice_reader` runs the CLI."""
import os
if os.environ.get("OCR_KEEP_OMP", "0") != "1":
    os.environ["OMP_NUM_THREADS"] = "1"

import sys

from ocr_invoice_reader.cli.extract import main

if __name__ == "__main__":
    sys.exit(main())
