# 项目重构方案：从OCR到智能文档信息提取

## 当前问题分析

### 现状
- ✅ 能识别文字
- ❌ 结果散乱（272个碎片）
- ❌ 无结构化信息
- ❌ 无法自动化处理
- ❌ 不知道哪个是发票号、金额、日期等

### 用户真实需求
**目标**：自动识别发票/单据，提取结构化信息用于后续处理

**需要输出**：
```json
{
  "invoice_number": "HTL506539397733",
  "date": "2026-05-12",
  "sender": {
    "company": "SEKI AOI TECHNO CO., LTD",
    "address": "...",
    "phone": "..."
  },
  "receiver": {
    "company": "...",
    "address": "..."
  },
  "items": [
    {"description": "...", "quantity": 10, "price": 100, "amount": 1000}
  ],
  "total_amount": 1000,
  "currency": "JPY"
}
```

而不是：
```json
{
  "results": [
    {"text": "HTL", "confidence": 0.98},
    {"text": "506539397733", "confidence": 0.95},
    {"text": "SEKI", "confidence": 0.92},
    // ... 269 more fragments
  ]
}
```

## 项目重新定位

### 方向1：文档理解系统（推荐）
**定位**：Invoice Information Extraction System（发票信息提取系统）

**核心能力**：
1. 文档分类（发票、运单、合同等）
2. 关键信息提取（KIE: Key Information Extraction）
3. 表格识别与提取
4. 结构化输出

### 方向2：通用文档OCR（当前）
**定位**：只做OCR识别
**问题**：无法满足"自动识别"需求

## 解决方案对比

### 方案A：PaddleOCR PP-Structure（最佳性价比）✅

**技术栈**：
- PP-Structure：文档结构分析
- PP-Layout：版面分析
- Table Recognition：表格识别
- KIE：关键信息提取

**优势**：
- ✅ 免费开源
- ✅ 中文文档完善
- ✅ CPU可运行
- ✅ 已经在用PaddleOCR，无需重新学习
- ✅ 支持自定义训练

**实现难度**：⭐⭐（中等）

**代码示例**：
```python
from paddleocr import PPStructure

# 初始化文档结构分析
table_engine = PPStructure(
    layout=True,           # 版面分析
    table=True,           # 表格识别
    ocr=True,             # OCR识别
    show_log=True
)

# 分析文档
result = table_engine(img_path)

# 输出结构化结果
for line in result:
    if line['type'] == 'table':
        # 表格数据
        print(line['res'])  # HTML格式的表格
    elif line['type'] == 'text':
        # 普通文本
        print(line['res'])
```

**实际输出**：
```python
[
  {
    'type': 'table',
    'bbox': [100, 200, 500, 600],
    'res': '<html><table><tr><td>Item</td><td>Price</td></tr>...</table></html>',
    'img': table_image
  },
  {
    'type': 'text',
    'bbox': [50, 50, 300, 100],
    'res': [('Invoice Number:', 0.98), ('HTL506539397733', 0.99)]
  }
]
```

### 方案B：Donut + 自定义训练（最高准确度）

**技术栈**：
- Donut：端到端文档理解
- 自定义训练：针对您的发票格式

**优势**：
- ✅ 最高准确度（SOTA）
- ✅ 直接输出结构化JSON
- ✅ 不需要OCR后处理

**劣势**：
- ❌ 需要GPU（至少8GB显存）
- ❌ 需要标注数据训练（50-100张发票）
- ❌ 推理较慢（3-5秒/页）

**实现难度**：⭐⭐⭐⭐（困难）

### 方案C：LLM智能提取（最简单）✅

**技术栈**：
- Claude API / GPT-4 Vision
- OCR结果 + 图片 → LLM提取

**优势**：
- ✅ 无需训练
- ✅ 实现简单（1天）
- ✅ 准确度高
- ✅ 灵活（可处理任何格式）

**劣势**：
- ❌ 需要付费（$0.01-0.05/页）
- ❌ 需要网络
- ❌ 处理速度慢（2-3秒/页）

**实现难度**：⭐（简单）

