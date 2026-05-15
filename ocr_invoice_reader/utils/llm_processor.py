"""
LLM推理处理器 - 用于OCR结果的智能后处理
"""
import json
from typing import Dict, List, Optional, Any
import requests


class LLMProcessor:
    """本地LLM处理器（基于Ollama）

    用途：
    - OCR文本纠错
    - 信息提取和结构化
    - 内容理解和分类
    """

    def __init__(self, model: str = "qwen2.5:0.5b", base_url: str = "http://localhost:11434"):
        """
        Args:
            model: Ollama模型名称（推荐: qwen2.5:0.5b, phi3:mini）
            base_url: Ollama服务地址
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

    def is_available(self) -> bool:
        """检查Ollama服务是否可用"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def check_model(self) -> bool:
        """检查模型是否已下载"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(m['name'].startswith(self.model.split(':')[0]) for m in models)
            return False
        except:
            return False

    def _generate(self, prompt: str, system: str = None, temperature: float = 0.3) -> str:
        """调用Ollama生成文本"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }

        if system:
            payload["system"] = system

        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '').strip()
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")

    def correct_text(self, text: str) -> str:
        """OCR文本纠错

        修正OCR识别中的常见错误：
        - 字符混淆（0/O, 1/l/I）
        - 断字错误
        - 多余空格
        """
        system = """你是一个OCR文本纠错专家。
用户会给你OCR识别的文本，可能包含识别错误。
请修正错误，保持原文格式，只返回修正后的文本，不要添加解释。"""

        prompt = f"""请修正以下OCR文本中的错误：

{text}

修正后的文本："""

        return self._generate(prompt, system, temperature=0.1)

    def extract_invoice_fields(self, text: str) -> Dict[str, Any]:
        """从发票文本中提取结构化字段

        提取：
        - 发票号码
        - 日期
        - 金额
        - 公司名称
        - 商品明细
        """
        system = """你是一个发票信息提取专家。
用户会给你发票OCR文本，请提取关键信息。
以JSON格式返回，包含：invoice_no, date, amount, company, items等字段。
如果某个字段不存在，使用null。"""

        prompt = f"""请从以下发票文本中提取信息：

{text}

以JSON格式返回提取结果："""

        response = self._generate(prompt, system, temperature=0.2)

        # 尝试解析JSON
        try:
            # 提取JSON部分（可能在markdown代码块中）
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except:
            return {"raw_response": response, "error": "Failed to parse JSON"}

    def classify_document(self, text: str) -> Dict[str, str]:
        """文档分类

        识别文档类型：
        - invoice（发票）
        - receipt（收据）
        - waybill（运单）
        - contract（合同）
        - other（其他）
        """
        system = """你是一个文档分类专家。
用户会给你文档OCR文本，请判断文档类型。
返回JSON格式：{"type": "类型", "confidence": "置信度(high/medium/low)"}"""

        prompt = f"""请判断以下文档的类型：

{' '.join(text.split())[:2000]}

返回JSON格式分类结果："""

        response = self._generate(prompt, system, temperature=0.1)

        try:
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            else:
                json_str = response.strip()

            return json.loads(json_str)
        except:
            return {"type": "unknown", "confidence": "low", "raw_response": response}

    def summarize_document(self, text: str, max_words: int = 100) -> str:
        """文档摘要"""
        system = f"""你是一个文档摘要专家。
用户会给你文档文本，请生成简洁的摘要（{max_words}字以内）。
只返回摘要内容，不要添加其他说明。"""

        prompt = f"""请为以下文档生成摘要：

{text}

摘要："""

        return self._generate(prompt, system, temperature=0.3)

    def extract_table_data(self, table_text: str) -> List[Dict[str, str]]:
        """从表格文本中提取结构化数据"""
        system = """你是一个表格数据提取专家。
用户会给你表格的OCR文本（可能格式混乱），请提取表格数据。
以JSON数组格式返回，每行是一个对象。"""

        prompt = f"""请从以下表格文本中提取数据：

{table_text}

以JSON数组格式返回："""

        response = self._generate(prompt, system, temperature=0.2)

        try:
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)
            return data if isinstance(data, list) else [data]
        except:
            return [{"error": "Failed to parse table", "raw_response": response}]

    def fix_ocr_errors(self, text: str, context: str = "invoice") -> str:
        """针对特定上下文修正OCR错误

        Args:
            text: OCR文本
            context: 上下文类型（invoice, waybill, etc.）
        """
        context_prompts = {
            "invoice": "这是一张发票文本，常见字段包括：发票号、日期、金额、公司名称、税号等。",
            "waybill": "这是一张运单文本，常见字段包括：运单号、收发货人、地址、重量等。",
            "receipt": "这是一张收据文本，常见字段包括：商品名称、数量、单价、总价等。",
        }

        context_hint = context_prompts.get(context, "这是一份商业文档。")

        system = f"""你是OCR文本纠错专家。{context_hint}
请修正OCR识别错误，保持原文格式，只返回修正后的文本。"""

        prompt = f"""请修正以下文本中的OCR错误：

{text}

修正后的文本："""

        return self._generate(prompt, system, temperature=0.1)


def create_llm_processor(model: str = "qwen2.5:0.5b") -> Optional[LLMProcessor]:
    """创建LLM处理器（带可用性检查）

    Args:
        model: 模型名称

    Returns:
        LLMProcessor实例，如果不可用则返回None
    """
    processor = LLMProcessor(model=model)

    if not processor.is_available():
        print("WARNING: Ollama service not available")
        print("Install: https://ollama.ai/download")
        return None

    if not processor.check_model():
        print(f"WARNING: Model '{model}' not found")
        print(f"Install: ollama pull {model}")
        return None

    return processor


# 便捷函数
def enhance_ocr_result(text: str, model: str = "qwen2.5:0.5b") -> Dict[str, Any]:
    """一键增强OCR结果

    包括：
    - 文本纠错
    - 字段提取
    - 文档分类

    Args:
        text: OCR识别的文本
        model: LLM模型名称

    Returns:
        增强后的结果字典
    """
    processor = create_llm_processor(model)

    if processor is None:
        return {
            "original_text": text,
            "enhanced": False,
            "error": "LLM not available"
        }

    try:
        # 文本纠错
        corrected = processor.correct_text(' '.join(text.split())[:2000])  # 限制长度避免太慢

        # 文档分类
        doc_type = processor.classify_document(' '.join(text.split())[:2000])

        # 字段提取（如果是发票）
        fields = None
        if doc_type.get('type') == 'invoice':
            fields = processor.extract_invoice_fields(text[:3000])

        return {
            "original_text": text,
            "corrected_text": corrected,
            "document_type": doc_type,
            "extracted_fields": fields,
            "enhanced": True
        }

    except Exception as e:
        return {
            "original_text": text,
            "enhanced": False,
            "error": str(e)
        }
