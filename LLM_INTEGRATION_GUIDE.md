# 🤖 LLM集成指南 - AI智能推理

## 📋 概述

通过集成本地LLM模型，为OCR结果提供智能后处理：
- ✅ 文本纠错 - 修正OCR识别错误
- ✅ 字段提取 - 自动提取发票号、金额等关键信息
- ✅ 文档分类 - 识别文档类型（发票/收据/运单等）
- ✅ 内容理解 - 表格数据结构化、文档摘要
- ✅ **CPU友好** - 小模型，无需GPU

## 🚀 快速开始

### 1. 安装Ollama

**Windows**:
```bash
# 下载并安装 Ollama
# https://ollama.ai/download

# 验证安装
ollama --version
```

**macOS/Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. 下载推荐模型

```bash
# CPU友好的小模型（推荐）
ollama pull qwen2.5:0.5b  # 0.5B参数，~300MB，CPU友好

# 或其他选择
ollama pull phi3:mini      # 3.8B参数，~2GB，效果更好但较慢
ollama pull gemma2:2b      # 2B参数，~1.5GB，平衡选择
```

**模型对比**：

| 模型 | 参数量 | 大小 | CPU速度 | 质量 | 推荐度 |
|------|--------|------|---------|------|--------|
| **qwen2.5:0.5b** | 0.5B | 300MB | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ CPU首选 |
| gemma2:2b | 2B | 1.5GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ 平衡 |
| phi3:mini | 3.8B | 2GB | ⚡⚡ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ 质量优先 |

### 3. 启用LLM处理

```bash
# 基本使用
ocr-enhanced --image invoice.pdf --lang ch --use-llm

# 指定模型
ocr-enhanced --image invoice.pdf --lang ch --use-llm --llm-model phi3:mini

# 完整命令
ocr-enhanced --image invoice.pdf --lang ch --use-cpu --use-llm --output-dir results_llm
```

## 🎯 功能详解

### 功能1: OCR文本纠错

**问题**：OCR识别错误
```
原文: 1nvoice Number: 2O24O1O1
错误: 1 → I, O → 0
```

**LLM纠正**：
```python
from ocr_invoice_reader.utils.llm_processor import LLMProcessor

processor = LLMProcessor(model="qwen2.5:0.5b")
corrected = processor.correct_text("1nvoice Number: 2O24O1O1")
print(corrected)
# Output: Invoice Number: 20240101
```

### 功能2: 字段自动提取

**输入**：OCR文本
```
发票号码：INV-2024-001
日期：2024-05-14
金额：￥1,234.56
公司：某某科技有限公司
```

**LLM提取**：
```python
fields = processor.extract_invoice_fields(ocr_text)
print(fields)
# Output:
# {
#   "invoice_no": "INV-2024-001",
#   "date": "2024-05-14",
#   "amount": "1234.56",
#   "currency": "CNY",
#   "company": "某某科技有限公司"
# }
```

### 功能3: 文档分类

```python
doc_type = processor.classify_document(ocr_text)
print(doc_type)
# Output:
# {
#   "type": "invoice",
#   "confidence": "high"
# }
```

支持的类型：
- `invoice` - 发票
- `receipt` - 收据
- `waybill` - 运单
- `contract` - 合同
- `other` - 其他

### 功能4: 表格数据结构化

**输入**：混乱的表格OCR文本
```
商品名称 | 数量 | 单价 | 金额
螺丝刀 | 10 | 5.00 | 50.00
扳手 | 5 | 15.00 | 75.00
```

**LLM结构化**：
```python
table_data = processor.extract_table_data(table_text)
print(table_data)
# Output:
# [
#   {"name": "螺丝刀", "quantity": "10", "price": "5.00", "amount": "50.00"},
#   {"name": "扳手", "quantity": "5", "price": "15.00", "amount": "75.00"}
# ]
```

### 功能5: 文档摘要

```python
summary = processor.summarize_document(long_text, max_words=50)
print(summary)
# Output: 这是一张由某某公司开具的商业发票，日期为2024年5月14日，
#         包含办公用品采购，总金额1234.56元。
```

