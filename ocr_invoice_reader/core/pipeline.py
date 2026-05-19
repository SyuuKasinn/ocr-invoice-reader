"""
End-to-end pipeline: file → PaddleOCR-VL → schemas → JSON / markdown / HTML.
"""
from __future__ import annotations

import logging
import time
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

    def run(self, input_path: str) -> DocumentResult:
        p = validate_input(input_path)
        t0 = time.time()
        pages_raw = self.engine.predict(str(p))
        logger.info("VL produced %d page(s) in %.2fs", len(pages_raw), time.time() - t0)

        pages = []
        for page in pages_raw:
            blocks = [Block(**b) for b in page["blocks"]]
            pages.append(PageResult(
                page_index=page["page_index"],
                source_file=p.name,
                image_path=page.get("image_path"),
                blocks=blocks,
                markdown=page.get("markdown"),
            ))

        return DocumentResult(
            document=p.stem,
            total_pages=len(pages),
            pages=pages,
        )

    def run_and_save(self, input_path: str) -> Path:
        p = validate_input(input_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(self.config.io.output_dir) / f"{p.stem}_{timestamp}"
        writer = ResultWriter(out_dir)

        pages_raw = self.engine.predict(str(p))

        pages: list[PageResult] = []
        markdown_images_merged = {}

        for page in pages_raw:
            page_idx = page["page_index"] + 1
            page_name = f"{p.stem}_page_{page_idx:04d}"

            blocks = [Block(**b) for b in page["blocks"]]
            page_result = PageResult(
                page_index=page["page_index"],
                source_file=p.name,
                image_path=page.get("image_path"),
                blocks=blocks,
                markdown=page.get("markdown"),
            )
            pages.append(page_result)

            if self.config.io.save_per_page_json:
                writer.write_page_json(page_name, page_result.model_dump())

            if self.config.io.save_markdown and page_result.markdown:
                writer.write_page_markdown(page_name, page_result.markdown)

            if self.config.io.save_visualization and page.get("_result_obj") is not None:
                _try_save_visualization(page["_result_obj"], out_dir, page_name)

            if page.get("markdown_images"):
                saved = writer.save_markdown_images(page["markdown_images"])
                markdown_images_merged.update(saved)

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
