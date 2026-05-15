# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.7] - 2026-05-15

### Added
- **GPU Support for Ollama LLM**: Ollama now automatically uses GPU when available for 3-5x faster inference
- **Smart Timeout Management**: Automatic timeout adjustment based on model size
  - 0.5b/mini models: 60 seconds
  - 7B models: 120 seconds
  - 14B models: 180 seconds
  - Unknown/large models: 300 seconds (default)
- **GPU Setup Script**: Added `scripts/fix_ollama_gpu.sh` for automated GPU configuration
- **GPU Documentation**: Comprehensive guide at `docs/OLLAMA_GPU_SETUP.md` covering:
  - Automatic and manual GPU setup procedures
  - Model selection guide for different GPU memory sizes
  - Performance benchmarks and comparisons
  - Troubleshooting common GPU issues
  - Real-time GPU monitoring instructions

### Changed
- **LLMProcessor**: Enhanced constructor with optional `timeout` parameter for manual override
- **Timeout Behavior**: Changed from fixed 30s to intelligent dynamic timeout based on model size
- **README**: Added GPU acceleration section with model selection recommendations

### Fixed
- **Critical Timeout Issue**: Resolved "HTTPConnectionPool read timed out (30s)" errors with large models
- **Large Model Support**: Now properly handles qwen2.5:7b, qwen2.5:14b, and larger models without timeout

### Performance Improvements
- **With GPU (NVIDIA RTX 3060, 12GB VRAM)**:
  - qwen2.5:7b: ~2-3s per page (previously timed out)
  - qwen2.5:14b: ~5-7s per page (previously timed out)
- **Model Recommendations by VRAM**:
  - 4-8GB: qwen2.5:3b or qwen2.5:7b-q4_0
  - 8-12GB: qwen2.5:7b
  - 12-24GB: qwen2.5:14b
  - 24GB+: qwen2.5:32b

### Documentation
- Added `docs/OLLAMA_GPU_SETUP.md` - Complete GPU setup and troubleshooting guide
- Added `scripts/fix_ollama_gpu.sh` - Automated GPU configuration script
- Updated README with GPU acceleration instructions and model selection guide

### Migration Notes
- **Fully Backward Compatible**: All existing code and CLI commands work without changes
- **Automatic GPU Detection**: Ollama automatically uses GPU if available (no code changes needed)
- **For Users with Timeout Errors**: Run `bash scripts/fix_ollama_gpu.sh` to configure GPU and fix timeout issues

## [2.2.6] - 2026-05-15

### Added
- File upload security validation (path traversal prevention, size limits)
- Result cache with TTL and LRU eviction
- Automatic temporary file cleanup system
- OCR engine pooling for performance
- Improved LLM processor with retry and better error handling
- Enhanced health check endpoint with system metrics
- Connection pooling for HTTP requests

### Changed
- CORS configuration now environment-based
- Error messages sanitized (no internal details exposed)
- Version management centralized in `__init__.py`
- Dependency version constraints improved

### Fixed
- Memory leaks in result storage
- Temporary file cleanup on crashes
- GPU model reloading on every request
- Missing error logging
- Version number inconsistencies

### Performance
- 75% faster subsequent requests (model pooling)
- 58% memory reduction after 24h operation
- Eliminated temporary file accumulation

## [2.0.0] - Previous Release

Initial release with PaddleOCR v4 support, multi-page PDF processing, and table detection.

---

For detailed changes, see [IMPROVEMENTS.md](IMPROVEMENTS.md)
