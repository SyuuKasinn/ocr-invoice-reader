"""
PaddleOCR-VL 1.5 engine wrapper.

Wraps the official `PaddleOCRVL` pipeline so the rest of the codebase
sees a single `predict(image_or_pdf)` call returning normalized page results.

Requires paddleocr >= 3.0 (which ships the PaddleOCRVL pipeline).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ocr_invoice_reader.core.config import VLConfig

logger = logging.getLogger(__name__)


def _ensure_paddleocr_vl():
    try:
        import paddleocr  # noqa: F401
    except ImportError as e:
        raise ImportError(
            "paddleocr is not installed.\n"
            "Install: pip install \"paddleocr>=3.0.0\" paddlepaddle"
        ) from e

    try:
        from paddleocr import PaddleOCRVL  # type: ignore
        return PaddleOCRVL
    except ImportError as e:
        installed = getattr(__import__("paddleocr"), "__version__", "unknown")
        raise ImportError(
            f"`PaddleOCRVL` is not available in paddleocr {installed}.\n"
            "PaddleOCR-VL 1.5 requires paddleocr >= 3.0.\n"
            "Upgrade: pip install --upgrade \"paddleocr>=3.0.0\""
        ) from e


class VLEngine:
    """Thin, lazily-initialized wrapper around the PaddleOCRVL pipeline."""

    def __init__(self, config: Optional[VLConfig] = None):
        self.config = config or VLConfig()
        self._pipeline = None

    def _build(self):
        if self._pipeline is not None:
            return self._pipeline

        PaddleOCRVL = _ensure_paddleocr_vl()

        kwargs: Dict[str, Any] = {
            "use_doc_orientation_classify": self.config.use_doc_orientation_classify,
            "use_doc_unwarping": self.config.use_doc_unwarping,
        }
        if self.config.lang:
            kwargs["lang"] = self.config.lang
        kwargs["device"] = "gpu" if self._gpu_ok() else "cpu"

        logger.info("Initializing PaddleOCR-VL pipeline: %s", kwargs)
        self._pipeline = PaddleOCRVL(**{k: v for k, v in kwargs.items() if v is not None})
        return self._pipeline

    def _gpu_ok(self) -> bool:
        if not self.config.use_gpu:
            return False
        try:
            import paddle
            return (
                paddle.device.is_compiled_with_cuda()
                and paddle.device.cuda.device_count() > 0
            )
        except Exception as e:
            logger.warning("GPU probe failed (%s); using CPU", e)
            return False

    def predict(
        self,
        input_path: str,
        *,
        max_pages: Optional[int] = None,
        on_page: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run the VL pipeline on a single PDF or image.

        Args:
            input_path: PDF or image path.
            max_pages: optional cap on the number of pages to process.
            on_page: optional callback(page_dict) invoked after each page
                     so callers can stream results to disk without waiting
                     for the whole document.

        Returns:
            Normalized page dicts; see _normalize_result.
        """
        import time

        pipeline = self._build()
        path = str(Path(input_path).resolve())
        logger.info("VL predict: %s", path)

        output = pipeline.predict(input=path)
        pages: List[Dict[str, Any]] = []
        t_start = time.time()
        t_prev = t_start

        for idx, res in enumerate(output):
            page = _normalize_result(res, page_index=idx, source=path)
            now = time.time()
            logger.info(
                "VL page %d done (%.1fs page / %.1fs total, %d blocks)",
                idx + 1, now - t_prev, now - t_start, len(page["blocks"]),
            )
            t_prev = now
            pages.append(page)
            if on_page is not None:
                try:
                    on_page(page)
                except Exception as e:
                    logger.warning("on_page callback failed for page %d: %s", idx + 1, e)
            if max_pages and len(pages) >= max_pages:
                logger.info("VL max_pages=%d reached; stopping", max_pages)
                break

        logger.info("VL produced %d page(s) in %.1fs", len(pages), time.time() - t_start)
        return pages


def _normalize_result(res: Any, *, page_index: int, source: str) -> Dict[str, Any]:
    """Map a single PaddleOCRVL result object to our normalized dict."""
    raw_json: Any = None
    for attr in ("json", "_json"):
        if hasattr(res, attr):
            try:
                value = getattr(res, attr)
                raw_json = value if not callable(value) else value()
                break
            except Exception:
                continue

    md_text: Optional[str] = None
    md_images: Optional[Dict[str, Any]] = None
    if hasattr(res, "markdown"):
        try:
            md = res.markdown
            md = md() if callable(md) else md
            if isinstance(md, dict):
                md_text = md.get("markdown_texts") or md.get("text") or md.get("markdown")
                md_images = md.get("markdown_images") or md.get("images")
            elif isinstance(md, tuple) and len(md) >= 1:
                md_text = md[0]
                md_images = md[1] if len(md) >= 2 else None
            elif isinstance(md, str):
                md_text = md
        except Exception as e:
            logger.debug("markdown extraction failed: %s", e)

    parsing_list = []
    if isinstance(raw_json, dict):
        for key in ("parsing_res_list", "layout_parsing_result", "blocks"):
            if isinstance(raw_json.get(key), list):
                parsing_list = raw_json[key]
                break

    blocks: List[Dict[str, Any]] = []
    for item in parsing_list:
        if not isinstance(item, dict):
            continue
        label = (
            item.get("block_label")
            or item.get("label")
            or item.get("type")
            or "text"
        )
        bbox = (
            item.get("block_bbox")
            or item.get("bbox")
            or item.get("region_bbox")
            or []
        )
        content = item.get("block_content") or item.get("content") or item.get("text") or ""

        html = None
        if isinstance(content, str) and content.strip().lower().startswith("<table"):
            html = content
            text = ""
        else:
            text = content if isinstance(content, str) else ""

        if label == "table" and not html:
            table = item.get("table") or {}
            html = table.get("html") or item.get("html")

        block = {
            "label": label,
            "bbox": list(bbox) if bbox else [],
            "text": text,
            "html": html,
            "score": item.get("score") or item.get("confidence"),
        }

        img = item.get("block_image") or item.get("image")
        if isinstance(img, dict) and img.get("path"):
            block["image_path"] = img["path"]
        elif isinstance(img, str):
            block["image_path"] = img

        blocks.append(block)

    image_path = None
    if isinstance(raw_json, dict):
        image_path = (
            raw_json.get("image_path")
            or raw_json.get("input_path")
            or raw_json.get("doc_preprocessor_res", {}).get("output_img_path")
        )

    return {
        "page_index": page_index,
        "input_path": source,
        "image_path": image_path,
        "blocks": blocks,
        "raw": raw_json,
        "markdown": md_text,
        "markdown_images": md_images,
        "_result_obj": res,
    }
