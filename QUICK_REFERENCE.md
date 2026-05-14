# 快速参考指南

## 🚀 命令速查

| 需求 | 命令 | 生成文件 |
|------|------|---------|
| **基本OCR** | `ocr-enhanced --image file.pdf --lang ch` | JSON + TXT + CSV统计 |
| **智能提取** | `ocr-enhanced --image file.pdf --lang ch --use-llm` | 上述 + LLM分析 + LLM CSV |
| **可视化调试** | `ocr-enhanced --image file.pdf --lang ch --visualize` | 上述 + 可视化图片 |
| **完整功能** | `ocr-enhanced --image file.pdf --lang ch --use-llm --visualize` | 所有文件 |

---

## 📊 输出文件速查

### 每页文件

| 文件 | 说明 | 何时生成 |
|------|------|---------|
| `*_page_0001.json` | OCR结构化数据 | ✅ 总是 |
| `*_page_0001.txt` | OCR文本 | ✅ 总是 |
| `*_page_0001_llm.txt` | LLM分析文本 | 🤖 --use-llm |
| `*_page_0001_llm.csv` | LLM字段CSV | 🤖 --use-llm |
| `*_page_0001_viz.jpg` | 可视化图片 | 🎨 --visualize |

### 汇总文件

| 文件 | 说明 | 何时生成 | 主要用途 |
|------|------|---------|---------|
| `*_all_pages.json` | 所有页JSON | ✅ 总是 | API、程序读取 |
| `*_all_pages.txt` | 所有页文本 | ✅ 总是 | 全文搜索 |
| `*_all_tables.html` | 所有表格 | ✅ 总是 | 浏览器查看 |
| `*_summary.csv` | 页面统计 | ✅ 总是 | Excel分析 |
| `*_llm_analysis.txt` | LLM汇总 | 🤖 --use-llm | 查看AI分析 |
| `*_llm.csv` | LLM字段汇总 | 🤖 --use-llm | **数据库导入** |

---

## 🎯 常见场景

### 1️⃣ 批量导入数据库

```bash
# 处理文档
ocr-enhanced --image invoice.pdf --lang ch --use-llm

# 导入数据库
python
>>> import pandas as pd
>>> df = pd.read_csv('results/*/invoice_llm.csv')
>>> df.to_sql('invoices', conn, if_exists='append', index=False)
```

**关键文件**: `*_llm.csv`（汇总）

---

### 2️⃣ 验证每页结果

**查看单页LLM字段**:
```bash
# Excel打开
start invoice_page_0001_llm.csv

# 或命令行查看
cat invoice_page_0001_llm.txt
```

**关键文件**: 
- `*_page_*_llm.csv`（CSV格式，Excel友好）
- `*_page_*_llm.txt`（文本格式，可读性好）

---

### 3️⃣ 调试OCR问题

```bash
# 生成可视化
ocr-enhanced --image problem.pdf --lang ch --visualize

# 查看识别框
open problem_page_0001_viz.jpg
```

**关键文件**: `*_viz.jpg`

---

### 4️⃣ 快速查看统计

```bash
# Excel打开统计CSV
start invoice_summary.csv
```

**关键文件**: `*_summary.csv`

列:
- `Page` - 页码
- `Method` - 分析方法
- `Regions` - 区域数
- `Tables` - 表格数
- `Text_Length` - 文本长度

---

## 📁 文件命名规则

### 单页文件

```
{document_name}_page_{page_number}{suffix}.{ext}
```

**示例**:
- `invoice_page_0001.json`
- `invoice_page_0001.txt`
- `invoice_page_0001_llm.txt`
- `invoice_page_0001_llm.csv`
- `invoice_page_0001_viz.jpg`

### 汇总文件

```
{document_name}{suffix}.{ext}
```

**示例**:
- `invoice_all_pages.json`
- `invoice_all_pages.txt`
- `invoice_all_tables.html`
- `invoice_summary.csv`
- `invoice_llm_analysis.txt`
- `invoice_llm.csv`

---

## 🔑 LLM CSV格式

### 单页CSV (`*_page_*_llm.csv`)

**结构**: 1行数据（该页信息）

```csv
page,doc_type,confidence,invoice_no,date,amount,currency,company
1,invoice,high,INV-001,2024-05-14,1234.56,CNY,某某科技公司
```

