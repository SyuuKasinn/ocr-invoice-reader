# LLM 输出文件结构说明

## 文件组织

使用 `--use-llm` 参数时，每页会生成 **5 个文件**（如果是发票）：

```
results/20260514_165810/
├── インボイス見本_page_0002.json       # 原始 OCR 数据
├── インボイス見本_page_0002.txt        # 原始 OCR 文本
├── インボイス見本_page_0002_llm.json   # LLM 分析结果
├── インボイス見本_page_0002_llm.txt    # LLM 可读文本
└── インボイス見本_page_0002_llm.csv    # 提取字段（仅发票）
```

## 文件内容详解

### 1. 原始 OCR 文件（不含 LLM）

#### `*_page_*.json` - OCR 结构化数据
```json
{
  "page_number": 2,
  "method": "coordinate_based",
  "image_path": "...",
  "regions": [
    {
      "type": "title",
      "bbox": [1004, 333, 1488, 431],
      "confidence": 0.985,
      "text": "INVOICE",
      "table_html": null
    },
    {
      "type": "table",
      "bbox": [...],
      "text": "...",
      "rows": 21,
      "columns": 7
    }
  ]
}
```

**用途：**
- 保留完整的 OCR 识别数据
- 包含区域坐标、类型、置信度
- 不包含任何 LLM 处理结果

#### `*_page_*.txt` - OCR 原始文本
```
PAGE 2
============================================================

[Region 1 - title]
INVOICE

[Region 2 - table]
Tracking No: | 506-538-938-065
...
```

**用途：**
- 人类可读的 OCR 文本
- 按区域组织
- 与 LLM 文本对比使用

### 2. LLM 处理文件（单独保存）

#### `*_page_*_llm.json` - LLM 分析结果
```json
{
  "page_number": 2,
  "image_path": "...",
  "corrected_text": "INVOICE\nTracking No: 506-538-938-065\n...",
  "document_type": {
    "type": "invoice",
    "confidence": "high"
  },
  "extracted_fields": {
    "invoice_no": "506-538-938-065",
    "date": "24-Sep-25",
    "amount": 4000.00,
    "company": "SANEI SANSYOU CORPORATION",
    "items": [...]
  }
}
```

**用途：**
- LLM 纠正后的文本
- 文档类型分类
- 结构化字段提取
- 可直接导入数据库或 API

#### `*_page_*_llm.txt` - LLM 可读文本
```
LLM ANALYSIS - PAGE 2
============================================================

[Corrected Text]
INVOICE
Tracking No: 506-538-938-065
DATE: 24-Sep-25
...

============================================================

[Document Classification]
Type: invoice
Confidence: high

[Extracted Fields]
Invoice No: 506-538-938-065
Date: 24-Sep-25
Company: SANEI SANSYOU CORPORATION
...
```

**用途：**
- 人类审阅 LLM 结果
- 对比原始 OCR 和纠正文本
- 验证字段提取准确性

#### `*_page_*_llm.csv` - 提取字段（仅发票）
```csv
page,doc_type,confidence,invoice_no,date,company,amount
2,invoice,high,506-538-938-065,24-Sep-25,SANEI SANSYOU CORPORATION,4000.00
```

**用途：**
- 直接导入 Excel / 数据库
- 批量处理多个发票
- 数据分析和统计

## 使用场景

### 场景 1：只需要 OCR 文本
```bash
# 不使用 LLM
ocr-enhanced --image invoice.pdf --lang ch
```
输出：`*.json`, `*.txt` (原始 OCR)

### 场景 2：需要 LLM 纠错和字段提取
```bash
# 使用 LLM 自动安装
ocr-enhanced --image invoice.pdf --lang ch --use-llm --auto-setup-ollama
```
输出：
- `*.json`, `*.txt` (原始 OCR)
- `*_llm.json`, `*_llm.txt`, `*_llm.csv` (LLM 结果)

### 场景 3：对比 OCR 和 LLM
```python
import json

# 读取原始 OCR
with open('page_0002.json') as f:
    ocr_data = json.load(f)

# 读取 LLM 结果
with open('page_0002_llm.json') as f:
    llm_data = json.load(f)

# 对比
original_text = ''.join([r['text'] for r in ocr_data['regions']])
corrected_text = llm_data['corrected_text']

print("OCR 识别率:", len(original_text.replace(' ', '')))
print("LLM 纠正后:", len(corrected_text.replace(' ', '')))
```

## 文件大小

典型文件大小（单页）：

| 文件 | 大小 | 说明 |
|------|------|------|
| `*.json` | 5-50 KB | 包含完整区域数据 |
| `*.txt` | 1-5 KB | 纯文本 |
| `*_llm.json` | 2-10 KB | LLM 结果 |
| `*_llm.txt` | 1-5 KB | 可读格式 |
| `*_llm.csv` | < 1 KB | 单行记录 |

## 数据流

```
PDF 输入
  ↓
OCR 识别 (PaddleOCR)
  ↓
保存原始数据 (*.json, *.txt)
  ↓
LLM 处理 (Ollama)
  ↓
保存 LLM 结果 (*_llm.json, *_llm.txt, *_llm.csv)
  ↓
合并文件 (*_all_pages.json, *_llm.csv)
```

## 注意事项

1. **文件独立**：原始 JSON 和 LLM JSON 完全独立，互不影响
2. **失败处理**：如果 LLM 处理失败，原始文件仍会保存
3. **选择性输出**：非发票文档不会生成 `*_llm.csv`
4. **编码**：所有文件使用 UTF-8 编码（CSV 使用 UTF-8-BOM）
