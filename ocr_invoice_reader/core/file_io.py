"""
Output writers: per-page JSON, combined JSON, markdown, embedded images.

PDF rasterization is delegated to the PaddleOCR-VL pipeline (which handles
PDF input natively), so we no longer need PyMuPDF here.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
PDF_EXT = {".pdf"}
SUPPORTED_EXT = IMAGE_EXT | PDF_EXT


def validate_input(path: str) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    ext = p.suffix.lower()
    if ext not in SUPPORTED_EXT:
        raise ValueError(
            f"Unsupported file type {ext!r}. "
            f"Supported: {sorted(SUPPORTED_EXT)}"
        )
    return p


class ResultWriter:
    """Persist DocumentResult / PageResult content to disk."""

    def __init__(self, output_dir: str | Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_page_json(self, page_name: str, payload: Dict[str, Any]) -> Path:
        path = self.output_dir / f"{page_name}.json"
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, default=_json_default),
            encoding="utf-8",
        )
        return path

    def write_page_markdown(self, page_name: str, markdown: str) -> Path:
        path = self.output_dir / f"{page_name}.md"
        path.write_text(markdown, encoding="utf-8")
        return path

    def write_document_json(self, name: str, payload: Dict[str, Any]) -> Path:
        path = self.output_dir / f"{name}.json"
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, default=_json_default),
            encoding="utf-8",
        )
        return path

    def write_html(self, name: str, html: str) -> Path:
        path = self.output_dir / f"{name}.html"
        path.write_text(html, encoding="utf-8")
        return path

    def save_markdown_images(self, images: Optional[Dict[str, Any]]) -> Dict[str, Path]:
        """Persist images referenced by markdown (key=relative path)."""
        if not images:
            return {}
        saved: Dict[str, Path] = {}
        for rel, value in images.items():
            try:
                dest = self.output_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                if hasattr(value, "save"):
                    value.save(str(dest))
                elif isinstance(value, (bytes, bytearray)):
                    dest.write_bytes(bytes(value))
                elif isinstance(value, str) and Path(value).exists():
                    dest.write_bytes(Path(value).read_bytes())
                else:
                    continue
                saved[rel] = dest
            except Exception as e:
                logger.warning("Failed to save markdown image %s: %s", rel, e)
        return saved


def _json_default(obj: Any) -> Any:
    if hasattr(obj, "tolist"):
        return obj.tolist()
    if isinstance(obj, Path):
        return str(obj)
    return str(obj)
