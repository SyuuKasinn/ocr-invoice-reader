# Release v2.2.7 - GPU Support & Smart Timeout Management

## 🎉 What's New

### 🚀 GPU Acceleration for LLM
- **Ollama now automatically uses NVIDIA GPU** when available
- **3-5x faster LLM inference** compared to CPU-only processing
- Automatic GPU detection and configuration
- Comprehensive GPU setup script for easy configuration

### ⏱️ Smart Timeout Management
No more timeout errors with large language models! The system now automatically adjusts timeout based on model size:

| Model Size | Timeout | Use Case |
|------------|---------|----------|
| 0.5b, mini | 60s | Fast, CPU-friendly |
| 7B | 120s | Balanced accuracy |
| 14B | 180s | High accuracy |
| Unknown/Large | 300s | Maximum compatibility |

### 📊 Performance Benchmarks

**With GPU (NVIDIA RTX 3060, 12GB VRAM):**
- `qwen2.5:7b`: ~2-3s per page (previously timed out ✗)
- `qwen2.5:14b`: ~5-7s per page (previously timed out ✗)

**Model Recommendations by GPU Memory:**
- **4-8GB VRAM**: qwen2.5:3b or qwen2.5:7b-q4_0
- **8-12GB VRAM**: qwen2.5:7b (recommended)
- **12-24GB VRAM**: qwen2.5:14b (high accuracy)
- **24GB+ VRAM**: qwen2.5:32b (maximum accuracy)

## 📦 What's Included

### New Files
1. **`scripts/fix_ollama_gpu.sh`** - Automated GPU configuration script
   - Detects NVIDIA GPU
   - Configures Ollama for GPU usage
   - Verifies GPU detection
   - Lists available models

2. **`docs/OLLAMA_GPU_SETUP.md`** - Comprehensive GPU setup guide
   - Automatic and manual setup procedures
   - Performance comparisons
   - Troubleshooting guide
   - Model selection recommendations
   - Real-time GPU monitoring instructions

### Modified Files
1. **`ocr_invoice_reader/utils/llm_processor.py`**
   - Added `timeout` parameter to constructor
   - Intelligent timeout selection based on model size
   - Manual timeout override option

2. **`README.md`**
   - Added GPU acceleration section
   - Model selection guide with VRAM requirements
   - Performance benchmarks

3. **`CHANGELOG.md`**
   - Complete v2.2.7 release notes

4. **`setup.py`**
   - Updated version to 2.2.7
   - Updated description

## 🚀 Quick Start

### For Users with GPU

```bash
# 1. Update to latest version
git pull origin main
pip install -e .

# 2. Setup GPU (one-time)
bash scripts/fix_ollama_gpu.sh

# 3. Install a GPU-optimized model
ollama pull qwen2.5:7b

# 4. Run with GPU acceleration
ocr-enhanced --image invoice.pdf --use-llm --llm-model qwen2.5:7b

# 5. Monitor GPU usage (optional)
watch -n 1 nvidia-smi
```

### For Users without GPU (CPU only)

```bash
# Continue using CPU-friendly models
ocr-enhanced --image invoice.pdf --use-llm --llm-model qwen2.5:0.5b
```

No changes needed! The system automatically detects and uses the best available hardware.

## 🔧 Features in Detail

### 1. Automatic GPU Detection
- Ollama automatically detects and uses NVIDIA GPU if available
- No code changes required
- Seamless fallback to CPU if GPU is not available

### 2. Smart Timeout Management
```python
from ocr_invoice_reader.utils.llm_processor import LLMProcessor

# Automatic timeout based on model size
processor = LLMProcessor(model="qwen2.5:14b")  # 180s timeout

# Manual override if needed
processor = LLMProcessor(model="qwen2.5:14b", timeout=600)  # 10 minutes
```

### 3. GPU Monitoring
```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi

# During processing, you'll see:
# - GPU memory usage increase when model loads
# - GPU utilization spike during inference
# - Memory stays allocated (model cached for reuse)
```

## 🐛 Bug Fixes

### Critical Timeout Issue (Fixed)
**Problem**: "HTTPConnectionPool read timed out. (read timeout=30)" errors when using large models (7B, 14B)

**Solution**: Dynamic timeout adjustment based on model size. Large models now have sufficient time to generate responses.

**Before v2.2.7**:
```
✗ LLM processing failed: HTTPConnectionPool(host='localhost', port=11434): 
  Read timed out. (read timeout=30)
```

**After v2.2.7**:
```
✓ LLM processing successful (14B model, ~6s)
```

## 📚 Documentation

- **[GPU Setup Guide](docs/OLLAMA_GPU_SETUP.md)** - Complete setup and troubleshooting
- **[LLM Integration Guide](LLM_INTEGRATION_GUIDE.md)** - Using LLM features
- **[API Usage](docs/API_USAGE.md)** - Python API reference
- **[Complete Documentation Index](DOCUMENTATION_INDEX.md)** - All guides

## 🔄 Upgrade Instructions

### From v2.2.6 or earlier

```bash
# 1. Pull latest changes
git pull origin main

# 2. Reinstall (if needed)
pip install -e .

# 3. Setup GPU (if you have NVIDIA GPU)
bash scripts/fix_ollama_gpu.sh

# 4. Test
ocr-enhanced --image examples/INVOICE.pdf --use-llm --llm-model qwen2.5:7b
```

### Compatibility
- ✅ **Fully backward compatible**
- ✅ All existing code works without changes
- ✅ Automatic GPU detection (no manual configuration required)
- ✅ CPU-only mode still supported

## 🎯 Use Cases

### 1. High-Volume Processing (GPU Recommended)
```bash
# Process many invoices with large, accurate model
for file in invoices/*.pdf; do
  ocr-enhanced --image "$file" --use-llm --llm-model qwen2.5:14b
done
```

### 2. Production Server (GPU)
```bash
# Run API server with GPU acceleration
ocr-api --host 0.0.0.0 --port 8000 --workers 4
# Configure with qwen2.5:7b or qwen2.5:14b
```

### 3. Development/Testing (CPU)
```bash
# Fast testing with small model
ocr-enhanced --image test.pdf --use-llm --llm-model qwen2.5:0.5b
```

## ⚠️ Known Issues

None reported for this version.

## 💬 Feedback & Support

- **Issues**: https://github.com/SyuuKasinn/ocr-invoice-reader/issues
- **Discussions**: https://github.com/SyuuKasinn/ocr-invoice-reader/discussions
- **GPU Setup Help**: See [docs/OLLAMA_GPU_SETUP.md](docs/OLLAMA_GPU_SETUP.md)

## 🙏 Acknowledgments

- Thanks to [Ollama](https://ollama.ai/) for the excellent local LLM platform
- Thanks to [Qwen Team](https://huggingface.co/Qwen) for the powerful language models
- Thanks to all contributors and users for feedback and testing

---

**Full Changelog**: https://github.com/SyuuKasinn/ocr-invoice-reader/compare/v2.2.6...v2.2.7
