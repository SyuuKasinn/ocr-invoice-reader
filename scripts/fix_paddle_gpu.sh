#!/bin/bash
# Quick fix for PaddlePaddle GPU installation

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "PaddlePaddle GPU Fix Script"
echo "=========================================="
echo ""

# Check if GPU is available
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${RED}✗ No NVIDIA GPU detected${NC}"
    exit 1
fi

# Get CUDA version
CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
echo "Detected CUDA: $CUDA_VERSION"

# Determine PaddlePaddle version
if [[ "$CUDA_VERSION" == 13.* ]] || [[ "$CUDA_VERSION" == 12.* ]]; then
    PADDLE_VERSION="2.6.2.post120"
    echo "Using PaddlePaddle for CUDA 12.0+"
elif [[ "$CUDA_VERSION" == 11.* ]]; then
    PADDLE_VERSION="2.6.2.post117"
    echo "Using PaddlePaddle for CUDA 11.x"
else
    echo -e "${YELLOW}⚠ Unknown CUDA version, using CUDA 12.0 package${NC}"
    PADDLE_VERSION="2.6.2.post120"
fi

echo ""
echo "Step 1: Uninstalling old PaddlePaddle..."
pip uninstall -y paddlepaddle paddlepaddle-gpu 2>/dev/null || true

echo ""
echo "Step 2: Installing PaddlePaddle-GPU $PADDLE_VERSION..."
pip install paddlepaddle-gpu==$PADDLE_VERSION -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

echo ""
echo "Step 3: Verifying installation..."
python3 -c "import paddle; print('✓ PaddlePaddle:', paddle.__version__); print('  CUDA compiled:', paddle.is_compiled_with_cuda())"

echo ""
PADDLE_GPU_CHECK=$(python3 -c "import paddle; print(paddle.is_compiled_with_cuda())" 2>/dev/null)

if [ "$PADDLE_GPU_CHECK" = "True" ]; then
    echo "=========================================="
    echo -e "${GREEN}✓ Success! PaddlePaddle GPU is working${NC}"
    echo "=========================================="
    echo ""
    echo "Now OCR will use GPU acceleration!"
    echo ""
    echo "Test with:"
    echo "  ocr-enhanced --image invoice.pdf --use-llm"
else
    echo "=========================================="
    echo -e "${RED}✗ Installation failed${NC}"
    echo "=========================================="
    echo ""
    echo "PaddlePaddle installed but CUDA support not detected."
    echo "This may be due to:"
    echo "  1. CUDA toolkit version mismatch"
    echo "  2. Missing CUDA libraries"
    echo "  3. Incompatible PaddlePaddle version"
    echo ""
    echo "You can still use the system - LLM will use GPU (main bottleneck)."
    echo "OCR will fall back to CPU mode."
fi

echo ""
