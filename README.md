# OCR Invoice Reader

> 🚀 **Version 2.2 - REST API, CSV Export & Enhanced Performance!**

Document information extraction system using PaddleOCR and PP-Structure. Extract structured information from invoices, waybills, and business documents with advanced table detection.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-v4-orange)](https://github.com/PaddlePaddle/PaddleOCR)
[![Version](https://img.shields.io/badge/version-2.2.6-blue)](setup.py)

📚 **[Complete Documentation Index](DOCUMENTATION_INDEX.md)** | 🚀 **[API Guide](docs/API_USAGE.md)** | ⚡ **[Performance Tips](PERFORMANCE_OPTIMIZATION.md)**

---

## ✨ Features

### Core Capabilities
- ⚡ **PaddleOCR v4 Models** - 30-37% faster than v3
- 🤖 **LLM Integration** - AI-powered text correction and field extraction (NEW!)
- 🔍 **Enhanced Structure Detection** - Coordinate-based table detection
- 📊 **Multi-Page PDF Support** - Process all pages automatically
- 🖼️ **Visual Output** - OCR boxes with region boundaries
- 🌍 **Multi-Language** - Chinese, English, Japanese, Korean
- 📝 **Structured Extraction** - Fields, tables, and layouts
- 🆓 **Free & Open Source** - MIT License

### Processing Modes

| Mode | Speed | Output | Use Case |
|------|-------|--------|----------|
| `ocr-simple` | ⚡⚡⚡ | Text only | Quick extraction |
| `ocr-extract` | ⚡⚡ | Structured fields | Document classification |
| `ocr-enhanced` | ⚡ | Full analysis | Production (Recommended) |
| `ocr-raw` | ⚡ | PP-Structure output | Debugging |
| `ocr-api` | 🌐 | REST API | Web services & integration |

---

## 📦 Installation

### Prerequisites

**Python 3.8+** and **pip** required.

### Quick Install

```bash
# Basic installation
pip install -e .

# With REST API support
pip install -e ".[api]"
```

This will automatically install:
- PaddleOCR 2.8.1+ (with v4 models)
- PaddlePaddle 3.0.0+
- PyMuPDF, OpenCV, Pydantic, etc.
- FastAPI & Uvicorn (with `[api]` option)

### GPU Support (Optional)

For 3-10x faster processing:

```bash
# Install GPU version of PaddlePaddle
pip install paddlepaddle-gpu==3.0.0
```

**Requirements:** NVIDIA GPU with CUDA 11.8 or 12.0

---

## 🚀 Quick Start

### Basic Usage

```bash
# Basic OCR
ocr-enhanced --image invoice.pdf --lang ch

# With LLM post-processing (AI-powered field extraction)
ocr-enhanced --image invoice.pdf --lang ch --use-llm

# With visualization
ocr-enhanced --image invoice.pdf --lang ch --visualize

# Force CPU mode
ocr-enhanced --image invoice.pdf --lang ch --use-cpu
```

### 🤖 LLM Integration (NEW! - Auto Setup)

Enable AI-powered post-processing with **automatic Ollama installation**:

```bash
# Automatic setup (recommended)
ocr-enhanced --image invoice.pdf --lang ch --use-llm --auto-setup-ollama

# Or interactive setup
ocr-enhanced --image invoice.pdf --lang ch --use-llm
# Choose option 1 when prompted
```

**What gets installed automatically:**
- ✅ Ollama service (if not installed)
- ✅ LLM model (qwen2.5:0.5b by default)
- ✅ All dependencies configured

**LLM Features:**
- ✅ Text correction (fix OCR errors)
- ✅ Auto-extract invoice fields (number, date, amount, etc.)
- ✅ Document classification (invoice/receipt/waybill)
- ✅ CPU-friendly models (300MB-2GB)
- ✅ Database-ready CSV export

**Manual setup (if needed):**
```bash
# One-time setup
ocr-setup-ollama

# Then use normally
ocr-enhanced --image invoice.pdf --lang ch --use-llm
```

See [AUTO_SETUP_GUIDE.md](AUTO_SETUP_GUIDE.md) or [LLM_INTEGRATION_GUIDE.md](LLM_INTEGRATION_GUIDE.md) for details.

### Output

The command generates a timestamped output directory:

```
results/
└── 20260514_123456/
    ├── invoice_page_0001.json       # Page 1 structured data (JSON)
    ├── invoice_page_0001.txt        # Page 1 OCR text
    ├── invoice_page_0001_llm.txt    # Page 1 LLM analysis (if --use-llm)
    ├── invoice_page_0001_llm.csv    # Page 1 LLM fields (CSV, if --use-llm)
    ├── invoice_page_0001_viz.jpg    # Visualization (if --visualize)
    ├── ...
    ├── invoice_all_pages.json       # All pages combined (JSON)
    ├── invoice_all_pages.txt        # All pages OCR text
    ├── invoice_all_tables.html      # All tables (HTML)
    ├── invoice_summary.csv          # Page summary (CSV, always)
    ├── invoice_llm_analysis.txt     # LLM analysis summary (if --use-llm)
    └── invoice_llm.csv              # LLM extracted fields summary (CSV, if --use-llm)
```

### Python API

```python
from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer

# Initialize (loads PaddleOCR v4 models)
analyzer = EnhancedStructureAnalyzer(use_gpu=False, lang='ch')

# Process document
result = analyzer.analyze('invoice.pdf')

# Access results
for region in result['regions']:
    print(f"Type: {region.type}, Text: {region.text}")
```

### REST API

```bash
# Start API server
pip install -e ".[api]"
ocr-api

# API Documentation: http://localhost:8000/docs
```

```python
# Python client example
import requests

url = "http://localhost:8000/api/v1/extract"
files = {"file": open("invoice.pdf", "rb")}
response = requests.post(url, files=files, params={"lang": "ch"})

result = response.json()
print(f"Total: {result['document']['total_amount']}")

# Download CSV
task_id = result["task_id"]
csv_response = requests.get(f"http://localhost:8000/api/v1/result/{task_id}/csv?mode=summary")
with open("result.csv", "wb") as f:
    f.write(csv_response.content)
```

---

## 📊 Performance

### PaddleOCR v4 Models

Version 2.1.0 uses PaddleOCR v4 models for improved performance:

| Metric | v3 | v4 | Improvement |
|--------|----|----|-------------|
| **CPU Speed** | 2.5s/page | 1.7s/page | **+32%** ⚡ |
| **GPU Speed** | 0.8s/page | 0.5s/page | **+37%** ⚡ |
| **Accuracy** | 95.2% | 96.8% | **+1.6%** 📈 |
| **Model Size** | 8.5MB | 6.9MB | **-19%** 💾 |

*Tested on A4 invoices with ~100 text boxes*

### Benchmarks

**CPU Mode (Intel i7-10700):**
- Simple text extraction: ~1.2s/page
- Full analysis with tables: ~1.7s/page

**GPU Mode (NVIDIA RTX 3060):**
- Simple text extraction: ~0.3s/page
- Full analysis with tables: ~0.5s/page

---

## 🌍 Language Support

| Language | Code | Quality | Notes |
|----------|------|---------|-------|
| Chinese | `ch` | ⭐⭐⭐⭐⭐ | Recommended for mixed CJK |
| English | `en` | ⭐⭐⭐⭐⭐ | Best for Latin only |
| Japanese | `japan` | ⭐⭐⭐⭐⭐ | Excellent for invoices |
| Korean | `korean` | ⭐⭐⭐⭐ | Good quality |

**Tip:** Use `--lang ch` for documents with mixed Chinese/English/Japanese text.

---

## 📖 Examples

### Process Multi-Page PDF

```bash
ocr-enhanced --image contract.pdf --lang en --output-dir ./results --visualize
```

### Extract Structured Fields

```bash
ocr-extract --image invoice.pdf --lang ch --output-dir ./data
```

### Quick Text Extraction

```bash
ocr-simple --image receipt.jpg --lang en
```

### Batch Processing (Python API)

```python
from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer

analyzer = EnhancedStructureAnalyzer(use_gpu=True, lang='ch')

files = ['invoice1.pdf', 'invoice2.pdf', 'invoice3.pdf']
for file in files:
    result = analyzer.analyze(file)
    print(f"Processed: {file}")
```

---

## 🖼️ GUI Application

Prefer a graphical interface? Check out the desktop app:

### [OCR Invoice Reader GUI](https://github.com/SyuuKasinn/ocr-invoice-reader-gui)

Features:
- 🎯 Drag & drop interface
- 📊 Real-time visualization
- 💾 Export to multiple formats
- 🖥️ Cross-platform (Windows, macOS, Linux)

---

## 🛠️ Advanced Usage

### Custom Output Directory

```bash
ocr-enhanced --image invoice.pdf --lang ch --output-dir /path/to/results
```

### Disable Visualization (Faster)

```bash
ocr-enhanced --image invoice.pdf --lang ch --output-dir ./results
# Note: Omitting --visualize saves 30-40% processing time
```

### Python API - Get PDF Text

```python
from ocr_invoice_reader.processors.file_handler import FileProcessor

processor = FileProcessor(dpi=200)
image_paths = processor.process_file('document.pdf')

# Get extracted text from PDF
pdf_text = processor.get_pdf_text_for_page(image_paths[0], page_num=0)
```

---

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed setup instructions
- **[Usage Guide](docs/USAGE.md)** - Comprehensive usage examples
- **[API Reference](docs/API.md)** - Python API documentation
- **[REST API Usage](docs/API_USAGE.md)** - REST API integration guide
- **[Performance Guide](docs/PERFORMANCE.md)** - Optimization tips

### PaddleOCR v4 Upgrade

- **[Upgrade Guide](docs/v4-upgrade/QUICKSTART.md)** - Quick start with v4 models
- **[What's New](docs/v4-upgrade/WHATS_NEW.md)** - v4 improvements and changes
- **[Migration](docs/v4-upgrade/MIGRATION.md)** - Upgrade from v3 to v4

---

## 🔧 Development

### Project Structure

```
ocr-invoice-reader/
├── ocr_invoice_reader/
│   ├── cli/              # Command-line interfaces
│   ├── processors/       # Core OCR processors (v4 models)
│   ├── extractors/       # Field extractors
│   ├── models/           # Data models
│   └── utils/            # Utilities
├── docs/                 # Documentation
├── examples/             # Example files
├── tests/                # Unit tests
└── setup.py              # Package setup
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=ocr_invoice_reader tests/
```

### Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 🐛 Troubleshooting

### Common Issues

**Q: "PaddleOCR model download failed"**

A: Check your network connection or use a mirror:
```bash
export PADDLEOCR_MODEL_URL="https://paddleocr.bj.bcebos.com/PP-OCRv4"
```

**Q: "GPU not available"**

A: Verify your GPU setup:
```bash
nvidia-smi  # Check GPU
python -c "import paddle; print(paddle.device.get_device())"  # Check PaddlePaddle
```

**Q: "Processing is slow"**

A: Try these optimizations:
- Use GPU: `--use-gpu` (3-10x faster)
- Disable visualization: omit `--visualize` (30-40% faster)
- Use simple mode: `ocr-simple` (2-3x faster)

See **[Performance Guide](docs/PERFORMANCE.md)** for more tips.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR engine with v4 models
- [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) - Deep learning framework
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) - PDF processing
- [OpenCV](https://opencv.org/) - Image processing

---

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/SyuuKasinn/ocr-invoice-reader/discussions)
- 📧 **Email**: [Your Email]

---

## 🗺️ Roadmap

### v2.1.0 (Current)
- ✅ PaddleOCR v4 models
- ✅ 30-37% performance improvement
- ✅ Improved accuracy

### v2.2.0 (Current Development)
- ✅ REST API service with FastAPI
- ✅ CSV export support (summary & items)
- 🔄 Parallel processing for multi-page PDFs
- 🔄 Result caching
- 🔄 Image preprocessing optimization

### v3.0.0 (Future)
- 🤖 LLM-based field extraction
- 🎨 Enhanced visualization options
- 📊 Advanced analytics dashboard

---

## ⭐ Star History

If you find this project useful, please give it a star! ⭐

---

**Made with ❤️ by the OCR Invoice Reader team**
