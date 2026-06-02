# OCR Invoice Reader

<div align="center">

**High-Performance Document Extraction System**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-v4-orange)](https://github.com/PaddlePaddle/PaddleOCR)
[![Version](https://img.shields.io/badge/version-2.3.2-blue)](setup.py)

Extract structured data from invoices, waybills, and customs documents using PaddleOCR v4 and optional LLM enhancement.

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Testing](#-testing)

</div>

---

## 🌟 Features

### Core Capabilities
- **Intelligent OCR**: PaddleOCR v4 with document layout analysis
- **Multi-Language**: Chinese, English, Japanese support
- **Parallel Processing**: 3-7x speedup with multi-worker architecture
- **LLM Enhancement**: Optional Qwen2.5 integration for 93% accuracy
- **Flexible Output**: JSON, CSV, SQL, Markdown formats

### Performance
| Method | Speed | Accuracy | Best For |
|--------|-------|----------|----------|
| Basic OCR | Fast (3s/page) | Good | Simple invoices |
| OCR + LLM | Moderate (15-49s/page) | Excellent (93%) | Complex documents |
| Parallel (3 workers) | 3.2x faster | Excellent | Batch processing |

### Specialized Features
- **GLOVIA Mode**: Optimized for Japanese customs clearance (18% accuracy improvement)
- **Table Detection**: Coordinate-based analysis for structured data
- **Visual Output**: Annotated images with detected regions
- **Hybrid Architecture**: LLM-first with regex fallback for reliability

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- 5GB free disk space

### Basic Installation

```bash
# Clone repository
git clone https://github.com/SyuuKasinn/ocr-invoice-reader.git
cd ocr-invoice-reader

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### GPU Acceleration (Optional)

For NVIDIA GPUs with CUDA:

```bash
# Install GPU dependencies
pip install -r requirements-gpu.txt
pip install -e .
```

### Verify Installation

```bash
# Check environment and hardware
ocr-check-env
```

---

## 🚀 Quick Start

### Command Line Interface

#### Basic OCR (No LLM)
```bash
# Process a single invoice
python -m ocr_invoice_reader.cli.extract invoice.pdf

# With visualization
python -m ocr_invoice_reader.cli.extract invoice.pdf --visualize
```

#### With LLM Enhancement
```bash
# Auto-detect hardware and select optimal model
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm

# Specify model size (3b/7b/14b)
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm --llm-model 7b

# For GLOVIA customs clearance
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm --glovia-mode
```

#### Parallel Processing
```bash
# 3 workers (recommended for 8-16GB RAM)
python -m ocr_invoice_reader.cli.parallel invoice.pdf --workers 3 --use-llm

# 6 workers (for 32GB+ RAM)
python -m ocr_invoice_reader.cli.parallel invoice.pdf --workers 6 --use-llm
```

### Python API

```python
from pathlib import Path
from ocr_invoice_reader.core.pipeline import Pipeline
from ocr_invoice_reader.core.config import PipelineConfig, VLConfig, IOConfig

# Configure pipeline
config = PipelineConfig(
    vl=VLConfig(
        use_gpu=True,  # Auto-detects GPU availability
        lang='japan',  # Language: 'ch', 'en', 'japan'
    ),
    io=IOConfig(
        output_dir='results',
        save_markdown=True,
        save_visualization=True,
        save_per_page_json=True,
    )
)

# Process document
pipeline = Pipeline(config)
document = pipeline.run('invoice.pdf')

# Access results
for page in document.pages:
    print(f"Page {page.page_index + 1}:")
    print(f"  Detected regions: {len(page.blocks)}")
    
    for block in page.blocks:
        print(f"  - {block.label}: {block.text[:50]}...")
```

### Output Structure

```
results/20260602_123456/
├── invoice_page_0001.json          # Structured data per page
├── invoice_page_0001.md            # Markdown formatted text
├── invoice_page_0001_viz.jpg       # Visual annotations
├── invoice_all_pages.json          # Combined results
└── invoice_summary.json            # Document summary
```

---

## 📖 Documentation

### Configuration Options

#### VLConfig (OCR Settings)
```python
VLConfig(
    use_gpu=True,                        # Enable GPU acceleration
    lang='japan',                        # Language: 'ch', 'en', 'japan'
    use_doc_orientation_classify=False,  # Detect page rotation
    use_doc_unwarping=False,            # Correct document distortion
)
```

#### IOConfig (Input/Output Settings)
```python
IOConfig(
    output_dir='results',              # Output directory
    pdf_dpi=300,                       # PDF conversion resolution
    save_markdown=True,                # Generate markdown files
    save_visualization=True,           # Generate annotated images
    save_per_page_json=True,          # Save JSON per page
    inline_images_in_html=True,       # Embed images in HTML
)
```

### LLM Models

| Model | Size | RAM/VRAM | Speed | Accuracy | Best For |
|-------|------|----------|-------|----------|----------|
| 3B | 2GB | Fast | Good | CPU systems, quick processing |
| 7B | 4GB | Moderate | Excellent | Balanced performance (recommended) |
| 14B | 8GB | Slow | Best | High accuracy requirements |

### Output Formats

#### JSON
```json
{
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-01-15",
  "total_amount": 135600.0,
  "currency": "JPY",
  "shipper": "ABC Company Ltd.",
  "consignee": "XYZ Corporation",
  "items": [
    {
      "description": "Product A",
      "quantity": 100,
      "unit_price": 1200.0,
      "amount": 120000.0
    }
  ]
}
```

#### CSV
```csv
invoice_number,invoice_date,total_amount,currency,shipper,consignee
INV-2024-001,2024-01-15,135600.0,JPY,ABC Company Ltd.,XYZ Corporation
```

#### SQL
```sql
INSERT INTO invoices (invoice_number, invoice_date, total_amount, currency)
VALUES ('INV-2024-001', '2024-01-15', 135600.0, 'JPY');
```

---

## 🧪 Testing

### Quick Test

```bash
# Test with sample invoice (basic OCR)
python simple_pdf_test.py
```

### Comprehensive Testing

```bash
# Full pipeline test with LLM
python test_invoice_pdfs.py

# Integration tests
python test_full_integration.py
python test_enhanced_features.py
python test_enhancements.py
```

### Test Scripts

| Script | Purpose | Duration | Output |
|--------|---------|----------|--------|
| `simple_pdf_test.py` | Basic OCR validation | 2-5 min | JSON, MD, Images |
| `test_invoice_pdfs.py` | Full pipeline with LLM | 5-10 min | JSON, MD, Images |
| `test_full_integration.py` | End-to-end integration | 3-8 min | Full report |
| `test_enhanced_features.py` | Feature validation | 2-4 min | Feature logs |
| `test_enhancements.py` | Enhancement tests | 2-4 min | Test results |

### Expected Output

Tests generate results in `test_results/<test_name>_<timestamp>/`:

```
test_results/invoice_sample_20260602_123456/
├── page_0001.json              # Structured data
├── page_0001.md                # Markdown text
├── page_0001_viz.jpg           # Visual annotations
└── summary.json                # Test summary
```

For detailed test results, see [TEST_RESULTS.md](TEST_RESULTS.md).

---

## 🎯 Use Cases

### 1. Standard Invoice Processing
Extract key fields from commercial invoices:
- Invoice number, date, due date
- Shipper and consignee information
- Item details (description, quantity, price)
- Totals, taxes, currency

**Command:**
```bash
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm
```

### 2. GLOVIA Customs Clearance
Specialized extraction for Japanese customs:
- MAWB/HAWB numbers (separated)
- TEL fields for importer matching
- Address with ZIP code extraction
- Tax details (customs duty, consumption tax)

**Command:**
```bash
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm --glovia-mode
```

### 3. Batch Processing
Process multiple documents efficiently:

```bash
# Process all PDFs in a directory
for file in invoices/*.pdf; do
    python -m ocr_invoice_reader.cli.parallel "$file" --workers 3 --use-llm
done
```

### 4. Integration with Business Systems
Use Python API for system integration:

```python
from ocr_invoice_reader.core.pipeline import Pipeline
from your_erp_system import upload_invoice

# Process invoice
pipeline = Pipeline()
document = pipeline.run('invoice.pdf')

# Extract data
invoice_data = {
    'number': document.invoice_number,
    'date': document.invoice_date,
    'amount': document.total_amount,
}

# Upload to ERP
upload_invoice(invoice_data)
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. GPU Not Detected

**Symptom:** Warning message "PaddlePaddle not compiled with CUDA"

**Solution:**
```bash
# Uninstall existing PaddlePaddle
pip uninstall -y paddlepaddle paddlepaddle-gpu

# Install GPU version
pip install paddlepaddle-gpu -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

# Verify GPU support
python -c "import paddle; print(paddle.is_compiled_with_cuda())"
```

#### 2. Out of Memory Error

**Solution:**
```bash
# Use smaller LLM model
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm --llm-model 3b

# Reduce parallel workers
python -m ocr_invoice_reader.cli.parallel invoice.pdf --workers 2

# Force CPU mode
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-cpu
```

#### 3. Slow Processing

**Solution:**
```bash
# Enable GPU acceleration
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm

# Use quantization (GPU only)
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm --llm-quantization int4

# Use parallel processing
python -m ocr_invoice_reader.cli.parallel invoice.pdf --workers 3
```

#### 4. Poor Accuracy

**Solution:**
```bash
# Use larger LLM model
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm --llm-model 14b

# Enable GLOVIA mode for Japanese documents
python -m ocr_invoice_reader.cli.extract invoice.pdf --use-llm --glovia-mode

# Increase PDF DPI
python -m ocr_invoice_reader.cli.extract invoice.pdf --dpi 400
```

### Getting Help

1. **Check environment:**
   ```bash
   ocr-check-env
   ```

2. **View logs:**
   Check `*.log` files in the output directory

3. **Report issues:**
   [GitHub Issues](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)

---

## 📊 Performance Benchmarks

### Processing Speed

| Document Type | Pages | Basic OCR | OCR + LLM | Parallel (3w) | Parallel (6w) |
|--------------|-------|-----------|-----------|---------------|---------------|
| Simple invoice | 1 | 3s | 49s | 15s | 12s |
| Complex invoice | 8 | 24s | 392s | 123s | 98s |
| Large batch | 50 | 150s | 2,450s | 768s | 613s |

*Tested on: Intel i7-10700K, 32GB RAM, NVIDIA RTX 3080*

### Accuracy Comparison

| Method | Standard Invoices | Complex Layout | Multi-language | GLOVIA Customs |
|--------|------------------|----------------|----------------|----------------|
| Basic OCR | 75% | 65% | 70% | 60% |
| OCR + Regex | 82% | 72% | 78% | 75% |
| **OCR + LLM** | **93%** | **89%** | **91%** | **93%** |

### System Requirements

| Configuration | CPU | RAM | GPU | Disk | Best For |
|--------------|-----|-----|-----|------|----------|
| Minimum | Any | 8GB | None | 5GB | Small batches |
| Recommended | 4+ cores | 16GB | 8GB VRAM | 15GB | Production use |
| Optimal | 8+ cores | 32GB | 16GB VRAM | 20GB | Large batches |

---

## 🗺️ Roadmap

### Completed
- [x] PaddleOCR v4 integration
- [x] Multi-language support (CN/EN/JP)
- [x] LLM-based extraction with Qwen2.5
- [x] Parallel processing (3-7x speedup)
- [x] GLOVIA customs optimization
- [x] Comprehensive test suite
- [x] Python API and CLI

### In Progress
- [ ] Web UI for easy document upload
- [ ] Docker containerization
- [ ] REST API service

### Planned
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] Multi-model ensemble for higher accuracy
- [ ] Real-time processing pipeline
- [ ] Support for more document types (receipts, forms)
- [ ] OCR result post-editing interface

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Ways to Contribute
1. **Report bugs** - Open an issue with details
2. **Suggest features** - Share your ideas
3. **Improve documentation** - Fix typos, add examples
4. **Submit code** - Fork, develop, and create PR

### Development Setup

```bash
# Clone and setup
git clone https://github.com/SyuuKasinn/ocr-invoice-reader.git
cd ocr-invoice-reader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/
```

### Pull Request Process
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Summary:**
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Private use allowed
- ⚠️ Liability and warranty not provided

---

## 🙏 Acknowledgments

This project builds upon excellent open-source technologies:

- **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** - Powerful OCR engine by Baidu
- **[Qwen2.5](https://github.com/QwenLM/Qwen2.5)** - Advanced language model by Alibaba
- **[Hugging Face Transformers](https://github.com/huggingface/transformers)** - ML model framework
- **[PaddlePaddle](https://github.com/PaddlePaddle/Paddle)** - Deep learning framework

Special thanks to all contributors and the open-source community.

---

## 📞 Support & Contact

### Get Help
- **Documentation**: [GitHub Wiki](https://github.com/SyuuKasinn/ocr-invoice-reader/wiki)
- **Issues**: [GitHub Issues](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SyuuKasinn/ocr-invoice-reader/discussions)

### Report a Bug
When reporting bugs, please include:
1. Python version
2. Operating system
3. Error message or unexpected behavior
4. Steps to reproduce
5. Sample file (if possible)

### Request a Feature
For feature requests:
1. Describe the use case
2. Explain the expected behavior
3. Suggest implementation approach (optional)

---

<div align="center">

**Built with ❤️ for invoice processing automation**

[⬆ Back to Top](#ocr-invoice-reader)

</div>
