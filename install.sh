#!/usr/bin/env bash
# Install ocr-invoice-reader with the right PaddlePaddle build for the host.
#
# - If `nvidia-smi` is present and reports a CUDA driver, install
#   `paddlepaddle-gpu` from the matching wheel index.
# - Otherwise install the CPU `paddlepaddle`.
# - Then `pip install -e .` to pull paddleocr / paddlex[ocr] / pydantic / ...
#
# Override CUDA index manually:
#     CUDA_INDEX=cu118 ./install.sh
#
# Force CPU even on a GPU host:
#     FORCE_CPU=1 ./install.sh

set -euo pipefail

PY="${PYTHON:-python3}"
PIP="$PY -m pip"

echo "[install] Python: $($PY --version 2>&1)"

# ---- decide paddle flavor ------------------------------------------------

flavor="cpu"
if [[ "${FORCE_CPU:-0}" != "1" ]] && command -v nvidia-smi >/dev/null 2>&1; then
    if nvidia-smi -L >/dev/null 2>&1; then
        flavor="gpu"
    else
        echo "[install] nvidia-smi present but reported no GPU; falling back to CPU"
    fi
fi

# ---- pick CUDA index for the GPU build -----------------------------------

if [[ "$flavor" == "gpu" ]]; then
    if [[ -n "${CUDA_INDEX:-}" ]]; then
        idx="$CUDA_INDEX"
    else
        cuda_str=$(nvidia-smi 2>/dev/null | grep -oE "CUDA Version: [0-9]+\.[0-9]+" | head -1 | awk '{print $3}')
        cuda_major="${cuda_str%%.*}"
        case "$cuda_major" in
            11) idx="cu118" ;;
            12) idx="cu126" ;;
            *)
                echo "[install] Unknown CUDA version '$cuda_str'; defaulting to cu126."
                echo "[install] Override with: CUDA_INDEX=cu118 ./install.sh"
                idx="cu126"
                ;;
        esac
        echo "[install] nvidia-smi reports CUDA $cuda_str -> using $idx wheel"
    fi
fi

# ---- clean any conflicting paddle install --------------------------------

echo "[install] Removing any existing paddlepaddle / paddlepaddle-gpu ..."
$PIP uninstall -y paddlepaddle paddlepaddle-gpu >/dev/null 2>&1 || true

# ---- install the right paddle --------------------------------------------

if [[ "$flavor" == "gpu" ]]; then
    echo "[install] Installing paddlepaddle-gpu (CUDA index: $idx)"
    $PIP install --upgrade "paddlepaddle-gpu>=3.0.0" \
        -i "https://www.paddlepaddle.org.cn/packages/stable/$idx/"
else
    echo "[install] Installing CPU paddlepaddle"
    $PIP install --upgrade "paddlepaddle>=3.0.0"
fi

# ---- install the rest via pyproject --------------------------------------

echo "[install] Installing ocr-invoice-reader (editable, no build isolation)"
$PIP install -e . --no-build-isolation

# ---- summary -------------------------------------------------------------

echo
echo "[install] Done."
$PY - <<'PY'
import paddle
print(f"  paddle.__version__      = {paddle.__version__}")
print(f"  compiled_with_cuda      = {paddle.device.is_compiled_with_cuda()}")
try:
    print(f"  visible GPU device count = {paddle.device.cuda.device_count()}")
except Exception as e:
    print(f"  visible GPU device count = (probe failed: {e})")
PY

echo
echo "Try it:"
echo "  ocr-extract path/to/your.pdf -o results"