### 汇总CSV (`*_llm.csv`)

**结构**: N行数据（所有页信息）

```csv
page,doc_type,confidence,invoice_no,date,amount,currency,company
1,invoice,high,INV-001,2024-05-14,1234.56,CNY,某某科技公司
2,invoice,high,INV-002,2024-05-15,5678.90,CNY,另一家公司
3,invoice,medium,INV-003,2024-05-16,999.00,CNY,第三家公司
```

**固定列**（必有）:
- `page` - 页码
- `doc_type` - 文档类型（invoice/receipt/waybill）
- `confidence` - 置信度（high/medium/low）

**动态列**（根据文档类型）:
- `invoice_no`, `date`, `amount`, `currency`, `company`, `tax_number`, `buyer`, `seller`, `items`（JSON字符串）

---

## 💡 快速技巧

### 只要LLM CSV文件

```bash
# 处理
ocr-enhanced --image file.pdf --lang ch --use-llm

# 只看CSV
ls results/*/*.csv
```

输出:
```
invoice_summary.csv          # 页面统计
invoice_page_0001_llm.csv    # Page 1 LLM字段
invoice_page_0002_llm.csv    # Page 2 LLM字段
...
invoice_llm.csv              # 所有页LLM字段汇总
```

### 合并多个汇总CSV

```python
import pandas as pd
import glob

dfs = []
for file in glob.glob('results/*/invoice_llm.csv'):
    dfs.append(pd.read_csv(file))

merged = pd.concat(dfs, ignore_index=True)
merged.to_csv('all_invoices.csv', index=False, encoding='utf-8-sig')
```

### 检查LLM是否成功

```bash
# 看有没有LLM文件
ls results/*/*_llm.*

# 看记录数
wc -l results/*/invoice_llm.csv
```

---

## ⚠️ 常见问题

### Q: 没有生成 `_llm.csv` 文件？

**检查**:
1. ✅ 是否使用了 `--use-llm` 参数
2. ✅ Ollama是否运行（`ollama list`）
3. ✅ 模型是否下载（`ollama pull qwen2.5:0.5b`）
4. ✅ 是否成功提取了字段（看 `_llm.txt` 有没有字段）

### Q: CSV中文乱码？

**解决**: 文件使用UTF-8 BOM编码，Excel应该正确打开

如果还是乱码:
```python
import pandas as pd
df = pd.read_csv('file.csv', encoding='utf-8-sig')
df.to_excel('file.xlsx', index=False)  # 转Excel格式
```

### Q: 单页CSV和汇总CSV的区别？

| 类型 | 文件名 | 内容 | 用途 |
|------|--------|------|------|
| **单页** | `*_page_*_llm.csv` | 1行（该页） | 验证单页结果 |
| **汇总** | `*_llm.csv` | N行（所有页） | **导入数据库** |

**建议**: 导入数据库用汇总CSV，验证数据用单页CSV

---

## 📊 文件数量速查

| 配置 | 10页PDF | 每页文件 | 汇总文件 | 总文件数 |
|------|---------|---------|---------|---------|
| 基本OCR | 20 | 2 | 4 | **24** |
| OCR + LLM | 40 | 4 | 6 | **46** |
| OCR + viz | 30 | 3 | 4 | **34** |
| 完整功能 | 50 | 5 | 6 | **56** |

---

## 🔗 相关文档

| 文档 | 内容 |
|------|------|
| **[README.md](README.md)** | 项目总体介绍 |
| **[OUTPUT_FILES_SUMMARY.md](OUTPUT_FILES_SUMMARY.md)** | 完整文件清单 |
| **[OUTPUT_FILES_GUIDE.md](OUTPUT_FILES_GUIDE.md)** | 每个文件详解 |
| **[CSV_OUTPUT_GUIDE.md](CSV_OUTPUT_GUIDE.md)** | CSV格式详解 |
| **[DATABASE_IMPORT_GUIDE.md](DATABASE_IMPORT_GUIDE.md)** | 数据库导入 |
| **[LLM_INTEGRATION_GUIDE.md](LLM_INTEGRATION_GUIDE.md)** | LLM使用指南 |

---

**版本**: v2.3.0  
**最后更新**: 2026-05-14
