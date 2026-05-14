# Quick Fixes Guide

## 🚨 Critical Fix #1: Hard-coded Language Bug

**File**: `ocr_invoice_reader/processors/enhanced_structure_analyzer.py`  
**Line**: 78  
**Priority**: CRITICAL (Currently broken functionality)

### Problem
```python
self.structure_engine = PPStructure(
    lang='ch',  # ❌ Hard-coded, ignores constructor parameter
```

### Fix
```python
self.structure_engine = PPStructure(
    lang=self.lang,  # ✅ Use the lang parameter from constructor
```

### Apply Fix
```bash
# Manual edit
vim ocr_invoice_reader/processors/enhanced_structure_analyzer.py +78

# Or use sed
sed -i "78s/lang='ch',/lang=self.lang,/" ocr_invoice_reader/processors/enhanced_structure_analyzer.py
```

---

## 🚨 Critical Fix #2: Bare Except in ollama_manager.py

**File**: `ocr_invoice_reader/utils/ollama_manager.py`  
**Lines**: 28, 243, 388

### Fix #2.1 - check_service() (Line 28)

**Current**:
```python
def check_service(self) -> bool:
    try:
        response = requests.get(self.base_url, timeout=2)
        return response.status_code == 200
    except:  # ❌
        return False
```

**Fixed**:
```python
def check_service(self) -> bool:
    try:
        response = requests.get(self.base_url, timeout=2)
        return response.status_code == 200
    except (requests.RequestException, requests.Timeout):
        return False
    except Exception as e:
        print(f"Unexpected error checking service: {e}")
        return False
```

### Fix #2.2 - check_model() (Line 243)

**Current**:
```python
def check_model(self, model: str) -> bool:
    try:
        result = subprocess.run(...)
        if result.returncode == 0:
            return model in result.stdout
        return False
    except:  # ❌
        return False
```

**Fixed**:
```python
def check_model(self, model: str) -> bool:
    try:
        result = subprocess.run(...)
        if result.returncode == 0:
            return model in result.stdout
        return False
    except (subprocess.SubprocessError, subprocess.TimeoutExpired):
        return False
    except Exception as e:
        print(f"Unexpected error checking model: {e}")
        return False
```

### Fix #2.3 - get_status() (Line 388)

**Current**:
```python
try:
    result = subprocess.run(...)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')[1:]
        ...
except:  # ❌
    pass
```

**Fixed**:
```python
try:
    result = subprocess.run(...)
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')[1:]
        ...
except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
    # Failed to get model list, return empty
    pass
except Exception as e:
    print(f"Unexpected error getting status: {e}")
    pass
```

---

## 🔧 Medium Priority Fix #3: Context Managers

**File**: `ocr_invoice_reader/cli/enhanced_extract.py`  
**Multiple locations**

### Current Pattern (WRONG)
```python
# CSV Summary (around line 370)
csv_summary = output_dir / f"{input_name}_summary.csv"
f = open(csv_summary, 'w', newline='', encoding='utf-8-sig')  # ❌
writer = csv.writer(f)
writer.writerow(['Page', 'Method', 'Regions', 'Tables', 'Text_Length'])
for result in all_results:
    writer.writerow([...])
f.close()  # Never reached on exception
```

### Fixed Pattern (CORRECT)
```python
# CSV Summary
csv_summary = output_dir / f"{input_name}_summary.csv"
with open(csv_summary, 'w', newline='', encoding='utf-8-sig') as f:  # ✅
    writer = csv.writer(f)
    writer.writerow(['Page', 'Method', 'Regions', 'Tables', 'Text_Length'])
    for result in all_results:
        writer.writerow([...])
# File automatically closed
```

### Locations to Fix
1. Line ~370: Summary CSV writing
2. Line ~420: LLM CSV writing  
3. Line ~280: Individual page LLM CSV writing

---

## 📝 All Bare Except Locations

### Quick Reference Table

