"""
Document extractors
"""
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor
from ocr_invoice_reader.extractors.simple_ocr import SimpleOCR

__all__ = ["DocumentExtractor", "SimpleOCR"]
