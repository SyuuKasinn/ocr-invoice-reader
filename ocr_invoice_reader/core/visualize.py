"""
Self-contained HTML report mimicking the official PaddleOCR-VL 1.5 UI:

  +----------------------+---------------------------------+
  | Source File          | Parsing model: PaddleOCR-VL-1.5 |
  |  [PDF / image embed] | [ Document parsing ] [ JSON ]   |
  |                      |  rendered tables / titles ...   |
  +----------------------+---------------------------------+
"""
from __future__ import annotations

import base64
import html as _html
import json
import logging
from pathlib import Path
from typing import List

from ocr_invoice_reader.core.schemas import Block, DocumentResult, PageResult

logger = logging.getLogger(__name__)


def render_html(
    *,
    document: DocumentResult,
    source_file: Path,
    inline_images: bool,
    output_dir: Path,
) -> str:
    """Render the full HTML report."""
    source_view = _embed_source(source_file, inline=inline_images, output_dir=output_dir)

    pages_html: List[str] = []
    pages_json: List[str] = []
    page_tabs: List[str] = []

    for i, page in enumerate(document.pages):
        active = " active" if i == 0 else ""
        page_tabs.append(
            f'<button class="page-tab{active}" data-page="{i}" '
            f'onclick="selectPage({i})">Page {page.page_index + 1}</button>'
        )
        pages_html.append(
            f'<div class="page-pane{active}" id="parse-page-{i}">'
            f"{_render_page_blocks(page)}"
            f"</div>"
        )
        pages_json.append(
            f'<div class="page-pane{active}" id="json-page-{i}">'
            f"<pre>{_html.escape(json.dumps(page.model_dump(), indent=2, ensure_ascii=False))}</pre>"
            f"</div>"
        )

    return _TEMPLATE.format(
        title=_html.escape(document.document),
        total_pages=document.total_pages,
        page_tabs="\n".join(page_tabs) if len(document.pages) > 1 else "",
        source_view=source_view,
        parsing_panes="\n".join(pages_html),
        json_panes="\n".join(pages_json),
    )


def _render_page_blocks(page: PageResult) -> str:
    if not page.blocks:
        return '<p class="empty">No blocks detected on this page.</p>'

    parts: List[str] = []
    for block in page.blocks:
        parts.append(_render_block(block))
    return "\n".join(parts)


def _render_block(block: Block) -> str:
    label = (block.label or "text").lower()

    if label == "table" and block.html:
        return (
            f'<div class="block block-table" data-bbox="{_bbox_attr(block)}">'
            f'  <div class="block-label">TABLE</div>'
            f'  <div class="table-wrap">{block.html}</div>'
            f"</div>"
        )

    if label in {"figure", "image", "chart"}:
        if block.image_path:
            return (
                f'<div class="block block-figure" data-bbox="{_bbox_attr(block)}">'
                f'  <div class="block-label">{label.upper()}</div>'
                f'  <img src="{_html.escape(block.image_path)}" alt="{label}" />'
                f"</div>"
            )
        return (
            f'<div class="block block-figure" data-bbox="{_bbox_attr(block)}">'
            f'  <div class="block-label">{label.upper()}</div>'
            f'  <div class="figure-placeholder">[{label}]</div>'
            f"</div>"
        )

    text = block.text or ""
    if label in {"doc_title", "title"}:
        return (
            f'<div class="block block-title" data-bbox="{_bbox_attr(block)}">'
            f'  <h1>{_html.escape(text)}</h1>'
            f"</div>"
        )
    if label in {"section_title", "header", "subtitle"}:
        return (
            f'<div class="block block-subtitle" data-bbox="{_bbox_attr(block)}">'
            f'  <h2>{_html.escape(text)}</h2>'
            f"</div>"
        )
    if label in {"formula", "equation"}:
        return (
            f'<div class="block block-formula" data-bbox="{_bbox_attr(block)}">'
            f'  <div class="block-label">FORMULA</div>'
            f'  <pre>{_html.escape(text)}</pre>'
            f"</div>"
        )

    return (
        f'<div class="block block-text" data-bbox="{_bbox_attr(block)}">'
        f'  <p>{_html.escape(text).replace(chr(10), "<br/>")}</p>'
        f"</div>"
    )


