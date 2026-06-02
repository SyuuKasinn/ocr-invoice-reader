# OCR Invoice Reader - 增强功能说明

## 📊 新增功能概览

本次更新为 OCR Invoice Reader 项目添加了**统计收集**和**增强的 HTML 报告**功能，完全向后兼容现有代码。

---

## ✨ 新增模块

### 1. `utils/stats_collector.py` - 统计收集模块

**功能**：
- 📊 收集文档处理的性能指标
- ⏱️ 页面级和文档级处理时间统计
- 🎯 置信度分析（平均值、低置信度页面检测）
- 📝 内容统计（区域数、表格数、文字量）

**使用示例**：
```python
from ocr_invoice_reader.utils.stats_collector import StatsCollector, format_stats_summary

# 初始化
collector = StatsCollector()
collector.start_document("invoice_001")

# 处理页面
for page_idx, page_image in enumerate(pages):
    collector.start_page(page_idx)
    # ... 进行 OCR 处理 ...
    collector.end_page(page_idx)

collector.end_document()

# 收集统计
stats = collector.collect_document_stats(
    all_pages_regions=[[region1, region2], [region3]],  # 每页的 regions
    document_name="invoice_001"
)

# 打印摘要
print(format_stats_summary(stats))
```

**输出示例**：
```
📄 Document: invoice_001
📊 Pages: 5
⏱️  Total Time: 12.34s
⚡ Throughput: 0.41 pages/sec
📝 Regions: 47 (avg 9.4/page)
📋 Tables: 3
🖼️  Figures: 2
📏 Text Length: 3,245 chars
🎯 Avg Confidence: 92.3%
⚠️  Low Confidence Pages: 3, 5
```

---

### 2. `utils/html_report.py` - HTML 报告生成器

**功能**：
- 📄 交互式 HTML 报告
- 🔲 网格视图（快速浏览所有页面）
- 📝 详细视图（单页深入分析）
- 📊 统计仪表盘（可选）
- 🎨 响应式设计（支持手机/平板/桌面）

**使用示例**：
```python
from ocr_invoice_reader.utils.html_report import generate_html_report

generate_html_report(
    document_name="invoice_001",
    all_pages_regions=[[region1, region2], [region3]],
    image_paths=["page1_vis.jpg", "page2_vis.jpg"],
    stats=stats,  # 可选：传入统计信息
    output_path="report.html",
)
```

**生成的 HTML 功能**：
- ✅ 左侧可视化图像，右侧区域列表
- ✅ 页面标签切换
- ✅ 网格/详细视图切换
- ✅ 置信度颜色编码（绿色/橙色/红色）
- ✅ 统计仪表盘（如果提供 stats）

---

## 🚀 快速开始

### 安装（无需额外依赖）

新模块使用 Python 标准库，无需安装额外依赖。

### 基础使用

#### 方式 1：独立使用统计收集

```python
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor
from ocr_invoice_reader.utils.stats_collector import StatsCollector, format_stats_summary

# 初始化
extractor = DocumentExtractor(use_gpu=True, lang='japan')
collector = StatsCollector()

# 开始处理
collector.start_document("my_document")

# 假设处理了一个页面
collector.start_page(0)
structure_result = extractor.structure_analyzer.analyze("page1.jpg")
regions = structure_result['regions']
collector.end_page(0)

collector.end_document()

# 收集统计
stats = collector.collect_document_stats([regions], "my_document")
print(format_stats_summary(stats))
```

#### 方式 2：完整示例（统计 + HTML）

查看 `examples/enhanced_extraction_example.py`：

```bash
python examples/enhanced_extraction_example.py invoice.pdf
```

---

## 📁 文件结构

```
ocr_invoice_reader/
├── utils/
│   ├── stats_collector.py      # ✨ 新增 - 统计收集
│   ├── html_report.py           # ✨ 新增 - HTML 报告
│   ├── visualizer.py            # (原有) - OCR 可视化
│   └── ...
│
├── examples/
│   └── enhanced_extraction_example.py  # ✨ 新增 - 使用示例
│
└── test_enhancements.py         # ✨ 新增 - 测试脚本
```

---

## 🧪 测试

运行测试脚本验证功能：

```bash
cd ocr-invoice-reader
python test_enhancements.py
```

**预期输出**：
```
[TEST] Testing Enhanced OCR Features

============================================================
Testing imports...
============================================================
[OK] stats_collector imported successfully
[OK] html_report imported successfully

============================================================
Testing StatsCollector...
============================================================
[OK] Statistics collected:
   - Total pages: 1
   - Total regions: 2
   - Processing time: 0.105s
   - Avg confidence: 90.00%

============================================================
Testing HTML generation...
============================================================
[OK] HTML report generated:
   - File: test_report.html
   - Size: 23485 bytes

============================================================
[SUMMARY] Test Summary
============================================================
[PASS]: Module Imports
[PASS]: StatsCollector
[PASS]: HTML Generation
============================================================
Result: 3/3 tests passed
============================================================
```

---

## 📊 数据结构说明

### StatsCollector 输入格式

```python
# all_pages_regions 结构
all_pages_regions = [
    # 第 1 页的 regions
    [
        {'type': 'text', 'confidence': 0.95, 'text': 'Sample'},
        {'type': 'table', 'confidence': 0.85, 'text': 'Table data'},
    ],
    # 第 2 页的 regions
    [
        {'type': 'title', 'confidence': 0.92, 'text': 'Title'},
    ],
]
```

