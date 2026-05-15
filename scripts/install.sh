#!/bin/bash

# OCR Invoice Reader - Smart Installer
# Automatically detects GPU and installs appropriate dependencies

set -e

echo "=========================================="
echo "OCR Invoice Reader - Smart Installer"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Detect GPU
echo "Step 1: Detecting hardware..."
if command -v nvidia-smi &> /dev/null; then
    if nvidia-smi &> /dev/null; then
        echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
        GPU_AVAILABLE=true

        # Get GPU info
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        echo "  GPU: $GPU_NAME"
        echo "  VRAM: ${GPU_MEMORY} MB"

        # Detect CUDA version
        CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
        echo "  CUDA: $CUDA_VERSION"
    else
        echo -e "${YELLOW}⚠ nvidia-smi found but not working${NC}"
        GPU_AVAILABLE=false
    fi
else
    echo -e "${YELLOW}⚠ No NVIDIA GPU detected${NC}"
    GPU_AVAILABLE=false
fi
echo ""

# Ask user preference
if [ "$GPU_AVAILABLE" = true ]; then
    echo "Step 2: Choose installation type"
    echo "  1. GPU version (recommended, faster)"
    echo "  2. CPU version (slower but works without GPU)"
    echo ""
    read -p "Your choice (1/2) [default: 1]: " CHOICE
    CHOICE=${CHOICE:-1}

    if [ "$CHOICE" = "2" ]; then
        USE_GPU=false
        echo -e "${YELLOW}Installing CPU version...${NC}"
    else
        USE_GPU=true
        echo -e "${GREEN}Installing GPU version...${NC}"
    fi
else
    USE_GPU=false
    echo "Step 2: Installing CPU version (no GPU available)"
fi
echo ""

# Uninstall conflicting packages
echo "Step 3: Cleaning up..."
pip uninstall -y paddlepaddle paddlepaddle-gpu torch torchvision torchaudio 2>/dev/null || true
echo ""

# Install base dependencies first
echo "Step 4: Installing base dependencies..."
pip install paddleocr pymupdf opencv-python Pillow numpy pandas requests tqdm
echo ""

# Install hardware-specific packages
if [ "$USE_GPU" = true ]; then
    echo "Step 5: Installing GPU packages..."

    # Detect CUDA version for appropriate packages
    if [[ "$CUDA_VERSION" == 12.* ]]; then
        echo "  Detected CUDA 12.x"
        CUDA_SHORT="120"
        TORCH_CUDA="cu121"
    elif [[ "$CUDA_VERSION" == 11.8* ]]; then
        echo "  Detected CUDA 11.8"
        CUDA_SHORT="118"
        TORCH_CUDA="cu118"
    else
        echo -e "${YELLOW}  ⚠ Unknown CUDA version, using CUDA 11.8 packages${NC}"
        CUDA_SHORT="118"
        TORCH_CUDA="cu118"
    fi

    # Install PaddlePaddle GPU
    echo "  Installing PaddlePaddle-GPU..."
    pip install paddlepaddle-gpu==3.0.0.post${CUDA_SHORT} -f https://www.paddlepaddle.org.cn/whl/linux/mkl/avx/stable.html

    # Install PyTorch GPU
    echo "  Installing PyTorch-GPU..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/${TORCH_CUDA}

    # Install transformers and quantization
    echo "  Installing LLM dependencies..."
    pip install transformers accelerate sentencepiece protobuf
    pip install bitsandbytes  # For quantization

else
    echo "Step 5: Installing CPU packages..."

    # Install PaddlePaddle CPU
    echo "  Installing PaddlePaddle-CPU..."
    pip install paddlepaddle==3.0.0.b2

    # Install PyTorch CPU
    echo "  Installing PyTorch-CPU..."
    pip install torch torchvision torchaudio

    # Install transformers (no quantization needed for CPU)
    echo "  Installing LLM dependencies..."
    pip install transformers accelerate sentencepiece protobuf
fi
echo ""

# Install optional API dependencies
echo "Step 6: Installing optional dependencies..."
read -p "Install API server support? (y/n) [default: y]: " INSTALL_API
INSTALL_API=${INSTALL_API:-y}

if [[ "$INSTALL_API" =~ ^[Yy]$ ]]; then
    pip install fastapi uvicorn python-multipart pydantic
    echo -e "${GREEN}  ✓ API support installed${NC}"
fi
echo ""

# Verify installation
echo "Step 7: Verifying installation..."

# Check PaddlePaddle
python3 -c "import paddle; print('✓ PaddlePaddle:', paddle.__version__)" || echo -e "${RED}✗ PaddlePaddle failed${NC}"

# Check PyTorch
python3 -c "import torch; print('✓ PyTorch:', torch.__version__); print('  CUDA available:', torch.cuda.is_available())" || echo -e "${RED}✗ PyTorch failed${NC}"

# Check Transformers
python3 -c "import transformers; print('✓ Transformers:', transformers.__version__)" || echo -e "${RED}✗ Transformers failed${NC}"

# Check OCR
python3 -c "from paddleocr import PaddleOCR; print('✓ PaddleOCR available')" || echo -e "${RED}✗ PaddleOCR failed${NC}"

echo ""

# Final message
echo "=========================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=========================================="
echo ""

if [ "$USE_GPU" = true ]; then
    echo "GPU Configuration:"
    echo "  ✓ PaddlePaddle-GPU installed"
    echo "  ✓ PyTorch-GPU installed"
    echo "  ✓ Quantization support (bitsandbytes)"
    echo ""
    echo "Test GPU:"
    echo "  python3 -c 'import torch; print(torch.cuda.is_available())'"
    echo "  nvidia-smi"
    echo ""
    echo "Recommended usage:"
    echo "  ocr-enhanced --image invoice.pdf --use-llm --llm-model 7b"
else
    echo "CPU Configuration:"
    echo "  ✓ PaddlePaddle-CPU installed"
    echo "  ✓ PyTorch-CPU installed"
    echo ""
    echo "Recommended usage:"
    echo "  ocr-enhanced --image invoice.pdf --use-llm --llm-model 3b"
fi

echo ""
echo "Test installation:"
echo "  python3 ocr_invoice_reader/utils/environment.py"
echo ""
echo "Run OCR:"
echo "  ocr-enhanced --image examples/INVOICE.pdf --use-llm"
echo ""
echo "=========================================="
