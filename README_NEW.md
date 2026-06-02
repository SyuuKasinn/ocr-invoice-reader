# OCR Invoice Reader

> **Document parsing powered by PaddleOCR-VL 1.5**  
> Extract structured data from PDFs and images: JSON + Markdown + Interactive HTML reports

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR--VL-1.5-orange)](https://github.com/PaddlePaddle/PaddleOCR)
[![Version](https://img.shields.io/badge/version-4.0.0-blue)](pyproject.toml)

---

## Features

- **Layout Analysis**: Automatically detect titles, text blocks, tables, and figures
- **OCR Recognition**: Multi-language text recognition (Chinese, English, Japanese, Korean)
- **Table Structure**: Extract tables with HTML format preservation
- **Multiple Outputs**: JSON, Markdown, visualization images, interactive HTML reports
- **Statistics Dashboard**: Performance metrics and confidence analysis
- **GPU Acceleration**: CUDA support for faster processing

---

## Architecture Overview

```
                        User Input
                    (PDF / Image File)
                           |
                           v
                   CLI / Python API
              (ocr_invoice_reader/cli/extract.py)
                           |
                           v
                       Pipeline
            (ocr_invoice_reader/core/pipeline.py)
                           |
      +--------------------|--------------------+
      |                    |                    |
  File I/O          VL Engine         Stats Collector
  (file_io.py)   (vl_engine.py)   (stats_collector.py)
      |                    |                    |
      +--------------------|--------------------+
                           |
                           v
                  PaddleOCR-VL 1.5
     (Layout Analysis + OCR + Table Recognition)
                           |
                           v
                  Processing Results
                           |
      +--------------------|--------------------+
      |         |          |          |         |
   JSON     Markdown   HTML       Viz      Statistics
  Output              Report    Images     Dashboard
```

---

## Quick Start

### Installation

```bash
git clone https://github.com/SyuuKasinn/ocr-invoice-reader.git
cd ocr-invoice-reader

# Install dependencies
pip install paddleocr>=3.0.0
pip install -e .
```

### Basic Usage

**Command Line:**
```bash
# Extract from PDF
python -m ocr_invoice_reader.cli.extract invoice.pdf

# Extract from image with visualization
python -m ocr_invoice_reader.cli.extract invoice.jpg --visualize
```

**Python API:**
```python
from ocr_invoice_reader.core.pipeline import Pipeline
from ocr_invoice_reader.core.config import PipelineConfig, VLConfig, IOConfig

# Configure pipeline
config = PipelineConfig(
    vl=VLConfig(
        use_gpu=True,
    ),
    io=IOConfig(
        output_dir='results',
        save_markdown=True,
        save_visualization=True,
    )
)

# Run extraction
pipeline = Pipeline(config)
document = pipeline.run('invoice.pdf')

# Access results
for page in document.pages:
    print(f"Page {page.page_index + 1}: {len(page.blocks)} regions")
    for block in page.blocks:
        print(f"  [{block.label}] {block.text[:50]}...")
```

---

## Enhanced Features

### Statistics Collection

Track performance metrics and analyze confidence scores:

```python
from ocr_invoice_reader.utils.stats_collector import StatsCollector, format_stats_summary

collector = StatsCollector()
collector.start_document("invoice")

# ... process document ...

collector.end_document()
stats = collector.collect_document_stats(
    all_pages_regions=[[region1, region2], [region3]],
    document_name="invoice"
)

print(format_stats_summary(stats))
```

**Output:**
```
Document: invoice
Pages: 5
Total Time: 12.34s
Throughput: 0.41 pages/sec
Regions: 47 (avg 9.4/page)
Tables: 3
Figures: 2
Text Length: 3,245 chars
Avg Confidence: 92.3%
Low Confidence Pages: 3, 5
```

### Interactive HTML Reports

Generate rich HTML reports with grid view and detail view:

```python
from ocr_invoice_reader.utils.html_report import generate_html_report

generate_html_report(
    document_name="invoice",
    all_pages_regions=[[region1, region2], [region3]],
    image_paths=["page1_vis.jpg", "page2_vis.jpg"],
    stats=stats,  # Optional: include statistics
    output_path="report.html",
)
```

**Features:**
- Grid View: Quick overview of all pages
- Detail View: Deep dive into each page
- Statistics Dashboard: Performance metrics
- Confidence Color Coding: Visual quality indicators (green/orange/red)
- Responsive Design: Works on mobile, tablet, and desktop

---

## Output Formats

### JSON Structure

```json
{
  "document": "invoice",
  "total_pages": 2,
  "pages": [
    {
      "page_index": 0,
      "blocks": [
        {
          "label": "title",
          "bbox": [100, 50, 500, 120],
          "text": "INVOICE",
          "score": 0.95
        },
        {
          "label": "table",
          "bbox": [50, 150, 550, 400],
          "html": "<table>...</table>",
          "score": 0.88
        }
      ],
      "markdown": "# INVOICE\n\n| Item | Price |\n|------|-------|\n| ... | ... |"
    }
  ]
}
```

### Markdown

```markdown
# INVOICE

**Date:** 2026-06-02  
**Invoice No:** INV-001

## Items

| Description | Quantity | Price |
|-------------|----------|-------|
| Product A   | 10       | $100  |
| Product B   | 5        | $50   |

**Total:** $150
```

### HTML Report (Interactive)

- Dual view modes (grid/detail)
- Embedded statistics
- Visualization images
- Responsive layout
- Confidence indicators

---

## Data Models

All results are strongly typed using Pydantic v2:

```python
class Block(BaseModel):
    """A single region/block in a page."""
    label: str                    # 'title', 'text', 'table', 'figure'
    bbox: List[float]             # [x1, y1, x2, y2]
    text: str                     # Extracted text
    html: Optional[str] = None    # HTML for tables
    image_path: Optional[str] = None  # Path for figures
    score: Optional[float] = None  # Confidence score

class PageResult(BaseModel):
    """Results for a single page."""
    page_index: int
    source_file: str
    blocks: List[Block]
    markdown: Optional[str] = None
    image_path: Optional[str] = None

class DocumentResult(BaseModel):
    """Complete document results."""
    document: str
    total_pages: int
    pages: List[PageResult]
```

---

## Configuration

### VLConfig

```python
VLConfig(
    use_gpu: bool = True,                        # Use GPU if available
    use_doc_orientation_classify: bool = False,   # Rotate correction
    use_doc_unwarping: bool = False,              # Perspective correction
)
```

### IOConfig

```python
IOConfig(
    output_dir: str = "results",           # Output directory
    save_markdown: bool = True,            # Save Markdown files
    save_visualization: bool = True,       # Save visualization images
    save_per_page_json: bool = False,      # Save JSON per page
    inline_images_in_html: bool = False,   # Embed images in HTML (larger file)
)
```

---

## Performance

| Mode | Speed (pages/sec) | GPU Required |
|------|-------------------|--------------|
| CPU  | 0.03 - 0.1        | No           |
| GPU  | 0.3 - 0.5         | Yes (CUDA)   |

**Processing Time Examples:**
- Single page: 2-5 seconds (GPU) / 10-30 seconds (CPU)
- 10-page document: 20-50 seconds (GPU) / 100-300 seconds (CPU)

**Memory Usage:**
- Base: ~2GB (PaddleOCR-VL models)
- Peak: +500MB per page during processing

---

## Requirements

- Python >= 3.10
- paddleocr >= 3.0.0
- paddlepaddle >= 3.2.0 (CPU) or paddlepaddle-gpu >= 3.2.0 (GPU)
- opencv-python >= 4.8.0
- numpy >= 1.24.0
- Pillow >= 10.0.0
- pydantic >= 2.0.0

**For GPU acceleration:**
- NVIDIA GPU with CUDA support
- CUDA >= 11.8 or 12.x
- 4GB+ VRAM recommended

---

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) - Detailed system architecture
- [Enhancement Features](ENHANCEMENTS_README.md) - Statistics and HTML reports
- [API Reference](docs/API.md) - Complete API documentation (coming soon)

---

## Examples

### Process Multiple Files

```bash
for file in invoices/*.pdf; do
    python -m ocr_invoice_reader.cli.extract "$file" --visualize
done
```

### Custom Post-Processing

```python
from ocr_invoice_reader.core.pipeline import Pipeline

pipeline = Pipeline(config)
document = pipeline.run('invoice.pdf')

# Custom processing
for page in document.pages:
    for block in page.blocks:
        if block.label == "table" and block.html:
            # Extract data from table HTML
            process_table(block.html)
```

### Stream Processing

```python
from ocr_invoice_reader.core.pipeline import Pipeline

def on_page_complete(page_result):
    """Called after each page is processed."""
    print(f"Completed page {page_result.page_index + 1}")
    # Save immediately, don't wait for entire document
    save_page(page_result)

pipeline = Pipeline(config)
document = pipeline.run_and_save(
    input_path='large_document.pdf',
    on_page=on_page_complete
)
```

---

## Testing

Run the test suite:

```bash
# Basic functionality tests
python test_enhancements.py

# Integration tests with real PDFs
python test_enhanced_features.py

# Full integration test
python test_full_integration.py path/to/invoice.pdf
```

---

## Troubleshooting

### PaddleOCR-VL Import Error

```
ImportError: cannot import name 'PaddleOCRVL'
```

**Solution:** Upgrade paddleocr to >= 3.0
```bash
pip install --upgrade "paddleocr>=3.0.0"
```

### GPU Not Detected

```
WARNING: using CPU
```

**Solution:** Install GPU version of paddlepaddle
```bash
# For CUDA 11.8
pip install paddlepaddle-gpu==3.2.0

# For CUDA 12.0
pip install paddlepaddle-gpu==3.2.0 -f https://www.paddlepaddle.org.cn/whl/linux/cu120/stable.html
```

### Out of Memory

**Solution:** Process fewer pages at once or use CPU mode
```python
# Process in batches
for i in range(0, total_pages, 10):
    document = pipeline.run('doc.pdf', max_pages=i+10)
```

---

## Roadmap

- [x] PaddleOCR-VL 1.5 integration
- [x] Statistics collection and analysis
- [x] Interactive HTML reports
- [x] Multi-language support
- [ ] Batch processing optimization
- [ ] REST API service
- [ ] Docker deployment
- [ ] Cloud platform support

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR engine and VL pipeline
- [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) - Deep learning framework
- [Pydantic](https://github.com/pydantic/pydantic) - Data validation

---

## Support

- **Issues**: [GitHub Issues](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SyuuKasinn/ocr-invoice-reader/discussions)

---

**Made for document processing automation**
