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

**Python 3.10+ is required** (PaddleOCR-VL pulls `safetensors>=0.7` which
dropped Python 3.8/3.9). On systems whose default Python is older — autodl
containers, Debian/Ubuntu LTS, etc. — create a fresh env first:

```bash
conda create -n vl python=3.10 -y && conda activate vl
# or: python3.10 -m venv .venv && source .venv/bin/activate
```

Then clone and run the installer:

```bash
git clone https://github.com/SyuuKasinn/ocr-invoice-reader.git
cd ocr-invoice-reader
./install.sh

ocr-extract path/to/your_invoice.pdf
```

`install.sh` probes for `nvidia-smi`; if a GPU is visible it installs the
matching `paddlepaddle-gpu` wheel (CUDA 11.x → `cu118`, CUDA 12.x → `cu126`),
otherwise it installs the CPU build. Override with:

```bash
FORCE_CPU=1 ./install.sh          # ignore GPU, install CPU build
CUDA_INDEX=cu118 ./install.sh     # pick a specific wheel index
```

After paddle is in place the script runs `pip install -e .` to pull the
remaining deps (paddleocr, paddlex[ocr], pydantic, ...).

> **Windows**: run via Git Bash or WSL. Pure PowerShell users can run
> the two install steps manually — see *Manual install* below.

> `examples/INVOICE.pdf` is gitignored (sample documents are not
> redistributed). Drop your own PDF or image in to test.

### Manual install

If you can't run `install.sh`:

```bash
# 1. install paddle (pick ONE)
pip install "paddlepaddle>=3.0.0"                            # CPU
pip install "paddlepaddle-gpu>=3.0.0" \
    -i https://www.paddlepaddle.org.cn/packages/stable/cu118/   # GPU CUDA 11.8
pip install "paddlepaddle-gpu>=3.0.0" \
    -i https://www.paddlepaddle.org.cn/packages/stable/cu126/   # GPU CUDA 12.x

# 2. install the rest
pip install -e . --no-build-isolation
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

| | |
|---|---|
| Python | **3.10+** (required by `safetensors>=0.7` which `paddlex[ocr]` pulls) |
| PaddlePaddle | `paddlepaddle>=3.0` (CPU) **or** `paddlepaddle-gpu>=3.0` (GPU). Picked by `install.sh` based on `nvidia-smi`; not pinned in `pyproject.toml` so the editable install does not overwrite the GPU build. |
| Runtime | `paddleocr>=3.0`, `paddlex[ocr]>=3.5.0` |
| Libraries | `opencv-python`, `numpy`, `Pillow`, `pydantic>=2` |

Everything except paddlepaddle is in `requirements.txt`; `install.sh`
takes care of paddle and then runs `pip install -e .`. At runtime,
`vl_engine._gpu_ok()` checks `paddle.device.is_compiled_with_cuda()` and
`paddle.device.cuda.device_count()`, and logs which backend it picked
(and why if it falls back to CPU).

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
