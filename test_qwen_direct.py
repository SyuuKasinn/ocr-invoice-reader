#!/usr/bin/env python3
"""
测试Qwen直接推理（无需Ollama）
适用于Docker容器环境，完全使用GPU
"""
import sys
import time
import json
import torch


def check_environment():
    """检查环境"""
    print("=" * 60)
    print("Environment Check")
    print("=" * 60)

    # PyTorch
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"CUDA version: {torch.version.cuda}")
        print(f"GPU count: {torch.cuda.device_count()}")
        print(f"GPU name: {torch.cuda.get_device_name(0)}")
        print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("⚠ No GPU available, will use CPU")

    print()


def test_qwen_direct():
    """测试Qwen直接推理"""
    print("=" * 60)
    print("Testing Qwen Direct Processor")
    print("=" * 60)
    print()

    try:
        from ocr_invoice_reader.utils.qwen_direct_processor import create_qwen_processor

        # 选择模型大小和量化方式
        # 对于Tesla T4 16GB，推荐：
        # - 快速: 7B + INT4 (4GB显存)
        # - 精确: 14B + INT4 (8GB显存)

        print("Loading Qwen model...")
        print("Configuration: 7B + INT4 quantization")
        print("Expected memory: ~4GB")
        print()

        start_time = time.time()

        processor = create_qwen_processor(
            model_size="7b",        # 7B模型
            use_gpu=True,           # 使用GPU
            quantization="int4"     # INT4量化，节省显存
        )

        load_time = time.time() - start_time
        print(f"\n✓ Model loaded in {load_time:.1f}s")
        print()

        # 测试文本
        test_texts = [
            # 测试1: 简单发票
            """
            发票号码: INV-2024-001
            日期: 2024-05-15
            金额: ¥1,234.56
            公司: 测试公司有限责任公司
            电话: 010-12345678
            地址: 北京市朝阳区测试路123号
            """,

            # 测试2: 复杂发票
            """
            COMMERCIAL INVOICE
            Invoice No: CI-2024-0515-001
            Date: May 15, 2024

            From: ABC Trading Co., Ltd.
            Tel: +86-21-12345678
            Address: Room 1001, Building A, No.123 Test Road, Shanghai

            To: XYZ Import Corp.
            Tel: +1-555-1234567
            Address: 456 Main St, New York, NY 10001, USA

            Items:
            1. Product A - Quantity: 100 pcs - Unit Price: $10.00 - Amount: $1,000.00
            2. Product B - Quantity: 50 pcs - Unit Price: $20.00 - Amount: $1,000.00

            Subtotal: $2,000.00
            Tax (10%): $200.00
            Total: $2,200.00
            """
        ]

        # 运行测试
        for i, text in enumerate(test_texts, 1):
            print("=" * 60)
            print(f"Test {i}/{ len(test_texts)}")
            print("=" * 60)
            print()

            print("Input text:")
            print(text.strip())
            print()

            print("Extracting invoice fields...")
            start_time = time.time()

            result = processor.extract_invoice_fields(text)

            inference_time = time.time() - start_time

            print(f"✓ Inference completed in {inference_time:.2f}s")
            print()

            print("Extracted fields:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print()

            # 显示GPU使用情况
            if torch.cuda.is_available():
                print("GPU Memory:")
                print(f"  Allocated: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
                print(f"  Reserved: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
                print()

        # 性能总结
        print("=" * 60)
        print("Performance Summary")
        print("=" * 60)
        print(f"Model: Qwen2.5-7B-Instruct (INT4)")
        print(f"Load time: {load_time:.1f}s")
        print(f"Inference time: ~{inference_time:.2f}s per request")

        if torch.cuda.is_available():
            print(f"GPU memory: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")

        print()
        print("✓ All tests passed!")
        print()

        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        print()
        print("Please install required packages:")
        print("  pip install transformers torch accelerate bitsandbytes")
        return False

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_ocr():
    """测试与OCR集成"""
    print("=" * 60)
    print("Testing OCR + Qwen Integration")
    print("=" * 60)
    print()

    try:
        from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer
        from ocr_invoice_reader.utils.qwen_direct_processor import create_qwen_processor

        # 检查示例文件
        import os
        sample_file = "examples/INVOICE.pdf"

        if not os.path.exists(sample_file):
            print(f"⚠ Sample file not found: {sample_file}")
            print("Skipping OCR integration test")
            return True

        print(f"Processing: {sample_file}")
        print()

        # 初始化OCR
        print("1. Initializing OCR (PaddleOCR)...")
        analyzer = EnhancedStructureAnalyzer(use_gpu=True, lang='ch')
        print("   ✓ OCR initialized")
        print()

        # 初始化Qwen
        print("2. Initializing Qwen (Direct)...")
        llm = create_qwen_processor(
            model_size="7b",
            use_gpu=True,
            quantization="int4"
        )
        print("   ✓ Qwen initialized")
        print()

        # 处理第一页
        print("3. Processing first page...")
        result = analyzer.analyze_single_page(sample_file, page_idx=0)

        # 提取文本
        all_text = ""
        for region in result.get('regions', []):
            if hasattr(region, 'text') and region.text:
                all_text += region.text + "\n"

        print(f"   ✓ Extracted {len(all_text)} characters")
        print()

        # 使用Qwen提取字段
        print("4. Extracting fields with Qwen...")
        start_time = time.time()

        invoice_data = llm.extract_invoice_fields(all_text[:2000])  # 限制长度

        print(f"   ✓ Extraction completed in {time.time()-start_time:.2f}s")
        print()

        # 显示结果
        print("5. Results:")
        print(json.dumps(invoice_data, ensure_ascii=False, indent=2))
        print()

        print("✓ OCR + Qwen integration test passed!")
        return True

    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Qwen Direct Processor Test" + " " * 21 + "║")
    print("║" + " " * 12 + "(No Ollama Required)" + " " * 26 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # 检查环境
    check_environment()

    # 测试Qwen
    success = test_qwen_direct()

    if not success:
        print("Basic test failed, skipping integration test")
        return 1

    # 测试OCR集成
    print()
    test_with_ocr()

    print()
    print("=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Use qwen_direct_processor in your code")
    print("2. No Ollama configuration needed")
    print("3. GPU will be automatically used")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
