# Changelog

All notable changes to this project will be documented in this file.

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
