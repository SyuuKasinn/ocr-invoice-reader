# CSV输出格式说明

## 📊 生成的CSV文件

`ocr-enhanced` 命令会生成以下CSV文件：

### 1. 页面摘要CSV（总是生成）

**文件名**: `{document_name}_summary.csv`

**说明**: 所有页面的基本统计信息汇总

**列**:
- `Page` - 页码
- `Method` - 使用的分析方法（ppstructure_enhanced / coordinate_based）
- `Regions` - 检测到的区域数量
- `Tables` - 检测到的表格数量
- `Text_Length` - 提取的文本总长度

**示例**: `invoice_summary.csv`
```csv
Page,Method,Regions,Tables,Text_Length
1,coordinate_based,2,1,1234
2,coordinate_based,1,1,856
3,ppstructure_enhanced,4,2,2104
```

### 2. 单页LLM CSV（需要--use-llm）

**文件名**: `{page_name}_llm.csv`

**说明**: 每页LLM提取的字段，单独保存为CSV

**特点**:
- 每页一个文件（如：`invoice_page_0001_llm.csv`）
- 只包含该页的一行数据
- 便于单独查看每页结果

**示例**: `invoice_page_0001_llm.csv`
```csv
page,doc_type,confidence,invoice_no,date,amount,currency,company
1,invoice,high,INV-2024-001,2024-05-14,1234.56,CNY,某某科技有限公司
```

### 3. 汇总LLM CSV（需要--use-llm）

**文件名**: `{document_name}_llm.csv`

**说明**: 所有页面LLM提取字段的汇总，格式易于导入数据库

**固定列**（始终包含）:
- `page` - 页码
- `doc_type` - 文档类型（invoice/receipt/waybill等）
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
- `items` - 商品明细（JSON字符串）

**示例**: `invoice_llm.csv`
```csv
page,doc_type,confidence,invoice_no,date,amount,currency,company,items
1,invoice,high,INV-2024-001,2024-05-14,1234.56,CNY,某某科技有限公司,"[{""name"":""办公用品"",""quantity"":""10"",""price"":""100.00""}]"
2,invoice,high,INV-2024-002,2024-05-15,5678.90,CNY,另一家公司,
```

**数据库友好特性**:
- 空值显示为空字符串（而非null）
- 嵌套数据（如items列表）转为JSON字符串
- 列顺序固定：page, doc_type, confidence在前
- UTF-8 BOM编码，Excel兼容

## 📁 完整输出结构

```
results/20260514_123456/
├── invoice_page_0001.json          # Page 1 结构化数据
├── invoice_page_0001.txt           # Page 1 OCR文本
├── invoice_page_0001_llm.txt       # Page 1 LLM分析 (--use-llm)
├── invoice_page_0001_llm.csv       # ⭐ Page 1 LLM字段CSV (--use-llm, 新增)
├── invoice_page_0002.json          # Page 2 结构化数据
├── invoice_page_0002.txt           # Page 2 OCR文本
├── invoice_page_0002_llm.txt       # Page 2 LLM分析 (--use-llm)
├── invoice_page_0002_llm.csv       # ⭐ Page 2 LLM字段CSV (--use-llm, 新增)
├── ...
├── invoice_all_pages.json          # 所有页JSON
├── invoice_all_pages.txt           # 所有页文本
├── invoice_all_tables.html         # 所有表格HTML
├── invoice_summary.csv             # ⭐ 页面摘要CSV（总是生成）
├── invoice_llm_analysis.txt        # LLM汇总文本 (--use-llm)
└── invoice_llm.csv                 # ⭐ LLM字段汇总CSV (--use-llm)
```

## 💡 使用场景

### 场景1: 批量统计

```bash
# 处理多个文档
ocr-enhanced --image document1.pdf --output-dir results
ocr-enhanced --image document2.pdf --output-dir results
ocr-enhanced --image document3.pdf --output-dir results

# 合并所有summary.csv
cat results/*/*.csv > all_documents_summary.csv
```

### 场景2: Excel分析

```python
import pandas as pd

# 读取摘要CSV
df_summary = pd.read_csv('results/20260514_123456/invoice_summary.csv')

# 统计
print(f"总页数: {len(df)}")
print(f"平均区域数: {df['Regions'].mean():.1f}")
print(f"总表格数: {df['Tables'].sum()}")
print(f"使用方法分布:\n{df['Method'].value_counts()}")
```

### 场景3: 发票批量导入数据库

```python
import pandas as pd
import json

# 读取LLM提取的字段
df = pd.read_csv('results/20260514_123456/invoice_llm.csv')

# 数据清洗
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# 解析JSON字段（如items）
if 'items' in df.columns:
    df['items_parsed'] = df['items'].apply(
        lambda x: json.loads(x) if x and x != '' else []
    )

# 导入数据库
import sqlite3
conn = sqlite3.connect('invoices.db')

# 创建表（如果不存在）
conn.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        page INTEGER,
        doc_type TEXT,
        confidence TEXT,
        invoice_no TEXT,
        date DATE,
        amount REAL,
        currency TEXT,
        company TEXT,
        tax_number TEXT,
        items TEXT
    )
''')

# 导入数据
df.to_sql('invoices', conn, if_exists='append', index=False)
conn.close()

print(f"已导入 {len(df)} 条发票记录")
```

### 场景4: 数据验证

