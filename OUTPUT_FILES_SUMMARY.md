# 输出文件汇总表

## 📊 文件类型统计

### 基本OCR（无--use-llm，无--visualize）

**每页生成**: 2个文件
- `*_page_*.json` - 结构化数据
- `*_page_*.txt` - OCR文本

**汇总文件**: 4个文件
- `*_all_pages.json` - 所有页JSON
- `*_all_pages.txt` - 所有页文本
- `*_all_tables.html` - 所有表格
- `*_summary.csv` - 页面统计

**10页PDF总计**: 2×10 + 4 = **24个文件**

---

### OCR + LLM增强（--use-llm）

**每页生成**: 4个文件
- `*_page_*.json` - 结构化数据（含LLM字段）
- `*_page_*.txt` - 原始OCR文本
- `*_page_*_llm.txt` - ⭐ LLM分析文本
- `*_page_*_llm.csv` - ⭐ LLM字段CSV

**汇总文件**: 6个文件
- `*_all_pages.json` - 所有页JSON（含LLM）
- `*_all_pages.txt` - 所有页文本
- `*_all_tables.html` - 所有表格
- `*_summary.csv` - 页面统计
- `*_llm_analysis.txt` - ⭐ LLM分析汇总
- `*_llm.csv` - ⭐ LLM字段汇总

**10页PDF总计**: 4×10 + 6 = **46个文件**

---

### OCR + 可视化（--visualize）

**每页生成**: 3个文件
- `*_page_*.json` - 结构化数据
- `*_page_*.txt` - OCR文本
- `*_page_*_viz.jpg` - ⭐ 可视化图片

**汇总文件**: 4个文件（同基本OCR）

**10页PDF总计**: 3×10 + 4 = **34个文件**

---

### 完整功能（--use-llm --visualize）

**每页生成**: 5个文件
- `*_page_*.json` - 结构化数据（含LLM字段）
- `*_page_*.txt` - 原始OCR文本
- `*_page_*_llm.txt` - LLM分析文本
- `*_page_*_llm.csv` - LLM字段CSV
- `*_page_*_viz.jpg` - 可视化图片

**汇总文件**: 6个文件（同LLM增强）

**10页PDF总计**: 5×10 + 6 = **56个文件**

---

## 📁 完整文件列表

### 基本OCR输出

```
results/20260514_123456/
# 单页文件（每页2个）
├── invoice_page_0001.json
├── invoice_page_0001.txt
├── invoice_page_0002.json
├── invoice_page_0002.txt
├── ...
├── invoice_page_0010.json
└── invoice_page_0010.txt

# 汇总文件（4个）
├── invoice_all_pages.json
├── invoice_all_pages.txt
├── invoice_all_tables.html
└── invoice_summary.csv
```

### LLM增强输出

```
results/20260514_123456/
# 单页文件（每页4个）
├── invoice_page_0001.json          # JSON含LLM字段
├── invoice_page_0001.txt           # 原始OCR文本
├── invoice_page_0001_llm.txt       # ⭐ LLM分析
├── invoice_page_0001_llm.csv       # ⭐ LLM字段CSV
├── invoice_page_0002.json
├── invoice_page_0002.txt
├── invoice_page_0002_llm.txt       # ⭐ LLM分析
├── invoice_page_0002_llm.csv       # ⭐ LLM字段CSV
├── ...
├── invoice_page_0010.json
├── invoice_page_0010.txt
├── invoice_page_0010_llm.txt       # ⭐ LLM分析
└── invoice_page_0010_llm.csv       # ⭐ LLM字段CSV

# 汇总文件（6个）
├── invoice_all_pages.json          # JSON含LLM字段
├── invoice_all_pages.txt
├── invoice_all_tables.html
├── invoice_summary.csv
├── invoice_llm_analysis.txt        # ⭐ LLM汇总
└── invoice_llm.csv                 # ⭐ LLM字段汇总
```

### 可视化输出

```
results/20260514_123456/
# 单页文件（每页3个）
├── invoice_page_0001.json
├── invoice_page_0001.txt
├── invoice_page_0001_viz.jpg       # ⭐ 可视化
├── invoice_page_0002.json
├── invoice_page_0002.txt
├── invoice_page_0002_viz.jpg       # ⭐ 可视化
├── ...
├── invoice_page_0010.json
├── invoice_page_0010.txt
└── invoice_page_0010_viz.jpg       # ⭐ 可视化

# 汇总文件（4个）
├── invoice_all_pages.json
├── invoice_all_pages.txt
├── invoice_all_tables.html
└── invoice_summary.csv
```

### 完整功能输出

```
results/20260514_123456/
# 单页文件（每页5个）
├── invoice_page_0001.json
├── invoice_page_0001.txt
├── invoice_page_0001_llm.txt       # ⭐ LLM分析
├── invoice_page_0001_llm.csv       # ⭐ LLM字段CSV
├── invoice_page_0001_viz.jpg       # ⭐ 可视化
├── invoice_page_0002.json
├── invoice_page_0002.txt
├── invoice_page_0002_llm.txt       # ⭐ LLM分析
├── invoice_page_0002_llm.csv       # ⭐ LLM字段CSV
├── invoice_page_0002_viz.jpg       # ⭐ 可视化
├── ...
├── invoice_page_0010.json
├── invoice_page_0010.txt
├── invoice_page_0010_llm.txt       # ⭐ LLM分析
├── invoice_page_0010_llm.csv       # ⭐ LLM字段CSV
└── invoice_page_0010_viz.jpg       # ⭐ 可视化

# 汇总文件（6个）
├── invoice_all_pages.json          # JSON含LLM字段
├── invoice_all_pages.txt
├── invoice_all_tables.html
├── invoice_summary.csv
├── invoice_llm_analysis.txt        # ⭐ LLM汇总
└── invoice_llm.csv                 # ⭐ LLM字段汇总
```

