# OCR Invoice Reader

> 🚀 **Now with PaddleOCR v4 models - 30-37% faster!**

Document information extraction system using PaddleOCR and PP-Structure. Extract structured information from invoices, waybills, and business documents with advanced table detection.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-v4-orange)](https://github.com/PaddlePaddle/PaddleOCR)
[![Version](https://img.shields.io/badge/version-2.1.0-blue)](setup.py)

---

## ✨ Features

### Core Capabilities
- ⚡ **PaddleOCR v4 Models** - 30-37% faster than v3
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

---

## 📦 Installation

### Prerequisites

**Python 3.8+** and **pip** required.

### Quick Install

```bash
pip install -e .
```

This will automatically install:
- PaddleOCR 2.8.1+ (with v4 models)
- PaddlePaddle 3.0.0+
- PyMuPDF, OpenCV, Pydantic, etc.

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
# Process an invoice (CPU mode)
ocr-enhanced --image invoice.pdf --lang ch --use-cpu

# With visualization
ocr-enhanced --image invoice.pdf --lang ch --visualize --use-cpu

# GPU mode (if available)
ocr-enhanced --image invoice.pdf --lang ch --visualize
```

### Output

The command generates a timestamped output directory:

```
results/
└── 20260514_123456/
    ├── invoice_result.json          # Structured data
    ├── invoice_all_pages.txt        # Extracted text
    ├── invoice_tables.html          # HTML tables
    └── invoice_page_0001_viz.jpg    # Visualization
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

### v2.2.0 (Planned)
- 🔄 Parallel processing for multi-page PDFs
- 🔄 Result caching
- 🔄 Image preprocessing optimization

### v3.0.0 (Future)
- 📋 Web API service
- 🤖 LLM-based field extraction
- 🎨 Enhanced visualization options

---

## ⭐ Star History

If you find this project useful, please give it a star! ⭐

---

**Made with ❤️ by the OCR Invoice Reader team**
