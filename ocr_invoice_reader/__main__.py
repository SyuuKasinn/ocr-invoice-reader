"""Entry point so `python -m ocr_invoice_reader` runs the CLI."""
import sys

from ocr_invoice_reader.cli.extract import main

if __name__ == "__main__":
    sys.exit(main())