def _bbox_attr(block: Block) -> str:
    if not block.bbox:
        return ""
    return ",".join(str(round(float(v), 2)) for v in block.bbox)


def _embed_source(source: Path, *, inline: bool, output_dir: Path) -> str:
    ext = source.suffix.lower()
    if ext == ".pdf":
        if inline:
            try:
                b64 = base64.b64encode(source.read_bytes()).decode("ascii")
                return (
                    f'<embed class="source-embed" '
                    f'src="data:application/pdf;base64,{b64}" '
                    f'type="application/pdf" />'
                )
            except Exception as e:
                logger.warning("Could not inline PDF (%s); copying file", e)

        dest = output_dir / source.name
        try:
            if not dest.exists():
                dest.write_bytes(source.read_bytes())
            return (
                f'<embed class="source-embed" '
                f'src="{_html.escape(source.name)}" '
                f'type="application/pdf" />'
            )
        except Exception as e:
            return f'<div class="source-error">Could not embed PDF: {_html.escape(str(e))}</div>'

    if inline:
        try:
            b64 = base64.b64encode(source.read_bytes()).decode("ascii")
            mime = {
                ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".bmp": "image/bmp",
                ".webp": "image/webp", ".tiff": "image/tiff", ".tif": "image/tiff",
            }.get(ext, "image/png")
            return f'<img class="source-img" src="data:{mime};base64,{b64}" alt="source" />'
        except Exception as e:
            logger.warning("Could not inline image (%s); falling back to copy", e)

    dest = output_dir / source.name
    try:
        if not dest.exists():
            dest.write_bytes(source.read_bytes())
        return f'<img class="source-img" src="{_html.escape(source.name)}" alt="source" />'
    except Exception as e:
        return f'<div class="source-error">Could not embed image: {_html.escape(str(e))}</div>'


