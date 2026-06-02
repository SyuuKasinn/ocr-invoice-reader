"""
HTML 报告生成器 - 增强的交互式可视化

与现有的 OCRVisualizer 配合使用，生成带统计仪表盘的 HTML 报告
"""
from __future__ import annotations

import base64
import html as _html
import json
from pathlib import Path
from typing import List, Dict, Optional

try:
    from ocr_invoice_reader.utils.stats_collector import DocumentStats, format_stats_summary
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False
    DocumentStats = None


def generate_html_report(
    document_name: str,
    all_pages_regions: List[List[Dict]],
    image_paths: List[str],
    stats: Optional[DocumentStats] = None,
    output_path: str = "report.html",
) -> str:
    """
    生成增强的 HTML 报告

    Args:
        document_name: 文档名称
        all_pages_regions: 所有页面的 regions 列表
        image_paths: 各页面的可视化图像路径
        stats: 可选的统计信息
        output_path: 输出路径

    Returns:
        HTML 内容
    """
    # 生成仪表盘
    dashboard_html = _render_dashboard(stats) if stats and STATS_AVAILABLE else ""

    # 生成页面内容
    pages_html = []
    page_tabs = []
    grid_items = []

    for i, (regions, img_path) in enumerate(zip(all_pages_regions, image_paths)):
        active = " active" if i == 0 else ""

        # Tab 按钮
        page_tabs.append(
            f'<button class="page-tab{active}" data-page="{i}" '
            f'onclick="selectPage({i})">Page {i + 1}</button>'
        )

        # 详细视图
        pages_html.append(
            f'<div class="page-pane{active}" id="page-{i}">'
            f'{_render_page_content(regions, img_path, i)}'
            f'</div>'
        )

        # 网格视图项
        page_stats = stats.page_stats[i] if stats and i < len(stats.page_stats) else None
        grid_items.append(_render_grid_item(i, img_path, page_stats))

    html = _HTML_TEMPLATE.format(
        title=_html.escape(document_name),
        total_pages=len(all_pages_regions),
        dashboard=dashboard_html,
        page_tabs="\n".join(page_tabs) if len(all_pages_regions) > 1 else "",
        pages_content="\n".join(pages_html),
        grid_items="\n".join(grid_items),
    )

    # 保存文件
    Path(output_path).write_text(html, encoding="utf-8")
    print(f"[OK] HTML report saved: {output_path}")

    return html


def _render_dashboard(stats: DocumentStats) -> str:
    """渲染统计仪表盘"""
    summary = format_stats_summary(stats)
    summary_html = "<br>".join(_html.escape(line) for line in summary.split("\n"))

    return f"""
    <div class="dashboard">
      <h3>📊 Statistics Dashboard</h3>
      <div class="stats-summary">{summary_html}</div>
    </div>
    """


def _render_page_content(regions: List[Dict], img_path: str, page_index: int) -> str:
    """渲染单页内容"""
    # 嵌入可视化图像
    try:
        img_data = Path(img_path).read_bytes()
        b64_img = base64.b64encode(img_data).decode('ascii')
        img_html = f'<img src="data:image/jpeg;base64,{b64_img}" style="max-width: 100%; height: auto;">'
    except Exception as e:
        img_html = f'<p class="error">Failed to load image: {_html.escape(str(e))}</p>'

    # 区域列表
    regions_html = []
    for region in regions:
        region_type = region.get('type', 'unknown')
        conf = region.get('confidence', 0)
        text = region.get('text', '')[:200]  # 截断长文本

        conf_class = "high" if conf > 0.8 else "medium" if conf > 0.6 else "low"

        regions_html.append(f"""
        <div class="region-item">
          <div class="region-header">
            <span class="region-type">{region_type.upper()}</span>
            <span class="confidence-badge confidence-{conf_class}">{conf:.2%}</span>
          </div>
          <div class="region-text">{_html.escape(text)}</div>
        </div>
        """)

    return f"""
    <div class="page-content">
      <div class="visualization">
        {img_html}
      </div>
      <div class="regions-list">
        <h4>Detected Regions ({len(regions)})</h4>
        {"".join(regions_html)}
      </div>
    </div>
    """


def _render_grid_item(page_index: int, img_path: str, page_stats=None) -> str:
    """渲染网格视图单元"""
    # 缩略图
    try:
        img_data = Path(img_path).read_bytes()
        b64_img = base64.b64encode(img_data).decode('ascii')
        thumbnail = f'<img src="data:image/jpeg;base64,{b64_img}" class="grid-thumbnail">'
    except:
        thumbnail = f'<div class="grid-thumbnail-placeholder">Page {page_index + 1}</div>'

    stats_html = ""
    if page_stats:
        stats_html = f"""
        <div class="grid-stats">
          <span>⏱️ {page_stats.processing_time:.2f}s</span>
          <span>📦 {page_stats.region_count} regions</span>
          <span>📋 {page_stats.table_count} tables</span>
        </div>
        """

    return f"""
    <div class="grid-item" data-page="{page_index}" onclick="selectPageFromGrid({page_index})">
      {thumbnail}
      <div class="grid-info">
        <strong>Page {page_index + 1}</strong>
        {stats_html}
      </div>
    </div>
    """


