#!/usr/bin/env python
"""Test LLM text correction"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from ocr_invoice_reader.utils.llm_processor import create_llm_processor

# Sample OCR text with errors
ocr_text = """DALIAN EVERCREDIT INTERNATIONAL TRADING CO.,LTD
R O O M 2 7 0 2 , B L O C K B , F O R T U N E P L A Z A N O . 2 0
C O M M E R C I A L INVOICE
INVOICE NO. 20250924
MESSRS. T O K O L I M Y C O . , L T D"""

print("Original OCR text:")
print("="*60)
print(ocr_text)
print("\n")

# Create LLM processor
llm = create_llm_processor()
if not llm:
    print("ERROR: LLM not available")
    sys.exit(1)

print("Running LLM correction...")
print("="*60)

try:
    corrected = llm.correct_text(ocr_text)
    print("\nCorrected text:")
    print("="*60)
    print(corrected)
    print("\n")
    print("[OK] Text correction successful!")
except Exception as e:
    print(f"[X] Error: {e}")
    sys.exit(1)
