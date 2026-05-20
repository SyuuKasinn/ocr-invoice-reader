"""
ocr-extract: parse a PDF or image with PaddleOCR-VL 1.5.

The pipeline auto-detects a CUDA-capable PaddlePaddle install and uses
GPU when present, otherwise CPU. Pass --cpu to force CPU for debugging.

Usage:
  ocr-extract invoice.pdf
  ocr-extract invoice.pdf -o results
  ocr-extract invoice.pdf --max-pages 1 -v
  ocr-extract invoice.pdf --no-html --no-markdown
"""
from __future__ import annotations

# Must run BEFORE any import that transitively loads paddle: paddle prints
# a loud warning (and risks OpenBLAS failures) when OMP_NUM_THREADS != 1.
# Container images often set it to the CPU count; force 1 unless the user
# really wants their own value.
import os
if os.environ.get("OCR_KEEP_OMP", "0") != "1":
    os.environ["OMP_NUM_THREADS"] = "1"

import argparse
import io
import logging
import sys
from pathlib import Path

from ocr_invoice_reader import __version__
from ocr_invoice_reader.core import IOConfig, Pipeline, PipelineConfig, VLConfig


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ocr-extract",
        description="Parse documents with PaddleOCR-VL 1.5.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("input", help="Path to PDF or image file")
    p.add_argument("-o", "--output-dir", default="results", help="Output root directory")

    p.add_argument("--cpu", action="store_true",
                   help="Force CPU even when a GPU is detected (debugging)")
    p.add_argument("--lang", default=None,
                   help="Language hint passed to PaddleOCR-VL (optional)")
    p.add_argument("--unwarp", action="store_true",
                   help="Enable document unwarping (slower)")
    p.add_argument("--orient", action="store_true",
                   help="Enable document orientation classification")

    p.add_argument("--max-pages", type=int, default=None,
                   help="Stop after N pages (useful for testing on long PDFs)")
    p.add_argument("--no-html", action="store_true", help="Skip HTML report")
    p.add_argument("--no-markdown", action="store_true", help="Skip per-page markdown")
    p.add_argument("--no-viz", action="store_true",
                   help="Skip per-page PaddleOCR-VL visualization images")
    p.add_argument("--no-inline-images", action="store_true",
                   help="Reference the source file instead of base64-embedding it")
    p.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    return p


def _setup_console() -> None:
    if sys.platform == "win32":
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main() -> int:
    _setup_console()
    args = _build_parser().parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    config = PipelineConfig(
        vl=VLConfig(
            use_gpu=not args.cpu,
            lang=args.lang,
            use_doc_orientation_classify=args.orient,
            use_doc_unwarping=args.unwarp,
        ),
        io=IOConfig(
            output_dir=args.output_dir,
            save_markdown=not args.no_markdown,
            save_visualization=not args.no_viz,
            inline_images_in_html=not args.no_inline_images,
        ),
    )

    pipeline = Pipeline(config)

    try:
        out_dir = pipeline.run_and_save(args.input, max_pages=args.max_pages)
    except FileNotFoundError as e:
        print(f"Input not found: {e}", file=sys.stderr)
        return 2
    except ImportError as e:
        print(f"\n{e}\n", file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        logging.exception("Pipeline error")
        print(f"\nError: {e}", file=sys.stderr)
        return 1

    print(f"\nResults: {out_dir}")
    if not args.no_html:
        report = out_dir / f"{Path(args.input).stem}_report.html"
        print(f"  open: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
