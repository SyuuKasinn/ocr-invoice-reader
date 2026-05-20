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

## CLI

```
ocr-extract INPUT [-o OUTPUT_DIR] [--lang LANG] [--unwarp] [--orient]
                  [--max-pages N] [--no-html] [--no-markdown] [--no-viz]
                  [--no-inline-images] [--cpu] [-v]
```

Device selection is automatic — the pipeline probes for a CUDA-capable
PaddlePaddle install at startup and uses GPU when present, otherwise CPU.

Common flags:

| Flag | Meaning |
|---|---|
| `--max-pages N` | Stop after N pages — useful for quick smoke tests on long PDFs |
| `--unwarp` | Enable document unwarping (slower, better on curved scans) |
| `--orient` | Enable orientation classification |
| `--no-html` | Skip the HTML report |
| `--no-inline-images` | Reference the source file instead of base64-embedding it |
| `--cpu` | Force CPU even when a GPU is detected (debugging) |
| `-v` | Debug logging (shows per-page progress) |

---

## Python API

```python
from ocr_invoice_reader import Pipeline, PipelineConfig, VLConfig, IOConfig

pipeline = Pipeline(PipelineConfig(
    vl=VLConfig(),  # use_gpu=True by default; auto-falls back to CPU if no GPU
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

For GPU acceleration, install the CUDA build of PaddlePaddle from the
[official channel](https://www.paddlepaddle.org.cn/install/quick).
The pipeline auto-detects CUDA on startup; no flags needed.

---

## Docker

```bash
docker compose up
```

The default `docker-compose.yml` mounts `./data` (input) and `./results`
(output) and runs `ocr-extract /app/data/invoice.pdf`. Uncomment the
`deploy.resources` block to expose an NVIDIA GPU to the container; the
pipeline picks it up automatically.

---

## License

MIT — see [LICENSE](LICENSE).
