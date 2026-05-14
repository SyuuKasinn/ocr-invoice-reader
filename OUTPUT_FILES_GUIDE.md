# 输出文件完整说明

## 📁 完整输出结构

### 基本OCR输出（无--use-llm）

```
results/20260514_123456/
├── invoice_page_0001.json          # Page 1 结构化数据（JSON）
├── invoice_page_0001.txt           # Page 1 OCR文本
├── invoice_page_0001_viz.jpg       # Page 1 可视化图片（需要--visualize）
├── invoice_page_0002.json          # Page 2 结构化数据
├── invoice_page_0002.txt           # Page 2 OCR文本
├── invoice_page_0002_viz.jpg       # Page 2 可视化图片（需要--visualize）
├── ...
├── invoice_all_pages.json          # ⭐ 所有页JSON合集
├── invoice_all_pages.txt           # ⭐ 所有页文本合集
├── invoice_all_tables.html         # ⭐ 所有表格HTML
└── invoice_summary.csv             # ⭐ 页面统计CSV（新增）
```

### LLM增强输出（使用--use-llm）

```
results/20260514_123456/
├── invoice_page_0001.json          # Page 1 结构化数据 + LLM字段
├── invoice_page_0001.txt           # Page 1 原始OCR文本（保持不变）
├── invoice_page_0001_llm.txt       # ⭐ Page 1 LLM分析文本
├── invoice_page_0001_llm.csv       # ⭐ Page 1 LLM字段CSV（新增）
├── invoice_page_0001_viz.jpg       # Page 1 可视化图片
├── invoice_page_0002.json          # Page 2 结构化数据 + LLM字段
├── invoice_page_0002.txt           # Page 2 原始OCR文本
├── invoice_page_0002_llm.txt       # ⭐ Page 2 LLM分析文本
├── invoice_page_0002_llm.csv       # ⭐ Page 2 LLM字段CSV（新增）
├── invoice_page_0002_viz.jpg       # Page 2 可视化图片
├── ...
├── invoice_all_pages.json          # 所有页JSON（包含LLM字段）
├── invoice_all_pages.txt           # 所有页OCR文本
├── invoice_all_tables.html         # 所有表格HTML
├── invoice_summary.csv             # ⭐ 页面统计CSV（总是生成）
├── invoice_llm_analysis.txt        # ⭐ LLM分析汇总文本
└── invoice_llm.csv                 # ⭐ LLM字段汇总CSV（数据库友好格式）
```

## 📄 文件详解

### 1. 单页JSON文件

**文件名**: `{page_name}.json`

**内容**: 包含OCR识别的所有区域、表格等结构化信息

**无LLM示例**:
```json
{
  "page_number": 1,
  "method": "coordinate_based",
  "image_path": "/path/to/image.jpg",
  "regions": [
    {
      "type": "text",
      "bbox": [100, 200, 300, 250],
      "confidence": 0.95,
      "text": "发票号码: INV-2024-001"
    },
    {
      "type": "table",
      "bbox": [100, 300, 800, 600],
      "confidence": 0.92,
      "text": "...",
      "table_html": "<table>...</table>"
    }
  ]
}
```

**含LLM示例**:
```json
{
  "page_number": 1,
  "method": "coordinate_based",
  "image_path": "/path/to/image.jpg",
  "regions": [...],
  "llm_document_type": {
    "type": "invoice",
    "confidence": "high"
  },
  "llm_extracted_fields": {
    "invoice_no": "INV-2024-001",
    "date": "2024-05-14",
    "amount": "1234.56",
    "currency": "CNY",
    "company": "某某科技有限公司"
  }
}
```

### 2. 单页TXT文件（原始OCR）

**文件名**: `{page_name}.txt`

**说明**: 原始OCR识别的文本，按区域分块

**示例**:
```
PAGE 1
============================================================

[Region 1 - text]
发票号码: INV-2024-001

[Region 2 - text]
日期: 2024-05-14

[Region 3 - table]
商品名称	数量	单价	金额
办公用品	10	100.00	1000.00
```

**重要**: 此文件始终保持OCR原始输出，不受LLM影响

### 3. 单页LLM分析文件（仅--use-llm时生成）

**文件名**: `{page_name}_llm.txt`

