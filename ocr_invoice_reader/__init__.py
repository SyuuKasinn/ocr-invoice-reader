"""
OCR Invoice Reader - Document Information Extraction System

A comprehensive document information extraction system using PaddleOCR and PP-Structure.
Extracts structured information from invoices, waybills, and other business documents.
"""

__version__ = "2.3.2"
__author__ = "Your Name"
__license__ = "MIT"

from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor
from ocr_invoice_reader.extractors.simple_ocr import SimpleOCR
from ocr_invoice_reader.models.base import BaseDocument, Address, DocumentItem

__all__ = [
    "DocumentExtractor",
    "SimpleOCR",
    "BaseDocument",
    "Address",
    "DocumentItem",
    "__version__",
]