## 💻 Python API使用

### 基础用法

```python
from ocr_invoice_reader.utils.llm_processor import LLMProcessor, create_llm_processor

# 方式1: 直接创建
processor = LLMProcessor(model="qwen2.5:0.5b")

# 方式2: 带可用性检查
processor = create_llm_processor(model="qwen2.5:0.5b")
if processor is None:
    print("Ollama not available")
    exit(1)

# 使用
corrected = processor.correct_text("原始OCR文本")
fields = processor.extract_invoice_fields("发票文本")
```

### 集成到OCR流程

```python
from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer
from ocr_invoice_reader.utils.llm_processor import create_llm_processor

# OCR处理
analyzer = EnhancedStructureAnalyzer(use_gpu=False, lang='ch')
result = analyzer.analyze('invoice.jpg')

# 提取文本
ocr_text = '\n'.join([r.text for r in result['regions'] if r.text])

# LLM增强
llm = create_llm_processor()
if llm:
    # 纠错
    corrected = llm.correct_text(ocr_text)
    
    # 提取字段
    fields = llm.extract_invoice_fields(corrected)
    
    # 分类
    doc_type = llm.classify_document(ocr_text)
    
    print(f"Document type: {doc_type}")
    print(f"Extracted fields: {fields}")
```

### 一键增强

```python
from ocr_invoice_reader.utils.llm_processor import enhance_ocr_result

# 一键增强OCR结果
enhanced = enhance_ocr_result(ocr_text, model="qwen2.5:0.5b")

print(enhanced)
# {
#   "original_text": "...",
#   "corrected_text": "...",
#   "document_type": {"type": "invoice", "confidence": "high"},
#   "extracted_fields": {...},
#   "enhanced": True
# }
```

## 🔧 高级配置

### 自定义提示词

```python
# 自定义system prompt
system = "你是专门处理中文发票的AI助手..."
prompt = "请提取以下发票的关键信息：\n\n{text}"

response = processor._generate(prompt.format(text=text), system=system)
```

### 调整temperature

```python
# 更确定性（纠错、分类）
result = processor.correct_text(text)  # temperature=0.1

# 更创造性（摘要）
summary = processor.summarize_document(text)  # temperature=0.3
```

### 批量处理

```python
from concurrent.futures import ThreadPoolExecutor

texts = [page1_text, page2_text, page3_text]

with ThreadPoolExecutor(max_workers=3) as executor:
    corrected_texts = list(executor.map(processor.correct_text, texts))
```

## 📊 性能测试

### 处理时间（CPU: Intel i7）

| 操作 | 输入长度 | qwen2.5:0.5b | phi3:mini | 说明 |
|------|----------|--------------|-----------|------|
| 文本纠错 | 500字 | 2-3秒 | 5-8秒 | 常用 |
| 字段提取 | 1000字 | 3-5秒 | 8-12秒 | 中等 |
| 文档分类 | 500字 | 2秒 | 4-6秒 | 快速 |
| 表格提取 | 800字 | 3-4秒 | 7-10秒 | 中等 |
| 文档摘要 | 2000字 | 5-8秒 | 12-18秒 | 较慢 |

### 完整流程时间

**10页发票PDF**：

| 阶段 | 时间 | 说明 |
|------|------|------|
| OCR识别 | 65秒 | PaddleOCR (CPU) |
| LLM后处理 | 30秒 | qwen2.5:0.5b, 10页 × 3秒/页 |
| **总计** | **95秒** | 比单纯OCR慢46% |

**权衡**：
- ✅ 获得结构化数据和字段提取
- ✅ 自动纠错和分类
- ❌ 增加30-50%处理时间

## ⚙️ 配置建议

### 场景1: 快速处理（不需要理解）

```bash
# 不使用LLM
ocr-enhanced --image invoice.pdf --use-cpu
```

### 场景2: 需要字段提取

```bash
# 使用小模型
ocr-enhanced --image invoice.pdf --use-cpu --use-llm
```

### 场景3: 需要高质量理解

```bash
# 使用更大模型
ocr-enhanced --image invoice.pdf --use-cpu --use-llm --llm-model phi3:mini
```

