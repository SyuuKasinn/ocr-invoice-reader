#!/usr/bin/env python
"""
LLM功能测试脚本
"""
from ocr_invoice_reader.utils.llm_processor import LLMProcessor, create_llm_processor

def test_ollama_connection():
    """测试Ollama连接"""
    print("=== Testing Ollama Connection ===")
    processor = LLMProcessor()

    if processor.is_available():
        print("✓ Ollama service is running")

        if processor.check_model():
            print(f"✓ Model '{processor.model}' is available")
            return processor
        else:
            print(f"✗ Model '{processor.model}' not found")
            print(f"  Install: ollama pull {processor.model}")
            return None
    else:
        print("✗ Ollama service not available")
        print("  Install from: https://ollama.ai/download")
        print("  Then run: ollama serve")
        return None

def test_text_correction():
    """测试文本纠错"""
    print("\n=== Testing Text Correction ===")

    test_text = """
    1nvoice Number: 2O24O1O1
    Date: 2O24-O5-14
    Amount: 1,234.56 CNY
    """

    processor = create_llm_processor()
    if not processor:
        print("Skipped: LLM not available")
        return

    print(f"Original text:\n{test_text}")
    print("\nCorrecting...")

    try:
        corrected = processor.correct_text(test_text)
        print(f"\nCorrected text:\n{corrected}")
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_field_extraction():
    """测试字段提取"""
    print("\n=== Testing Field Extraction ===")

    test_text = """
    商业发票
    发票号码：INV-2024-001
    开票日期：2024年5月14日
    金额：￥1,234.56
    公司名称：某某科技有限公司
    税号：91110000123456789X
    """

    processor = create_llm_processor()
    if not processor:
        print("Skipped: LLM not available")
        return

    print(f"Invoice text:\n{test_text}")
    print("\nExtracting fields...")

    try:
        fields = processor.extract_invoice_fields(test_text)
        print(f"\nExtracted fields:")
        import json
        print(json.dumps(fields, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"✗ Failed: {e}")

def test_document_classification():
    """测试文档分类"""
    print("\n=== Testing Document Classification ===")

    test_docs = [
        ("发票号码：INV-001\n金额：1000元", "invoice"),
        ("收据\n收款人：张三\n金额：500元", "receipt"),
        ("运单号：SF123456\n发件人：李四", "waybill"),
    ]

    processor = create_llm_processor()
    if not processor:
        print("Skipped: LLM not available")
        return

    for text, expected in test_docs:
        print(f"\nText: {text[:50]}...")
        print("Classifying...")

        try:
            result = processor.classify_document(text)
            doc_type = result.get('type', 'unknown')
            confidence = result.get('confidence', 'unknown')

            status = "✓" if doc_type == expected else "✗"
            print(f"{status} Detected: {doc_type} (confidence: {confidence})")

        except Exception as e:
            print(f"✗ Failed: {e}")

def test_performance():
    """测试性能"""
    print("\n=== Testing Performance ===")

    processor = create_llm_processor()
    if not processor:
        print("Skipped: LLM not available")
        return

    import time
    test_text = "发票号码：INV-2024-001\n日期：2024-05-14\n金额：1234.56元" * 5

    operations = [
        ("Text Correction", lambda: processor.correct_text(test_text[:200])),
        ("Document Classification", lambda: processor.classify_document(test_text[:200])),
        ("Field Extraction", lambda: processor.extract_invoice_fields(test_text[:500])),
    ]

    for name, func in operations:
        print(f"\n{name}:")
        start = time.time()

        try:
            result = func()
            elapsed = time.time() - start
            print(f"  ✓ Completed in {elapsed:.2f}s")
        except Exception as e:
            print(f"  ✗ Failed: {e}")

if __name__ == "__main__":
    print("="*60)
    print("LLM Integration Test")
    print("="*60)

    # Test connection
    processor = test_ollama_connection()

    if processor:
        print("\n" + "="*60)

        # Run tests
        test_text_correction()
        test_field_extraction()
        test_document_classification()
        test_performance()

        print("\n" + "="*60)
        print("All tests completed!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("Setup Required:")
        print("1. Install Ollama: https://ollama.ai/download")
        print("2. Download model: ollama pull qwen2.5:0.5b")
        print("3. Run tests again")
        print("="*60)
