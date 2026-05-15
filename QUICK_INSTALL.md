# Quick Installation Guide

## 🚀 5-Minute Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/SyuuKasinn/ocr-invoice-reader.git
cd ocr-invoice-reader
```

### Step 2: Run Smart Installer

The installer automatically detects your hardware and installs everything:

```bash
bash scripts/install.sh
```

**What it does:**
1. ✅ Detects GPU/CPU and CUDA version
2. ✅ Installs PaddlePaddle (GPU or CPU version)
3. ✅ Installs PyTorch with correct CUDA support
4. ✅ Installs Transformers and LLM dependencies
5. ✅ Installs the OCR Invoice Reader package
6. ✅ Registers all commands (ocr-enhanced, ocr-check-env, etc.)

### Step 3: Verify Installation

```bash
# Check version
ocr-enhanced --version

# Check environment and hardware
ocr-check-env
```

### Step 4: Run Your First OCR

```bash
# Basic OCR
ocr-enhanced --image examples/インボイス見本.pdf --visualize

# With LLM enhancement (auto-selects best model)
ocr-enhanced --image examples/インボイス見本.pdf --use-llm --visualize
```

---

## 📋 Manual Installation (Alternative)

If you prefer manual control:

### For GPU Systems

```bash
# 1. Install dependencies
pip install -r requirements-gpu.txt

# 2. Install the package
pip install -e .

# 3. Verify
ocr-check-env
```

### For CPU-Only Systems

```bash
# 1. Install dependencies
pip install -r requirements-cpu.txt

# 2. Install the package
pip install -e .

# 3. Verify
ocr-check-env
```

---

## 🔍 Troubleshooting

### "command not found: ocr-enhanced"

**Cause:** Package not installed.

**Solution:**
```bash
cd ocr-invoice-reader
pip install -e .
```

### "No package metadata was found for ocr-invoice-reader"

**Cause:** Package not installed or installed incorrectly.

**Solution:**
```bash
pip uninstall ocr-invoice-reader  # If previously installed
pip install -e .                   # Reinstall in editable mode
```

### CUDA/GPU Issues

**Check GPU availability:**
```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

**If GPU not detected:**
1. Check CUDA version: `nvidia-smi`
2. Reinstall with correct CUDA support: `bash scripts/install.sh`
3. Verify: `ocr-check-env`

### PaddlePaddle Installation Failed

**For CUDA 13.0:**
```bash
pip install paddlepaddle-gpu==2.6.2.post120 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

**For CUDA 12.x:**
```bash
pip install paddlepaddle-gpu==2.6.2.post120 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

**For CUDA 11.x:**
```bash
pip install paddlepaddle-gpu==2.6.2.post117 -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html
```

**For CPU:**
```bash
pip install paddlepaddle==2.6.2
```

---

## 💡 What Gets Installed

### Core Components
- **PaddleOCR** - OCR engine
- **PaddlePaddle** - Deep learning framework (GPU or CPU)
- **PyTorch** - For LLM inference
- **Transformers** - Hugging Face library
- **Qwen2.5 Models** - Downloaded on first use (3B/7B/14B)

### Commands
- `ocr-enhanced` - Main CLI
- `ocr-enhanced-parallel` - Parallel processing
- `ocr-check-env` - Environment checker
- `ocr-api` - API server (optional)

### Storage Requirements
- **Minimal**: ~5GB (CPU, no LLM)
- **Standard**: ~15GB (GPU + 7B model)
- **Full**: ~30GB (GPU + 14B model)

---

## 🎯 Next Steps

1. **Read Documentation**: [COMPLETE_GUIDE.md](docs/COMPLETE_GUIDE.md)
2. **Try Examples**: `ocr-enhanced --image examples/*.pdf --use-llm`
3. **Check Performance**: `ocr-check-env`
4. **Optimize Settings**: Based on your hardware recommendations

---

## 📞 Need Help?

- **Check Environment**: `ocr-check-env`
- **View Logs**: Look for error messages in terminal
- **GitHub Issues**: [Report a problem](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)
- **Documentation**: [docs/](docs/)

---

**Installation takes 5-10 minutes. First model download adds 5-10 minutes (one-time).**