```python
import pandas as pd

# 读取LLM结果
df = pd.read_csv('invoice_llm.csv')

# 检查文档类型分布
print("文档类型分布:")
print(df['doc_type'].value_counts())
print(f"\n高置信度记录: {(df['confidence'] == 'high').sum()} / {len(df)}")

# 检查必填字段
required_fields = ['invoice_no', 'date', 'amount']
for field in required_fields:
    if field in df.columns:
        missing = (df[field] == '').sum() + df[field].isna().sum()
        if missing > 0:
            print(f"警告: {field} 有 {missing} 个缺失值")

# 数据类型转换和验证
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# 检查金额范围
invalid_amounts = df[(df['amount'] <= 0) | (df['amount'] > 1000000)]
if len(invalid_amounts) > 0:
    print(f"\n异常金额: {len(invalid_amounts)} 条")
    print(invalid_amounts[['page', 'doc_type', 'invoice_no', 'amount']])

# 检查日期格式
df['date'] = pd.to_datetime(df['date'], errors='coerce')
invalid_dates = df[df['date'].isna()]
if len(invalid_dates) > 0:
    print(f"\n日期格式错误: {len(invalid_dates)} 条")
```

## 📈 CSV格式详情

### 编码

- **UTF-8 with BOM** (`utf-8-sig`)
- Excel可直接打开，正确显示中文

### 分隔符

- **逗号** (`,`)
- 标准CSV格式

### 引号规则

- 包含逗号、换行或引号的字段会自动加引号
- 引号使用双引号转义 (`""`)

### 示例

```csv
page,invoice_no,company,amount,notes
1,INV-001,"某某科技有限公司",1234.56,"这是备注，包含逗号"
2,INV-002,简单公司名,5678.90,
3,INV-003,"包含""引号""的公司",999.00,
```

## 🔧 自定义CSV输出

如果需要自定义CSV列或格式，可以修改代码：

### 修改摘要CSV

编辑 `ocr_invoice_reader/cli/enhanced_extract.py`:

```python
# 添加自定义列
writer.writerow(['Page', 'Method', 'Regions', 'Tables', 'Text_Length', 'Custom_Field'])

for result in all_results:
    # ... 现有字段
    custom_value = calculate_custom_value(result)  # 你的逻辑
    writer.writerow([page_num, method, region_count, table_count_page, text_length, custom_value])
```

### 自定义LLM CSV

编辑提取逻辑：

```python
# 只提取特定字段
for result in llm_results:
    if 'llm_extracted_fields' in result:
        fields = result['llm_extracted_fields']
        row = {
            'page': result['page_number'],
            'invoice_no': fields.get('invoice_no', ''),
            'amount': fields.get('amount', ''),
            # 只要你需要的字段
        }
        csv_data.append(row)
```

## 🐛 常见问题

### Q: Excel打开CSV中文乱码？

**A**: 文件使用UTF-8 BOM编码，Excel应该能正确打开。如果还是乱码：

```python
# 手动转换
import pandas as pd
df = pd.read_csv('file.csv', encoding='utf-8-sig')
df.to_excel('file.xlsx', index=False)  # 转为Excel格式
```

### Q: LLM CSV没有生成？

**A**: 检查：
1. 是否使用了 `--use-llm` 参数
2. Ollama是否运行（`ollama list` 查看已安装模型）
3. 是否成功提取了字段（查看JSON中的`llm_extracted_fields`）
4. 命令行是否显示 "LLM CSV: xxx.csv" 消息

### Q: CSV中有些列为空？

**A**: 正常情况。LLM只提取能识别的字段，无法识别的字段会显示为空字符串（便于数据库导入）。

### Q: 如何处理items等嵌套字段？

**A**: 这些字段以JSON字符串存储：
```python
import pandas as pd
import json

df = pd.read_csv('invoice_llm.csv')

# 解析JSON字段
if 'items' in df.columns:
    df['items_list'] = df['items'].apply(
        lambda x: json.loads(x) if x and x != '' else []
    )
    
    # 提取第一个商品名称
    df['first_item'] = df['items_list'].apply(
        lambda x: x[0]['name'] if len(x) > 0 else ''
    )
```

### Q: 如何合并多个CSV？

```bash
# Linux/Mac
cat results/*/invoice_summary.csv | awk 'NR==1 || !/^Page/' > merged.csv

# Python
import pandas as pd
import glob

dfs = []
for file in glob.glob('results/*/invoice_summary.csv'):
    dfs.append(pd.read_csv(file))

merged = pd.concat(dfs, ignore_index=True)
merged.to_csv('merged_summary.csv', index=False)
```

## 📊 数据分析示例

### 统计分析

```python
import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv('invoice_summary.csv')

# 基本统计
print(df.describe())

# 可视化
df.plot(x='Page', y=['Regions', 'Tables'], kind='bar')
plt.title('Regions and Tables per Page')
plt.show()
```

### 发票金额分析

```python
import pandas as pd
import numpy as np

df = pd.read_csv('invoice_llm.csv')
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# 基本统计
print(f"文档总数: {len(df)}")
print(f"发票类型: {(df['doc_type'] == 'invoice').sum()}")
print(f"高置信度: {(df['confidence'] == 'high').sum()}")

# 金额统计（只统计发票）
invoices = df[df['doc_type'] == 'invoice']
print(f"\n总金额: {invoices['amount'].sum():.2f}")
print(f"平均金额: {invoices['amount'].mean():.2f}")
print(f"中位数: {invoices['amount'].median():.2f}")
print(f"最大: {invoices['amount'].max():.2f}")
print(f"最小: {invoices['amount'].min():.2f}")

# 按币种分组
if 'currency' in df.columns:
    by_currency = invoices.groupby('currency').agg({
        'amount': ['sum', 'count', 'mean']
    })
    print("\n按币种统计:")
    print(by_currency)
```

---

**版本**: v2.3.0  
**最后更新**: 2026-05-14
