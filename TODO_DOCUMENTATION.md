# Documentation Update TODO

## ✅ Completed

- [x] Main README.md - Updated to Qwen Direct
- [x] CHANGELOG.md - Added v2.3.2 release notes
- [x] RELEASE_v2.3.2.md - Created release documentation
- [x] setup.py - Updated version, registered ocr-check-env
- [x] ocr_invoice_reader/__init__.py - Version 2.3.2
- [x] requirements.txt - PaddlePaddle 3.0.0 → 2.6.2
- [x] requirements-cpu.txt - Created with correct versions
- [x] requirements-gpu.txt - Created with correct versions
- [x] scripts/install.sh - Smart installer with CUDA 13.0 support
- [x] ocr_invoice_reader/cli/enhanced_extract.py - Qwen Direct integration
- [x] ocr_invoice_reader/cli/enhanced_extract_parallel.py - Qwen Direct integration
- [x] ocr_invoice_reader/utils/environment.py - Environment auto-detection
- [x] ocr_invoice_reader/cli/check_env.py - Diagnostic tool

## 🔄 Needs Update (Low Priority)

### Documentation Files

1. **docs/COMPLETE_GUIDE.md**
   - [ ] Line 3: Update version 2.3.1 → 2.3.2
   - [ ] Line 34-35: Replace `--auto-setup-ollama` with new installation
   - [ ] Installation section: Update with smart installer
   - [ ] Model references: `qwen2.5:14b` → `14b`

2. **docs/QUICK_START_GUIDE.md**
   - [ ] Update model naming convention
   - [ ] Replace Ollama references with Qwen Direct
   - [ ] Update installation instructions

3. **docs/OLLAMA_GPU_SETUP.md**
   - [ ] Mark as **DEPRECATED** at top
   - [ ] Add redirect to QWEN_DIRECT_SETUP.md
   - [ ] Keep for historical reference

4. **guides/QUICK_START_HYBRID.md**
   - [ ] Update model naming: `qwen2.5:X` → `Xb`
   - [ ] Update LLM initialization examples
   - [ ] Remove Ollama setup instructions

5. **guides/PARALLEL_PROCESSING.md**
   - [ ] Update command examples with new model naming
   - [ ] Update performance benchmarks if needed

6. **guides/LLM_HYBRID_EXTRACTION.md**
   - [ ] Update model references
   - [ ] Update code examples to use qwen_direct_processor

7. **guides/GLOVIA_INVOICE_EXTRACTION.md**
   - [ ] Update model naming in examples
   - [ ] Update installation instructions

### Python Code Files (Legacy, Low Priority)

8. **ocr_invoice_reader/cli/enhanced_extract_refactored.py**
   - [ ] Check if still used (may be old version)
   - [ ] Update if used, or mark as deprecated

9. **ocr_invoice_reader/cli/setup_ollama.py**
   - [ ] Mark as deprecated
   - [ ] Consider removing (replaced by check_env.py)

### API Documentation

10. **docs/API_USAGE.md**
    - [ ] Update code examples with Qwen Direct
    - [ ] Update model naming in examples

## 📝 Batch Update Script

Use `update_docs.sh` for batch replacements:

```bash
bash update_docs.sh
```

This will automatically replace:
- `qwen2.5:14b` → `14b`
- `qwen2.5:7b` → `7b`
- `qwen2.5:3b` → `3b`
- `--auto-setup-ollama` → (removed)
- Version 2.3.1 → 2.3.2

## 🎯 Priority

**HIGH** (Already completed):
- Core functionality (CLI, environment detection)
- Installation scripts
- Main README and CHANGELOG

**MEDIUM** (Next):
- COMPLETE_GUIDE.md
- QUICK_START guides
- Mark OLLAMA_GPU_SETUP.md as deprecated

**LOW** (Can defer):
- Other guides (users can infer from main docs)
- Legacy/refactored files
- Detailed API documentation

## 📌 Notes

- All core functionality is working with Qwen Direct
- Documentation inconsistencies won't break functionality
- Users will see correct info in README.md first
- Can update remaining docs incrementally
- Keep OLLAMA_GPU_SETUP.md for historical reference (mark as deprecated)

## 🚀 Server Priority

For immediate server deployment, focus on:
1. ✅ Pull latest code from GitHub
2. ✅ Run `bash scripts/install.sh`
3. ✅ Run `ocr-check-env` to verify
4. ✅ Test with sample invoice

Documentation updates can happen alongside server usage.