_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{title} — PaddleOCR-VL 1.5</title>
<style>
  :root {{
    --border: #e5e7eb;
    --bg: #f8fafc;
    --panel-bg: #ffffff;
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --tab-inactive: #6b7280;
    --header-bg: #ffffff;
    --table-border: #d1d5db;
    --table-header-bg: #f3f4f6;
    --code-bg: #1f2937;
    --code-fg: #f9fafb;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0; height: 100%;
    background: var(--bg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                 "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #111827;
  }}
  .app {{
    display: grid;
    grid-template-columns: 1fr 1.4fr;
    gap: 12px;
    height: 100vh;
    padding: 12px;
  }}
  .panel {{
    display: flex; flex-direction: column;
    background: var(--panel-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    min-height: 0;
  }}
  .panel-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    background: var(--header-bg);
    font-size: 13px; font-weight: 500;
  }}
  .pill {{
    background: #ecfdf5; color: #047857;
    border: 1px solid #a7f3d0;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 11px; font-weight: 600;
    margin-left: 8px;
  }}
  .source-pane {{
    flex: 1; overflow: auto; padding: 12px;
    display: flex; align-items: flex-start; justify-content: center;
    background: #f9fafb;
  }}
  .source-embed {{ width: 100%; height: 100%; min-height: 600px; border: 0; }}
  .source-img    {{ max-width: 100%; height: auto; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  .source-error  {{ color: #b91c1c; padding: 16px; }}

  .right-tabs {{ display: flex; gap: 4px; }}
  .tab-btn {{
    background: transparent; border: 0;
    padding: 8px 14px; border-radius: 6px;
    color: var(--tab-inactive); font-size: 13px; cursor: pointer;
  }}
  .tab-btn.active {{
    background: #eff6ff; color: var(--primary);
    font-weight: 600;
  }}
  .tab-body {{ flex: 1; overflow: auto; }}
  .tab-pane {{ display: none; padding: 16px 20px; }}
  .tab-pane.active {{ display: block; }}

  .page-tabs {{
    display: flex; gap: 4px;
    padding: 6px 14px;
    border-bottom: 1px solid var(--border);
    background: #f9fafb;
    overflow-x: auto;
  }}
  .page-tab {{
    background: transparent; border: 1px solid transparent;
    padding: 4px 10px; border-radius: 6px;
    color: var(--tab-inactive); cursor: pointer; font-size: 12px;
  }}
  .page-tab.active {{
    background: white; border-color: var(--border);
    color: var(--primary); font-weight: 600;
  }}
  .page-pane {{ display: none; }}
  .page-pane.active {{ display: block; }}

  .block {{ margin: 12px 0; }}
  .block-label {{
    font-size: 10px; letter-spacing: 1px; font-weight: 700;
    color: #9ca3af; margin-bottom: 4px;
  }}
  .block-title h1 {{
    font-size: 20px; margin: 4px 0 12px;
    border-bottom: 2px solid var(--border); padding-bottom: 6px;
  }}
  .block-subtitle h2 {{
    font-size: 16px; margin: 12px 0 6px; color: #374151;
  }}
  .block-text p {{
    margin: 6px 0; line-height: 1.55; font-size: 13px;
  }}
  .block-formula pre {{
    background: #f9fafb; border: 1px solid var(--border);
    padding: 8px 10px; border-radius: 6px;
    overflow-x: auto; font-size: 13px;
  }}
  .block-figure img {{
    max-width: 100%; border: 1px solid var(--border); border-radius: 6px;
  }}
  .figure-placeholder {{
    background: #f3f4f6; color: #6b7280;
    padding: 24px; text-align: center;
    border: 1px dashed var(--border); border-radius: 6px;
    font-size: 13px;
  }}

  .table-wrap {{ overflow-x: auto; }}
  .table-wrap table {{
    border-collapse: collapse; width: 100%;
    background: white; font-size: 12.5px;
  }}
  .table-wrap th, .table-wrap td {{
    border: 1px solid var(--table-border);
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
  }}
  .table-wrap th, .table-wrap tr:first-child td {{
    background: var(--table-header-bg);
    font-weight: 600;
  }}

  pre {{
    background: var(--code-bg); color: var(--code-fg);
    padding: 14px; border-radius: 8px;
    overflow: auto; font-size: 12px;
    font-family: "SFMono-Regular", Menlo, Consolas, monospace;
    line-height: 1.5;
  }}
  .empty {{ color: #9ca3af; font-style: italic; }}
</style>
</head>
<body>
  <div class="app">
    <section class="panel">
      <div class="panel-header">
        <span>Source File</span>
        <span style="color: var(--tab-inactive); font-size: 12px;">{title} · {total_pages} page(s)</span>
      </div>
      <div class="source-pane">{source_view}</div>
    </section>

    <section class="panel">
      <div class="panel-header">
        <div>
          <span>Parsing model</span>
          <span class="pill">PaddleOCR-VL-1.5</span>
        </div>
        <div class="right-tabs">
          <button class="tab-btn active" id="tab-parse"
                  onclick="selectTab('parse')">Document parsing</button>
          <button class="tab-btn" id="tab-json"
                  onclick="selectTab('json')">JSON</button>
        </div>
      </div>

      <div class="page-tabs">{page_tabs}</div>

      <div class="tab-body">
        <div class="tab-pane active" id="pane-parse">{parsing_panes}</div>
        <div class="tab-pane" id="pane-json">{json_panes}</div>
      </div>
    </section>
  </div>

<script>
  function selectTab(name) {{
    document.getElementById('pane-parse').classList.toggle('active', name === 'parse');
    document.getElementById('pane-json').classList.toggle('active', name === 'json');
    document.getElementById('tab-parse').classList.toggle('active', name === 'parse');
    document.getElementById('tab-json').classList.toggle('active', name === 'json');
  }}
  function selectPage(idx) {{
    document.querySelectorAll('.page-tab').forEach(function (el) {{
      el.classList.toggle('active', el.dataset.page === String(idx));
    }});
    ['parse', 'json'].forEach(function (kind) {{
      document.querySelectorAll('#pane-' + kind + ' .page-pane').forEach(function (el) {{
        var match = el.id === (kind === 'parse' ? 'parse-page-' : 'json-page-') + idx;
        el.classList.toggle('active', match);
      }});
    }});
  }}
</script>
</body>
</html>
"""
