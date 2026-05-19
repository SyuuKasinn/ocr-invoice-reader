"""
OCR Invoice Reader — PaddleOCR-VL 1.5 document parsing.

Single-pass parsing of invoices, waybills, customs declarations, and
other business documents using PaddleOCR-VL 1.5. Outputs structured
JSON, Markdown, and a self-contained HTML report.

Primary entry point: `ocr-extract` CLI.
"""

__version__ = "4.0.0"
__author__ = "Your Name"
__license__ = "MIT"

from ocr_invoice_reader.core import (
    Block,
    DocumentResult,
    IOConfig,
    PageResult,
    Pipeline,
    PipelineConfig,
    VLConfig,
)

__all__ = [
    "Pipeline",
    "PipelineConfig",
    "VLConfig",
    "IOConfig",
    "Block",
    "PageResult",
    "DocumentResult",
    "__version__",
]