**代码示例**：
```python
import anthropic
import base64

def extract_invoice_info(image_path):
    client = anthropic.Anthropic(api_key="your-key")
    
    # 读取图片
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode()
    
    # 调用Claude
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": """Extract structured information from this invoice/waybill.

Return JSON format:
{
  "document_type": "invoice/waybill/contract",
  "invoice_number": "...",
  "date": "YYYY-MM-DD",
  "sender": {
    "company": "...",
    "address": "...",
    "phone": "..."
  },
  "receiver": {
    "company": "...",
    "address": "...",
    "phone": "..."
  },
  "items": [
    {"description": "...", "quantity": 0, "unit_price": 0, "amount": 0}
  ],
  "total_amount": 0,
  "currency": "JPY/USD/CNY",
  "notes": "..."
}

Return only valid JSON, no explanation."""
                }
            ]
        }]
    )
    
    return json.loads(message.content[0].text)
```

**实际效果**：
```python
result = extract_invoice_info("invoice.jpg")
print(result)
# {
#   "document_type": "waybill",
#   "invoice_number": "HTL506539397733",
#   "sender": {
#     "company": "SEKI AOI TECHNO CO., LTD",
#     "address": "..."
#   },
#   ...
# }
```

### 方案D：规则+模板匹配（最快速）

**适用场景**：固定格式发票（如：同一供应商的发票格式相同）

**技术栈**：
- 正则表达式
- 位置匹配
- 关键词提取

**优势**：
- ✅ 速度快（<0.5秒）
- ✅ 免费
- ✅ 可控性强

**劣势**：
- ❌ 只能处理固定格式
- ❌ 格式变化需重新配置
- ❌ 维护成本高

**实现难度**：⭐⭐⭐（中高）

## 推荐方案组合

### 🎯 推荐配置：PP-Structure + LLM混合模式

```
输入文档
    ↓
[PP-Structure 文档分析]
    ↓
├─ 版面分析（标题、文本块、表格）
├─ 表格识别（结构化表格数据）
└─ OCR识别（文字内容）
    ↓
[规则提取]（快速模式）
    ↓
提取明显字段（发票号、日期等）
    ↓
[LLM补充]（可选，按需触发）
    ↓
处理复杂/低置信度字段
    ↓
[结构化输出]
    ↓
JSON/Excel/Database
```

**优势**：
- 速度快（PP-Structure）
- 成本低（规则优先）
- 准确度高（LLM兜底）
- 灵活性强（支持多种格式）

## 具体实施方案

### 阶段1：快速实现LLM方案（1-2天）✅

**为什么先做这个**：
- 最快验证可行性
- 了解实际需求
- 积累数据样本

**实现步骤**：

1. 安装依赖
```bash
pip install anthropic
```

2. 创建智能提取器
```bash
# 我将创建 intelligent_extractor.py
```

3. 测试并收集数据
```bash
python intelligent_extractor.py --image invoice.jpg --output result.json
```

4. 分析结果，确定常见字段

### 阶段2：集成PP-Structure（3-5天）

**目标**：减少对LLM依赖，降低成本

**实现步骤**：

1. 安装PP-Structure
```bash
pip install "paddleocr>=2.7"
pip install paddlehub
```

2. 集成版面分析
```python
# 将创建 structure_analyzer.py
```

3. 表格识别优化

4. 建立规则库

### 阶段3：优化与自动化（持续）

1. 建立字段映射规则
2. 添加数据验证
3. 批量处理优化
4. 错误处理与人工审核

## 代码实现方案

### 新的项目结构

```
ocr-invoice-reader/
├── core/
│   ├── ocr_engine.py          # 基础OCR（保留）
│   ├── structure_analyzer.py  # PP-Structure集成
│   ├── intelligent_extractor.py # LLM提取器
│   ├── field_extractor.py     # 规则提取器
│   └── table_parser.py        # 表格解析器
├── models/
│   ├── invoice.py             # 发票数据模型
│   ├── waybill.py             # 运单数据模型
│   └── base.py                # 基础模型
├── extractors/
│   ├── invoice_extractor.py   # 发票专用提取器
│   ├── waybill_extractor.py   # 运单专用提取器
│   └── generic_extractor.py   # 通用提取器
├── utils/
│   ├── validator.py           # 数据验证
│   ├── formatter.py           # 格式化输出
│   └── postprocessor.py       # 后处理
├── config/
│   ├── field_mapping.json     # 字段映射配置
│   └── extraction_rules.json  # 提取规则
├── main.py                     # 新的主程序
└── ocr_reader.py              # 保留旧版本
```

