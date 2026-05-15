# Quick Start: Hybrid Invoice Extraction

## 简介

v2.3.0 引入了**混合发票提取架构**，结合 LLM 的灵活性和正则表达式的可靠性。

## 核心优势

### 问题：纯正则表达式方法的困境

```
发票格式A → 添加 10 个正则模式
发票格式B → 再添加 8 个模式  
发票格式C → 再添加 12 个模式
...
格式越来越多 → invoice_extractor_v2.py 已有 500+ 行正则 😱
```

**维护问题**：
- ❌ 每种新格式都要分析、测试、调试
- ❌ 模式冲突（格式A的模式误匹配格式B）
- ❌ 优先级混乱（需要精心排列）
- ❌ 无法泛化（遇到全新格式就失效）

### 解决方案：LLM-First 混合架构

```
OCR 文本
   ↓
1️⃣ LLM 提取（主要方法）
   - 使用结构化提示词
   - 自动适应新格式
   - 多语言支持
   ↓
   验证结果质量
   ↓
   ✅ 通过？→ 使用 LLM 结果
   ↓
   ❌ 失败？
   ↓
2️⃣ 正则兜底（备用方法）
   - 使用 InvoiceExtractorV2
   - 可靠处理标准格式
   ↓
3️⃣ 返回最佳结果
```

## 快速开始

### 1. 基础使用

```bash
# 自动混合提取（开启 --use-llm 即可）
ocr-enhanced --image invoice.pdf --use-llm
```

系统会：
1. OCR 提取文本
2. 尝试 LLM 提取
3. 验证结果
4. 失败时回退到正则
5. 保存结果并标记 `extraction_method`

### 2. 查看结果

```bash
# 查看单页提取结果
cat results/20260515_123456/invoice_page_0001_llm.json
```

**输出示例**：

```json
{
  "page": 1,
  "source_file": "invoice_001",
  "extraction_method": "llm",  // 表示 LLM 提取成功
  "extracted_fields": {
    "invoice_number": "NCY250924",
    "invoice_date": "2025-09-24",
    "tracking_number": "820111868365",
    "total_amount": 135600.0,
    "currency": "JPY",
    "shipper_name": "DALIAN LONG SHENG WOOD INDUSTRY CO.LTD",
    "consignee_name": "MINORU SANGYO CORPORATION"
  }
}
```

如果是 `"extraction_method": "regex_fallback"`，表示 LLM 验证失败，使用了正则兜底。

### 3. 查看汇总统计

```bash
# 查看所有页面的提取统计
cat results/20260515_123456/invoices.json
```

**汇总示例**：

```json
{
  "summary": {
    "with_invoice_number": 8,
    "with_company": 8,
    "with_amount": 7,
    "llm_extracted": 6,      // 6 页由 LLM 成功提取
    "regex_fallback": 2      // 2 页回退到正则
  }
}
```

## 使用场景

### ✅ 推荐使用 LLM 混合模式

- 处理多样化的发票格式
- 遇到新的发票布局
- 需要快速适应而不修改代码
- 准确性比速度更重要
- 文档有复杂的多语言内容

**命令**：
```bash
ocr-enhanced --image diverse_invoices.pdf --use-llm
```

### ✅ 推荐使用纯正则模式

- 大批量处理标准格式
- 速度至关重要
- 文档遵循已知模式
- 在低资源系统上运行
- 需要最大一致性

**命令**：
```bash
# 不加 --use-llm 即为纯正则模式
ocr-enhanced --image standard_invoices.pdf
```

## 工作流程建议

### 第一次处理新格式

```bash
# 1. 使用混合模式测试
ocr-enhanced --image new_format.pdf --use-llm

# 2. 查看提取方法
cat results/*/new_format_invoices.json | grep extraction_method

# 3. 分析结果
# - 如果大部分是 "llm" → 格式多样，保持混合模式
# - 如果大部分是 "regex_fallback" → 格式标准，可用纯正则
```

### 性能对比

| 方法 | 速度 | 准确率 | 灵活性 | 资源消耗 |
|------|------|--------|--------|----------|
| LLM | 20-60秒/页 | 90-95% | ⭐⭐⭐⭐⭐ | GPU 推荐 |
| 正则 | <1秒/页 | 已知格式95%<br>新格式0% | ⭐⭐ | 最小 |
| 混合 | 智能选择 | 最佳 | ⭐⭐⭐⭐⭐ | 优化 |

## 自定义

### 调整 LLM 模型

```bash
# 使用更小的模型（更快，稍低准确率）
ocr-enhanced --image invoice.pdf --use-llm --llm-model 7b

# 使用默认模型（平衡）
ocr-enhanced --image invoice.pdf --use-llm --llm-model 14b

# 使用更大的模型（如果有，更慢但更准确）
ocr-enhanced --image invoice.pdf --use-llm --llm-model 14b
```

