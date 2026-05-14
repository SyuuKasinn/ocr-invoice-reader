# Performance Optimization Guide

This guide covers optimization techniques to maximize OCR processing speed while maintaining accuracy.

## Quick Wins (5 minutes)

### 1. Enable GPU Acceleration

**Impact:** 3-10x faster

```bash
# Install GPU version
pip install paddlepaddle-gpu==3.0.0

# Use GPU mode
ocr-enhanced --image invoice.pdf --lang ch  # omit --use-cpu
```

### 2. Disable Visualization (Production)

**Impact:** 30-40% faster

```bash
# Without visualization
ocr-enhanced --image invoice.pdf --lang ch --output-dir results

# With visualization (slower)
ocr-enhanced --image invoice.pdf --lang ch --visualize --output-dir results
```

### 3. Choose the Right Mode

**Impact:** 50-200% faster

```bash
# Fast: Text only
ocr-simple --image invoice.pdf --lang ch  # ~1.0s/page

# Medium: Structured fields
ocr-extract --image invoice.pdf --lang ch  # ~1.5s/page

# Full: Tables + layout
ocr-enhanced --image invoice.pdf --lang ch  # ~1.7s/page
```

## Optimization Tips

### Hardware

#### CPU Optimization

```python
from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer

analyzer = EnhancedStructureAnalyzer(
    use_gpu=False,
    lang='ch',
    # CPU optimization parameters
    enable_mkldnn=True,    # Enable MKL-DNN acceleration
    cpu_threads=10         # Use multiple threads
)
```

**Impact:** +20-30% CPU performance

#### GPU Optimization

```python
analyzer = EnhancedStructureAnalyzer(
    use_gpu=True,
    lang='ch',
    gpu_mem=500,          # Limit GPU memory (MB)
    use_tensorrt=False    # Enable TensorRT (requires setup)
)
```

**Note:** TensorRT requires additional configuration but can provide 40-60% speedup.

### Image Processing

#### Reduce PDF Resolution

```python
from ocr_invoice_reader.processors.file_handler import FileProcessor

# Default: 300 DPI
processor = FileProcessor(dpi=300)

# Faster: 200 DPI (25% faster, <1% accuracy loss)
processor = FileProcessor(dpi=200)

# Fastest: 150 DPI (40% faster, ~2% accuracy loss)
processor = FileProcessor(dpi=150)
```

**Recommendation:** Use 200 DPI for most invoices and documents.

#### Image Preprocessing

Optimize large images:

```python
import cv2
import numpy as np

def preprocess_image(image_path, max_size=2000):
    """Resize large images before OCR"""
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    return img
```

### Batch Processing

#### Reuse Analyzer Instance

```python
analyzer = EnhancedStructureAnalyzer(use_gpu=True, lang='ch')

files = ['file1.pdf', 'file2.pdf', 'file3.pdf']

# ✅ Good: Reuse instance
for file in files:
    result = analyzer.analyze(file)

# ❌ Bad: Recreate each time (slow!)
for file in files:
    analyzer = EnhancedStructureAnalyzer(use_gpu=True, lang='ch')
    result = analyzer.analyze(file)
```

**Impact:** 5-10s saved per file (avoids model reload)

#### Memory Management

For large batches:

```python
import gc

analyzer = EnhancedStructureAnalyzer(use_gpu=True, lang='ch')

for idx, file in enumerate(large_file_list):
    result = analyzer.analyze(file)
    
    # Process result immediately
    save_result(result)
    
    # Periodic garbage collection
    if (idx + 1) % 10 == 0:
        gc.collect()
        print(f"Processed {idx + 1} files, freed memory")
```

## Benchmarks

### Single Page Processing

| Configuration | Time | vs Baseline |
|---------------|------|-------------|
| **Baseline** (CPU, DPI 300, viz) | 2.8s | - |
| GPU enabled | 0.9s | **3.1x faster** |
| DPI 200 (CPU) | 2.1s | **1.3x faster** |
| No visualization (CPU) | 1.7s | **1.6x faster** |
| Simple mode (CPU) | 1.0s | **2.8x faster** |
| **Optimized** (GPU, DPI 200, no viz) | 0.5s | **5.6x faster** |

