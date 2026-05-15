#!/bin/bash

# Ollama GPU Setup and Timeout Fix Script
# This script configures Ollama to use GPU and fixes timeout issues with large models

echo "=========================================="
echo "Ollama GPU Setup & Timeout Fix"
echo "=========================================="

# 1. Check GPU
echo ""
echo "[1/4] Checking GPU..."
if nvidia-smi &>/dev/null; then
    echo "✓ GPU detected:"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
else
    echo "✗ No NVIDIA GPU found"
    echo "Ollama will run in CPU mode"
fi

# 2. Setup Ollama environment for GPU
echo ""
echo "[2/4] Configuring Ollama for GPU..."
export CUDA_VISIBLE_DEVICES=0
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_MAX_LOADED_MODELS=1

# Restart Ollama to apply settings
echo "Restarting Ollama service..."
pkill ollama 2>/dev/null
sleep 2
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 5

# Check if Ollama is running
if curl -s http://localhost:11434 > /dev/null; then
    echo "✓ Ollama service is running"
else
    echo "✗ Failed to start Ollama service"
    exit 1
fi

# Check if GPU is detected by Ollama
echo ""
echo "[3/4] Verifying GPU detection..."
if [ -f /tmp/ollama.log ]; then
    if grep -iq "nvidia gpu detected" /tmp/ollama.log; then
        echo "✓ Ollama detected NVIDIA GPU"
    else
        echo "⚠ GPU detection uncertain, check /tmp/ollama.log"
        echo "Last 10 lines of Ollama log:"
        tail -10 /tmp/ollama.log
    fi
fi

# 4. List available models
echo ""
echo "[4/4] Checking installed models..."
ollama list

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "GPU Status:"
echo "  - Run 'watch -n 1 nvidia-smi' to monitor GPU usage"
echo ""
echo "Recommended models for different GPU memory sizes:"
echo "  - 4-8GB VRAM:  qwen2.5:3b or qwen2.5:7b-q4_0"
echo "  - 8-12GB VRAM: qwen2.5:7b"
echo "  - 12-24GB VRAM: qwen2.5:14b"
echo "  - 24GB+ VRAM:   qwen2.5:32b"
echo ""
echo "To install a model:"
echo "  ollama pull qwen2.5:7b"
echo ""
echo "To test OCR with LLM:"
echo "  ocr-enhanced --image invoice.pdf --lang ch --use-llm"
