# OCR Invoice Reader - 项目架构

## 📐 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Input                                │
│                    (PDF / Image File)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CLI / Python API                               │
│              (ocr_invoice_reader/cli/extract.py)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Pipeline                                    │
│            (ocr_invoice_reader/core/pipeline.py)                 │
│                                                                   │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │  File I/O      │  │  VL Engine      │  │  Stats Collector │ │
│  │  (file_io.py)  │  │ (vl_engine.py)  │  │(stats_collector) │ │
│  └────────────────┘  └─────────────────┘  └──────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PaddleOCR-VL 1.5                                │
│          (Layout Analysis + OCR + Table Recognition)             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Processing Results                             │
│                                                                   │
│  ┌───────────────┐   ┌────────────────┐   ┌──────────────────┐ │
│  │ JSON Output   │   │ Markdown       │   │  HTML Report     │ │
│  │ (schemas.py)  │   │                │   │ (html_report.py) │ │
│  └───────────────┘   └────────────────┘   └──────────────────┘ │
│                                                                   │
│  ┌───────────────┐   ┌────────────────┐                         │
│  │ Visualization │   │ Statistics     │                         │
│  │(visualize.py) │   │ Dashboard      │                         │
│  └───────────────┘   └────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 数据流

### 输入阶段
```
PDF/Image → File Validation → Format Conversion (if PDF)
                                        ↓
                                 Image Ready for OCR
```

### 处理阶段
```
Image → PaddleOCR-VL 1.5
           ├─ Layout Analysis (Title, Text, Table, Figure)
           ├─ OCR Text Recognition
           └─ Table Structure Recognition
                    ↓
              Raw Results (Dict)
                    ↓
         Normalization & Schema Validation
                    ↓
        PageResult Objects (Pydantic Models)
```

### 输出阶段
```
PageResult[] → DocumentResult
                     ├─→ JSON Output
                     ├─→ Markdown Output
                     ├─→ Visualization (Original)
                     └─→ Enhanced HTML Report (New!)
                              ├─ Statistics Dashboard
                              ├─ Grid View
                              ├─ Detail View
                              └─ Interactive Features
```

---

## 📦 模块说明

### Core Modules (核心模块)

#### 1. `pipeline.py` - 主流程编排器
- **职责**: 协调整个处理流程
- **输入**: PDF/图像路径
- **输出**: `DocumentResult` 对象
- **关键方法**:
  - `run()`: 一次性处理，返回结果
  - `run_and_save()`: 流式处理，逐页保存

#### 2. `vl_engine.py` - PaddleOCR-VL 引擎封装
- **职责**: 封装 PaddleOCR-VL API
- **功能**:
  - GPU/CPU 自动检测
  - 文档方向矫正（可选）
  - 文档去扭曲（可选）
  - 批量处理支持

#### 3. `schemas.py` - 数据模型
```python
DocumentResult
├─ document: str              # 文档名称
├─ total_pages: int           # 总页数
└─ pages: List[PageResult]    # 页面列表

PageResult
├─ page_index: int            # 页码
├─ source_file: str           # 源文件
├─ blocks: List[Block]        # 区域列表
└─ markdown: str              # Markdown 内容

Block
├─ label: str                 # 类型 (title/text/table/figure)
├─ bbox: List[float]          # 边界框 [x1, y1, x2, y2]
├─ text: str                  # 文本内容
├─ html: str                  # HTML (表格)
├─ image_path: str            # 图像路径 (图片)
└─ score: float               # 置信度
```

#### 4. `config.py` - 配置管理
```python
PipelineConfig
├─ vl: VLConfig               # PaddleOCR-VL 配置
│  ├─ use_gpu: bool
│  ├─ lang: str
│  ├─ use_doc_orientation_classify: bool
│  └─ use_doc_unwarping: bool
└─ io: IOConfig               # 输入输出配置
   ├─ output_dir: str
   ├─ save_markdown: bool
   ├─ save_visualization: bool
   └─ inline_images_in_html: bool
```

---

### Utils Modules (工具模块)

#### 5. `stats_collector.py` - 统计收集器 ✨ 新增
- **职责**: 性能监控和准确率分析
- **功能**:
  - 文档/页面级处理时间统计
  - 置信度分析（平均值、低置信度检测）
  - 内容统计（区域数、表格数、文字量）
- **数据结构**:
  ```python
  DocumentStats
  ├─ total_pages: int
  ├─ total_processing_time: float
  ├─ throughput: float        # 页/秒
  ├─ avg_confidence: float
  └─ page_stats: List[PageStats]
  ```

#### 6. `html_report.py` - HTML 报告生成器 ✨ 新增
- **职责**: 生成交互式 HTML 报告
- **功能**:
  - 统计仪表盘
  - 网格视图 / 详细视图切换
  - 响应式设计
  - 置信度颜色编码
