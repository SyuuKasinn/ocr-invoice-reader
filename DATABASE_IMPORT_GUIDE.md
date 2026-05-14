# 数据库导入指南

## 📊 LLM CSV格式说明

使用 `--use-llm` 参数后，会生成 `{document_name}_llm.csv` 文件，专门优化用于数据库导入。

### 文件特点

✅ **数据库友好设计**:
- 空值使用空字符串（`''`），不是`null`或`NaN`
- 嵌套数据转为JSON字符串存储
- 列顺序固定，便于批量导入
- UTF-8 BOM编码，Excel兼容

## 📋 CSV结构

### 固定列（必有）

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `page` | INTEGER | 页码 | 1, 2, 3 |
| `doc_type` | TEXT | 文档类型 | invoice, receipt, waybill |
| `confidence` | TEXT | 置信度 | high, medium, low |

### 动态列（根据文档类型）

**发票 (invoice)**:

| 列名 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `invoice_no` | TEXT | 发票号 | INV-2024-001 |
| `date` | TEXT | 日期 | 2024-05-14 |
| `amount` | TEXT | 金额 | 1234.56 |
| `currency` | TEXT | 币种 | CNY, USD |
| `company` | TEXT | 公司名称 | 某某科技有限公司 |
| `tax_number` | TEXT | 税号 | 91110000123456789X |
| `buyer` | TEXT | 购买方 | 客户公司 |
| `seller` | TEXT | 销售方 | 我方公司 |
| `items` | TEXT | 商品明细（JSON） | `[{"name":"办公用品",...}]` |

**收据 (receipt)**:

| 列名 | 类型 | 说明 |
|------|------|------|
| `receipt_no` | TEXT | 收据号 |
| `date` | TEXT | 日期 |
| `amount` | TEXT | 金额 |
| `items` | TEXT | 商品明细（JSON） |

**运单 (waybill)**:

| 列名 | 类型 | 说明 |
|------|------|------|
| `tracking_no` | TEXT | 运单号 |
| `sender` | TEXT | 发件人 |
| `receiver` | TEXT | 收件人 |
| `weight` | TEXT | 重量 |
| `destination` | TEXT | 目的地 |

## 🎯 数据库导入方案

### 方案1: SQLite（轻量级）

**推荐场景**: 个人使用、小规模数据（<10万条）

```python
import pandas as pd
import sqlite3
import json

# 1. 读取CSV
df = pd.read_csv('results/20260514_123456/invoice_llm.csv')

# 2. 数据清洗
# 转换金额为数字
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

# 转换日期
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# 3. 连接数据库
conn = sqlite3.connect('invoices.db')

# 4. 创建表（首次导入）
conn.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page INTEGER,
        doc_type TEXT,
        confidence TEXT,
        invoice_no TEXT,
        date DATE,
        amount REAL,
        currency TEXT,
        company TEXT,
        tax_number TEXT,
        buyer TEXT,
        seller TEXT,
        items TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 5. 导入数据
df.to_sql('invoices', conn, if_exists='append', index=False)

# 6. 验证
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM invoices")
count = cursor.fetchone()[0]
print(f"已导入 {count} 条记录")

# 7. 查询示例
cursor.execute("""
    SELECT invoice_no, date, amount, company 
    FROM invoices 
    WHERE doc_type = 'invoice' AND confidence = 'high'
    ORDER BY date DESC
    LIMIT 10
""")
for row in cursor.fetchall():
    print(row)

conn.close()
```

### 方案2: PostgreSQL（企业级）

**推荐场景**: 多用户、大规模数据、生产环境

```python
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# 1. 读取CSV
df = pd.read_csv('invoice_llm.csv')

# 2. 数据清洗
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# 空字符串转为None（PostgreSQL友好）
df = df.replace('', None)

# 3. 连接PostgreSQL
engine = create_engine('postgresql://user:password@localhost:5432/invoices_db')

# 4. 创建表（首次）
with engine.connect() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            page INTEGER,
            doc_type VARCHAR(50),
            confidence VARCHAR(20),
            invoice_no VARCHAR(100),
            date DATE,
            amount DECIMAL(15, 2),
            currency VARCHAR(10),
            company TEXT,
            tax_number VARCHAR(50),
            buyer TEXT,
            seller TEXT,
            items JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建索引
    conn.execute("CREATE INDEX IF NOT EXISTS idx_invoice_no ON invoices(invoice_no)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON invoices(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_type ON invoices(doc_type)")

# 5. 导入数据
df.to_sql('invoices', engine, if_exists='append', index=False, method='multi')

print(f"已导入 {len(df)} 条记录")
```

### 方案3: MySQL（常用）