**说明**: LLM对该页的分析结果，包括文档分类和提取的字段

**示例**:
```
LLM ANALYSIS - PAGE 1
============================================================

[Document Classification]
Type: invoice
Confidence: high

[Extracted Fields]
Invoice No: INV-2024-001
Date: 2024-05-14
Amount: 1234.56
Currency: CNY
Company: 某某科技有限公司
Tax Number: 91110000123456789X
Items: [
  {
    "name": "办公用品",
    "quantity": "10",
    "unit_price": "100.00",
    "amount": "1000.00"
  }
]
```

### 4. 单页LLM字段CSV（仅--use-llm时生成）

**文件名**: `{page_name}_llm.csv`

**说明**: 每页LLM提取的字段，单独保存为CSV格式

**特点**:
- 每页一个独立文件
- 只包含该页的一行数据
- 数据库友好格式
- 便于单独查看和验证每页结果

**示例**: `invoice_page_0001_llm.csv`
```csv
page,doc_type,confidence,invoice_no,date,amount,currency,company,tax_number
1,invoice,high,INV-2024-001,2024-05-14,1234.56,CNY,某某科技有限公司,91110000123456789X
```

**使用场景**:
- 📄 逐页验证LLM提取结果
- 🔍 快速查看单页字段（Excel打开）
- 📊 单独分析某一页的数据
- ✅ 调试和质量检查

### 5. 可视化图片（仅--visualize时生成）

**文件名**: `{page_name}_viz.jpg`

**说明**: OCR识别结果的可视化，显示文本框、表格边界等

### 6. 合并JSON文件

**文件名**: `{document_name}_all_pages.json`

**说明**: 所有页面的结构化数据合并

**示例**:
```json
{
  "document": "invoice",
  "total_pages": 3,
  "pages": [
    {
      "page_number": 1,
      "method": "coordinate_based",
      "regions": [...],
      "llm_document_type": {...},
      "llm_extracted_fields": {...}
    },
    {
      "page_number": 2,
      "method": "coordinate_based",
      "regions": [...],
      "llm_document_type": {...},
      "llm_extracted_fields": {...}
    }
  ]
}
```

### 7. 合并TXT文件

**文件名**: `{document_name}_all_pages.txt`

**说明**: 所有页面的OCR文本合并

**示例**:
```
============================================================
PAGE 1
============================================================

[Region 1 - text]
发票号码: INV-2024-001

[Region 2 - text]
日期: 2024-05-14


============================================================
PAGE 2
============================================================

[Region 1 - text]
发票号码: INV-2024-002
...
```

### 8. 表格HTML文件

**文件名**: `{document_name}_all_tables.html`

**说明**: 所有页面中检测到的表格，以HTML格式保存

**示例**:
```html
<html>
<head><meta charset="utf-8"><style>...</style></head>
<body>
  <h2>Page 1</h2>
  <h3>Table 1</h3>
  <table>
    <tr><td>商品名称</td><td>数量</td><td>单价</td></tr>
    <tr><td>办公用品</td><td>10</td><td>100.00</td></tr>
  </table>
  
  <h2>Page 2</h2>
  <h3>Table 2</h3>
  <table>...</table>
</body>
</html>
```

### 9. 页面摘要CSV（新增）

**文件名**: `{document_name}_summary.csv`

**说明**: 每页的基本统计信息

**列**:
- `Page` - 页码
- `Method` - 使用的分析方法
- `Regions` - 检测到的区域数量
- `Tables` - 检测到的表格数量
- `Text_Length` - 提取的文本总长度

**示例**:
```csv
Page,Method,Regions,Tables,Text_Length
1,coordinate_based,5,1,917
2,coordinate_based,2,1,733
3,coordinate_based,5,1,1547
4,coordinate_based,3,1,2157
5,coordinate_based,1,1,874
```

**使用场景**:
- 快速了解文档结构
- 批量统计分析
- Excel数据透视表
- 质量检查（检测空页、异常页）

### 10. LLM分析汇总文件（仅--use-llm时生成）

**文件名**: `{document_name}_llm_analysis.txt`

**说明**: 所有页面的LLM分析汇总