- **输出**: 单个自包含 HTML 文件

#### 7. `visualize.py` - 原始可视化
- **职责**: 生成 PaddleOCR 风格的可视化图像
- **输出**: 带标注的 PNG/JPG 图像

---

## 🎨 可视化层级

### Level 1: 原始可视化 (visualize.py)
```
┌────────────────────────────────┐
│  Source Image with Overlays    │
│  ┌──────────────────────────┐  │
│  │ [TITLE]                  │  │
│  │ ┌─────────┐              │  │
│  │ │ TEXT    │  [TABLE]     │  │
│  │ └─────────┘  ┌─────────┐ │  │
│  │              │ █ █ █ █ │ │  │
│  │              └─────────┘ │  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
     bbox + label overlays
```

### Level 2: 增强 HTML 报告 (html_report.py) ✨
```
┌─────────────────────────────────────────────────┐
│  [Enhanced HTML Report]                         │
│  ┌───────────────────────────────────────────┐  │
│  │ 📊 Statistics Dashboard                   │  │
│  │ ⏱️ 12.3s | 📝 47 regions | 🎯 92% conf    │  │
│  └───────────────────────────────────────────┘  │
│                                                  │
│  [🔲 Grid View] [📄 Detail View]                │
│  ┌──────┐ ┌──────┐ ┌──────┐                     │
│  │ P1   │ │ P2   │ │ P3   │  ← 快速浏览         │
│  │ ⏱️1.2s│ │ ⏱️1.3s│ │ ⏱️1.1s│                    │
│  └──────┘ └──────┘ └──────┘                     │
│                                                  │
│  OR                                              │
│                                                  │
│  ┌─────────────┬───────────────────────────┐    │
│  │ Vis Image   │ Regions List               │    │
│  │             │ ┌─────────────────────┐    │    │
│  │ [PDF View]  │ │ TITLE         95%  │    │    │
│  │             │ │ Sample text...      │    │    │
│  │             │ └─────────────────────┘    │    │
│  └─────────────┴───────────────────────────┘    │
└─────────────────────────────────────────────────┘
     Interactive, responsive, with statistics
```

---

## 🔧 扩展点

### 1. 自定义后处理
```python
# 在 pipeline.py 中添加 hook
class Pipeline:
    def __init__(self, config, post_processor=None):
        self.post_processor = post_processor
    
    def run(self, input_path):
        result = # ... 处理 ...
        if self.post_processor:
            result = self.post_processor(result)
        return result
```

### 2. 自定义可视化
```python
# 继承 html_report 生成器
from ocr_invoice_reader.utils.html_report import generate_html_report

def custom_html_report(...):
    # 添加自定义组件
    html = generate_html_report(...)
    # 注入自定义 JS/CSS
    return html
```

### 3. 自定义统计指标
```python
# 扩展 StatsCollector
from ocr_invoice_reader.utils.stats_collector import StatsCollector

class CustomStatsCollector(StatsCollector):
    def collect_custom_metrics(self, data):
        # 自定义指标
        pass
```

---

## ⚙️ 配置流程

### 标准配置
```python
from ocr_invoice_reader.core.pipeline import Pipeline
from ocr_invoice_reader.core.config import PipelineConfig, VLConfig, IOConfig

config = PipelineConfig(
    vl=VLConfig(
        use_gpu=True,
        lang='japan',  # ch/en/japan/korean
    ),
    io=IOConfig(
        output_dir='results',
        save_markdown=True,
        save_visualization=True,
    )
)

pipeline = Pipeline(config)
```

### 增强配置（带统计）
```python
from ocr_invoice_reader.utils.stats_collector import StatsCollector

pipeline = Pipeline(config)
collector = StatsCollector()

collector.start_document('invoice')
result = pipeline.run('invoice.pdf')
collector.end_document()

stats = collector.collect_document_stats(...)
```

---

## 📊 性能特征

### 处理速度
- **GPU**: 2-5 秒/页 (取决于内容复杂度)
- **CPU**: 10-30 秒/页

### 内存使用
- **基础**: ~2GB (PaddleOCR-VL 模型)
- **峰值**: +500MB/页 (处理时)

### 输出大小
- **JSON**: 10-50 KB/页
- **Markdown**: 5-20 KB/页
- **HTML (不嵌入图像)**: 20-100 KB
- **HTML (嵌入图像)**: 1-5 MB

---

## 🚀 未来扩展

### 短期
- [ ] 批量处理优化（多线程/多进程）
- [ ] 更多语言支持
- [ ] 自定义模板系统

### 中期
- [ ] REST API 服务
- [ ] WebSocket 实时预览
- [ ] 云端部署支持

### 长期
- [ ] 自定义模型训练
- [ ] 多模型集成（切换 OCR 引擎）
- [ ] AI 辅助校正

---

**最后更新**: 2026-06-02  
**架构版本**: 2.0
