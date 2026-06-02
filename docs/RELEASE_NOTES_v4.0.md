# Release Notes - OCR Invoice Reader v4.0

## Overview

Version 4.0 represents a major architectural upgrade, migrating from PaddleOCR v2.8 to PaddleOCR-VL 1.5/1.6, with completely redesigned core pipeline and enhanced reporting capabilities.

---

## Breaking Changes

### API Changes
- **Removed**: Old `DocumentExtractor` class (legacy v2.x API)
- **Added**: New `Pipeline` class with streaming support
- **Changed**: Configuration moved to Pydantic v2 models (`PipelineConfig`, `VLConfig`, `IOConfig`)
- **Changed**: PaddleOCR language parameter (`lang`) removed (auto-detection in VL 1.6)

### Dependency Changes
- **Minimum Python**: 3.10+ (was 3.8+)
- **PaddleOCR**: >= 3.0.0 (was 2.8.1)
- **PaddleX**: >= 3.6.0 with `[ocr]` extra
- **Pydantic**: >= 2.0 (was v1.x)

### Migration Guide

**Old Code (v2.x):**
```python
from ocr_invoice_reader.extractors.document_extractor import DocumentExtractor

extractor = DocumentExtractor(use_gpu=True, lang='japan')
result = extractor.extract('invoice.pdf')
```

**New Code (v4.0):**
```python
from ocr_invoice_reader.core.pipeline import Pipeline
from ocr_invoice_reader.core.config import PipelineConfig, VLConfig, IOConfig

config = PipelineConfig(
    vl=VLConfig(use_gpu=True),
    io=IOConfig(output_dir='results')
)
pipeline = Pipeline(config)
document = pipeline.run('invoice.pdf')
```

---

## New Features

### 1. PaddleOCR-VL 1.5/1.6 Integration

**Benefits:**
- Superior layout analysis (title, text, table, figure detection)
- Better table structure recognition with HTML output
- Improved multi-language support (auto-detection)
- Native PDF processing (no intermediate image conversion)

**Performance:**
- 2-5 seconds per page (GPU)
- 10-30 seconds per page (CPU)
- Automatic GPU/CPU detection

### 2. Streaming Pipeline

**New API:**
```python
def on_page_complete(page_result):
    save_immediately(page_result)

document = pipeline.run_and_save(
    'large_doc.pdf',
    on_page=on_page_complete
)
```

**Benefits:**
- Process large documents without memory overflow
- Real-time progress monitoring
- Early failure detection

### 3. Statistics Collection

**New Module:** `ocr_invoice_reader/utils/stats_collector.py`

**Features:**
- Processing time tracking (document/page level)
- Confidence score analysis
- Content statistics (regions, tables, figures, text length)
- Low-confidence page detection
- Throughput calculation

**Example:**
```python
from ocr_invoice_reader.utils.stats_collector import StatsCollector

collector = StatsCollector()
collector.start_document('invoice')
# ... process ...
collector.end_document()
stats = collector.collect_document_stats(all_pages_regions, 'invoice')
```

**Output:**
```
Document: invoice
Pages: 5
Total Time: 12.34s
Throughput: 0.41 pages/sec
Avg Confidence: 92.3%
Low Confidence Pages: 3, 5
```

### 4. Interactive HTML Reports

**New Module:** `ocr_invoice_reader/utils/html_report.py`

**Features:**
- **Grid View**: Quick overview of all pages with thumbnails
- **Detail View**: Deep dive into each page with region list
- **Statistics Dashboard**: Performance metrics and quality indicators
- **Confidence Color Coding**:
  - Green: >= 90% (high confidence)
  - Orange: 70-90% (medium confidence)
  - Red: < 70% (low confidence)
- **Responsive Design**: Works on mobile, tablet, desktop
- **Self-contained**: Single HTML file, optionally embed images

**Example:**
```python
from ocr_invoice_reader.utils.html_report import generate_html_report

generate_html_report(
    document_name='invoice',
    all_pages_regions=[[region1, region2]],
    image_paths=['page1_vis.jpg'],
    stats=stats,
    output_path='report.html'
)
```

### 5. Strongly Typed Data Models

**Using Pydantic v2:**
```python
class Block(BaseModel):
    label: str                    # 'title', 'text', 'table', 'figure'
    bbox: List[float]             # [x1, y1, x2, y2]
    text: str
    html: Optional[str] = None
    image_path: Optional[str] = None
    score: Optional[float] = None

class PageResult(BaseModel):
    page_index: int
    source_file: str
    blocks: List[Block]
    markdown: Optional[str] = None

class DocumentResult(BaseModel):
    document: str
    total_pages: int
    pages: List[PageResult]
```

**Benefits:**
- IDE autocomplete
- Type checking
- Runtime validation
- JSON schema generation

---

## Improvements

### Architecture
- **Modular Design**: Clear separation of concerns (Pipeline → VLEngine → Normalization)
- **Lazy Initialization**: Models loaded only when needed
- **Better Error Handling**: Graceful degradation, informative error messages
- **Extensible**: Easy to add custom post-processors

### Configuration
- **Type-Safe**: Pydantic models with validation
- **Hierarchical**: `PipelineConfig` → `VLConfig` + `IOConfig`
- **Documented**: Full docstrings and examples