**示例**:
```
LLM ANALYSIS SUMMARY
============================================================
Document: invoice
Total pages analyzed: 3
============================================================


============================================================
PAGE 1
============================================================

[Document Classification]
  Type: invoice
  Confidence: high

[Extracted Fields]
  Invoice No: INV-2024-001
  Date: 2024-05-14
  Amount: 1234.56
  Currency: CNY
  Company: 某某科技有限公司


============================================================
PAGE 2
============================================================

[Document Classification]
  Type: invoice
  Confidence: high

[Extracted Fields]
  Invoice No: INV-2024-002
  Date: 2024-05-15
  Amount: 5678.90
```

### 11. LLM提取字段汇总CSV（仅--use-llm时生成）

**文件名**: `{document_name}_llm.csv`

**说明**: 所有页面LLM提取字段的汇总CSV，**专门优化用于数据库导入**

**固定列**（始终包含）:
- `page` - 页码
- `doc_type` - 文档类型（invoice/receipt/waybill/contract/other）
- `confidence` - 识别置信度（high/medium/low）

**动态列**（根据文档类型而定）:

**发票类型常见列**:
- `invoice_no` - 发票号
- `date` - 日期
- `amount` - 金额
- `currency` - 币种
- `company` - 公司名称
- `tax_number` - 税号
- `buyer` - 购买方
- `seller` - 销售方
- `items` - 商品明细（JSON字符串格式）

**数据库友好特性**:
- ✅ 空值显示为空字符串（不是null），避免数据库导入问题
- ✅ 嵌套数据自动转为JSON字符串（如items列表）
- ✅ 列顺序固定：page, doc_type, confidence在前，便于查询
- ✅ UTF-8 BOM编码，Excel直接打开无乱码

**示例**:
```csv
page,doc_type,confidence,invoice_no,date,amount,currency,company,tax_number,items
1,invoice,high,INV-2024-001,2024-05-14,1234.56,CNY,某某科技有限公司,91110000123456789X,"[{""name"":""办公用品"",""quantity"":""10"",""price"":""100.00""}]"
2,invoice,high,INV-2024-002,2024-05-15,5678.90,CNY,另一家公司,91110000123456789Y,
3,invoice,medium,INV-2024-003,2024-05-16,999.00,CNY,第三家公司,,
```

**使用场景**:
- 🎯 **批量导入数据库**（主要用途）
- 📊 Excel数据分析和透视表
- 💰 财务对账和统计
- ✅ 数据验证和质量检查

**导入数据库示例**:
```python
import pandas as pd
import sqlite3

# 读取CSV
df = pd.read_csv('invoice_llm.csv')

# 数据类型转换
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# 直接导入数据库
conn = sqlite3.connect('invoices.db')
df.to_sql('invoices', conn, if_exists='append', index=False)
conn.close()
```

## 🎯 文件命名规则

### 基本规则

- `{document_name}` - 文档名（不含扩展名）
- `{page_name}` - 页面名（文档名 + _page_0001）
- UTF-8编码（所有文本文件）
- UTF-8-BOM编码（所有CSV文件，Excel友好）

### 示例

**输入**: `发票样本.pdf`

**输出**:
- `发票样本_page_0001.json`
- `发票样本_page_0001.txt`
- `发票样本_page_0001_llm.txt` （仅--use-llm）
- `发票样本_page_0001_viz.jpg` （仅--visualize）
- `发票样本_all_pages.json`
- `发票样本_all_pages.txt`
- `发票样本_all_tables.html`
- `发票样本_summary.csv`
- `发票样本_llm_analysis.txt` （仅--use-llm）
- `发票样本_llm_extracted.csv` （仅--use-llm）

## 📊 文件大小估算

**单页A4发票（假设100个文本框，1个表格）**:

| 文件类型 | 大小 | 说明 |
|---------|------|------|
| `*_page_*.json` | 15-50KB | 结构化数据 |
| `*_page_*.txt` | 1-3KB | 纯文本 |
| `*_page_*_llm.txt` | 0.5-2KB | LLM分析 |
| `*_page_*_viz.jpg` | 1-2MB | 可视化图片 |
| `*_all_pages.json` | 50-200KB | 所有页合并 |
| `*_all_pages.txt` | 5-15KB | 所有文本 |
| `*_all_tables.html` | 2-10KB | 表格HTML |
| `*_summary.csv` | <1KB | 统计CSV |
| `*_llm_analysis.txt` | 2-8KB | LLM汇总 |
| `*_llm_extracted.csv` | <1KB | 字段CSV |

