"""
LLM Factory - 统一的LLM处理器工厂
支持多种后端：Qwen Direct（推荐）、Ollama、API等
"""
import os
from typing import Optional, Literal

LLMBackend = Literal["qwen_direct", "ollama", "auto"]


class LLMFactory:
    """LLM处理器工厂

    根据环境和配置自动选择最佳的LLM后端
    """

    @staticmethod
    def create_processor(
        model: str = "7b",
        backend: LLMBackend = "auto",
        use_gpu: bool = True,
        quantization: Optional[str] = "int4",
        **kwargs
    ):
        """创建LLM处理器

        Args:
            model: 模型名称或大小
                - 对于qwen_direct: "3b", "7b", "14b"
                - 对于ollama: "qwen2.5:7b", "qwen2.5:14b"
            backend: 后端选择
                - "auto": 自动选择（优先qwen_direct）
                - "qwen_direct": 直接使用transformers
                - "ollama": 使用Ollama服务
            use_gpu: 是否使用GPU
            quantization: 量化方式 (None, "int4", "int8")，仅qwen_direct有效
            **kwargs: 其他参数

        Returns:
            LLM处理器实例
        """

        if backend == "auto":
            # 自动选择：优先qwen_direct
            try:
                return LLMFactory._create_qwen_direct(model, use_gpu, quantization)
            except Exception as e:
                print(f"⚠ Qwen Direct not available: {e}")
                print("Falling back to Ollama...")
                return LLMFactory._create_ollama(model, **kwargs)

        elif backend == "qwen_direct":
            return LLMFactory._create_qwen_direct(model, use_gpu, quantization)

        elif backend == "ollama":
            return LLMFactory._create_ollama(model, **kwargs)

        else:
            raise ValueError(f"Unknown backend: {backend}")

    @staticmethod
    def _create_qwen_direct(model: str, use_gpu: bool, quantization: Optional[str]):
        """创建Qwen Direct处理器"""
        from ocr_invoice_reader.utils.qwen_direct_processor import create_qwen_processor

        # 标准化模型名称
        if model in ["3b", "7b", "14b"]:
            model_size = model
        elif "3b" in model.lower():
            model_size = "3b"
        elif "7b" in model.lower():
            model_size = "7b"
        elif "14b" in model.lower():
            model_size = "14b"
        else:
            print(f"⚠ Unknown model size '{model}', defaulting to 7b")
            model_size = "7b"

        print(f"Creating Qwen Direct processor: {model_size} (quantization: {quantization})")

        processor = create_qwen_processor(
            model_size=model_size,
            use_gpu=use_gpu,
            quantization=quantization
        )

        if processor is None:
            raise RuntimeError("Failed to create Qwen Direct processor")

        return processor

    @staticmethod
    def _create_ollama(model: str, base_url: str = "http://localhost:11434", timeout: int = None):
        """创建Ollama处理器"""
        from ocr_invoice_reader.utils.llm_processor import LLMProcessor

        # 标准化模型名称
        if model in ["3b", "7b", "14b"]:
            model = f"qwen2.5:{model}"

        print(f"Creating Ollama processor: {model}")

        processor = LLMProcessor(
            model=model,
            base_url=base_url,
            timeout=timeout
        )

        # 检查可用性
        if not processor.is_available():
            raise RuntimeError("Ollama service not available")

        if not processor.check_model():
            raise RuntimeError(f"Model {model} not found in Ollama")

        return processor

    @staticmethod
    def is_qwen_direct_available() -> bool:
        """检查Qwen Direct是否可用"""
        try:
            import torch
            import transformers
            return torch.cuda.is_available()  # 需要GPU
        except ImportError:
            return False

    @staticmethod
    def is_ollama_available() -> bool:
        """检查Ollama是否可用"""
        try:
            from ocr_invoice_reader.utils.llm_processor import LLMProcessor
            processor = LLMProcessor()
            return processor.is_available()
        except:
            return False

    @staticmethod
    def get_recommended_backend() -> LLMBackend:
        """获取推荐的后端"""
        if LLMFactory.is_qwen_direct_available():
            return "qwen_direct"
        elif LLMFactory.is_ollama_available():
            return "ollama"
        else:
            return "auto"  # 让create_processor自动处理错误

    @staticmethod
    def print_status():
        """打印可用后端状态"""
        print("\n" + "="*60)
        print("LLM Backend Status")
        print("="*60)

        # Qwen Direct
        qwen_available = LLMFactory.is_qwen_direct_available()
        print(f"Qwen Direct: {'✓ Available' if qwen_available else '✗ Not available'}")
        if qwen_available:
            import torch
            print(f"  - GPU: {torch.cuda.get_device_name(0)}")
            print(f"  - VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

        # Ollama
        ollama_available = LLMFactory.is_ollama_available()
        print(f"Ollama: {'✓ Available' if ollama_available else '✗ Not available'}")

        # 推荐
        recommended = LLMFactory.get_recommended_backend()
        print(f"\nRecommended: {recommended}")
        print("="*60 + "\n")


def create_llm_processor(
    model: str = "7b",
    backend: LLMBackend = "auto",
    use_gpu: bool = True,
    **kwargs
):
    """便捷函数：创建LLM处理器

    这是主要的入口点，用于替代旧的create_llm_processor

    Args:
        model: 模型大小 ("3b", "7b", "14b") 或完整名称
        backend: 后端选择 ("auto", "qwen_direct", "ollama")
        use_gpu: 是否使用GPU
        **kwargs: 其他参数

    Returns:
        LLM处理器实例

    Examples:
        >>> # 自动选择最佳后端
        >>> processor = create_llm_processor("7b")

        >>> # 强制使用Qwen Direct
        >>> processor = create_llm_processor("7b", backend="qwen_direct")

        >>> # 使用Ollama
        >>> processor = create_llm_processor("qwen2.5:7b", backend="ollama")
    """
    return LLMFactory.create_processor(
        model=model,
        backend=backend,
        use_gpu=use_gpu,
        **kwargs
    )


if __name__ == "__main__":
    # 测试和状态检查
    LLMFactory.print_status()

    print("\nTesting LLM creation...")
    try:
        processor = create_llm_processor("7b", backend="auto")
        print("✓ LLM processor created successfully")

        # 测试推理
        test_text = "发票号码: INV-001\n日期: 2024-05-15\n金额: ¥1000"
        result = processor.extract_invoice_fields(test_text)
        print("✓ Test inference successful")

        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