### Documentation
- **Architecture Guide**: `docs/ARCHITECTURE.md` with ASCII diagrams
- **Enhancement Guide**: `ENHANCEMENTS_README.md` with examples
- **Updated README**: Comprehensive usage guide
- **Test Scripts**: `test_enhancements.py`, `test_enhanced_features.py`

### Performance
- **Auto-Detection**: Automatic GPU/CPU selection
- **Optimized Processing**: Direct PDF handling (no intermediate files)
- **Memory Efficient**: Streaming support for large documents

---

## Bug Fixes

- Fixed Unicode encoding issues on Windows (removed emoji characters from output)
- Fixed PaddleOCR v3.x API compatibility (`lang` parameter removed)
- Fixed dependency conflicts (paddlex[ocr] extra)
- Fixed GPU detection warnings
- Fixed data structure inconsistencies in test scripts

---

## Deprecated Features

### Removed in v4.0
- `DocumentExtractor` class (use `Pipeline` instead)
- `StructureAnalyzer` class (integrated into VLEngine)
- Direct `lang` parameter (auto-detected by PaddleOCR-VL)
- Old JSON output format (replaced with Pydantic models)

### Will be Removed in v5.0
- Legacy `ocr_invoice_reader.extractors` module
- Old-style configuration dictionaries (use Pydantic models)

---

## Installation Changes

### New Requirements

**Minimum:**
```bash
pip install "paddleocr>=3.0.0"
pip install "paddlex[ocr]>=3.6.0"
pip install -e .
```

**With GPU:**
```bash
pip install paddlepaddle-gpu>=3.2.0
pip install "paddleocr>=3.0.0"
pip install "paddlex[ocr]>=3.6.0"
pip install -e .
```

### Model Download

First run will automatically download models (~2-3 GB):
- PP-DocLayoutV3 (layout analysis)
- PaddleOCR-VL-1.6-0.9B (OCR + table recognition)

Models cached in: `~/.paddlex/official_models/`

---

## Testing

### New Test Suite

**Basic Tests:**
```bash
python test_enhancements.py
```

**Integration Tests:**
```bash
python test_enhanced_features.py
```

**With Custom PDF:**
```bash
python test_enhanced_features.py path/to/invoice.pdf
```

### Test Coverage
- Module imports ✓
- Statistics collection ✓
- HTML report generation ✓
- Full pipeline integration ✓
- Real PDF processing ✓

---

## Performance Benchmarks

### Processing Speed (CPU)
| Document Size | Pages | Time | Per Page |
|---------------|-------|------|----------|
| Small         | 1-5   | 10-50s | ~10s |
| Medium        | 10-20 | 100-300s | ~15s |
| Large         | 50+   | 500+s | ~10-20s |

### Processing Speed (GPU)
| Document Size | Pages | Time | Per Page |
|---------------|-------|------|----------|
| Small         | 1-5   | 5-15s | ~3s |
| Medium        | 10-20 | 30-60s | ~3-5s |
| Large         | 50+   | 150-250s | ~3-5s |

### Memory Usage
- Base: ~2GB (models)
- Peak: +500MB per page during processing
- HTML (no images): 20-100 KB
- HTML (with images): 1-5 MB

---

## Known Issues

### Limitations
1. **PDF Encryption**: Encrypted PDFs not supported (PaddleOCR-VL limitation)
2. **Complex Layouts**: Very complex multi-column layouts may need manual review
3. **Handwriting**: Handwritten text recognition quality varies
4. **Windows Encoding**: Console output may show encoding issues (use `chcp 65001`)

### Workarounds
1. **Memory**: Use streaming API for large documents
2. **GPU**: CPU mode is slow but works reliably
3. **Tables**: Complex nested tables may need post-processing

---

## Upgrade Checklist

- [ ] Update Python to >= 3.10
- [ ] Uninstall old paddleocr: `pip uninstall paddleocr`
- [ ] Install new dependencies: `pip install "paddleocr>=3.0.0" "paddlex[ocr]>=3.6.0"`
- [ ] Update code to use `Pipeline` instead of `DocumentExtractor`
- [ ] Update configuration to use Pydantic models
- [ ] Remove `lang` parameter (auto-detected now)
- [ ] Test with sample documents
- [ ] Update deployment scripts
- [ ] Clear old model cache (optional)

---

## Future Roadmap (v4.1+)

### Planned Features
- [ ] REST API service
- [ ] WebSocket real-time preview
- [ ] Docker containerization
- [ ] Cloud deployment (AWS/Azure/GCP)
- [ ] Batch processing optimization
- [ ] Custom model training
- [ ] Multi-model ensemble
- [ ] AI-assisted correction

### Community Requests
- [ ] Web UI dashboard
- [ ] More output formats (Excel, Word)
- [ ] Database integration
- [ ] Workflow automation
- [ ] Multi-document comparison

---

## Credits

**Lead Developer**: SyuuKasinn  
**AI Assistant**: Claude Code (Anthropic)  
**Contributors**: Community feedback and testing

**Special Thanks**:
- PaddleOCR team for the amazing VL pipeline
- PaddlePaddle team for the deep learning framework
- All users who provided feedback on v2.x

---

## Support

- **Issues**: [GitHub Issues](https://github.com/SyuuKasinn/ocr-invoice-reader/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SyuuKasinn/ocr-invoice-reader/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/SyuuKasinn/ocr-invoice-reader/wiki)

---

**Release Date**: 2026-06-02  
**Version**: 4.0.0  
**Status**: Stable
