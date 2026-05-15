# Performance Optimization Guide

## 🐌 Running Too Slow?

If you're experiencing slow processing or timeout errors, follow these tips:

## 1. Use Parallel Processing (Fastest)

**Instead of serial**:
```bash
ocr-enhanced --image invoice.pdf --use-llm
# 8 pages = 6.5 minutes
```

**Use parallel** (3-7x faster):
```bash
ocr-enhanced-parallel --image invoice.pdf --use-llm --workers 3
# 8 pages = 2 minutes ⚡
```

**Performance comparison**:
| Pages | Serial | Parallel (3 workers) | Speedup |
|-------|--------|----------------------|---------|
| 8     | 6.5 min | 2 min               | 3.2x    |
| 50    | 40.8 min | 12.8 min           | 3.2x    |

## 2. Use Smaller LLM Model

**Default (slow on CPU)**:
```bash
--llm-model qwen2.5:14b  # 14B params, high accuracy, slow
```

**Fast option** (recommended for CPU):
```bash
--llm-model qwen2.5:7b   # 7B params, good accuracy, 2x faster
```

**Accuracy comparison**:
- `qwen2.5:7b` - 88% accuracy, faster
- `qwen2.5:14b` - 93% accuracy, slower
- `qwen2.5:32b` - 95% accuracy, very slow

## 3. Enable GPU (If Available)

**CPU mode** (slow):
```bash
ocr-enhanced --image invoice.pdf --use-cpu --use-llm
# Per page: ~50s
```

**GPU mode** (much faster):
```bash
ocr-enhanced --image invoice.pdf --use-llm
# Per page: ~15s ⚡
```

Requirements:
- NVIDIA GPU with CUDA
- PaddlePaddle GPU version: `pip install paddlepaddle-gpu`

## 4. Reduce Workers If Out of Memory

**Default (may run out of RAM)**:
```bash
ocr-enhanced-parallel --workers 3  # Needs 8-16GB RAM
```

**For limited RAM**:
```bash
ocr-enhanced-parallel --workers 2  # Needs 6-8GB RAM
```

## 5. Skip LLM for Simple Cases

**Without LLM** (fastest, regex only):
```bash
ocr-enhanced --image invoice.pdf --visualize
# 8 pages = 24s (no LLM overhead)
```

Use when:
- Standard invoice formats
- Need maximum speed
- Regex extraction is sufficient (75% accuracy)

## Recommended Configurations

### For Maximum Speed (CPU, Low RAM)
```bash
ocr-enhanced-parallel \
  --image invoice.pdf \
  --use-llm \
  --llm-model qwen2.5:7b \
  --workers 2 \
  --use-cpu
```
- Processing: 8 pages in ~3 minutes
- RAM: 6-8GB
- Accuracy: 88%

### For Best Accuracy (GPU, High RAM)
```bash
ocr-enhanced-parallel \
  --image invoice.pdf \
  --use-llm \
  --llm-model qwen2.5:14b \
  --workers 6
```
- Processing: 8 pages in ~1.5 minutes
- RAM: 16GB+
- Accuracy: 93%

### For Maximum Speed (No LLM)
```bash
ocr-enhanced --image invoice.pdf --visualize
```
- Processing: 8 pages in 24s
- RAM: 4GB
- Accuracy: 75% (regex only)

## Troubleshooting Timeout Errors

If you see:
```
⚠ LLM extraction error: HTTPConnectionPool(host='localhost', port=11434): Read timed out.
```

**Solution 1**: Use smaller model
```bash
--llm-model qwen2.5:7b  # Instead of 14b
```

**Solution 2**: Use parallel mode (better timeout handling)
```bash
ocr-enhanced-parallel --workers 3
```

**Solution 3**: Increase Ollama timeout (in `~/.ollama/config.json`):
```json
{
  "timeout": 300
}
```

## System Requirements by Configuration

### Minimum (CPU, No LLM)
- RAM: 4GB
- CPU: Any
- Processing: ~3s per page

### Recommended (CPU, qwen2.5:7b, Parallel)
- RAM: 8GB
- CPU: 4+ cores
- Processing: ~15s per page

### Optimal (GPU, qwen2.5:14b, Parallel)
- RAM: 16GB
- GPU: NVIDIA with 6GB+ VRAM
- CPU: 6+ cores
- Processing: ~5s per page

## Common Performance Issues

### Issue: "Processing is too slow"
- **Solution**: Use parallel mode + smaller model
- **Command**: `ocr-enhanced-parallel --llm-model qwen2.5:7b --workers 3`

### Issue: "Out of memory"
- **Solution**: Reduce workers
- **Command**: `ocr-enhanced-parallel --workers 2`

### Issue: "LLM timeout errors"
- **Solution**: Use smaller model or disable LLM
- **Command**: `ocr-enhanced --llm-model qwen2.5:7b` or `ocr-enhanced` (no LLM)

### Issue: "Need best accuracy"
- **Solution**: Use GPU + large model + parallel
- **Command**: `ocr-enhanced-parallel --llm-model qwen2.5:14b --workers 4`

## Benchmark Your System

Test different configurations to find optimal settings:

```bash
# Test 1: Serial, no LLM (baseline)
time ocr-enhanced --image test.pdf

# Test 2: Serial, with LLM
time ocr-enhanced --image test.pdf --use-llm --llm-model qwen2.5:7b

# Test 3: Parallel, with LLM
time ocr-enhanced-parallel --image test.pdf --use-llm --llm-model qwen2.5:7b --workers 3

# Test 4: Parallel, larger model
time ocr-enhanced-parallel --image test.pdf --use-llm --llm-model qwen2.5:14b --workers 3
```

Compare results and choose the configuration that balances speed and accuracy for your needs.