### HTML Report 输入格式

```python
# image_paths: 每页对应的可视化图像路径
image_paths = [
    "results/page1_vis.jpg",
    "results/page2_vis.jpg",
]

# all_pages_regions: 同上
# stats: StatsCollector.collect_document_stats() 返回值（可选）
```

---

## 🎨 HTML 报告截图说明

### 详细视图
```
+--------------------------------------------------------+
| invoice_001 · 2 pages          [🔲 Grid] [📄 Detail] |
+--------------------------------------------------------+
| 📊 Statistics Dashboard                                |
| 📄 Document: invoice_001                               |
| ⏱️  Total Time: 2.5s | ⚡ 0.8 pages/sec                |
+--------------------------------------------------------+
| Page: [1] [2]                                          |
+--------------------------------------------------------+
| +----------------------+-----------------------------+ |
| | [Visualization]      | Detected Regions (5)        | |
| |                      | ┌─────────────────────────┐ | |
| |   [PDF/Image]        | │ TEXT           95%      │ | |
| |                      | │ Sample text...          │ | |
| |                      | └─────────────────────────┘ | |
| |                      | ┌─────────────────────────┐ | |
| |                      | │ TABLE          85%      │ | |
| |                      | │ Table data...           │ | |
| +----------------------+-----------------------------+ |
+--------------------------------------------------------+
```

### 网格视图
```
+--------------------------------------------------------+
| invoice_001 · 2 pages          [🔲 Grid] [📄 Detail] |
+--------------------------------------------------------+
| ┌────────────┐  ┌────────────┐                        |
| │   Page 1   │  │   Page 2   │                        |
| │ [Preview]  │  │ [Preview]  │                        |
| │ ⏱️ 1.2s     │  │ ⏱️ 1.3s     │                        |
| │ 📦 5 regions│  │ 📦 3 regions│                        |
| │ 📋 1 table  │  │ 📋 0 table  │                        |
| └────────────┘  └────────────┘                        |
+--------------------------------------------------------+
```

---

## 🔧 集成到现有代码

### 最小改动集成

在现有的提取流程中添加统计收集：

```python
# 原有代码
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor

extractor = DocumentExtractor()
document = extractor.extract("invoice.pdf", visualize=True)

# 新增：添加统计（仅 3 行代码）
from ocr_invoice_reader.utils.stats_collector import StatsCollector
collector = StatsCollector()
collector.start_document("invoice")
# ... 原有处理逻辑 ...
collector.end_document()
# stats = collector.collect_document_stats(...)
```

### 完全集成

参考 `examples/enhanced_extraction_example.py` 的完整流程。

---

## ⚡ 性能影响

| 功能 | 额外开销 | 说明 |
|------|---------|------|
| StatsCollector | < 1% | 仅计时操作，几乎无影响 |
| HTML Report | 一次性 | 仅在最后生成，不影响处理速度 |
| 可视化图像嵌入 | 取决于图像大小 | Base64 编码，约增加 30-40% 文件大小 |

---

## 🐛 常见问题

### Q1: 报告中看不到可视化图像
**A:** 确保传入的 `image_paths` 指向存在的图像文件。

### Q2: 统计信息不准确
**A:** 确保 `start_page()` 和 `end_page()` 调用配对，且在正确的时机调用。

### Q3: HTML 文件过大
**A:** 可以选择不嵌入图像，而是使用相对路径（需修改 `html_report.py`）。

### Q4: Unicode 显示问题（Windows）
**A:** 确保终端使用 UTF-8 编码，或者使用新版 Windows Terminal。

---

## 📝 更新日志

### v1.1.0 (2026-06-02)
- ✨ 新增统计收集模块 (`stats_collector.py`)
- ✨ 新增 HTML 报告生成器 (`html_report.py`)
- ✨ 新增使用示例 (`examples/enhanced_extraction_example.py`)
- ✨ 新增测试脚本 (`test_enhancements.py`)
- ✅ 完全向后兼容，无破坏性变更
- ✅ 所有测试通过 (3/3)

---

## 📚 API 文档

### StatsCollector

#### `start_document(name: str = "")`
开始文档处理计时。

#### `end_document()`
结束文档处理计时。

#### `start_page(page_index: int)`
开始页面处理计时。

#### `end_page(page_index: int)`
结束页面处理计时。

#### `collect_page_stats(regions: List[Dict], page_index: int) -> PageStats`
从 regions 列表收集单页统计。

#### `collect_document_stats(all_pages_regions: List[List[Dict]], document_name: str = None) -> DocumentStats`
收集文档级统计。

### HTML Report

#### `generate_html_report(...) -> str`
生成 HTML 报告并保存到文件。

**参数**：
- `document_name`: 文档名称
- `all_pages_regions`: 所有页面的 regions 列表
- `image_paths`: 各页面的可视化图像路径
- `stats`: 可选的统计信息（DocumentStats 对象）
- `output_path`: 输出 HTML 文件路径

**返回**：
- HTML 内容字符串

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

与主项目相同。

---

**作者**: Claude Code Assistant  
**日期**: 2026-06-02  
**版本**: 1.1.0
