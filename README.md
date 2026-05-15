# OCR Invoice Reader

> 🚀 **Version 2.3.2 - Direct Qwen Integration & CPU/GPU Auto-Detection**

High-performance document extraction system using PaddleOCR v4 and LLM enhancement. Extract structured data from invoices, waybills, and customs documents with **3-7x parallel speedup** and **93% accuracy**.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-v4-orange)](https://github.com/PaddlePaddle/PaddleOCR)
[![Version](https://img.shields.io/badge/version-2.3.2-blue)](setup.py)

## 📚 Documentation

- **[Complete Guide](docs/COMPLETE_GUIDE.md)** - Comprehensive documentation
- **[Quick Start](guides/QUICK_START_HYBRID.md)** - 5-minute setup
- **[API Usage](docs/API_USAGE.md)** - Python API reference
- **[Parallel Processing](guides/PARALLEL_PROCESSING.md)** - 3-7x speedup guide
- **[GLOVIA Integration](guides/GLOVIA_INVOICE_EXTRACTION.md)** - Customs clearance optimization

---

## ✨ Key Features

### Performance
- ⚡ **3-7x Parallel Speedup** - Process 8 pages in 2 minutes (vs 6.5 minutes serial)
- 🚀 **PaddleOCR v4** - 30-37% faster than v3
- 📊 **93% Accuracy** - LLM + Regex hybrid extraction

### Intelligence
- 🤖 **LLM Enhancement** - Smart field extraction with Qwen2.5
- 🔄 **Hybrid Architecture** - LLM-first with regex fallback
- 🎯 **GLOVIA Optimized** - Specialized for Japanese customs clearance
- 🌍 **Multi-language** - Chinese, English, Japanese support

### Output
- 📝 **Structured Data** - JSON, CSV, SQL formats
- 🔍 **Invoice Fields** - Number, date, amount, tax details, items
- 📊 **Table Detection** - Smart coordinate-based analysis
- 🖼️ **Visual Output** - Annotated images with OCR boxes

---

## 🚀 Quick Start

### Installation

#### Auto-Installation (Recommended)

The smart installer automatically detects your hardware (CPU/GPU) and installs the appropriate dependencies:

```bash
git clone https://github.com/SyuuKasinn/ocr-invoice-reader.git
cd ocr-invoice-reader

# Smart installer - auto-detects GPU and installs correct packages
bash scripts/install.sh
```

#### Manual Installation

**For GPU systems** (NVIDIA GPU with CUDA):
```bash
pip install -r requirements-gpu.txt
pip install -e .
```

**For CPU-only systems**:
```bash
pip install -r requirements-cpu.txt
pip install -e .
```

#### Check Environment

Verify your installation and see recommended settings:

```bash
ocr-check-env
# Or: python -m ocr_invoice_reader.cli.check_env
```

### Basic Usage

```bash
# Simple OCR (no LLM)
ocr-enhanced --image invoice.pdf --visualize

# With LLM enhancement (auto-detects best model for your hardware)
ocr-enhanced --image invoice.pdf --use-llm

# Parallel processing (3-7x faster)
ocr-enhanced-parallel --image invoice.pdf --use-llm --workers 3
```

### 🚀 GPU Acceleration

**Direct Qwen integration with automatic GPU acceleration!**

The system automatically detects your hardware and uses:
- **GPU available**: Fast inference with INT4/INT8 quantization
- **CPU only**: Optimized for CPU with smaller models

**Model Selection Guide:**
- `3b` - Fast, CPU-friendly (2GB) ⚡
- `7b` - Balanced, recommended for GPU (4GB VRAM with quantization) ⚡⚡
- `14b` - High accuracy, requires powerful GPU (8GB VRAM with quantization) ⚡⚡⚡

```bash
# Auto-select model based on hardware
ocr-enhanced --image invoice.pdf --use-llm

# Manually specify model size
ocr-enhanced --image invoice.pdf --use-llm --llm-model 7b

# Control quantization (GPU only)
ocr-enhanced --image invoice.pdf --use-llm --llm-model 7b --llm-quantization int4
```

See [docs/QWEN_DIRECT_SETUP.md](docs/QWEN_DIRECT_SETUP.md) for detailed configuration.

### Output

```
results/20260515_123456/
├── invoice_page_0001.json          # Structured data
├── invoice_page_0001.txt           # Extracted text
├── invoice_page_0001_llm.json      # Invoice fields
├── invoice_page_0001_viz.jpg       # Visual output
├── invoice_all_pages.json          # Combined results
└── invoice_invoices.json           # All invoice data
```

---

## 📖 Usage Examples

### Serial Processing (Standard)

```bash
# CPU mode (no GPU required)
ocr-enhanced --image invoice.pdf --lang ch --use-cpu

# GPU mode (faster)
ocr-enhanced --image invoice.pdf --lang ch

# With LLM for better accuracy
ocr-enhanced --image invoice.pdf --lang ch --use-llm
```

**Performance**: ~49s per page with LLM

### Parallel Processing (Recommended)

```bash
# 3 workers (recommended for 8-16GB RAM)
ocr-enhanced-parallel --image invoice.pdf --use-llm --workers 3

# 6 workers (for 32GB+ RAM)
ocr-enhanced-parallel --image invoice.pdf --use-llm --workers 6
```

**Performance**: 
- 8 pages: **123s** (vs 392s serial) - **3.2x faster**
- 50 pages: **12.8 min** (vs 40.8 min serial) - **68% time saved**

### Python API

```python
from ocr_invoice_reader.utils.llm_invoice_extractor import LLMInvoiceExtractor
from ocr_invoice_reader.utils.qwen_direct_processor import create_qwen_processor

# Initialize (auto-detects GPU and selects optimal settings)
llm_processor = create_qwen_processor(model_size='7b', use_gpu=True, quantization='int4')
extractor = LLMInvoiceExtractor(llm_processor)

# Extract
result = extractor.extract_from_text(ocr_text)
invoice_data = result['invoice_data']

# Access fields
print(f"Invoice: {invoice_data['invoice_number']}")
print(f"Amount: {invoice_data['total_amount']}")
```

---

## 🎯 Use Cases

### Standard Invoices

**Command**: `ocr-enhanced --image invoice.pdf --use-llm`

**Extracts**:
- Invoice number, date
- Company names (shipper/consignee)
- Total amount, currency
- Phone, fax, address
- Item list

### GLOVIA Customs Clearance

**Command**: `ocr-enhanced --image invoice.pdf --use-llm --glovia-mode`

**Specialized Extraction**:
- MAWB/HAWB numbers (separated)
- TEL field (critical for importer matching)
- Address ZIP (postal code extraction)
- Tax details (customs duty, consumption tax)
- 18% accuracy improvement over generic

### Batch Processing

```bash
# Process multiple files
for file in invoices/*.pdf; do
  ocr-enhanced-parallel --image "$file" --use-llm --workers 3
done
```

---

## 📊 Performance Comparison

| Method | 8 Pages | Per Page | Speedup |
|--------|---------|----------|---------|
| **Serial (no LLM)** | 24s | 3s | 1x |
| **Serial (with LLM)** | 392s | 49s | - |
| **Parallel (3 workers)** | **123s** | **15.4s** | **3.2x** |
| **Parallel (6 workers)** | **98s** | **12.3s** | **4.0x** |

### Accuracy Comparison

| Extractor | Accuracy | Use Case |
|-----------|----------|----------|
| **Regex only** | 75% | Standard formats |
| **LLM hybrid** | **93%** | Diverse formats |
| **GLOVIA optimized** | **93%** | Customs clearance |

---

## 🛠️ Advanced Features

### LLM Models

```bash
# Fast model (3B, CPU-friendly)
ocr-enhanced --image invoice.pdf --use-llm --llm-model 3b

# Balanced model (7B, recommended for GPU)
ocr-enhanced --image invoice.pdf --use-llm --llm-model 7b

# High accuracy model (14B, requires powerful GPU)
ocr-enhanced --image invoice.pdf --use-llm --llm-model 14b
```

### Hybrid Extraction

**Automatic fallback** for reliability:

```
OCR Text → LLM Extraction → Validation
                              ↓
                         ✓ Pass → Use LLM result (93% accurate)
                              ↓
                         ✗ Fail → Regex fallback (reliable)
```

### Output Formats

**JSON** (structured):
```json
{
  "invoice_number": "NCY250924",
  "invoice_date": "2025-09-24",
  "total_amount": 135600.0,
  "currency": "JPY"
}
```

**CSV** (spreadsheet):
```csv
invoice_number,invoice_date,total_amount,currency
NCY250924,2025-09-24,135600.0,JPY
```

**SQL** (database):
```sql
INSERT INTO invoices (invoice_number, invoice_date, total_amount, currency)
VALUES ('NCY250924', '2025-09-24', 135600.0, 'JPY');
```

---

## 📋 System Requirements

### Minimum (CPU-only)
- Python 3.8+
- 8GB RAM
- 5GB disk space
- CPU (any)

### Recommended (GPU-accelerated)
- Python 3.10+
- 16GB RAM
- 15GB disk space
- NVIDIA GPU with 8GB+ VRAM
- CUDA 11.8 or 12.0+

### For Parallel Processing
- 8GB+ RAM (3 workers)
- 16GB+ RAM (6 workers)
- Multi-core CPU (4+ cores)

### Model Requirements
- **3B model**: 2-4GB RAM (CPU) or 2GB VRAM (GPU)
- **7B model**: 6-8GB RAM (CPU) or 4GB VRAM with quantization (GPU)
- **14B model**: 12-16GB RAM (CPU) or 8GB VRAM with quantization (GPU)

---

## 🔧 Troubleshooting

### Check Your Environment

```bash
# Diagnose hardware and dependencies
ocr-check-env
```

### PaddlePaddle GPU Not Working

If you see "WARNING: PaddlePaddle not compiled with CUDA":

```bash
# Quick fix script
bash scripts/fix_paddle_gpu.sh

# Or manually:
pip uninstall -y paddlepaddle paddlepaddle-gpu
pip install paddlepaddle-gpu==2.6.2.post120 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

# Verify
python -c "import paddle; print(paddle.is_compiled_with_cuda())"
```

**Note**: LLM uses GPU regardless of PaddlePaddle status. This fix accelerates OCR portion.

### LLM Loading Error

```bash
# Use smaller model for limited memory
ocr-enhanced --image invoice.pdf --use-llm --llm-model 3b

# Force CPU mode
ocr-enhanced --image invoice.pdf --use-llm --use-cpu
```

### Memory Error

```bash
# Reduce workers
ocr-enhanced-parallel --image invoice.pdf --workers 2

# Or use serial processing
ocr-enhanced --image invoice.pdf --use-llm
```

### Slow Processing

```bash
# Use GPU if available (check with check_env)
ocr-enhanced --image invoice.pdf --use-llm --llm-model 7b

# Use parallel processing
ocr-enhanced-parallel --image invoice.pdf --use-llm --workers 3

# Use quantization (GPU only)
ocr-enhanced --image invoice.pdf --use-llm --llm-quantization int4
```

More solutions: [Complete Guide](docs/COMPLETE_GUIDE.md#troubleshooting)

---

## 📚 Documentation Structure

```
docs/
├── COMPLETE_GUIDE.md           # Main documentation
├── API_USAGE.md                # Python API reference
├── DOCUMENT_EXTRACTION_GUIDE.md # Extraction guide
└── QUICK_START_GUIDE.md        # Getting started

guides/
├── QUICK_START_HYBRID.md       # Hybrid extraction
├── PARALLEL_PROCESSING.md      # Performance optimization
├── GLOVIA_INVOICE_EXTRACTION.md # GLOVIA integration
├── LLM_HYBRID_EXTRACTION.md    # LLM architecture
├── PERFORMANCE_COMPARISON.md   # Benchmarks
├── EXTRACTOR_V2_IMPROVEMENTS.md # Extractor details
└── INVOICE_EXTRACTION.md       # Invoice guide
```

---

## 🗺️ Roadmap

- [x] PaddleOCR v4 integration
- [x] LLM-based extraction
- [x] Parallel processing (3-7x speedup)
- [x] GLOVIA optimization
- [ ] Web UI
- [ ] Docker support
- [ ] Cloud deployment
- [ ] Multi-model ensemble

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** - OCR engine
- **[Qwen2.5](https://github.com/QwenLM/Qwen2.5)** - Language model
- **[Hugging Face Transformers](https://github.com/huggingface/transformers)** - LLM inference

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)
- **Documentation**: [Complete Guide](docs/COMPLETE_GUIDE.md)
- **Examples**: See `examples/` directory

---

**Made with ❤️ for invoice processing automation**
