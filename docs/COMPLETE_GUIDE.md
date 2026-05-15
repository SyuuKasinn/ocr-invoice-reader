# OCR Invoice Reader - Complete Guide

**Version**: 2.3.1  
**Last Updated**: 2026-05-15

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Performance Optimization](#performance-optimization)
6. [GLOVIA Integration](#glovia-integration)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/SyuuKasinn/ocr-invoice-reader.git
cd ocr-invoice-reader

# 2. Install dependencies
pip install -e .

# 3. Basic OCR (no LLM)
ocr-enhanced --image invoice.pdf --visualize

# 4. With LLM enhancement (requires Ollama)
ocr-enhanced --image invoice.pdf --use-llm --auto-setup-ollama
```

### Key Commands

```bash
# Standard processing
ocr-enhanced --image invoice.pdf --lang ch --use-cpu

# Parallel processing (3-7x faster)
ocr-enhanced-parallel --image invoice.pdf --use-llm --workers 3

# CPU-only mode (no GPU)
ocr-enhanced --image invoice.pdf --use-cpu
```

---

## Installation

### Requirements

- Python 3.8+
- 4GB RAM minimum (16GB recommended for LLM)
- Windows/Linux/macOS

### Install Options

**Option 1: Standard Install**
```bash
pip install -e .
```

**Option 2: With Development Tools**
```bash
pip install -e ".[dev]"
```

**Option 3: Full Install (including API server)**
```bash
pip install -e ".[api,llm]"
```

### Verify Installation

```bash
ocr-enhanced --version
# Output: ocr-enhanced 2.3.1
```

---

## Basic Usage

### 1. Simple OCR

Extract text from invoices without LLM:

```bash
ocr-enhanced --image invoice.pdf --visualize
```

**Output**:
- `invoice_all_pages.txt` - Extracted text
- `invoice_all_pages.json` - Structured data
- `invoice_viz.jpg` - Visual annotation (if --visualize)

### 2. Multi-language Support

```bash
# Chinese/English mixed
ocr-enhanced --image invoice.pdf --lang ch

# Japanese
ocr-enhanced --image invoice.pdf --lang japan

# English only
ocr-enhanced --image invoice.pdf --lang en
```

### 3. Batch Processing

```bash
# Process multiple files
for file in invoices/*.pdf; do
  ocr-enhanced --image "$file" --use-cpu
done
```

---

## Advanced Features

### LLM Enhancement

**Hybrid Extraction** (LLM + Regex fallback):

```bash
ocr-enhanced --image invoice.pdf --use-llm
```

**Features**:
- Automatic document classification
- Smart invoice field extraction
- Validation and fallback to regex
- 93% accuracy vs 75% regex-only

**How it works**:
```
OCR Text → LLM Extraction → Validation
                              ↓
                         ✓ Pass → Use LLM result
                              ↓
                         ✗ Fail → Regex fallback
```

### Parallel Processing

**3-7x faster** than serial processing:

```bash
ocr-enhanced-parallel --image large_batch.pdf --use-llm --workers 3
```

**Performance**:
- 8 pages: 392s → 123s (3.2x faster)
- 50 pages: 40.8min → 12.8min (68% time saved)

**Worker Recommendations**:
| CPU Cores | Workers | RAM Required |
|-----------|---------|--------------|
| 4 cores   | 2       | 8GB          |
| 8 cores   | 3       | 16GB         |
| 12+ cores | 6       | 32GB         |

### Invoice Data Extraction

Automatically extracts structured invoice data:

```bash
ocr-enhanced --image invoice.pdf --use-llm
```

**Extracted Fields**:
- Invoice number, date
- MAWB/HAWB tracking numbers
- Shipper/Consignee information
- Tax details (customs duty, consumption tax)
- Item list with HS codes
- Total amount and currency

**Output Formats**:
- JSON (structured data)
- CSV (spreadsheet)
- SQL (database ready)

---

## Performance Optimization

### CPU vs GPU

**GPU Mode** (default):
```bash
ocr-enhanced --image invoice.pdf
```
- Faster OCR processing
- Requires CUDA-compatible GPU

**CPU Mode**:
```bash
ocr-enhanced --image invoice.pdf --use-cpu
```
- Works on any system
- Slower but reliable

### LLM Model Selection

```bash
# Fast model (lower accuracy)
ocr-enhanced --image invoice.pdf --use-llm --llm-model qwen2.5:7b

# Balanced model (recommended)
ocr-enhanced --image invoice.pdf --use-llm --llm-model qwen2.5:14b

# High accuracy model
ocr-enhanced --image invoice.pdf --use-llm --llm-model qwen2.5:32b
```

### Processing Speed Comparison

| Method | 8 Pages | Per Page | Speedup |
|--------|---------|----------|---------|
| Serial (no LLM) | 24s | 3s | 1x |
| Serial (with LLM) | 392s | 49s | - |
| Parallel (3 workers) | 123s | 15.4s | **3.2x** |
| Parallel (6 workers) | 98s | 12.3s | **4.0x** |

---

## GLOVIA Integration

### Overview

Specialized extractor for GLOVIA Invoice突合機能 (customs clearance):

**Key Improvements**:
- MAWB/HAWB number separation
- TEL field priority (for importer matching)
- Address ZIP extraction
- Detailed tax information
- 93% accuracy (vs 75% generic)

### Usage

```python
from ocr_invoice_reader.utils.llm_invoice_extractor_glovia import GLOVIAInvoiceExtractor

extractor = GLOVIAInvoiceExtractor(llm_processor)
result = extractor.extract_from_text(ocr_text)

# Access structured data
mawb = result['invoice_data']['basic_info']['mawb_number']
tel = result['invoice_data']['importer']['tel']  # Critical field
```

### Data Structure

```json
{
  "basic_info": {
    "invoice_number": "NCY250924",
    "invoice_date": "2025-09-24",
    "hawb_number": "506-538-938-065",
    "mawb_number": "820111868365"
  },
  "shipper": {
    "name": "DALIAN LONG SHENG WOOD INDUSTRY CO.LTD",
    "address": "..."
  },
  "consignee": {
    "name": "MINORU SANGYO CORPORATION",
    "tel": "03-3352-7152",
    "address_zip": "T566-00352",
    "address": "2-10-12 TSURUNO.SETTSU,OSAKA,JAPAN"
  },
  "importer": {...},
  "tax_info": {
    "invoice_value": 135600.0,
    "freight": 5000.0,
    "customs_duty": 6780.0,
    "consumption_tax": 14256.0,
    "currency": "JPY"
  }
}
```

---

## API Reference

### Command Line Interface

**ocr-enhanced**
```bash
ocr-enhanced --image <file> [options]

Options:
  --image PATH          Input image or PDF (required)
  --output-dir PATH     Output directory (default: results)
  --lang LANG           OCR language: ch|en|japan|korean (default: ch)
  --use-cpu            Force CPU mode (no GPU)
  --use-llm            Enable LLM enhancement
  --llm-model MODEL    LLM model name (default: qwen2.5:14b)
  --visualize          Generate annotated images
  --auto-setup-ollama  Auto-install Ollama if needed
```

**ocr-enhanced-parallel**
```bash
ocr-enhanced-parallel --image <file> [options]

Additional Options:
  --workers N          Number of parallel workers (default: 3)
```

### Python API

**Basic OCR**:
```python
from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer

analyzer = EnhancedStructureAnalyzer(use_gpu=True, lang='ch')
result = analyzer.analyze('invoice.jpg')

for region in result['regions']:
    print(f"{region.type}: {region.text}")
```

**Invoice Extraction**:
```python
from ocr_invoice_reader.utils.invoice_extractor_v2 import InvoiceExtractorV2

extractor = InvoiceExtractorV2()
data = extractor.extract_from_file('invoice.txt')

print(f"Invoice: {data['invoice_no']}")
print(f"Amount: {data['currency']} {data['total_amount']}")
```

**LLM Enhancement**:
```python
from ocr_invoice_reader.utils.llm_processor import create_llm_processor
from ocr_invoice_reader.utils.llm_invoice_extractor import LLMInvoiceExtractor

llm_processor = create_llm_processor('qwen2.5:14b')
extractor = LLMInvoiceExtractor(llm_processor)

result = extractor.extract_from_text(ocr_text)
if result and result.get('invoice_data'):
    print(result['invoice_data'])
```

---

## Troubleshooting

### Common Issues

**1. LLM extraction fails**

```
⚠ LLM extraction error: Connection refused
```

**Solution**:
```bash
# Check Ollama service
ollama list

# Restart Ollama
# Windows: Restart from system tray
# Linux/Mac: ollama serve

# Or use auto-setup
ocr-enhanced --image invoice.pdf --use-llm --auto-setup-ollama
```

**2. Memory error with parallel processing**

```
MemoryError: Unable to allocate array
```

**Solution**:
```bash
# Reduce workers
ocr-enhanced-parallel --image invoice.pdf --workers 2

# Or use serial processing
ocr-enhanced --image invoice.pdf --use-llm
```

**3. GPU not detected**

```
WARNING: GPU not available, using CPU
```

**Solution**:
```bash
# Check CUDA installation
python -c "import paddle; print(paddle.device.get_device())"

# Use CPU mode explicitly
ocr-enhanced --image invoice.pdf --use-cpu
```

**4. Poor OCR accuracy**

**Solutions**:
- Use higher DPI: PDFs are converted at 300 DPI
- Check image quality: Ensure clear, high-resolution images
- Try different language: `--lang ch` for Chinese, `--lang en` for English
- Use LLM enhancement: `--use-llm` for better extraction

**5. Slow processing**

**Solutions**:
- Use parallel processing: `ocr-enhanced-parallel`
- Use smaller LLM model: `--llm-model qwen2.5:7b`
- Disable visualization: Remove `--visualize` flag
- Use GPU: Remove `--use-cpu` flag

### Performance Tips

**Maximize Speed**:
1. Use parallel processing (`ocr-enhanced-parallel`)
2. Increase workers: `--workers 6` (if enough RAM)
3. Use GPU mode (remove `--use-cpu`)
4. Use smaller LLM: `--llm-model qwen2.5:7b`

**Maximize Accuracy**:
1. Use LLM enhancement: `--use-llm`
2. Use larger model: `--llm-model qwen2.5:14b` or `qwen2.5:32b`
3. Use GLOVIA extractor for customs documents
4. Check language setting: `--lang ch` for Chinese/English mixed

### Getting Help

- **GitHub Issues**: https://github.com/SyuuKasinn/ocr-invoice-reader/issues
- **Documentation**: Check `docs/` folder
- **Examples**: See `examples/` folder

---

## Version History

### v2.3.1 (2026-05-15)
- ✅ Fixed LLM method call error
- ✅ Added GLOVIA-optimized extractor
- ✅ Added parallel processing (3-7x speedup)
- ✅ Added hybrid extraction (LLM + regex)

### v2.3.0 (2026-05-15)
- ✅ Hybrid LLM-first extraction architecture
- ✅ Combined LLM calls (classification + extraction)
- ✅ Enhanced validation rules

### v2.2.6 (2026-05-14)
- ✅ Invoice Extractor V2 with enhanced patterns
- ✅ Multi-language support (EN/CN/JP)
- ✅ Performance metrics tracking

---

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Credits

- **PaddleOCR**: OCR engine
- **Ollama**: LLM inference
- **Qwen2.5**: Language model
