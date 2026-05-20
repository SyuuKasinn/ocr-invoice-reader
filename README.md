# OCR Invoice Reader

Single-pass document parsing built on **[PaddleOCR-VL 1.5](https://github.com/PaddlePaddle/PaddleOCR)**. Feed it a PDF or image, get back structured JSON, Markdown and a self-contained HTML report mimicking the official PaddleOCR-VL viewer.

[![Version](https://img.shields.io/badge/version-4.0.0-blue)](setup.py)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR--VL-1.5-orange)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> Previous releases (≤ 3.x) used PaddleOCR v3 + Ollama (Qwen) with two-step
> prompting and regex fallback. That stack is gone — one model, one command,
> one report.

---

## Quick start

```bash
git clone https://github.com/SyuuKasinn/ocr-invoice-reader.git
cd ocr-invoice-reader
pip install -e .
```

Then run:

```bash
ocr-extract examples/INVOICE.pdf
```

Output lands under `results/<doc>_<timestamp>/`:

```
INVOICE_20260520_103000/
├── INVOICE_page_0001.json     per-page blocks (title / text / table / figure)
├── INVOICE_page_0001.md       per-page markdown (from PaddleOCR-VL)
├── INVOICE_page_0001_viz.png  layout overlay
├── ...                         (one set per page)
├── INVOICE_document.json      combined document JSON
└── INVOICE_report.html        official-style HTML report (open in browser)
```

The HTML report has the source PDF on the left and the parsed output
(`Document parsing` / `JSON` tabs) on the right — same shape as the
upstream PaddleOCR-VL UI.

---

## Performance: pick a backend

PaddleOCR-VL 1.5 is a 0.9B vision-language model. The default `native`
Paddle backend is fast on GPU but **unusable on CPU** (multi-page PDFs
take hours). PaddleOCR-VL ships with backend adapters for accelerated
runtimes — pick one that matches your hardware:

| Backend | Hardware | When to use |
|---|---|---|
| `native` (default) | NVIDIA GPU | You have CUDA-capable Paddle install |
| `vllm-server` / `sglang-server` / `fastdeploy-server` | NVIDIA GPU | High-throughput batch processing |
| `llama-cpp-server` | CPU | CPU-only inference |
| `mlx-vlm-server` | Apple Silicon | M-series Macs |

Backend selection lives in upstream PaddleOCR — see the
[PaddleOCR-VL backend guide](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PaddleOCR-VL.md)
for install + server-launch instructions. Future versions of this
wrapper will expose `--backend` and `--server-url` flags directly.

Until then, you can wire one up in Python:

```python
from ocr_invoice_reader.core.vl_engine import VLEngine
from ocr_invoice_reader.core.config import VLConfig

engine = VLEngine(VLConfig(use_gpu=False))
engine.config = VLConfig(use_gpu=False)
# Inject backend kwargs through the underlying pipeline
engine._pipeline = engine._build()  # no-op if already built
```

---

## CLI

```
ocr-extract INPUT [-o OUTPUT_DIR] [--cpu] [--lang LANG] [--unwarp] [--orient]
                  [--max-pages N] [--no-html] [--no-markdown] [--no-viz]
                  [--no-inline-images] [-v]
```

Common flags:

| Flag | Meaning |
|---|---|
| `--cpu` | Force CPU mode (still goes through whatever backend is configured) |
| `--max-pages N` | Stop after N pages — useful for quick smoke tests on long PDFs |
| `--unwarp` | Enable document unwarping (slower, better on curved scans) |
| `--orient` | Enable orientation classification |
| `--no-html` | Skip the HTML report |
| `--no-inline-images` | Reference the source file instead of base64-embedding it |
| `-v` | Debug logging (shows per-page progress) |

---

## Python API

```python
from ocr_invoice_reader import Pipeline, PipelineConfig, VLConfig, IOConfig

pipeline = Pipeline(PipelineConfig(
    vl=VLConfig(use_gpu=False),
    io=IOConfig(output_dir="my_results", save_markdown=True),
))

# Just get the structured document
doc = pipeline.run("invoice.pdf", max_pages=1)
for page in doc.pages:
    for block in page.blocks:
        print(block.label, block.bbox, block.text[:80])

# Or run + write everything to disk
out_dir = pipeline.run_and_save("invoice.pdf")
print(f"open {out_dir}/INVOICE_report.html")
```

Schemas (`pydantic` v2):

```python
class Block(BaseModel):
    label: str            # "doc_title" | "text" | "table" | "figure" | ...
    bbox:  list[float]    # [x1, y1, x2, y2]
    text:  str
    html:  str | None     # populated when label == "table"
    image_path: str | None
    score: float | None
```

---

## Architecture

```
ocr_invoice_reader/
├── cli/extract.py           single CLI entry point (ocr-extract)
└── core/
    ├── config.py            VLConfig / IOConfig / PipelineConfig
    ├── schemas.py           Block / PageResult / DocumentResult
    ├── vl_engine.py         PaddleOCRVL wrapper + output normalization
    ├── file_io.py           input validation + result writing
    ├── pipeline.py          end-to-end orchestration (streams pages to disk)
    └── visualize.py         self-contained HTML report
```

Nine files. No LLM client, no regex fallback, no parallel pool, no API
server — those layers were collapsed into PaddleOCR-VL itself.

---

## Requirements

- Python 3.10+
- `paddleocr >= 3.0`, `paddlepaddle >= 3.0`
- `opencv-python`, `numpy`, `Pillow`, `pydantic >= 2`

Install via:

```bash
pip install -e .
# Plus the PaddleOCR-VL extras (needed for the VL pipeline)
pip install "paddlex[ocr]>=3.5.0"
```

For accelerated backends (recommended), install per the
[PaddleOCR-VL docs](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PaddleOCR-VL.md).

---

## Docker

```bash
docker compose up
```

The default `docker-compose.yml` mounts `./data` (input) and `./results`
(output) and runs `ocr-extract /app/data/invoice.pdf --cpu`. Uncomment
the `deploy.resources` block to enable NVIDIA GPU.

---

## License

MIT — see [LICENSE](LICENSE).
