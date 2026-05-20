# Changelog

## [4.0.0] - 2026-05-19

Complete rewrite around PaddleOCR-VL 1.5.

### Added
- `core/` package: `Pipeline`, `VLEngine`, `Block` / `PageResult` /
  `DocumentResult` pydantic schemas, official-style HTML report.
- Single `ocr-extract` CLI entry point.
- Per-page streaming: each page is written to disk as soon as PaddleOCR-VL
  finishes inference, instead of buffering the whole document.
- `--max-pages N` flag for fast smoke tests on long PDFs.
- Per-page progress logging in `vl_engine.predict()`.

### Removed
- Ollama / Qwen LLM extraction stack (`utils/llm_processor.py`,
  `utils/llm_invoice_extractor*.py`, `utils/ollama_manager.py`).
- Regex fallback extractors (`utils/invoice_extractor*.py`,
  `utils/customs_extractor.py`).
- PaddleOCR v3 + PP-Structure custom row-grouping layer
  (`processors/enhanced_structure_analyzer.py`,
  `processors/structure_analyzer.py`, `processors/field_extractor.py`).
- Six legacy CLI entry points (`ocr-enhanced`, `ocr-enhanced-parallel`,
  `ocr-simple`, `ocr-raw`, `ocr-customs`, `ocr-api`, `ocr-setup-ollama`).
- Flask HTTP API (`api/`).
- All `models/`, `extractors/`, `config/` (settings.py),
  most of `utils/`.

### Changed
- Requires `paddleocr>=3.0` and `paddlepaddle>=3.0` (was 2.8.x).
- `requirements.txt` slimmed from ~20 packages to 6.
- Output layout: one timestamped directory per run, containing per-page
  JSON/Markdown/visualization plus a combined `*_document.json` and a
  self-contained `*_report.html`.
- `setup.py` reads `__version__` from the package via regex instead of
  importing, so `pip install -e .` no longer needs runtime deps in
  the build env.

### Notes
- Device selection is automatic (CUDA-capable PaddlePaddle → GPU,
  otherwise CPU). `--cpu` is kept as an override for debugging.
- Docs under `docs/` and `guides/` from previous releases were removed;
  current docs live in this README.

---

## [2.3.x] and earlier

PaddleOCR v3 + Ollama (Qwen) hybrid pipeline. See git history before
`bc41591` for details.
