# LLM输出格式说明

## 📁 输出文件结构

使用 `--use-llm` 参数后，会额外生成LLM分析文件：

```
results/20260514_123456/
├── invoice_page_0001.json          # 原OCR结果 + LLM字段
├── invoice_page_0001.txt           # OCR文本
├── invoice_page_0001_llm.txt       # ⭐ LLM分析（单页）
├── invoice_all_pages.json          # 所有页面（含LLM）
├── invoice_all_pages.txt           # 所有OCR文本
├── invoice_llm_analysis.txt        # ⭐ LLM分析汇总（所有页）
└── invoice_all_tables.html         # 表格HTML
```

## 📄 单页LLM文件格式

**文件名**: `{page_name}_llm.txt`

**示例**: `invoice_page_0001_llm.txt`

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
    "price": "100.00"
  }
]
```

## 📋 汇总LLM文件格式

**文件名**: `{document_name}_llm_analysis.txt`

**示例**: `invoice_llm_analysis.txt`

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
  Currency: CNY
  Company: 另一家公司有限公司
```

## 🔧 JSON格式（含LLM字段）

**文件名**: `{page_name}.json` 或 `{document_name}_all_pages.json`

**新增字段**:

```json
{
  "page_number": 1,
  "method": "ppstructure_enhanced",
  "image_path": "...",
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
    "company": "某某科技有限公司",
    "tax_number": "91110000123456789X",
    "items": [
      {
        "name": "办公用品",
        "quantity": "10",
        "unit_price": "100.00",
        "amount": "1000.00"
      }
    ]
  }
}
```

### 错误情况

如果LLM处理失败：

```json
{
  "page_number": 1,
  "regions": [...],
  
  "llm_error": "Connection timeout"
}
```

或者字段提取失败：

```json
{
  "llm_document_type": {
    "type": "invoice",
    "confidence": "high"
  },
  
  "llm_extracted_fields": {
    "error": "Failed to parse JSON",
    "raw_response": "发票号码是INV-001..."
  }
}
```

## 📊 字段说明

### llm_document_type

| 字段 | 类型 | 说明 | 可能值 |
|------|------|------|--------|
| type | string | 文档类型 | invoice, receipt, waybill, contract, other |
| confidence | string | 置信度 | high, medium, low |

### llm_extracted_fields（发票类型）

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| invoice_no | string | 发票号码 | "INV-2024-001" |
| date | string | 开票日期 | "2024-05-14" |
| amount | string | 总金额 | "1234.56" |
| currency | string | 币种 | "CNY", "USD" |
| company | string | 公司名称 | "某某科技有限公司" |
| tax_number | string | 税号 | "91110000123456789X" |
| buyer | string | 购买方 | "客户公司" |
| seller | string | 销售方 | "我方公司" |
| items | array | 商品明细 | [...] |

**注意**: 
- 不是所有字段都会出现
- 字段取决于LLM从文本中提取到的内容
- 如果某字段未提取到，值为 `null` 或不出现

### llm_extracted_fields（其他类型）

根据文档类型，字段会有所不同：

**收据 (receipt)**:
- receipt_no
- date
- amount
- items

**运单 (waybill)**:
- tracking_no
- sender
- receiver
- weight
- destination

## 🎯 使用示例

### 命令行

```bash
# 生成LLM分析文件
ocr-enhanced --image invoice.pdf --use-llm --output-dir results

# 查看LLM分析
cat results/*/invoice_llm_analysis.txt

# 查看单页LLM分析
cat results/*/invoice_page_0001_llm.txt
```

### Python读取

```python
import json
from pathlib import Path

# 读取JSON（含LLM字段）
result_file = Path("results/20260514_123456/invoice_page_0001.json")
with open(result_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 获取LLM结果
doc_type = data.get('llm_document_type', {})
fields = data.get('llm_extracted_fields', {})

print(f"Type: {doc_type.get('type')}")
print(f"Invoice No: {fields.get('invoice_no')}")
print(f"Amount: {fields.get('amount')}")

# 读取LLM分析文本
llm_txt = Path("results/20260514_123456/invoice_llm_analysis.txt")
with open(llm_txt, 'r', encoding='utf-8') as f:
    analysis = f.read()
    print(analysis)
```

### 批量处理

```python
import json
from pathlib import Path

# 读取所有页面
all_pages_file = Path("results/20260514_123456/invoice_all_pages.json")
with open(all_pages_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取所有发票字段
invoices = []
for page in data['pages']:
    if 'llm_extracted_fields' in page:
        fields = page['llm_extracted_fields']
        if 'error' not in fields:
            invoices.append({
                'page': page['page_number'],
                'invoice_no': fields.get('invoice_no'),
                'amount': fields.get('amount'),
                'date': fields.get('date')
            })

# 生成CSV
import csv
with open('extracted_invoices.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['page', 'invoice_no', 'amount', 'date'])
    writer.writeheader()
    writer.writerows(invoices)
```

## 📈 输出质量

### 准确率

根据文档质量和OCR准确性：

| OCR质量 | LLM提取准确率 |
|---------|--------------|
| 优秀 (>95%) | 90-95% |
| 良好 (85-95%) | 80-90% |
| 一般 (70-85%) | 60-80% |
| 较差 (<70%) | <60% |

### 提升建议

1. **提高OCR质量**
   - 使用高分辨率图像
   - 确保文档清晰、光线充足
   - 使用GPU加速（提高识别准确率）

2. **选择合适的模型**
   - qwen2.5:0.5b - 快速但准确率略低
   - phi3:mini - 慢但准确率高

3. **提供上下文**
   ```python
   # 使用上下文纠错
   corrected = llm.fix_ocr_errors(text, context="invoice")
   ```

4. **人工验证**
   - LLM输出建议人工复核
   - 特别是金额、日期等关键字段

## 🔍 调试

### 检查LLM是否运行

```bash
# 查看输出目录
ls results/20260514_123456/

# 应该看到 *_llm.txt 文件
# 如果没有，说明LLM未运行或失败
```

### 查看LLM错误

```bash
# 查看是否有 llm_error 字段
cat results/*/invoice_page_0001.json | grep llm_error
```

### 查看原始响应

如果字段提取失败，JSON中会包含 `raw_response`：

```json
{
  "llm_extracted_fields": {
    "error": "Failed to parse JSON",
    "raw_response": "这里是LLM的原始输出..."
  }
}
```

可以根据raw_response手动提取信息或调整提示词。

## ⚙️ 自定义

如果需要自定义输出格式或提取的字段，可以修改：

```python
# ocr_invoice_reader/utils/llm_processor.py

def extract_invoice_fields(self, text: str) -> Dict[str, Any]:
    system = """你是发票信息提取专家。
    请提取以下字段：
    - invoice_no（发票号）
    - date（日期）
    - amount（金额）
    - 你需要的其他字段...
    
    以JSON格式返回。
    """
    # ...
```

---

**版本**: v2.3.0  
**最后更新**: 2026-05-14
