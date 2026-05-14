# Changes in v2.2.0

## 🎉 New Features

### 1. REST API Support

完整的REST API服务，支持Web应用集成。

**安装:**
```bash
pip install -e ".[api]"
```

**启动API服务器:**
```bash
ocr-api
```

**主要端点:**
- `POST /api/v1/extract` - 单文档提取（同步）
- `POST /api/v1/extract/enhanced` - 增强结构分析
- `POST /api/v1/extract/batch` - 批量提取（异步）
- `GET /api/v1/result/{task_id}` - 获取结果
- `GET /api/v1/result/{task_id}/csv` - 下载CSV

**文档:** http://localhost:8000/docs

---

### 2. CSV导出功能

支持将提取结果导出为CSV格式，便于数据分析。

**两种导出模式:**

1. **Summary模式** - 每个文档一行（文档级别汇总）
2. **Items模式** - 每个明细项一行（明细级别）

**命令行使用:**
```bash
# 批量处理时自动生成CSV
ocr-extract --input-dir invoices/ --output-dir results/
# 生成:
#   results/extraction_summary.csv
#   results/extraction_items.csv
```

**Python API:**
```python
# 单个文档导出
document.save_to_csv('result.csv', mode='summary')

# 批量文档导出
BaseDocument.save_multiple_to_csv(documents, 'batch.csv', mode='items')
```

**REST API:**
```bash
# 下载CSV
curl "http://localhost:8000/api/v1/result/{task_id}/csv?mode=summary" -o result.csv
```

---

## 📝 新增文件

### API相关
- `ocr_invoice_reader/api/` - REST API模块
  - `app.py` - FastAPI应用
  - `__init__.py` - API模块初始化
- `ocr_invoice_reader/cli/api_server.py` - API服务器CLI入口

### 文档
- `docs/API_USAGE.md` - REST API完整使用文档
- `docs/QUICKSTART_API_CSV.md` - API和CSV快速开始指南
- `CHANGES_v2.2.md` - 版本更新说明（本文档）

### 示例
- `examples/api_client_example.py` - REST API客户端示例
- `examples/csv_export_example.py` - CSV导出使用示例

### 测试
- `tests/test_csv_export.py` - CSV导出功能单元测试

---

## 🔧 代码改进

### BaseDocument模型增强
- `to_csv_row()` - 转换为CSV行（文档级别）
- `to_csv_items()` - 转换为CSV行（明细级别）
- `save_to_csv()` - 保存单个文档为CSV
- `save_multiple_to_csv()` - 批量保存为CSV（静态方法）

### DocumentExtractor增强
- `_generate_summary()` - 批量处理时自动生成CSV文件

### setup.py更新
- 新增 `api` extra依赖（FastAPI, uvicorn）
- 新增 `ocr-api` 命令行入口

---

## 📊 CSV格式说明

### Summary CSV（汇总模式）
文档级别信息，每个文档一行：

| 字段 | 说明 |
|------|------|
| document_type | 文档类型 |
| document_number | 文档编号 |
| date | 日期 |
| sender_company | 发件人公司 |
| sender_address | 发件人地址 |
| sender_phone | 发件人电话 |
| receiver_company | 收件人公司 |
| receiver_address | 收件人地址 |
| receiver_phone | 收件人电话 |
| item_count | 明细项数量 |
| subtotal | 小计 |
| tax | 税额 |
| total_amount | 总金额 |
| currency | 币种 |
| confidence | 置信度 |
| extraction_method | 提取方法 |
| source_file | 源文件 |

### Items CSV（明细模式）
明细项级别信息，每个明细项一行：

| 字段 | 说明 |
|------|------|
| document_number | 文档编号 |
| document_type | 文档类型 |
| item_index | 明细项索引 |
| description | 描述 |
| quantity | 数量 |
| unit | 单位 |
| unit_price | 单价 |
| amount | 金额 |
| notes | 备注 |
| source_file | 源文件 |

---

## 🌐 API端点详情

### 1. 单文档提取（同步）
```
POST /api/v1/extract
Parameters: file, lang, use_gpu, visualize
Returns: 立即返回提取结果
```

### 2. 增强结构分析
```
POST /api/v1/extract/enhanced
Parameters: file, lang, use_gpu
Returns: 详细的结构信息（区域、表格）
```

### 3. 批量提取（异步）
```
POST /api/v1/extract/batch
Parameters: files[], lang, use_gpu
Returns: task_id（后台处理）
```

### 4. 获取结果
```
GET /api/v1/result/{task_id}
Returns: 提取结果JSON
```

### 5. 下载CSV
```
GET /api/v1/result/{task_id}/csv?mode=summary|items
Returns: CSV文件下载
```

### 6. 列出结果
```
GET /api/v1/results?limit=10
Returns: 最近的提取结果列表
```

### 7. 删除结果
```
DELETE /api/v1/result/{task_id}
Returns: 删除确认
```

---

## 🚀 使用场景

### 1. Web应用集成
通过REST API接入Web应用，实现文档上传和提取功能。

### 2. 数据分析管道
批量提取文档，导出CSV，导入分析工具（Excel、Pandas等）。

### 3. 自动化工作流
监控文件夹，自动提取，生成CSV报告。

### 4. 会计系统集成
提取发票数据，导出CSV，导入会计软件。

---

## 📖 快速开始

### REST API
```bash
# 1. 安装
pip install -e ".[api]"

# 2. 启动服务器
ocr-api

# 3. 访问文档
open http://localhost:8000/docs

# 4. 测试
curl -X POST "http://localhost:8000/api/v1/extract?lang=ch" \
  -F "file=@invoice.pdf"
```

### CSV导出
```python
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor

# 批量处理（自动生成CSV）
extractor = DocumentExtractor(use_gpu=False, lang='ch')
documents = extractor.batch_extract('invoices/', 'results/')

# 结果: results/extraction_summary.csv 和 extraction_items.csv
```

---

## 🔗 相关文档

- **REST API完整文档**: [docs/API_USAGE.md](docs/API_USAGE.md)
- **快速开始指南**: [docs/QUICKSTART_API_CSV.md](docs/QUICKSTART_API_CSV.md)
- **API客户端示例**: [examples/api_client_example.py](examples/api_client_example.py)
- **CSV导出示例**: [examples/csv_export_example.py](examples/csv_export_example.py)

---

## ⚠️ 注意事项

1. **API存储**: 当前版本使用内存存储结果，生产环境建议使用数据库（Redis、PostgreSQL等）

2. **文件大小**: 建议单文件不超过10MB

3. **批量限制**: API批量处理最多50个文件

4. **认证**: 当前版本未实现认证，生产环境请添加OAuth2/JWT

5. **速率限制**: 未实现速率限制，生产环境建议添加中间件

---

## 🐛 已知问题

无重大已知问题。

---

## 💡 未来计划

- [ ] 数据库持久化存储
- [ ] 认证和授权
- [ ] WebSocket支持（实时进度）
- [ ] Excel格式导出
- [ ] 更多数据分析功能

---

**版本**: 2.2.0  
**发布日期**: 2024-05-14  
**作者**: OCR Invoice Reader Team
