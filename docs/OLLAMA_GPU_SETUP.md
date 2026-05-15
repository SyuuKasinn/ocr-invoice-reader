# Ollama GPU Setup Guide

> ⚠️ **DEPRECATED - This guide is for historical reference only**
> 
> **As of v2.3.2, this project uses direct Qwen integration instead of Ollama.**
> 
> **Please see [QWEN_DIRECT_SETUP.md](QWEN_DIRECT_SETUP.md) for current installation instructions.**
> 
> **Benefits of Qwen Direct:**
> - ✅ 4-15x faster inference
> - ✅ 95% GPU utilization (vs 0% with Ollama)
> - ✅ Simpler installation (no Ollama needed)
> - ✅ Better CUDA compatibility (supports 11.x, 12.x, 13.x)

---

## Historical Content (Deprecated)

This guide helps you configure Ollama to use GPU acceleration for faster LLM processing.

## 🚀 Quick Setup

### Option 1: Automated Script (Recommended)

```bash
# Run the setup script
bash scripts/fix_ollama_gpu.sh
```

### Option 2: Manual Setup

1. **Verify GPU is available**

```bash
nvidia-smi
```

You should see your GPU listed with available memory.

2. **Configure Ollama for GPU**

```bash
# Set environment variables
export CUDA_VISIBLE_DEVICES=0
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_MAX_LOADED_MODELS=1

# Restart Ollama
pkill ollama
nohup ollama serve > /tmp/ollama.log 2>&1 &

# Wait a few seconds
sleep 5

# Check Ollama is running
curl http://localhost:11434
```

3. **Verify GPU detection**

```bash
# Check Ollama logs
tail -20 /tmp/ollama.log | grep -i gpu

# Should see something like:
# time=... level=INFO source=gpu.go:... msg="Nvidia GPU detected"
```

4. **Install a model**

Choose based on your GPU memory:

```bash
# For 4-8GB VRAM
ollama pull qwen2.5:3b

# For 8-12GB VRAM  
ollama pull qwen2.5:7b

# For 12-24GB VRAM
ollama pull qwen2.5:14b

# For 24GB+ VRAM
ollama pull qwen2.5:32b
```

## 🔧 Timeout Fix

If you're experiencing timeout errors with large models, the code now automatically adjusts timeout based on model size:

- Small models (0.5b, mini): 60 seconds
- 7B models: 120 seconds  
- 14B models: 180 seconds
- Unknown models: 300 seconds (default)

You can also manually specify timeout:

```python
from ocr_invoice_reader.utils.llm_processor import LLMProcessor

processor = LLMProcessor(
    model="qwen2.5:14b",
    timeout=300  # 5 minutes
)
```

## 📊 Performance Comparison

| GPU Model | Model Size | Speed (per page) | Memory Used |
|-----------|-----------|------------------|-------------|
| RTX 3060 (12GB) | qwen2.5:7b | ~2-3s | ~6GB |
| RTX 3060 (12GB) | qwen2.5:14b | ~5-7s | ~10GB |
| RTX 4090 (24GB) | qwen2.5:14b | ~2-3s | ~10GB |
| CPU (no GPU) | qwen2.5:0.5b | ~10-15s | ~2GB RAM |

## 🐛 Troubleshooting

### Issue: "Read timed out" error

**Cause**: Model is too large or GPU is busy

**Solutions**:
1. Use a smaller model (e.g., qwen2.5:7b instead of 14b)
2. Increase timeout in code
3. Use quantized models (e.g., qwen2.5:7b-q4_0)

### Issue: Ollama not using GPU

**Check**:
```bash
# Monitor GPU usage while running OCR
watch -n 1 nvidia-smi
```

If GPU usage is 0%, verify:
1. CUDA is installed: `nvcc --version`
2. Ollama service restarted after setting environment variables
3. Check Ollama logs: `tail -50 /tmp/ollama.log`

### Issue: Out of memory

**Solutions**:
1. Use a smaller model
2. Use quantized models (q4_0, q5_0)
3. Limit GPU memory:
   ```bash
   export OLLAMA_MAX_VRAM=8192  # Limit to 8GB
   ```

### Issue: Slow processing even with GPU

**Check**:
1. GPU is actually being used: `nvidia-smi`
2. Model is fully loaded (first inference is slow)
3. Network latency if Ollama is remote
4. Consider using smaller quantized models

## 📝 Model Selection Guide

### For Development/Testing
- **qwen2.5:0.5b** or **qwen2.5:3b**
- Fast, low memory, good for testing workflow
- Accuracy: Good for simple invoices

### For Production (CPU)
- **qwen2.5:3b** or **qwen2.5:7b-q4_0**
- Balanced speed and accuracy
- Works on CPU servers

### For Production (GPU)
- **qwen2.5:7b** or **qwen2.5:14b**
- High accuracy
- Requires GPU with 8-16GB VRAM

### For Maximum Accuracy
- **qwen2.5:14b** or **qwen2.5:32b**
- Best accuracy for complex documents
- Requires powerful GPU (16GB+ VRAM)

## 🔍 Monitoring GPU Usage

### Real-time monitoring
```bash
watch -n 1 nvidia-smi
```

### During OCR processing
```bash
# Terminal 1: Monitor GPU
watch -n 1 nvidia-smi

# Terminal 2: Run OCR
ocr-enhanced --image invoice.pdf --lang ch --use-llm --llm-model qwen2.5:7b
```

You should see:
- GPU Memory usage increase when model loads
- GPU Utilization spike during LLM inference
- Memory stay allocated (model cached for reuse)

## 🌐 Remote Ollama Server

If running Ollama on a different machine:

```python
from ocr_invoice_reader.utils.llm_processor import LLMProcessor

processor = LLMProcessor(
    model="qwen2.5:7b",
    base_url="http://gpu-server:11434",
    timeout=120
)
```

## 📚 Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Qwen2.5 Model Card](https://huggingface.co/Qwen)
- [CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)

## ✅ Best Practices

1. **Start small**: Test with small models first
2. **Monitor resources**: Use `nvidia-smi` to check GPU usage
3. **Choose right model**: Balance accuracy vs speed for your use case
4. **Cache models**: Keep Ollama running to avoid reload overhead
5. **Batch processing**: Process multiple documents in one session
6. **Use quantization**: q4_0/q5_0 models are 2-3x faster with minimal accuracy loss

## 🆘 Still Having Issues?

1. Check [GitHub Issues](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)
2. Review Ollama logs: `tail -100 /tmp/ollama.log`
3. Test Ollama independently:
   ```bash
   ollama run qwen2.5:7b "Hello"
   ```
4. Open a new issue with:
   - GPU model and VRAM
   - Ollama version: `ollama --version`
   - Error logs
