# Test Results for OCR Invoice Reader

## Test Environment
- **Test Date**: 2026-06-02
- **Platform**: Windows 11 Pro 10.0.26200
- **Python Version**: 3.10
- **PaddleOCR Version**: v4 (PaddleOCR-VL-1.6-0.9B)
- **Hardware**: CPU (no CUDA GPU detected)

## Test Files

### 1. インボイス見本.pdf (Invoice Sample)
- **File Path**: `C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\インボイス見本.pdf`
- **File Size**: 1,962,630 bytes (1.9 MB)
- **Description**: Japanese invoice sample document

### 2. INVOICE.pdf (Invoice Main)
- **File Path**: `C:\Work\SVN\trunk\SBS_GLOVIA\00.資料\INVOICE関連\INVOICE.pdf`
- **File Size**: 2,188,863 bytes (2.1 MB)
- **Description**: Main invoice document

## Test Scripts

### simple_pdf_test.py
Simple test script using PaddleOCR-VL without LLM enhancement:
- CPU-only processing for faster initialization
- Generates markdown, visualization, and JSON outputs per page
- Tests both invoice PDFs sequentially

### test_invoice_pdfs.py
Comprehensive test script with full configuration:
- GPU/CPU auto-detection
- Japanese language support
- Full visualization and JSON export
- Detailed region detection and text extraction

## Expected Outputs

Each test generates the following outputs in `test_results/<output_name>_<timestamp>/`:

1. **Markdown files** (`*.md`) - Structured text output
2. **Visualization files** (`*_viz.jpg`) - Annotated images showing detected regions
3. **JSON files** (`*_page_*.json`) - Structured data per page including:
   - Detected regions (text, tables, figures, headers, footers, etc.)
   - OCR confidence scores
   - Bounding boxes for each region
   - Extracted text content

## Test Status

### Test Execution

```bash
# Run simple test
cd C:/Users/kants/ocr-invoice-reader
python simple_pdf_test.py

# Run comprehensive test
python test_invoice_pdfs.py
```

## Known Issues

1. **Unicode Display**: Windows console (CP932) cannot display emoji characters - fixed by using plain text labels
2. **GPU Support**: PaddlePaddle-GPU not installed - tests run on CPU (slower but functional)
3. **Processing Time**: CPU processing can take several minutes per page (expected behavior)

## Performance Metrics

Expected processing times on CPU:
- **Model Loading**: ~40 seconds (one-time initialization)
- **Per Page Processing**: 30-90 seconds depending on content complexity
- **Total Time** (2 files): Approximately 5-10 minutes

## Validation Checklist

- [x] Test scripts created
- [x] Test environment configured
- [x] PaddleOCR-VL model loaded successfully
- [ ] First PDF (インボイス見本.pdf) processed successfully
- [ ] Second PDF (INVOICE.pdf) processed successfully
- [ ] Output files generated
- [ ] Markdown output validated
- [ ] JSON structure validated
- [ ] Visual annotations generated
- [ ] Test summary report created

> **Note**: Tests are designed to run on both CPU and GPU. CPU processing may take 5-10 minutes total.

## Next Steps

1. Wait for test completion
2. Review generated output files
3. Validate extracted data accuracy
4. Update GitHub repository with:
   - Test scripts (simple_pdf_test.py, test_invoice_pdfs.py)
   - This test results documentation
   - Sample output files (if appropriate)
   - README section on testing

## Notes

- Tests are running in background processes
- Output logs saved to respective `.txt` files
- Results will be available in `test_results/` directory after completion
