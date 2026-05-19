"""
Schemas for PaddleOCR-VL parsing results.

A document is a list of pages; a page is a list of typed blocks (title,
paragraph, table, figure, ...). Tables carry HTML, figures carry image
paths, everything carries a bbox for visualization.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class Block(_Base):
    """A single layout block from PaddleOCR-VL."""
    label: str = "text"
    bbox: List[float] = Field(default_factory=list)
    text: str = ""
    html: Optional[str] = None
    image_path: Optional[str] = None
    score: Optional[float] = None


class PageResult(_Base):
    page_index: int = 0
    source_file: str = ""
    image_path: Optional[str] = None
    blocks: List[Block] = Field(default_factory=list)
    markdown: Optional[str] = None

    @property
    def table_count(self) -> int:
        return sum(1 for b in self.blocks if b.label == "table")

    @property
    def text_block_count(self) -> int:
        return sum(1 for b in self.blocks if b.label not in {"table", "figure", "image"})


class DocumentResult(_Base):
    document: str = ""
    total_pages: int = 0
    pages: List[PageResult] = Field(default_factory=list)