### 核心数据模型

```python
# models/invoice.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class Address(BaseModel):
    company: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    contact: Optional[str] = None

class InvoiceItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None

class Invoice(BaseModel):
    # 文档类型
    document_type: str = Field(..., description="invoice/waybill/contract")
    
    # 基础信息
    invoice_number: Optional[str] = None
    date: Optional[date] = None
    
    # 发送方
    sender: Optional[Address] = None
    
    # 接收方
    receiver: Optional[Address] = None
    
    # 商品/服务
    items: List[InvoiceItem] = []
    
    # 金额
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total_amount: Optional[float] = None
    currency: str = "JPY"
    
    # 备注
    notes: Optional[str] = None
    
    # 元数据
    confidence: float = 0.0
    extraction_method: str = "unknown"  # llm/rule/hybrid
    
    def to_dict(self):
        return self.model_dump()
    
    def to_json(self):
        return self.model_dump_json(indent=2)
```

### 智能提取器实现

```python
# core/intelligent_extractor.py
import anthropic
import base64
import json
from pathlib import Path
from models.invoice import Invoice

class IntelligentExtractor:
    """使用LLM进行智能信息提取"""
    
    def __init__(self, api_key: str = None, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def extract(self, image_path: str, document_type: str = "auto") -> Invoice:
        """
        从图片中提取结构化信息
        
        Args:
            image_path: 图片路径
            document_type: 文档类型（auto/invoice/waybill/contract）
        
        Returns:
            Invoice对象
        """
        # 读取图片
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        # 确定文件类型
        ext = Path(image_path).suffix.lower()
        media_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp'
        }.get(ext, 'image/jpeg')
        
        # 构建提示
        prompt = self._build_prompt(document_type)
        
        # 调用API
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )
            
            # 解析结果
            result_text = message.content[0].text
            
            # 提取JSON（处理markdown代码块）
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result_dict = json.loads(result_text)
            
            # 转换为Invoice对象
            invoice = Invoice(**result_dict)
            invoice.extraction_method = "llm"
            invoice.confidence = 0.9  # LLM结果默认高置信度
            
            return invoice
            
        except Exception as e:
            print(f"提取失败: {e}")
            # 返回空Invoice
            return Invoice(
                document_type="unknown",
                extraction_method="llm_failed",
                confidence=0.0
            )
    
    def _build_prompt(self, document_type: str) -> str:
        """构建提示词"""
        base_prompt = """Analyze this document and extract structured information.

This appears to be a business document (invoice, waybill, or contract). Please extract all relevant information.

Return ONLY valid JSON in this exact format:
{
  "document_type": "invoice|waybill|contract|other",
  "invoice_number": "document number or tracking number",
  "date": "YYYY-MM-DD format",
  "sender": {
    "company": "company name",
    "address": "full address",
    "phone": "phone number",
    "contact": "contact person"
  },
  "receiver": {
    "company": "company name",
    "address": "full address",
    "phone": "phone number",
    "contact": "contact person"
  },
  "items": [
    {
      "description": "item or service description",
      "quantity": 0.0,
      "unit_price": 0.0,
      "amount": 0.0
    }
  ],
  "subtotal": 0.0,
  "tax": 0.0,
  "total_amount": 0.0,
  "currency": "JPY|USD|CNY|EUR",
  "notes": "any additional notes or remarks"
}

Rules:
- Use null for missing fields
- Numbers should be float (not string)
- Date must be YYYY-MM-DD or null
- Extract all table items if present
- Keep original language for text fields
- Return ONLY JSON, no explanation

JSON:"""
        
        return base_prompt
    
    def batch_extract(self, image_paths: List[str], output_dir: str = "extracted_data"):
        """批量提取"""
        Path(output_dir).mkdir(exist_ok=True)
        
        results = []
        for image_path in image_paths:
            print(f"处理: {image_path}")
            invoice = self.extract(image_path)
            
            # 保存结果
            output_path = Path(output_dir) / f"{Path(image_path).stem}.json"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(invoice.to_json())
            
            results.append({
                'image': image_path,
                'output': str(output_path),
                'success': invoice.extraction_method != "llm_failed"
            })
        
        return results
```

### 主程序示例