**10页PDF总大小估算**:
- 无可视化: ~500KB
- 有可视化: ~15-20MB

## 🔧 使用示例

### 基本OCR（无LLM）

```bash
ocr-enhanced --image invoice.pdf --lang ch --output-dir results
```

**生成文件**:
- JSON（单页 + 合并）
- TXT（单页 + 合并）
- HTML（表格）
- CSV（摘要统计）

### OCR + LLM增强

```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm --output-dir results
```

**额外生成**:
- `*_llm.txt`（每页LLM分析）
- `*_llm_analysis.txt`（LLM汇总）
- `*_llm_extracted.csv`（提取字段）
- JSON文件包含LLM字段

### OCR + 可视化

```bash
ocr-enhanced --image invoice.pdf --lang ch --visualize --output-dir results
```

**额外生成**:
- `*_viz.jpg`（每页可视化图片）

### 完整功能

```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm --visualize --output-dir results
```

**生成所有文件**（10种文件类型）

## 📈 数据分析示例

### Python读取CSV

```python
import pandas as pd

# 读取摘要CSV
df_summary = pd.read_csv('results/20260514_123456/invoice_summary.csv')
print(f"总页数: {len(df_summary)}")
print(f"总表格数: {df_summary['Tables'].sum()}")
print(f"平均区域数: {df_summary['Regions'].mean():.1f}")

# 读取LLM提取CSV
df_llm = pd.read_csv('results/20260514_123456/invoice_llm_extracted.csv')
df_llm['amount'] = pd.to_numeric(df_llm['amount'], errors='coerce')
print(f"总金额: {df_llm['amount'].sum():.2f}")
print(f"发票数: {len(df_llm)}")
```

### Excel分析

1. 打开 `*_summary.csv`
2. 创建数据透视表
3. 按Method分组统计
4. 可视化Regions/Tables分布

### 数据库导入

```python
import pandas as pd
import sqlite3

# 读取LLM CSV
df = pd.read_csv('invoice_llm_extracted.csv')

# 导入数据库
conn = sqlite3.connect('invoices.db')
df.to_sql('invoices', conn, if_exists='append', index=False)
conn.close()
```

## 🔍 故障排除

### Q: 为什么没有生成CSV文件？

**A**: 检查以下情况：
1. 确认使用的是 `ocr-enhanced` 命令（不是 `ocr-simple` 或 `ocr-extract`）
2. 处理完成后检查输出目录
3. CSV生成是自动的，无需额外参数

### Q: 为什么没有 *_llm.txt 和 *_llm_extracted.csv？

**A**: 需要满足：
1. 使用 `--use-llm` 参数
2. Ollama服务正在运行
3. 模型已下载（如 qwen2.5:0.5b）
4. LLM成功提取了字段

### Q: CSV中文乱码怎么办？

**A**: CSV使用UTF-8 BOM编码，Excel应该正确打开。如果还是乱码：
```python
import pandas as pd
df = pd.read_csv('file.csv', encoding='utf-8-sig')
df.to_excel('file.xlsx', index=False)  # 转为Excel格式
```

### Q: 如何合并多次处理的CSV？

```python
import pandas as pd
import glob

# 合并所有summary CSV
dfs = []
for file in glob.glob('results/*/invoice_summary.csv'):
    dfs.append(pd.read_csv(file))

merged = pd.concat(dfs, ignore_index=True)
merged.to_csv('all_summaries.csv', index=False, encoding='utf-8-sig')
```

## 📚 相关文档

- **[CSV_OUTPUT_GUIDE.md](CSV_OUTPUT_GUIDE.md)** - CSV文件格式详解
- **[LLM_OUTPUT_FORMAT.md](LLM_OUTPUT_FORMAT.md)** - LLM输出格式详解
- **[LLM_INTEGRATION_GUIDE.md](LLM_INTEGRATION_GUIDE.md)** - LLM集成完整指南
- **[README.md](README.md)** - 项目总体说明

---

**版本**: v2.3.0  
**最后更新**: 2026-05-14  
**状态**: ✅ 所有输出格式已实现
