# Visual Examples - OCR Invoice Reader

This document provides detailed visual examples of the OCR Invoice Reader's capabilities.

## 📸 Overview

The OCR Invoice Reader generates professional visualizations showing:
- **Text Detection**: Red polygons around each recognized text
- **Region Classification**: Color-coded boxes for different content types
- **Structure Analysis**: Table boundaries and cell detection
- **Multi-Page Support**: Individual visualization for each page

## 🎨 Visualization Color Coding

| Color | Region Type | Description |
|-------|------------|-------------|
| 🔴 Red Polygon | Text Box | Individual character/word detection |
| 🟧 Orange Box | Table | Structured table regions |
| 🔵 Blue Box | Title/Header | Document headers and titles |
| 🟢 Green Box | Text Block | Plain text paragraphs |

## 🚀 Usage Examples

### Example 1: Japanese Invoice Processing

**Command:**
```bash
ocr-enhanced --image invoice.pdf --lang japan --visualize --use-cpu
```

**Input:** Multi-page Japanese invoice (インボイス見本.pdf)

**Output Structure:**
```
results/20260512_173743/
├── インボイス見本_all_pages.json       # Complete structured data (10 pages)
├── インボイス見本_all_pages.txt        # All extracted text
├── インボイス見本_all_tables.html      # All detected tables
├── インボイス見本_page_0001_viz.jpg    # Page 1 visualization
├── インボイス見本_page_0002_viz.jpg    # Page 2 visualization
├── インボイス見本_page_0003_viz.jpg    # Page 3 visualization
└── ... (one visualization per page)
```

**Visualization Features:**
- ✅ Japanese text recognition (Kanji, Hiragana, Katakana)
- ✅ Company names and addresses highlighted
- ✅ Table structure detection (rows × columns)
- ✅ Date and document number extraction
- ✅ Mixed Japanese-English text support

### Example 2: Waybill/Shipping Document

**Command:**
```bash
ocr-enhanced --image waybill.pdf --lang ch --visualize --use-cpu
```

**Detected Elements:**
- Document number: HTL506539397733
- Sender information with address
- Receiver information with address
- Shipping date and details
- Item descriptions in table format

**Table Detection Example:**
```json
{
  "type": "table",
  "bbox": [46, 791, 3383, 1513],
  "rows": 10,
  "columns": 4,
  "confidence": 0.94,
  "table_html": "<table>...</table>"
}
```

### Example 3: Chinese Document Processing

**Command:**
```bash
ocr-enhanced --image chinese_invoice.pdf --lang ch --visualize --use-cpu
```

**Features:**
- Chinese character recognition (简体中文/繁體中文)
- Company seals/stamps detection
- Mixed Chinese-English content
- Complex table layouts
- Multi-column text regions

## 📊 Four Extraction Modes Comparison

### Mode 1: ocr-enhanced (Recommended)

**Best for:** Production invoices, waybills, complex documents

**Features:**
- Coordinate-based table detection
- Region boundary visualization
- Full structure analysis
- HTML table output

**Sample Output:**
```json
{
  "method": "coordinate_based",
  "total_pages": 10,
  "pages": [
    {
      "page_number": 1,
      "regions": [
        {
          "type": "table",
          "bbox": [46, 791, 3383, 1513],
          "rows": 10,
          "columns": 4,
          "confidence": 0.94
        }
      ]
    }
  ]
}
```

### Mode 2: ocr-raw

**Best for:** Debugging, comparing with PP-Structure original output

**Features:**
- Raw PP-Structure JSON output
- Original PaddleOCR visualization
- No post-processing
- Direct engine results

### Mode 3: ocr-extract

**Best for:** Document classification, field extraction

**Features:**
- Structured field extraction
- Document type detection
- Sender/receiver parsing
- Date and number extraction

**Sample Output:**
```json
{
  "document_type": "waybill",
  "document_number": "HTL506539397733",
  "date": "2026-05-12",
  "sender": {
    "company": "SEKIAOI ELECTRONICS(WUXI)CO.,LTD",
    "address": "WUXI, JIANGSU, CHINA"
  },
  "receiver": {
    "company": "SEKI AOI TECHNO CO.,LTD",
    "address": "AICHI, JAPAN"
  },
  "confidence": 0.55
}
```

### Mode 4: ocr-simple

**Best for:** Quick text extraction, simple documents

**Features:**
- Fast text-only extraction
- Minimal processing
- Handwriting support option
- No structure analysis

## 🌍 Multi-Language Examples

### Japanese Documents (--lang japan)
```bash
ocr-enhanced --image japanese_invoice.pdf --lang japan --visualize --use-cpu
```

**Recognition Quality:** ⭐⭐⭐⭐⭐ Excellent
- Kanji: 漢字
- Hiragana: ひらがな
- Katakana: カタカナ
- Mixed with English: ABC株式会社