```python
import pandas as pd
import pymysql
from sqlalchemy import create_engine

# 1. 读取CSV
df = pd.read_csv('invoice_llm.csv')

# 2. 数据清洗
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.replace('', None)

# 3. 连接MySQL
engine = create_engine('mysql+pymysql://user:password@localhost:3306/invoices_db?charset=utf8mb4')

# 4. 创建表
with engine.connect() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            page INT,
            doc_type VARCHAR(50),
            confidence VARCHAR(20),
            invoice_no VARCHAR(100),
            date DATE,
            amount DECIMAL(15, 2),
            currency VARCHAR(10),
            company TEXT,
            tax_number VARCHAR(50),
            buyer TEXT,
            seller TEXT,
            items JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_invoice_no (invoice_no),
            INDEX idx_date (date),
            INDEX idx_doc_type (doc_type)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

# 5. 导入数据
df.to_sql('invoices', engine, if_exists='append', index=False, method='multi')

print(f"已导入 {len(df)} 条记录")
```

## 🔧 高级用法

### 1. 处理JSON字段

CSV中的`items`列存储为JSON字符串，导入数据库后可以：

**SQLite**:
```python
import json

# 读取并解析
cursor.execute("SELECT items FROM invoices WHERE id = 1")
items_str = cursor.fetchone()[0]
items_list = json.loads(items_str) if items_str else []

for item in items_list:
    print(f"{item['name']}: {item['quantity']} x {item['price']}")
```

**PostgreSQL** (使用JSONB):
```sql
-- 查询items中的商品名称
SELECT invoice_no, items->0->>'name' as first_item_name
FROM invoices
WHERE items IS NOT NULL;

-- 查询包含特定商品的发票
SELECT invoice_no, amount
FROM invoices
WHERE items @> '[{"name": "办公用品"}]'::jsonb;
```

### 2. 批量导入多个CSV

```python
import pandas as pd
import sqlite3
from pathlib import Path
import glob

conn = sqlite3.connect('all_invoices.db')

# 创建表
conn.execute('''
    CREATE TABLE IF NOT EXISTS invoices (
        file_name TEXT,
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

# 遍历所有LLM CSV文件
total_records = 0
for csv_file in glob.glob('results/*/*_llm.csv'):
    print(f"导入: {csv_file}")
    
    df = pd.read_csv(csv_file)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # 添加文件名列
    df.insert(0, 'file_name', Path(csv_file).stem)
    
    # 导入
    df.to_sql('invoices', conn, if_exists='append', index=False)
    total_records += len(df)
    print(f"  已导入 {len(df)} 条")

print(f"\n总计: {total_records} 条记录")
conn.close()
```

### 3. 数据验证和清洗

```python
import pandas as pd
import numpy as np

df = pd.read_csv('invoice_llm.csv')

# 1. 数据类型转换
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# 2. 验证必填字段
print("=== 必填字段检查 ===")
required_fields = ['invoice_no', 'date', 'amount']
for field in required_fields:
    if field in df.columns:
        missing_count = df[field].isna().sum() + (df[field] == '').sum()
        if missing_count > 0:
            print(f"警告: {field} 缺失 {missing_count} 条")
            # 显示缺失的行
            missing_rows = df[df[field].isna() | (df[field] == '')]
            print(missing_rows[['page', field]])

# 3. 数据范围验证
print("\n=== 数据范围检查 ===")
# 金额范围
invalid_amounts = df[(df['amount'] < 0) | (df['amount'] > 10000000)]
if len(invalid_amounts) > 0:
    print(f"异常金额: {len(invalid_amounts)} 条")
    print(invalid_amounts[['page', 'invoice_no', 'amount']])

# 日期范围
from datetime import datetime
now = datetime.now()
invalid_dates = df[(df['date'] < '2000-01-01') | (df['date'] > now)]
if len(invalid_dates) > 0:
    print(f"异常日期: {len(invalid_dates)} 条")

# 4. 去重
print("\n=== 重复检查 ===")
duplicates = df[df.duplicated(subset=['invoice_no'], keep=False)]
if len(duplicates) > 0:
    print(f"重复发票号: {len(duplicates)} 条")
    print(duplicates[['page', 'invoice_no']])
    
    # 可选：保留第一条，删除重复
    df = df.drop_duplicates(subset=['invoice_no'], keep='first')

# 5. 置信度统计
print("\n=== 置信度分布 ===")
print(df['confidence'].value_counts())
print(f"高置信度比例: {(df['confidence'] == 'high').sum() / len(df) * 100:.1f}%")

# 6. 保存清洗后的数据
df.to_csv('invoice_llm_cleaned.csv', index=False, encoding='utf-8-sig')
print(f"\n清洗后数据: {len(df)} 条")
```

### 4. 增量导入（避免重复）