### 场景4: 批量处理

```python
# 批量OCR，然后统一LLM处理（更快）
ocr_results = [process_page(p) for p in pages]  # 不用LLM

llm = create_llm_processor()
enhanced_results = [
    llm.extract_invoice_fields(r['text'])
    for r in ocr_results
]
```

## 🐛 故障排除

### 问题1: `Ollama service not available`

```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 启动Ollama（Windows）
# Ollama会自动在后台运行，检查任务管理器

# 启动Ollama（Linux/Mac）
ollama serve
```

### 问题2: `Model not found`

```bash
# 列出已安装模型
ollama list

# 下载模型
ollama pull qwen2.5:0.5b
```

### 问题3: LLM太慢

**解决方案**：
1. 使用更小的模型（qwen2.5:0.5b）
2. 限制输入文本长度
3. 只对关键页面使用LLM
4. 考虑批量处理

### 问题4: JSON解析失败

LLM有时返回非JSON格式。代码已处理：
```python
# 自动提取JSON
if '```json' in response:
    json_str = response.split('```json')[1].split('```')[0]
# 解析失败时返回raw_response
```

## 📝 最佳实践

### 1. 选择合适的模型

```python
# 小批量、快速响应 → qwen2.5:0.5b
# 大批量、高质量 → phi3:mini
# 平衡 → gemma2:2b
```

### 2. 限制输入长度

```python
# 避免传入过长文本
short_text = full_text[:2000]  # 限制2000字符
corrected = processor.correct_text(short_text)
```

### 3. 缓存结果

```python
# 相同文档不要重复处理
cache = {}
if text_hash not in cache:
    cache[text_hash] = processor.extract_invoice_fields(text)
```

### 4. 错误处理

```python
try:
    fields = processor.extract_invoice_fields(text)
except Exception as e:
    print(f"LLM failed: {e}")
    fields = {}  # 回退到空结果
```

## 🎯 实际应用示例

### 示例1: 发票批量处理

```python
from pathlib import Path
from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer
from ocr_invoice_reader.utils.llm_processor import create_llm_processor
import json

# 初始化
ocr = EnhancedStructureAnalyzer(use_gpu=False, lang='ch')
llm = create_llm_processor("qwen2.5:0.5b")

# 处理多个发票
invoice_files = Path("invoices/").glob("*.pdf")
results = []

for invoice_file in invoice_files:
    # OCR
    ocr_result = ocr.analyze(str(invoice_file))
    text = '\n'.join([r.text for r in ocr_result['regions'] if r.text])
    
    # LLM提取
    if llm:
        fields = llm.extract_invoice_fields(text)
        results.append({
            "file": invoice_file.name,
            "invoice_no": fields.get("invoice_no"),
            "amount": fields.get("amount"),
            "date": fields.get("date")
        })

# 保存结果
with open("extracted_invoices.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
```

### 示例2: 智能文档路由

```python
# 根据文档类型自动路由
def route_document(file_path):
    ocr = EnhancedStructureAnalyzer(use_gpu=False, lang='ch')
    llm = create_llm_processor()
    
    # OCR识别
    result = ocr.analyze(file_path)
    text = '\n'.join([r.text for r in result['regions'] if r.text])
    
    # 分类
    doc_type = llm.classify_document(text)
    
    # 路由
    if doc_type['type'] == 'invoice':
        # 发票处理流程
        fields = llm.extract_invoice_fields(text)
        save_to_database('invoices', fields)
    elif doc_type['type'] == 'waybill':
        # 运单处理流程
        process_waybill(text)
    else:
        # 其他文档
        archive_document(file_path)
```

## 📚 扩展阅读

- **Ollama官网**: https://ollama.ai
- **Qwen2.5模型**: https://ollama.ai/library/qwen2.5
- **Phi-3模型**: https://ollama.ai/library/phi3
- **PaddleOCR**: https://github.com/PaddlePaddle/PaddleOCR

---

**版本**: v2.3.0  
**最后更新**: 2026-05-14  
**维护者**: SyuuKasinn
