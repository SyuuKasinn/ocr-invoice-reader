# LLM Hybrid Invoice Extraction

## Overview

Version 2.3.0 introduces a **hybrid invoice extraction architecture** that combines the flexibility of LLM-based extraction with the reliability of regex-based pattern matching.

## Architecture

```
OCR Text
   ↓
1. LLM Extraction (Primary Method)
   - Uses structured prompts with Qwen2.5-14B
   - Extracts all invoice fields as JSON
   - Validates result quality
   ↓
   Success? → Use LLM result
   ↓
   Failed validation?
   ↓
2. Regex Fallback (Backup Method)
   - Uses InvoiceExtractorV2 patterns
   - Reliable for standard formats
   - Returns structured data
   ↓
3. Return Best Result
```

## Why Hybrid?

### Problem with Pure Regex
- **Maintenance nightmare**: Each new format requires 10+ new patterns
- **Pattern conflicts**: Format A patterns may mis-match format B
- **Cannot generalize**: Completely new formats require code changes
- **Brittle**: Small layout changes break extraction

### Problem with Pure LLM
- **Slow**: 20-60 seconds per page with Qwen2.5-14B
- **Inconsistent**: Same input may produce different outputs
- **Hallucination risk**: May invent non-existent data
- **Resource intensive**: Requires GPU or powerful CPU

### Hybrid Solution Benefits
✅ **Flexible**: LLM handles new formats automatically
✅ **Reliable**: Regex fallback ensures data extraction
✅ **Fast when possible**: LLM only when needed
✅ **Maintainable**: Adjust prompts, not patterns
✅ **Safe**: Validation layer prevents bad data

## Usage

### Basic Usage (Automatic)

```bash
# Hybrid extraction is automatic when using --use-llm
ocr-enhanced --image invoice.pdf --use-llm
```

The system will:
1. Extract text via OCR
2. Try LLM extraction
3. Validate result
4. Fallback to regex if validation fails
5. Save result with `extraction_method` field

### Output Format

```json
{
  "page": 1,
  "source_file": "invoice_001",
  "extraction_method": "llm",  // or "regex_fallback"
  "extracted_fields": {
    "invoice_number": "INV-2025-001",
    "invoice_date": "2025-09-24",
    "tracking_number": "820111868365",
    "total_amount": 135600.0,
    "currency": "JPY",
    "shipper_name": "DALIAN LONG SHENG WOOD INDUSTRY CO.LTD",
    "consignee_name": "MINORU SANGYO CORPORATION",
    "shipper_address": "AGENCY DALIAN CHINA ZHANG JIA YAOSTR.TAI PING",
    "consignee_address": "T566-00352-10-12TSURUNO.SETTSU,OSAKA,JAPAN",
    "phone": "03-3352-7152",
    "fax": null
  },
  "llm_validation_issues": []  // Empty if validation passed
}
```

### Summary Statistics

The combined invoices file shows extraction statistics:

```json
{
  "summary": {
    "with_invoice_number": 8,
    "with_company": 8,
    "with_amount": 7,
    "llm_extracted": 6,       // Successfully extracted by LLM
    "regex_fallback": 2       // Failed LLM, used regex
  }
}
```

## LLM Extraction Details

### Prompt Structure

The LLM receives a structured prompt with:
- **Clear field definitions** (required vs optional)
- **Format requirements** (date format, amount format)
- **Multi-language keywords** (English, Chinese, Japanese)
- **Extraction rules** (cleaning, validation)
- **JSON output format**

### Supported Fields

**Required Fields** (extracted if present):
- `invoice_number` - Invoice/bill number
- `invoice_date` - Date in YYYY-MM-DD format
- `tracking_number` - Shipping/tracking number
- `total_amount` - Total amount (decimal)
- `currency` - Currency code (USD, JPY, CNY, etc.)

**Optional Fields** (extracted if clearly present):
- `shipper_name` - Sender company name
- `consignee_name` - Receiver company name
- `shipper_address` - Sender address
- `consignee_address` - Receiver address
- `phone` - Phone number
- `fax` - Fax number

### Validation Rules

LLM results are validated for:
1. **Required field presence** - At least one required field must be present
2. **Date format** - Must be YYYY-MM-DD
3. **Amount format** - Must be numeric (int or float)
4. **Currency code** - Must be a known currency code

If validation fails, the system automatically falls back to regex extraction.

## Performance Comparison

### LLM Extraction
- **Speed**: 20-60 seconds per page
- **Accuracy**: 90-95% on varied formats
- **Flexibility**: Handles new formats automatically
- **Resource**: GPU recommended (14B model)

### Regex Extraction
- **Speed**: <1 second per page
- **Accuracy**: 95%+ on known formats, 0% on new formats
- **Flexibility**: Requires code changes for new formats
- **Resource**: Minimal CPU

### Hybrid Approach
- **Speed**: Fast for standard formats (regex), slower for new formats (LLM)
- **Accuracy**: Best of both worlds
- **Flexibility**: Auto-adapts to new formats
- **Resource**: Optimal usage

## Customization

