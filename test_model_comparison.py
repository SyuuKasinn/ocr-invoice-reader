#!/usr/bin/env python
"""Compare qwen2.5:0.5b vs qwen2.5:1.5b for OCR correction"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from ocr_invoice_reader.utils.llm_processor import LLMProcessor

# Sample OCR text with common errors
test_cases = [
    {
        "name": "空格分隔字符",
        "text": "S E M I C O N D U C T O R PACKAGING E Q U I P M E N T"
    },
    {
        "name": "混合语言",
        "text": "SANEI SANSYOU C O R P O R A T I O N 三荣商社株式会社"
    },
    {
        "name": "数字和符号",
        "text": "Invoice No. | 506-538-938-065 | DATE:24-Sep-25"
    }
]

print("="*60)
print("LLM 模型对比测试")
print("="*60)

for case in test_cases:
    print(f"\n【测试 {case['name']}】")
    print(f"原文: {case['text']}")
    print("-"*60)

    # Test 0.5b
    try:
        llm_05b = LLMProcessor(model="qwen2.5:0.5b")
        result_05b = llm_05b.correct_text(case['text'])
        print(f"0.5b: {result_05b}")
    except Exception as e:
        print(f"0.5b: [错误] {e}")

    # Test 1.5b
    try:
        llm_15b = LLMProcessor(model="qwen2.5:1.5b")
        result_15b = llm_15b.correct_text(case['text'])
        print(f"1.5b: {result_15b}")
    except Exception as e:
        print(f"1.5b: [错误] {e}")

print("\n" + "="*60)
print("测试完成")
print("="*60)