### Chinese Documents (--lang ch)
```bash
ocr-enhanced --image chinese_invoice.pdf --lang ch --visualize --use-cpu
```

**Recognition Quality:** ⭐⭐⭐⭐⭐ Excellent
- Simplified: 简体中文
- Traditional: 繁體中文
- Company seals: 公司印章
- Mixed content support

**Tip:** `--lang ch` is recommended for mixed-language documents (Japanese + English, Chinese + English) as it provides the most robust recognition.

### English Documents (--lang en)
```bash
ocr-enhanced --image english_invoice.pdf --lang en --visualize --use-cpu
```

**Recognition Quality:** ⭐⭐⭐⭐⭐ Excellent
- Standard business documents
- Table-heavy invoices
- Mixed fonts and sizes

### Korean Documents (--lang korean)
```bash
ocr-enhanced --image korean_invoice.pdf --lang korean --visualize --use-cpu
```

**Recognition Quality:** ⭐⭐⭐⭐ Good
- Hangul: 한글
- Mixed Korean-English content

## 🎯 Real-World Use Cases

### Use Case 1: Logistics Company - Waybill Processing
**Challenge:** Process 1000+ waybills daily with mixed Chinese/English text

**Solution:**
```bash
ocr-extract --input-dir waybills/ --lang ch --visualize --use-cpu
```

**Results:**
- Batch processing with timestamps
- Automatic document number extraction
- Sender/receiver parsing
- Structured JSON output for database import

### Use Case 2: Accounting Department - Invoice Digitization
**Challenge:** Extract table data from Japanese invoices for accounting system

**Solution:**
```bash
ocr-enhanced --image invoices/*.pdf --lang japan --visualize --use-cpu
```

**Results:**
- HTML table output for easy parsing
- Item-level detail extraction
- Amount and date recognition
- Multi-page PDF support

### Use Case 3: Quality Assurance - OCR Verification
**Challenge:** Verify OCR accuracy and debug recognition issues

**Solution:**
```bash
ocr-raw --image problem_invoice.pdf --lang ch --visualize --use-cpu
```

**Results:**
- Raw PP-Structure output for debugging
- Visual comparison with enhanced mode
- Confidence scores per region
- Original bounding box coordinates

## 📈 Performance Metrics

### Speed Benchmarks
- **Single Page**: 2-5 seconds (CPU mode)
- **10-Page PDF**: 20-50 seconds (CPU mode)
- **GPU Acceleration**: 3-5× faster (if available)

### Accuracy Metrics
- **Text Recognition**: 95-98% accuracy (clean documents)
- **Table Detection**: 90-95% accuracy (standard layouts)
- **Field Extraction**: 85-90% accuracy (structured documents)

## 🛠️ Advanced Visualization Options

### Custom Output Directory
```bash
ocr-enhanced --image invoice.pdf --output-dir custom_results/ --visualize --use-cpu
```

### Batch Processing with Visualization
```bash
ocr-extract --input-dir invoices/ --output-dir batch_results/ --visualize --use-cpu
```

### GPU-Accelerated Processing
```bash
ocr-enhanced --image invoice.pdf --visualize
# Note: Omit --use-cpu to enable GPU acceleration (if CUDA available)
```

## 📝 Notes

1. **Visualization File Size**: Visualization images are typically 500KB-2MB per page depending on document size and complexity.

2. **Color Rendering**: The visualization uses OpenCV for rendering. Colors may appear slightly different depending on the image viewer.

3. **Text Overlay**: Recognized text is displayed above each text box. For very dense documents, some text may overlap.

4. **Coordinate System**: Bounding boxes use [x_min, y_min, x_max, y_max] format. Origin is at top-left corner.

5. **Performance**: First run downloads PaddleOCR models (~100-200MB). Subsequent runs are faster due to caching.

## 🆘 Troubleshooting

### Issue: Visualization images are blank
**Solution:** Check that `--visualize` flag is set and output directory is writable.

### Issue: Chinese/Japanese text not displayed in visualization
**Solution:** Install appropriate fonts (see DOCKER_DEPLOYMENT.md for font configuration).

### Issue: Low confidence scores
**Solution:** Try different language models (--lang ch vs japan vs en) or preprocess images for better quality.

### Issue: Tables not detected
**Solution:** Use `ocr-enhanced` mode instead of `ocr-raw` for better table detection.

## 🔗 Related Documentation

- [README.md](README.md) - Main documentation
- [QUICK_START_GUIDE.md](docs/QUICK_START_GUIDE.md) - Getting started
- [DOCUMENT_EXTRACTION_GUIDE.md](docs/DOCUMENT_EXTRACTION_GUIDE.md) - Field extraction
- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Docker setup with fonts

---

**Made with ❤️ using PaddleOCR and PP-Structure**