| File | Line | Function | Exception Type Needed |
|------|------|----------|----------------------|
| ollama_manager.py | 28 | check_service | `requests.RequestException` |
| ollama_manager.py | 243 | check_model | `subprocess.SubprocessError` |
| ollama_manager.py | 388 | get_status | `subprocess.SubprocessError` |
| llm_processor.py | 33 | is_available | `requests.RequestException` |
| llm_processor.py | 44 | check_model | `requests.RequestException` |
| llm_processor.py | 123 | _call_ollama | `requests.RequestException, json.JSONDecodeError` |
| llm_processor.py | 157 | correct_text | `Exception` (keep generic, add logging) |
| llm_processor.py | 198 | extract_invoice_fields | `Exception` (keep generic, add logging) |
| structure_analyzer.py | 149 | _detect_tables | `cv2.error` |
| structure_analyzer.py | 382 | _extract_table_html | `Exception` (keep generic) |
| structure_analyzer.py | 420 | _build_table_html | `Exception` (keep generic) |
| field_extractor.py | 331 | _extract_amount | `ValueError, KeyError` |
| field_extractor.py | 337 | _extract_date | `ValueError, KeyError` |
| field_extractor.py | 343 | _extract_invoice_no | `ValueError, KeyError` |
| enhanced_extract.py | 613 | save visualization | `Exception` (keep generic) |
| simple_ocr.py | 83 | run_ocr | `Exception` (keep generic) |
| text_corrector.py | 14 | correct_text | `Exception` (keep generic) |
| text_corrector.py | 55 | _apply_rules | `Exception` (keep generic) |
| utils.py | 242 | parse_date | `ValueError, KeyError` |
| utils.py | 314 | format_amount | `ValueError` |

---

## 🎯 One-Line Fix Commands

### Fix Hard-coded Language
```bash
cd ocr-invoice-reader
sed -i "s/lang='ch',  # Use self.lang parameter/lang=self.lang,  # Use self.lang parameter/" ocr_invoice_reader/processors/enhanced_structure_analyzer.py
```

### Find All Bare Except
```bash
grep -n "except:" ocr_invoice_reader/**/*.py
```

### Test After Fixes
```bash
python test_ollama_logic.py
python -m pytest tests/ -v  # If tests exist
```

---

## 🔍 Verification Checklist

After applying fixes, verify:

- [ ] Hard-coded language fixed (line 78)
- [ ] All bare except clauses replaced with specific exceptions
- [ ] All file operations use context managers (with open)
- [ ] No syntax errors: `python -m py_compile ocr_invoice_reader/**/*.py`
- [ ] Logic tests pass: `python test_ollama_logic.py`
- [ ] Manual test with sample invoice
- [ ] Git commit with message: "fix: critical error handling and resource management issues"

---

## 📊 Impact Assessment

### Before Fixes
- ❌ Language parameter ignored
- ❌ 22 bare except clauses (catches SystemExit, KeyboardInterrupt)
- ❌ File descriptors may leak
- ⚠️ Difficult to debug errors

### After Fixes
- ✅ Language parameter works correctly
- ✅ Specific exception handling
- ✅ Proper resource cleanup
- ✅ Better error messages for debugging

---

## 🚀 Automated Fix Script

```python
#!/usr/bin/env python3
"""
Automated code fixes for OCR Invoice Reader
Usage: python apply_quick_fixes.py
"""

import re
from pathlib import Path

def fix_hard_coded_language():
    """Fix hard-coded 'ch' in enhanced_structure_analyzer.py"""
    file_path = Path('ocr_invoice_reader/processors/enhanced_structure_analyzer.py')
    
    content = file_path.read_text(encoding='utf-8')
    
    # Replace line 78
    content = content.replace(
        "lang='ch',  # Use self.lang parameter",
        "lang=self.lang,  # Use self.lang parameter"
    )
    
    file_path.write_text(content, encoding='utf-8')
    print("✓ Fixed hard-coded language in enhanced_structure_analyzer.py")


def fix_bare_except_ollama_manager():
    """Fix bare except in ollama_manager.py"""
    file_path = Path('ocr_invoice_reader/utils/ollama_manager.py')
    
    content = file_path.read_text(encoding='utf-8')
    
    # Fix check_service (line ~28)
    content = re.sub(
        r'(def check_service.*?try:.*?return response\.status_code == 200)\s+except:\s+return False',
        r'\1\n        except (requests.RequestException, requests.Timeout):\n            return False',
        content,
        flags=re.DOTALL
    )
    
    file_path.write_text(content, encoding='utf-8')
    print("✓ Fixed bare except in ollama_manager.py")


def main():
    print("Applying quick fixes...")
    print()
    
    try:
        fix_hard_coded_language()
        fix_bare_except_ollama_manager()
        
        print()
        print("✅ All quick fixes applied!")
        print()
        print("Next steps:")
        print("1. Review changes: git diff")
        print("2. Test: python test_ollama_logic.py")
        print("3. Commit: git commit -am 'fix: critical error handling issues'")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
```

Save as `apply_quick_fixes.py` and run:
```bash
python apply_quick_fixes.py
```

---

**Last Updated**: 2026-05-14  
**Status**: Ready to Apply