### Batch Processing (10 files)

| Configuration | Total Time | Per File |
|---------------|------------|----------|
| Default (CPU) | 28s | 2.8s |
| Reused instance (CPU) | 17s | 1.7s |
| GPU + reused | 5s | 0.5s |

*Hardware: Intel i7-10700, NVIDIA RTX 3060*

## Performance Checklist

### Before Processing

- [ ] Is GPU available and enabled?
- [ ] Is DPI set appropriately? (200 for most documents)
- [ ] Is visualization disabled in production?
- [ ] Is the right mode selected? (simple/extract/enhanced)
- [ ] Are analyzer instances reused in batch processing?

### During Development

- [ ] Profile with actual documents
- [ ] Test different DPI settings
- [ ] Measure accuracy vs speed tradeoffs
- [ ] Monitor memory usage

### Production Deployment

- [ ] GPU properly configured
- [ ] Visualization disabled
- [ ] Result caching enabled (if applicable)
- [ ] Logging configured appropriately
- [ ] Error handling in place

## Common Bottlenecks

### 1. Model Loading

**Symptom:** Slow first run or each run  
**Solution:** Reuse analyzer instances

### 2. PDF Conversion

**Symptom:** Long delay before OCR starts  
**Solution:** Reduce DPI or cache converted images

### 3. Visualization

**Symptom:** Processing takes 30-40% longer  
**Solution:** Disable in production

### 4. Large Images

**Symptom:** Very slow or out of memory  
**Solution:** Preprocess/resize images before OCR

### 5. Network I/O

**Symptom:** Slow first run  
**Solution:** Pre-download models or use local cache

## Advanced Optimizations

### Result Caching

Cache OCR results for repeated processing:

```python
import json
import hashlib
from pathlib import Path

class CachedAnalyzer:
    def __init__(self, analyzer, cache_dir='./cache'):
        self.analyzer = analyzer
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def analyze(self, image_path, force=False):
        # Calculate cache key
        with open(image_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:16]
        
        cache_file = self.cache_dir / f"{file_hash}.json"
        
        # Check cache
        if not force and cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Process
        result = self.analyzer.analyze(image_path)
        
        # Save cache
        with open(cache_file, 'w') as f:
            json.dump(result, f)
        
        return result
```

### Parallel Processing

**Warning:** Experimental, use with caution

```python
from multiprocessing import Pool
from functools import partial

def process_file(file_path, lang='ch'):
    # Each process creates its own analyzer
    from ocr_invoice_reader.processors.enhanced_structure_analyzer import EnhancedStructureAnalyzer
    analyzer = EnhancedStructureAnalyzer(use_gpu=False, lang=lang)
    return analyzer.analyze(file_path)

# Process multiple files in parallel
files = ['file1.pdf', 'file2.pdf', 'file3.pdf', 'file4.pdf']

with Pool(processes=4) as pool:
    results = pool.map(process_file, files)
```

**Note:** GPU mode may conflict with multiprocessing.

## Monitoring Performance

### Simple Timing

```python
import time

start = time.time()
result = analyzer.analyze('invoice.pdf')
elapsed = time.time() - start

print(f"Processing time: {elapsed:.2f}s")
```

### Detailed Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

result = analyzer.analyze('invoice.pdf')

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

## FAQ

**Q: Should I always use GPU?**

A: Yes, if available. GPU is 3-10x faster with no downside.

**Q: What DPI should I use?**

A: 200 DPI for most documents. 150 DPI if speed is critical. 300 DPI for small text or high quality.

**Q: Can I process files in parallel?**

A: Yes with CPU mode. GPU mode may have conflicts. Test thoroughly.

**Q: How much faster is v4 vs v3?**

A: 30-37% faster with same accuracy. See [v4 upgrade guide](v4-upgrade/WHATS_NEW.md).

## Further Reading

- [PaddleOCR Performance Guide](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.8/doc/doc_en/inference_ppocr_en.md)
- [v4 Upgrade Guide](v4-upgrade/QUICKSTART.md)
- [API Reference](API.md)

---

**Need Help?** [Open an issue](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)