---

## 📋 文件用途对照表

| 文件后缀 | 格式 | 内容 | 用途 | 生成条件 |
|---------|------|------|------|---------|
| `.json` | JSON | OCR结构化数据 | 程序读取、API返回 | 总是 |
| `.txt` | 文本 | OCR纯文本 | 人工阅读、搜索 | 总是 |
| `_llm.txt` | 文本 | LLM分析结果 | 查看AI提取的字段 | --use-llm |
| `_llm.csv` | CSV | LLM字段（单页） | Excel查看、验证 | --use-llm |
| `_viz.jpg` | 图片 | OCR可视化 | 调试、质量检查 | --visualize |
| `_all_pages.json` | JSON | 所有页JSON | 批量处理 | 总是 |
| `_all_pages.txt` | 文本 | 所有页文本 | 全文搜索 | 总是 |
| `_all_tables.html` | HTML | 所有表格 | 浏览器查看 | 总是 |
| `_summary.csv` | CSV | 页面统计 | 数据分析 | 总是 |
| `_llm_analysis.txt` | 文本 | LLM汇总 | 查看所有分析 | --use-llm |
| `_llm.csv` | CSV | LLM字段汇总 | **数据库导入** | --use-llm |

---

## 🎯 文件选择指南

### 场景1: 快速查看结果

**最少文件**:
```bash
ocr-enhanced --image invoice.pdf --lang ch
```

**查看**:
- `*_all_pages.txt` - 所有OCR文本
- `*_summary.csv` - 页面统计（Excel打开）

---

### 场景2: 数据库批量导入

**推荐命令**:
```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm
```

**重点文件**:
- `*_llm.csv` - ⭐ 直接导入数据库
- `*_llm_analysis.txt` - 查看提取结果
- 每页 `*_llm.csv` - 验证单页数据

**导入示例**:
```python
import pandas as pd
df = pd.read_csv('invoice_llm.csv')
df.to_sql('invoices', conn, if_exists='append', index=False)
```

---

### 场景3: 调试OCR问题

**推荐命令**:
```bash
ocr-enhanced --image invoice.pdf --lang ch --visualize
```

**重点文件**:
- `*_viz.jpg` - 查看OCR识别框
- `*_page_*.json` - 查看bbox坐标
- `*_page_*.txt` - 查看识别文本

---

### 场景4: 完整分析和存档

**推荐命令**:
```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm --visualize
```

**全部文件**: 
- JSON - 结构化数据
- TXT - 可读文本
- LLM TXT - AI分析
- LLM CSV - 数据库数据
- 可视化 - 质量验证

---

## 💾 文件大小估算

### 单页A4发票

| 文件类型 | 大小 | 占比 |
|---------|------|------|
| `.json` | 15-50KB | 2% |
| `.txt` | 1-3KB | <1% |
| `_llm.txt` | 0.5-2KB | <1% |
| `_llm.csv` | <1KB | <1% |
| `_viz.jpg` | 1-2MB | 97% |
| **总计（含viz）** | **~2MB** | 100% |
| **总计（不含viz）** | **~60KB** | 3% |

### 10页PDF

| 配置 | 文件数 | 总大小 |
|------|--------|--------|
| 基本OCR | 24 | ~600KB |
| OCR + LLM | 46 | ~800KB |
| OCR + viz | 34 | ~20MB |
| 完整功能 | 56 | ~22MB |

**建议**: 
- 生产环境：不使用 `--visualize`，节省97%空间
- 调试阶段：使用 `--visualize`，便于排查问题

---

## 🔍 快速定位文件

### 查看所有CSV文件

```bash
ls results/20260514_123456/*.csv
```

输出:
```
invoice_summary.csv      # 页面统计（总是有）
invoice_llm.csv          # LLM汇总（--use-llm时）
```

### 查看单页LLM文件

```bash
ls results/20260514_123456/*_page_*_llm.*
```

输出:
```
invoice_page_0001_llm.txt    # Page 1 LLM分析
invoice_page_0001_llm.csv    # Page 1 LLM字段
invoice_page_0002_llm.txt    # Page 2 LLM分析
invoice_page_0002_llm.csv    # Page 2 LLM字段
...
```

### 统计文件数量

```bash
# 所有文件
ls results/20260514_123456/ | wc -l

# 只看CSV
ls results/20260514_123456/*.csv | wc -l

# 只看LLM CSV
ls results/20260514_123456/*_llm.csv | wc -l
```

---

## 📚 相关文档

- **[OUTPUT_FILES_GUIDE.md](OUTPUT_FILES_GUIDE.md)** - 每个文件的详细说明
- **[CSV_OUTPUT_GUIDE.md](CSV_OUTPUT_GUIDE.md)** - CSV格式和用法
- **[DATABASE_IMPORT_GUIDE.md](DATABASE_IMPORT_GUIDE.md)** - 数据库导入指南
- **[LLM_OUTPUT_FORMAT.md](LLM_OUTPUT_FORMAT.md)** - LLM输出格式

---

**版本**: v2.3.0  
**最后更新**: 2026-05-14  
**状态**: ✅ 完整文件清单
