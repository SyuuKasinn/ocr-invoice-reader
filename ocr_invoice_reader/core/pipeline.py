"""
End-to-end pipeline: file → PaddleOCR-VL → schemas → JSON / markdown / HTML.

Pages are written to disk as soon as each one finishes inference, so on
slow CPU runs you can see partial output immediately instead of waiting
for the entire document.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from ocr_invoice_reader.core.config import PipelineConfig
from ocr_invoice_reader.core.file_io import ResultWriter, validate_input
from ocr_invoice_reader.core.schemas import Block, DocumentResult, PageResult
from ocr_invoice_reader.core.visualize import render_html
from ocr_invoice_reader.core.vl_engine import VLEngine

logger = logging.getLogger(__name__)


class Pipeline:
    """Run PaddleOCR-VL 1.5 over a file and serialize the results."""

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.engine = VLEngine(self.config.vl)

    def run(self, input_path: str, *, max_pages: Optional[int] = None) -> DocumentResult:
        p = validate_input(input_path)
        pages_raw = self.engine.predict(str(p), max_pages=max_pages)
        pages = [_page_from_raw(page, p.name) for page in pages_raw]
        return DocumentResult(document=p.stem, total_pages=len(pages), pages=pages)

    def run_and_save(self, input_path: str, *, max_pages: Optional[int] = None) -> Path:
        p = validate_input(input_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(self.config.io.output_dir) / f"{p.stem}_{timestamp}"
        writer = ResultWriter(out_dir)

        pages: list[PageResult] = []

        def on_page(page_raw: dict) -> None:
            """Stream one finished page straight to disk."""
            page_result = _page_from_raw(page_raw, p.name)
            pages.append(page_result)
            page_name = f"{p.stem}_page_{page_result.page_index + 1:04d}"

            if self.config.io.save_per_page_json:
                writer.write_page_json(page_name, page_result.model_dump())
                logger.info("wrote %s.json", page_name)

            if self.config.io.save_markdown and page_result.markdown:
                writer.write_page_markdown(page_name, page_result.markdown)

            if self.config.io.save_visualization and page_raw.get("_result_obj") is not None:
                _try_save_visualization(page_raw["_result_obj"], out_dir, page_name)

            if page_raw.get("markdown_images"):
                writer.save_markdown_images(page_raw["markdown_images"])

        self.engine.predict(str(p), max_pages=max_pages, on_page=on_page)

        document = DocumentResult(
            document=p.stem,
            total_pages=len(pages),
            pages=pages,
        )

        writer.write_document_json(
            f"{p.stem}_document",
            {
                "document": document.document,
                "total_pages": document.total_pages,
                "pipeline": "PaddleOCR-VL-1.5",
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "pages": [pg.model_dump() for pg in pages],
            },
        )

        html = render_html(
            document=document,
            source_file=p,
            inline_images=self.config.io.inline_images_in_html,
            output_dir=out_dir,
        )
        writer.write_html(f"{p.stem}_report", html)

        logger.info("Output written to %s", out_dir)
        return out_dir


def _page_from_raw(page_raw: dict, source_name: str) -> PageResult:
    blocks = [Block(**b) for b in page_raw["blocks"]]
    return PageResult(
        page_index=page_raw["page_index"],
        source_file=source_name,
        image_path=page_raw.get("image_path"),
        blocks=blocks,
        markdown=page_raw.get("markdown"),
    )


def _try_save_visualization(result_obj, out_dir: Path, page_name: str) -> None:
    """Best-effort: ask the PaddleOCR-VL result to render its overlay image."""
    try:
        if hasattr(result_obj, "save_to_img"):
            result_obj.save_to_img(save_path=str(out_dir / f"{page_name}_viz.png"))
            return
        if hasattr(result_obj, "save_to_image"):
            result_obj.save_to_image(save_path=str(out_dir / f"{page_name}_viz.png"))
            return
    except Exception as e:
        logger.warning("save visualization failed for %s: %s", page_name, e)