# HTML Template
_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - OCR Report</title>
<style>
  :root {{
    --bg: #f5f7fa;
    --panel-bg: #ffffff;
    --border: #e5e7eb;
    --primary: #2563eb;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0; padding: 0;
    background: var(--bg);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: #111827;
  }}

  /* Toolbar */
  .toolbar {{
    position: sticky; top: 0; z-index: 100;
    background: white; border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    display: flex; align-items: center; justify-content: space-between;
  }}
  .toolbar-left {{ font-size: 18px; font-weight: 600; }}
  .toolbar-right {{ display: flex; gap: 8px; }}
  .view-toggle {{
    display: flex; gap: 4px;
    background: #f3f4f6; padding: 4px; border-radius: 8px;
  }}
  .view-btn {{
    background: transparent; border: 0;
    padding: 6px 12px; border-radius: 6px;
    cursor: pointer; font-size: 13px;
  }}
  .view-btn.active {{ background: white; color: var(--primary); font-weight: 600; }}

  /* Dashboard */
  .dashboard {{
    background: white; border: 1px solid var(--border);
    border-radius: 10px; margin: 12px; padding: 20px;
  }}
  .dashboard h3 {{ margin-top: 0; }}
  .stats-summary {{
    background: #f9fafb; padding: 16px; border-radius: 8px;
    font-family: monospace; font-size: 13px; line-height: 1.8;
  }}

  /* Grid View */
  .grid-view {{
    display: none; padding: 12px;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 12px;
  }}
  .grid-view.active {{ display: grid; }}
  .grid-item {{
    background: white; border: 1px solid var(--border);
    border-radius: 8px; padding: 12px; cursor: pointer;
    transition: all 0.2s;
  }}
  .grid-item:hover {{
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border-color: var(--primary);
  }}
  .grid-thumbnail {{
    width: 100%; height: 150px; object-fit: cover;
    border-radius: 6px; margin-bottom: 8px;
  }}
  .grid-thumbnail-placeholder {{
    background: #f3f4f6; height: 150px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 6px; margin-bottom: 8px;
    color: #9ca3af; font-weight: 500;
  }}
  .grid-stats {{ display: flex; gap: 8px; flex-wrap: wrap; font-size: 11px; color: #6b7280; }}

  /* Detail View */
  .detail-view {{ display: none; padding: 12px; }}
  .detail-view.active {{ display: block; }}
  .panel {{
    background: white; border: 1px solid var(--border);
    border-radius: 10px; padding: 20px; margin-bottom: 12px;
  }}
  .page-tabs {{
    display: flex; gap: 4px; padding: 12px 0;
    border-bottom: 1px solid var(--border);
    overflow-x: auto;
  }}
  .page-tab {{
    background: transparent; border: 1px solid transparent;
    padding: 6px 12px; border-radius: 6px;
    color: #6b7280; cursor: pointer; font-size: 13px;
  }}
  .page-tab.active {{
    background: white; border-color: var(--border);
    color: var(--primary); font-weight: 600;
  }}
  .page-pane {{ display: none; padding-top: 12px; }}
  .page-pane.active {{ display: block; }}

  /* Page Content */
  .page-content {{
    display: grid; grid-template-columns: 1fr 400px; gap: 20px;
  }}
  .visualization {{ background: #f9fafb; padding: 12px; border-radius: 8px; }}
  .regions-list {{ overflow-y: auto; max-height: 70vh; }}
  .region-item {{
    background: #f9fafb; padding: 12px; border-radius: 6px;
    margin-bottom: 8px;
  }}
  .region-header {{
    display: flex; justify-content: space-between; margin-bottom: 6px;
  }}
  .region-type {{ font-weight: 600; color: #374151; }}
  .confidence-badge {{
    padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;
  }}
  .confidence-high {{ background: #d1fae5; color: #065f46; }}
  .confidence-medium {{ background: #fed7aa; color: #92400e; }}
  .confidence-low {{ background: #fecaca; color: #991b1b; }}
  .region-text {{ font-size: 12px; color: #6b7280; }}
  .error {{ color: var(--danger); }}

  @media (max-width: 768px) {{
    .page-content {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
  <div class="toolbar">
    <div class="toolbar-left">{title} · {total_pages} pages</div>
    <div class="toolbar-right">
      <div class="view-toggle">
        <button class="view-btn" id="viewGrid" onclick="switchView('grid')">🔲 Grid</button>
        <button class="view-btn active" id="viewDetail" onclick="switchView('detail')">📄 Detail</button>
      </div>
    </div>
  </div>

  {dashboard}

  <div class="grid-view" id="gridView">{grid_items}</div>

  <div class="detail-view active" id="detailView">
    <div class="panel">
      <div class="page-tabs">{page_tabs}</div>
      {pages_content}
    </div>
  </div>

<script>
  function switchView(view) {{
    document.getElementById('gridView').classList.toggle('active', view === 'grid');
    document.getElementById('detailView').classList.toggle('active', view === 'detail');
    document.getElementById('viewGrid').classList.toggle('active', view === 'grid');
    document.getElementById('viewDetail').classList.toggle('active', view === 'detail');
  }}

  function selectPage(idx) {{
    document.querySelectorAll('.page-tab').forEach(el => {{
      el.classList.toggle('active', el.dataset.page === String(idx));
    }});
    document.querySelectorAll('.page-pane').forEach(el => {{
      const match = el.id === `page-${{idx}}`;
      el.classList.toggle('active', match);
    }});
  }}

  function selectPageFromGrid(idx) {{
    switchView('detail');
    selectPage(idx);
  }}
</script>
</body>
</html>
"""
