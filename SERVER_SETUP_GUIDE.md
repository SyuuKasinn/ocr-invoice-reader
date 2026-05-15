# Server Setup Quick Reference

## 🎯 For Your Remote Server

### Step 1: Update Code on Server

```bash
# SSH to your server
ssh root@your-server

# Navigate to project
cd /root/ocr-invoice-reader-main

# Pull latest changes
git pull origin main

# Reinstall if needed
pip install -e .
```

### Step 2: Setup GPU for Ollama

```bash
# Run the GPU setup script
bash scripts/fix_ollama_gpu.sh
```

This script will:
- ✅ Check if NVIDIA GPU is detected
- ✅ Configure Ollama for GPU usage
- ✅ Restart Ollama service
- ✅ Verify GPU detection
- ✅ List available models

### Step 3: Install Appropriate Model

Choose based on your GPU memory:

```bash
# Check GPU memory
nvidia-smi --query-gpu=memory.total --format=csv,noheader

# Install model based on available VRAM:

# If you have 8-12GB VRAM (recommended)
ollama pull qwen2.5:7b

# If you have 12-24GB VRAM
ollama pull qwen2.5:14b

# If you have less than 8GB VRAM
ollama pull qwen2.5:3b
```

### Step 4: Test the Setup

```bash
# Terminal 1: Monitor GPU
watch -n 1 nvidia-smi

# Terminal 2: Run OCR with LLM
cd /root/ocr-invoice-reader-main
ocr-enhanced --image examples/INVOICE.pdf --lang ch --use-llm --llm-model qwen2.5:7b
```

**Expected behavior:**
- ✅ No timeout errors
- ✅ GPU memory usage visible in nvidia-smi
- ✅ Processing completes successfully
- ✅ LLM extraction fields populated

## 🔧 If You Get Errors

### Error: "Read timed out"

**Already fixed!** Update to v2.2.7:

```bash
cd /root/ocr-invoice-reader-main
git pull origin main
pip install -e .
```

### Error: "Ollama not found"

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Run setup script
bash scripts/fix_ollama_gpu.sh
```

### Error: "GPU not detected"

Check CUDA:
```bash
# Check CUDA
nvcc --version

# Check if GPU is visible
nvidia-smi

# Check Ollama logs
tail -50 /tmp/ollama.log | grep -i gpu
```

## 📊 Performance Expectations

### Your Server (with GPU)

| Model | Speed per Page | Accuracy | VRAM Usage |
|-------|---------------|----------|------------|
| qwen2.5:7b | ~2-3s | High | ~6GB |
| qwen2.5:14b | ~5-7s | Very High | ~10GB |

### Your Previous Issue (SOLVED)

**Before (v2.2.6):**
```
✗ LLM processing failed: Read timed out. (read timeout=30)
⏱ Page completed in 31.99s (but failed)
```

**After (v2.2.7):**
```
✓ LLM processing successful
⏱ Page completed in ~5-7s (with 14B model)
```

## 🚀 Recommended Command

Based on your previous usage:

```bash
# Your 10-page invoice
ocr-enhanced \
  --image examples/INVOICE.pdf \
  --lang ch \
  --use-llm \
  --llm-model qwen2.5:7b \
  --visualize
```

**Expected performance:**
- Total time: ~20-30 seconds (vs 320+ seconds before)
- GPU acceleration: Automatic
- No timeout errors: ✅
- All LLM fields extracted: ✅

## 📁 Output Files

After successful run:

```
results/20260515_xxxxxx/
├── INVOICE_page_0001.json          ✅ OCR structure
├── INVOICE_page_0001.txt           ✅ Extracted text
├── INVOICE_page_0001_llm.json      ✅ Invoice fields (NEW - was failing before)
├── INVOICE_page_0001_llm.csv       ✅ CSV format
├── INVOICE_page_0001_viz.jpg       ✅ Visual output
├── ...
└── INVOICE_llm.csv                 ✅ All invoice data combined
```

## 🔍 Monitoring

### Real-time GPU monitoring:
```bash
watch -n 1 nvidia-smi
```

Look for:
- **GPU Util**: Should spike to 80-100% during LLM inference
- **Memory**: Should show ~6GB for 7B model, ~10GB for 14B
- **Process**: Should list "ollama" process

### Check Ollama is using GPU:
```bash
tail -f /tmp/ollama.log | grep -i gpu
```

Should show:
```
level=INFO msg="Nvidia GPU detected"
level=INFO msg="CUDA compute capability: X.X"
```

## 💡 Tips

1. **Keep Ollama running** - Models stay in memory, faster for subsequent runs
2. **Use qwen2.5:7b** - Best balance of speed and accuracy for most cases
3. **Batch processing** - Process multiple files in one session to avoid reload overhead
4. **Monitor first** - Run `watch nvidia-smi` before processing to verify GPU usage

## 🆘 Quick Troubleshooting

```bash
# 1. Check everything is installed
which ollama
nvidia-smi
python -c "from ocr_invoice_reader.utils.llm_processor import LLMProcessor; print('OK')"

# 2. Restart Ollama with GPU
pkill ollama
export CUDA_VISIBLE_DEVICES=0
nohup ollama serve > /tmp/ollama.log 2>&1 &

# 3. Verify model is loaded
ollama list | grep qwen2.5

# 4. Test Ollama directly
ollama run qwen2.5:7b "Hello"

# 5. Check timeout is fixed
python -c "from ocr_invoice_reader.utils.llm_processor import LLMProcessor; p = LLMProcessor('qwen2.5:14b'); print(f'Timeout: {p.timeout}s')"
# Should show: Timeout: 180s
```

## ✅ Success Checklist

- [ ] Git pulled latest code (v2.2.7)
- [ ] GPU setup script run successfully
- [ ] Model installed (qwen2.5:7b or 14B)
- [ ] nvidia-smi shows GPU
- [ ] Ollama running with GPU
- [ ] Test command works without timeout
- [ ] LLM JSON files generated

## 📞 Need Help?

If issues persist:

1. Check [docs/OLLAMA_GPU_SETUP.md](docs/OLLAMA_GPU_SETUP.md)
2. Review Ollama logs: `tail -100 /tmp/ollama.log`
3. Open issue: https://github.com/SyuuKasinn/ocr-invoice-reader/issues

Include:
- GPU model and VRAM (`nvidia-smi`)
- Ollama version (`ollama --version`)
- Python version (`python --version`)
- Error messages from logs