```python
# main.py
import argparse
from core.intelligent_extractor import IntelligentExtractor
from models.invoice import Invoice
import json

def main():
    parser = argparse.ArgumentParser(description="Invoice Information Extraction System")
    parser.add_argument('--image', type=str, help="Input image path")
    parser.add_argument('--input_dir', type=str, help="Input directory")
    parser.add_argument('--output', type=str, default="extracted.json", help="Output JSON path")
    parser.add_argument('--api_key', type=str, help="Claude API key")
    parser.add_argument('--method', choices=['llm', 'structure', 'hybrid'], default='llm')
    
    args = parser.parse_args()
    
    if args.method == 'llm':
        # 使用LLM提取
        extractor = IntelligentExtractor(api_key=args.api_key)
        
        if args.image:
            print(f"提取信息: {args.image}")
            invoice = extractor.extract(args.image)
            
            # 打印结果
            print("\n" + "="*50)
            print("提取结果：")
            print("="*50)
            print(invoice.to_json())
            
            # 保存结果
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(invoice.to_json())
            
            print(f"\n结果已保存到: {args.output}")
        
        elif args.input_dir:
            # 批量处理
            from pathlib import Path
            images = list(Path(args.input_dir).glob("*.jpg")) + \
                    list(Path(args.input_dir).glob("*.png"))
            
            results = extractor.batch_extract([str(p) for p in images])
            print(f"\n处理完成: {len(results)} 个文件")
            
            # 生成汇总
            summary = {
                'total': len(results),
                'success': sum(1 for r in results if r['success']),
                'failed': sum(1 for r in results if not r['success']),
                'results': results
            }
            
            with open('batch_summary.json', 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"成功: {summary['success']}, 失败: {summary['failed']}")

if __name__ == "__main__":
    main()
```

## 使用示例

### 单张提取
```bash
python main.py --image invoice.jpg --output result.json --api_key sk-ant-xxx
```

### 批量提取
```bash
python main.py --input_dir invoices/ --api_key sk-ant-xxx
```

### 输出示例
```json
{
  "document_type": "waybill",
  "invoice_number": "HTL506539397733",
  "date": "2026-05-12",
  "sender": {
    "company": "SEKI AOI TECHNO CO., LTD",
    "address": "WUXI, JIANGSU, CHINA",
    "phone": null,
    "contact": null
  },
  "receiver": {
    "company": "ZAZA SYOUGI",
    "address": "GIFU KURODA, KOHTA-CHO, INAZAWA-GUN, AICHI, JAPAN",
    "phone": null,
    "contact": null
  },
  "items": [],
  "subtotal": null,
  "tax": null,
  "total_amount": null,
  "currency": "JPY",
  "notes": "International Express Waybill",
  "confidence": 0.9,
  "extraction_method": "llm"
}
```

## 下一步建议

### 立即行动（今天）：
1. ✅ **验证LLM方案可行性**
   - 用3-5张发票测试
   - 确认提取准确度
   - 评估成本（每张约$0.02-0.05）

### 短期（本周）：
2. **建立数据模型**
   - 确定需要提取的所有字段
   - 创建验证规则
   - 设计输出格式

3. **优化提示词**
   - 针对您的具体文档类型
   - 添加示例
   - 提高准确率

### 中期（2-4周）：
4. **集成PP-Structure**
   - 减少LLM调用
   - 降低成本
   - 提高速度

5. **建立规则库**
   - 常见字段模式
   - 位置规则
   - 格式验证

## 总结

**当前项目问题**：只做OCR，输出散乱，无法自动化

**解决方案**：重新定位为"文档信息提取系统"

**推荐路径**：
1. 快速实现LLM方案（验证可行性）
2. 集成PP-Structure（降低成本）
3. 建立规则库（提高速度）
4. 混合模式（最佳平衡）

**预期效果**：
- 从272个文本片段 → 结构化JSON
- 从人工整理 → 自动提取
- 从不可用 → 可编程处理

**需要您决定**：
1. 是否接受LLM方案（需要API费用）
2. 主要处理什么类型文档（发票/运单/合同）
3. 需要提取哪些字段
4. 准确度要求（90%/95%/99%）

我可以立即开始实现LLM方案，或者先实现免费的PP-Structure方案。您希望先尝试哪个？