```python
import pandas as pd
import sqlite3

def import_with_deduplication(csv_file, db_file):
    # 读取新数据
    df_new = pd.read_csv(csv_file)
    df_new['amount'] = pd.to_numeric(df_new['amount'], errors='coerce')
    df_new['date'] = pd.to_datetime(df_new['date'], errors='coerce')
    
    # 连接数据库
    conn = sqlite3.connect(db_file)
    
    # 读取已有数据的发票号
    try:
        existing_invoices = pd.read_sql(
            "SELECT DISTINCT invoice_no FROM invoices",
            conn
        )
        existing_set = set(existing_invoices['invoice_no'])
    except:
        existing_set = set()
    
    # 过滤已存在的记录
    df_to_import = df_new[~df_new['invoice_no'].isin(existing_set)]
    
    if len(df_to_import) > 0:
        df_to_import.to_sql('invoices', conn, if_exists='append', index=False)
        print(f"新导入: {len(df_to_import)} 条")
        print(f"跳过重复: {len(df_new) - len(df_to_import)} 条")
    else:
        print("没有新数据需要导入")
    
    conn.close()

# 使用
import_with_deduplication('invoice_llm.csv', 'invoices.db')
```

## 📊 查询示例

### SQLite查询

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('invoices.db')

# 1. 基本统计
print("=== 基本统计 ===")
stats = pd.read_sql("""
    SELECT 
        COUNT(*) as total_count,
        SUM(amount) as total_amount,
        AVG(amount) as avg_amount,
        COUNT(DISTINCT company) as company_count
    FROM invoices
    WHERE doc_type = 'invoice'
""", conn)
print(stats)

# 2. 按月统计
print("\n=== 按月统计 ===")
monthly = pd.read_sql("""
    SELECT 
        strftime('%Y-%m', date) as month,
        COUNT(*) as count,
        SUM(amount) as total,
        AVG(amount) as average
    FROM invoices
    WHERE doc_type = 'invoice'
    GROUP BY month
    ORDER BY month DESC
""", conn)
print(monthly)

# 3. 按公司统计
print("\n=== 按公司统计 ===")
by_company = pd.read_sql("""
    SELECT 
        company,
        COUNT(*) as invoice_count,
        SUM(amount) as total_amount
    FROM invoices
    WHERE doc_type = 'invoice' AND company != ''
    GROUP BY company
    ORDER BY total_amount DESC
    LIMIT 10
""", conn)
print(by_company)

# 4. 按置信度统计
print("\n=== 按置信度统计 ===")
by_confidence = pd.read_sql("""
    SELECT 
        confidence,
        COUNT(*) as count,
        AVG(amount) as avg_amount
    FROM invoices
    GROUP BY confidence
""", conn)
print(by_confidence)

# 5. 异常检测
print("\n=== 异常金额检测 ===")
outliers = pd.read_sql("""
    SELECT invoice_no, date, amount, company
    FROM invoices
    WHERE amount > (SELECT AVG(amount) + 3 * (
        SELECT AVG(ABS(amount - avg_amount))
        FROM (SELECT amount, AVG(amount) OVER() as avg_amount FROM invoices)
    ) FROM invoices)
    ORDER BY amount DESC
""", conn)
if len(outliers) > 0:
    print(outliers)
else:
    print("未发现异常金额")

conn.close()
```

## 🚀 生产环境最佳实践

### 1. 使用事务

```python
import sqlite3

conn = sqlite3.connect('invoices.db')
try:
    conn.execute('BEGIN')
    
    # 导入数据
    df.to_sql('invoices', conn, if_exists='append', index=False)
    
    # 验证
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM invoices")
    count = cursor.fetchone()[0]
    
    conn.commit()
    print(f"成功导入 {len(df)} 条")
except Exception as e:
    conn.rollback()
    print(f"导入失败，已回滚: {e}")
finally:
    conn.close()
```

### 2. 添加审计字段

```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 业务字段
    page INTEGER,
    doc_type TEXT,
    invoice_no TEXT,
    ...
    -- 审计字段
    source_file TEXT,           -- 来源文件
    import_batch_id TEXT,        -- 批次ID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

```python
import uuid
from datetime import datetime

# 添加审计信息
df['source_file'] = 'invoice_llm.csv'
df['import_batch_id'] = str(uuid.uuid4())
df['created_at'] = datetime.now()

df.to_sql('invoices', conn, if_exists='append', index=False)
```

### 3. 错误日志

```python
import logging
import pandas as pd

logging.basicConfig(
    filename='import.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    df = pd.read_csv('invoice_llm.csv')
    logging.info(f"读取CSV: {len(df)} 条")
    
    df.to_sql('invoices', conn, if_exists='append', index=False)
    logging.info(f"导入成功: {len(df)} 条")
    
except Exception as e:
    logging.error(f"导入失败: {e}")
    raise
```

## 📚 相关文档

- **[CSV_OUTPUT_GUIDE.md](CSV_OUTPUT_GUIDE.md)** - CSV文件格式详解
- **[OUTPUT_FILES_GUIDE.md](OUTPUT_FILES_GUIDE.md)** - 所有输出文件说明
- **[LLM_INTEGRATION_GUIDE.md](LLM_INTEGRATION_GUIDE.md)** - LLM集成指南

---

**版本**: v2.3.0  
**最后更新**: 2026-05-14  
**状态**: ✅ 数据库导入方案完整
