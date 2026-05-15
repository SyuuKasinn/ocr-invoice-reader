# Fix OCR Excessive Spaces

## Problem

OCR results contain excessive spaces between characters:
```
Before: T E L : 0 0 4 4 2 0 8 4 3 2 3 0 8 8
After:  TEL: 00442084323088
```

## Root Cause

The `split_words=True` parameter in `text_processor.py` was intended to split concatenated words but incorrectly added spaces.

## Solutions Applied

### Solution 1: Disable Word Splitting ✅

**File**: `ocr_invoice_reader/processors/enhanced_structure_analyzer.py`

**Change**: `split_words=True` → `split_words=False` (3 locations)

**Lines**: 231, 266, 522

**Result**: Prevents further word splitting, but doesn't clean existing spaces.

### Solution 2: Text Cleaner Module ✅ 

**File**: `ocr_invoice_reader/utils/text_cleaner.py` (NEW)

**Features**:
- Merges spaced letters: "T E L" → "TEL"
- Merges spaced numbers: "5 0 6" → "506"  
- Merges letter-number: "RM 1 0 1" → "RM101"
- Cleans punctuation: " : " → ": "

**Usage**:
```python
from ocr_invoice_reader.utils.text_cleaner import clean_ocr_spaces

text = "T E L : 0 0 4 4 2 0 8 4 3 2 3 0 8 8"
cleaned = clean_ocr_spaces(text)
# Result: "TEL: 00442084323088"
```

## Integration Options

### Option A: Post-Process Output Files (Recommended)

Clean the text files after generation:

```python
# Add to enhanced_extract.py after saving TXT files
from ocr_invoice_reader.utils.text_cleaner import process_ocr_text

# After writing region.text:
cleaned_text = process_ocr_text(region.text)
f.write(cleaned_text + '\n\n')
```

### Option B: Clean in Structure Analyzer

Apply cleaning in the analyzer itself:

```python
# In enhanced_structure_analyzer.py
from ocr_invoice_reader.utils.text_cleaner import clean_ocr_spaces

# After getting OCR text:
region.text = clean_ocr_spaces(region.text)
```

### Option C: Post-Processing Script

Create a script to clean existing output files:

```python
# clean_ocr_results.py
import glob
from pathlib import Path
from ocr_invoice_reader.utils.text_cleaner import process_ocr_text

for txt_file in glob.glob("results/**/*_page_*.txt", recursive=True):
    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    cleaned = process_ocr_text(content)
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    
    print(f"Cleaned: {txt_file}")
```

## Test Results

| Input | Output | Status |
|-------|--------|--------|
| `T E L : 0 0 4 4` | `TEL: 0044` | ✅ |
| `M I N O R U` | `MINORU` | ✅ |
| `R M 1 0 1` | `RM101` | ✅ |
| `5 0 6 5 3 8` | `506538` | ✅ |
| `25 T1676` | `25T1676` | ✅ |

## Known Limitations

1. **May merge intentional spaces**:
   - "MAPLE HOUSE" → "MAPLEHOUSE"
   - Solution: Adjust regex patterns to preserve common word boundaries

2. **Complex patterns**:
   - "1 6 A 8 1 8 3 - 2 - 1" → "16 A 8183 - 2 - 1" (partially fixed)
   - Some mixed patterns may not be perfectly cleaned

## Recommendations

1. ✅ **Applied**: Disabled `split_words` to prevent new issues
2. ✅ **Created**: Text cleaner module
3. ⏳ **TODO**: Integrate cleaner into output pipeline
4. ⏳ **TODO**: Add option flag `--clean-spaces` to enable/disable

## Quick Fix for Existing Files

Clean all result files in a directory:

```bash
cd results/20260515_110114/
python << 'PYSCRIPT'
import glob
from pathlib import Path
import sys
sys.path.insert(0, '../..')
from ocr_invoice_reader.utils.text_cleaner import process_ocr_text

for txt in glob.glob("*_page_*.txt"):
    with open(txt, 'r', encoding='utf-8') as f:
        content = f.read()
    cleaned = process_ocr_text(content)
    with open(txt, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f"Cleaned: {txt}")
PYSCRIPT
```

---

**Status**: Partially Fixed ✅  
**Files Changed**: 2 (enhanced_structure_analyzer.py, text_cleaner.py [new])  
**Next**: Integrate into output pipeline or add CLI flag