### 修改提示词

编辑 `ocr_invoice_reader/utils/llm_invoice_extractor.py`:

```python
class LLMInvoiceExtractor:
    def __init__(self, llm_processor=None):
        self.extraction_prompt_template = """
        You are an expert invoice extraction system...
        
        # 在这里修改：
        # - 添加新字段
        # - 更改提取规则
        # - 支持新文档类型
        # - 为特定格式提高准确率
        """
```

### 调整验证规则

编辑 `validate_extraction_result()`:

```python
def validate_extraction_result(data: Dict) -> tuple[bool, list[str]]:
    issues = []
    
    # 添加自定义验证规则
    # 例如：要求必填字段
    if not data.get('invoice_number') and not data.get('tracking_number'):
        issues.append("必须有 invoice_number 或 tracking_number")
    
    # 例如：验证金额范围
    if data.get('total_amount'):
        if data['total_amount'] < 0:
            issues.append("金额不能为负数")
        if data['total_amount'] > 10000000:
            issues.append("金额过大，可能有误")
    
    return len(issues) == 0, issues
```

## 常见问题

### Q: 为什么有些页面使用 regex_fallback？

**A**: 可能的原因：
1. LLM 返回的 JSON 格式无效
2. 验证规则未通过（日期格式、金额等）
3. OCR 文本质量太差
4. 提示词与文档格式不匹配

**解决方法**：
- 查看控制台输出的验证消息
- 检查 `llm_validation_issues` 字段
- 用已知好文档测试
- 如果验证规则太严格，可以调整

### Q: LLM 提取很慢怎么办？

**A**: 这是正常的（14B 模型每页 20-60 秒）

**加速方法**：
1. 使用更小的模型：`--llm-model 7b`
2. 使用 GPU（如果支持）
3. 对标准格式批处理，不使用 `--use-llm`
4. 让正则处理标准格式（它们又快又准）

### Q: LLM 会不会产生幻觉数据？

**A**: 有可能，但混合架构有多层保护：

**保护机制**：
1. ✅ 验证层（检查格式和逻辑）
2. ✅ 正则兜底（验证失败时）
3. ✅ 明确的 extraction_method 标记
4. ✅ 可选的人工复核

**建议**：
- 对关键数据添加更严格的验证
- 使用更大的模型（14B 或更高）
- 在提示词中添加具体约束
- 添加后处理检查
- 与正则结果交叉验证

### Q: 控制台总是显示 "LLM extraction validation failed"？

**A**: 检查验证规则是否太严格：

```python
# 查看具体失败原因
print(f"Validation issues: {issues}")

# 如果是日期格式问题
# 可能需要在 _normalize_date() 中添加更多格式支持

# 如果是必填字段问题
# 可能需要调整 validate_extraction_result() 的要求
```

## 实际效果

### 测试结果（8 页发票）

**使用 v2.2.6（纯正则）**：
```
✓ 准确率：~95%
✓ 速度：<8 秒总计
❌ 新格式：需要添加新模式
❌ 维护：每种格式都要调试
```

**使用 v2.3.0（混合）**：
```
✓ 准确率：~95%
✓ LLM 成功：6/8 页
✓ 正则兜底：2/8 页
✓ 新格式：自动适应
✓ 维护：只需调整提示词
⚠ 速度：稍慢（LLM 需要时间）
```

## 最佳实践

### 1️⃣ 初次使用

```bash
# 先用混合模式测试一批文档
ocr-enhanced --image test_batch/*.pdf --use-llm

# 分析提取方法分布
# 如果 80%+ 是 regex_fallback → 考虑纯正则
# 如果 80%+ 是 llm → 需要混合模式
```

### 2️⃣ 生产环境

```bash
# 多样化格式 → 使用混合
ocr-enhanced --image diverse/*.pdf --use-llm

# 标准格式 → 纯正则（更快）
ocr-enhanced --image standard/*.pdf

# 新格式 → 混合（自动适应）
ocr-enhanced --image new_format/*.pdf --use-llm
```

### 3️⃣ 持续优化

1. 定期检查 `extraction_method` 分布
2. 对失败案例调整提示词
3. 对成功的标准格式添加正则模式（提速）
4. 新文档类型时重新测试

## 下一步

- 阅读完整文档：[LLM_HYBRID_EXTRACTION.md](LLM_HYBRID_EXTRACTION.md)
- 查看正则模式：[EXTRACTOR_V2_IMPROVEMENTS.md](EXTRACTOR_V2_IMPROVEMENTS.md)
- 了解发票提取：[INVOICE_EXTRACTION.md](INVOICE_EXTRACTION.md)

---

**版本**: 2.3.0  
**更新日期**: 2026-05-15  
**许可证**: MIT
