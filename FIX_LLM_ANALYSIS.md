# LLM Analysis Improvement Guide

## Current Issues

1. **Text Truncation** - Only first 500 chars used for classification
2. **OCR Quality** - Spaces between characters (T E L instead of TEL)
3. **Timeout** - 30s not enough for 3000 chars

## Quick Fixes Applied

✅ Increased text limits:
- Classification: 500 → 2000 chars
- Field extraction: 1500 → 3000 chars

## Recommended Improvements

### Fix 1: Clean OCR Text (High Priority)

Add text cleaning in `llm_processor.py`:

```python
def clean_ocr_text(text: str) -> str:
    """Remove excessive spaces from OCR text"""
    import re
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Fix spaced letters: "T E L" → "TEL"
    text = re.sub(r'([A-Z])\s+([A-Z])\s+([A-Z])', r'\1\2\3', text)
    return text.strip()

# Use in classify_document and extract_invoice_fields:
cleaned_text = clean_ocr_text(text)
text_sample = cleaned_text[:2000]
```

### Fix 2: Increase Timeout

In `llm_processor.py`, line 62:

```python
# Change from:
response = requests.post(self.api_url, json=payload, timeout=30)

# To:
timeout = min(60, 30 + len(prompt) // 1000)  # Dynamic: 30s + 1s per 1000 chars
response = requests.post(self.api_url, json=payload, timeout=timeout)
```

### Fix 3: Better Prompts (English)

```python
system = """You are an invoice extraction expert.
Extract these fields from invoice text:
- invoice_no: Invoice/tracking number
- date: Invoice date  
- amount: Total amount
- currency: Currency code
- company: Company name
- items: Array of {item_name, quantity, unit_price, amount}

Return valid JSON only. Use null for missing fields."""

prompt = f"""Extract invoice information:

{text_sample}

JSON:"""
```

## Test After Fixes

```bash
# Rerun OCR with improved LLM
ocr-enhanced --image your_invoice.pdf --lang ch --use-cpu --use-llm

# Check results
cat results/*/your_invoice_llm_analysis.txt
```

## Expected Results

After fixes, page 3 should show:
```
[Document Classification]
Type: invoice
Confidence: high

[Extracted Fields]
Invoice No: NCY250924
Date: 2025-9-24
Company: UK LIANTAI CO, LIMITED
Items: [
  {item_name: "T1676", quantity: "2", unit_price: "2500", amount: "5000"},
  ... (16 items)
]
Total Amount: 135600
Currency: JPY
```

## Performance Tips

1. Use faster model: `qwen2.5:0.5b` (current) is good
2. Reduce text if >5000 chars: Focus on first page + tables
3. Add caching for repeated documents

---

**Status**: Text limits increased ✅  
**Next**: Add text cleaning and timeout improvements
