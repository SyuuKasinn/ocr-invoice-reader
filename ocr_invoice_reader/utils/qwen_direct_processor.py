"""
Direct Qwen LLM Processor - 直接使用transformers库，无需Ollama
支持GPU加速，性能更好
"""
import json
import torch
from typing import Dict, List, Optional, Any
from transformers import AutoModelForCausalLM, AutoTokenizer


class QwenDirectProcessor:
    """直接使用Qwen模型（通过transformers库）

    优势：
    - 无需Ollama，直接使用GPU
    - 更好的GPU利用率
    - 更灵活的配置
    - 支持量化（INT8, INT4）节省显存
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        device: str = "auto",
        quantization: Optional[str] = None,
        max_length: int = 2048
    ):
        """
        Args:
            model_name: HuggingFace模型名称
                - "Qwen/Qwen2.5-7B-Instruct" (推荐，6GB显存)
                - "Qwen/Qwen2.5-14B-Instruct" (高精度，12GB显存)
                - "Qwen/Qwen2.5-3B-Instruct" (小模型，3GB显存)
            device: 设备 ("auto", "cuda", "cpu")
            quantization: 量化方式 (None, "int8", "int4")
            max_length: 最大生成长度
        """
        self.model_name = model_name
        self.device = device
        self.quantization = quantization
        self.max_length = max_length

        print(f"Loading Qwen model: {model_name}")
        print(f"Device: {device}, Quantization: {quantization}")

        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True
        )

        # 配置量化
        model_kwargs = {"trust_remote_code": True}

        if quantization == "int8":
            model_kwargs["load_in_8bit"] = True
            model_kwargs["device_map"] = "auto"
        elif quantization == "int4":
            model_kwargs["load_in_4bit"] = True
            model_kwargs["device_map"] = "auto"
        elif device == "auto":
            model_kwargs["device_map"] = "auto"

        # 加载模型
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            **model_kwargs
        )

        # 设置评估模式
        self.model.eval()

        # 如果没有使用量化且指定了设备，移动模型
        if quantization is None and device not in ["auto", None]:
            self.model = self.model.to(device)

        print(f"✓ Model loaded successfully")

        # 打印GPU信息
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

    def _generate(self, prompt: str, system: str = None, temperature: float = 0.3) -> str:
        """调用Qwen生成文本"""
        # 构建消息
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # 格式化为模型输入
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize
        inputs = self.tokenizer([text], return_tensors="pt")

        # 移动到正确的设备
        if self.quantization is None:
            device = next(self.model.parameters()).device
            inputs = {k: v.to(device) for k, v in inputs.items()}

        # 生成
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_length,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9 if temperature > 0 else None,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # 解码
        response = self.tokenizer.decode(
            outputs[0][len(inputs["input_ids"][0]):],
            skip_special_tokens=True
        )

        return response.strip()

    def is_available(self) -> bool:
        """检查模型是否可用"""
        return self.model is not None

    def extract_invoice_fields(self, text: str) -> Dict[str, Any]:
        """从发票文本中提取结构化字段"""
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
        """文档分类"""
        system = """你是一个文档分类专家。
用户会给你文档OCR文本，请判断文档类型。
返回JSON格式：{"type": "类型", "confidence": "置信度(high/medium/low)"}"""

        prompt = f"""请判断以下文档的类型：

{text[:500]}

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

    def correct_text(self, text: str) -> str:
        """OCR文本纠错"""
        system = """你是一个OCR文本纠错专家。
用户会给你OCR识别的文本，可能包含识别错误。
请修正错误，保持原文格式，只返回修正后的文本，不要添加解释。"""

        prompt = f"""请修正以下OCR文本中的错误：

{text}

修正后的文本："""

        return self._generate(prompt, system, temperature=0.1)

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


def create_qwen_processor(
    model_size: str = "7b",
    use_gpu: bool = True,
    quantization: Optional[str] = None
) -> Optional[QwenDirectProcessor]:
    """创建Qwen处理器（带便捷配置）

    Args:
        model_size: 模型大小 ("3b", "7b", "14b")
        use_gpu: 是否使用GPU
        quantization: 量化方式 (None, "int8", "int4")

    Returns:
        QwenDirectProcessor实例
    """
    # 模型映射
    model_map = {
        "3b": "Qwen/Qwen2.5-3B-Instruct",
        "7b": "Qwen/Qwen2.5-7B-Instruct",
        "14b": "Qwen/Qwen2.5-14B-Instruct",
    }

    model_name = model_map.get(model_size.lower(), model_map["7b"])
    device = "auto" if use_gpu else "cpu"

    try:
        processor = QwenDirectProcessor(
            model_name=model_name,
            device=device,
            quantization=quantization
        )
        return processor
    except Exception as e:
        print(f"Failed to create Qwen processor: {e}")
        print("Please install required packages:")
        print("  pip install transformers torch accelerate")
        if quantization:
            print("  pip install bitsandbytes")
        return None


# 便捷函数
def enhance_ocr_result_qwen(text: str, model_size: str = "7b") -> Dict[str, Any]:
    """一键增强OCR结果（使用Qwen直接推理）

    Args:
        text: OCR识别的文本
        model_size: 模型大小 ("3b", "7b", "14b")

    Returns:
        增强后的结果字典
    """
    processor = create_qwen_processor(model_size=model_size)

    if processor is None:
        return {
            "original_text": text,
            "enhanced": False,
            "error": "Failed to create Qwen processor"
        }

    try:
        # 文档分类
        doc_type = processor.classify_document(text[:500])

        # 字段提取（如果是发票）
        fields = None
        if doc_type.get('type') == 'invoice':
            fields = processor.extract_invoice_fields(text[:1500])

        return {
            "original_text": text,
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


if __name__ == "__main__":
    # 测试代码
    print("Testing Qwen Direct Processor...")

    # 创建处理器
    processor = create_qwen_processor(
        model_size="7b",
        use_gpu=True,
        quantization="int4"  # 使用INT4量化节省显存
    )

    if processor:
        # 测试文本
        test_text = """
        发票号码: INV-2024-001
        日期: 2024-05-15
        金额: ¥1,234.56
        公司: 测试公司
        """

        print("\nTesting invoice extraction...")
        result = processor.extract_invoice_fields(test_text)
        print(json.dumps(result, ensure_ascii=False, indent=2))