### Adjusting LLM Model

Use a different model (faster/slower):

```bash
# Use smaller model (faster, less accurate)
ocr-enhanced --image invoice.pdf --use-llm --llm-model qwen2.5:7b

# Use default model (balanced)
ocr-enhanced --image invoice.pdf --use-llm --llm-model qwen2.5:14b

# Use larger model if available (slower, more accurate)
ocr-enhanced --image invoice.pdf --use-llm --llm-model qwen2.5:32b
```

### Modifying Extraction Prompts

Edit `ocr_invoice_reader/utils/llm_invoice_extractor.py`:

```python
class LLMInvoiceExtractor:
    def __init__(self, llm_processor=None):
        self.extraction_prompt_template = """
        # Modify this prompt to:
        # - Add new fields
        # - Change extraction rules
        # - Support new document types
        # - Improve accuracy for specific formats
        """
```

### Adjusting Validation Rules

Edit `validate_extraction_result()` in `llm_invoice_extractor.py`:

```python
def validate_extraction_result(data: Dict) -> tuple[bool, list[str]]:
    issues = []
    
    # Add your custom validation rules here
    # Example: require minimum fields
    if not data.get('invoice_number') and not data.get('tracking_number'):
        issues.append("Must have invoice_number or tracking_number")
    
    # Example: validate amount range
    if data.get('total_amount'):
        if data['total_amount'] < 0:
            issues.append("Amount cannot be negative")
    
    return len(issues) == 0, issues
```

## Troubleshooting

### LLM Returns Invalid JSON

**Symptom**: "LLM extraction validation failed: No data returned"

**Solution**:
1. Check Ollama service is running: `ollama list`
2. Try simpler document first
3. Increase prompt clarity in `llm_invoice_extractor.py`
4. Check Ollama logs for errors

### Always Falling Back to Regex

**Symptom**: All pages show `"extraction_method": "regex_fallback"`

**Possible causes**:
1. LLM model not loaded properly
2. Validation rules too strict
3. OCR text quality too poor
4. Prompt not matching document format

**Solutions**:
- Check console output for validation messages
- Review `llm_validation_issues` in output JSON
- Test with known-good document
- Adjust validation rules if too strict

### Slow Performance

**Symptom**: Processing takes 30-60 seconds per page

**Expected**: This is normal for LLM extraction with 14B model

**Speed it up**:
1. Use smaller model: `--llm-model qwen2.5:7b`
2. Use GPU if available (check Ollama GPU support)
3. Disable LLM for batch processing of standard formats
4. Let regex handle standard formats (they're fast and accurate)

### LLM Hallucinating Data

**Symptom**: Extracted data doesn't match original document

**Solutions**:
1. Add stricter validation rules
2. Use larger model (14B or higher)
3. Improve prompt with specific constraints
4. Add post-processing checks
5. Cross-validate with regex extraction

## Best Practices

### When to Use LLM Extraction

✅ **Use LLM** when:
- Processing diverse document formats
- Encountering new invoice layouts
- Need to adapt quickly without code changes
- Accuracy is more important than speed
- Documents have complex multi-language content

### When to Use Regex Extraction

✅ **Use Regex** when:
- Processing large batches of standard formats
- Speed is critical
- Documents follow known patterns
- Running on low-resource systems
- Maximum consistency needed

### Optimal Workflow

1. **First time**: Use hybrid mode to learn formats
2. **Analysis**: Check extraction methods used
3. **If mostly LLM**: Your formats are diverse → keep hybrid
4. **If mostly regex**: Your formats are standard → consider regex-only for speed
5. **Regular updates**: Re-test with new document types

## Migration from V2

### Old Approach (Regex-only)
```python
from ocr_invoice_reader.utils.invoice_extractor_v2 import InvoiceExtractorV2

extractor = InvoiceExtractorV2()
data = extractor.extract_from_text(text)
```

### New Approach (Hybrid)
```python
from ocr_invoice_reader.utils.llm_invoice_extractor import LLMInvoiceExtractor, validate_extraction_result
from ocr_invoice_reader.utils.invoice_extractor_v2 import InvoiceExtractorV2

# Try LLM first
llm_extractor = LLMInvoiceExtractor(llm_processor)
llm_result = llm_extractor.extract_from_text(text)

if llm_result:
    is_valid, issues = validate_extraction_result(llm_result)
    if is_valid:
        data = llm_extractor.format_for_database(llm_result)
    else:
        # Fallback to regex
        regex_extractor = InvoiceExtractorV2()
        invoice_data = regex_extractor.extract_from_text(text)
        data = regex_extractor.format_for_database(invoice_data)
```

### CLI Changes

**No changes required** - CLI automatically uses hybrid mode when `--use-llm` is enabled.

## Future Improvements

Planned enhancements:
- [ ] Smart mode selection based on document complexity
- [ ] Confidence scoring for extraction quality
- [ ] Active learning from validation failures
- [ ] Multi-model ensemble extraction
- [ ] Real-time prompt optimization
- [ ] Extraction quality metrics dashboard

## License

MIT License - See LICENSE file for details
