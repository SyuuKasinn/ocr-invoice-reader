"""
Core pipeline for PaddleOCR-VL 1.5 document parsing.

Modules:
- config: pipeline configuration
- vl_engine: PaddleOCRVL wrapper, normalized output
- schemas: pydantic models (Block / PageResult / DocumentResult)
- file_io: input validation and result writing
- visualize: official-style self-contained HTML report
- pipeline: end-to-end orchestration
"""
from ocr_invoice_reader.core.config import (
    IOConfig,
    PipelineConfig,
    VLConfig,
)
from ocr_invoice_reader.core.pipeline import Pipeline
from ocr_invoice_reader.core.schemas import (
    Block,
    DocumentResult,
    PageResult,
)

__all__ = [
    "Pipeline",
    "PipelineConfig",
    "VLConfig",
    "IOConfig",
    "Block",
    "PageResult",
    "DocumentResult",
]
