#!/bin/bash

# OCR Invoice Reader v2.2.7 Update Test Script
# This script tests the GPU support and timeout fix on your server

set -e  # Exit on error

echo "=========================================="
echo "OCR Invoice Reader v2.2.7 Update Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

print_error() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Test 1: Check if we're in the right directory
echo "Test 1: Checking project directory..."
if [ -f "setup.py" ] && [ -d "ocr_invoice_reader" ]; then
    print_success "Project directory confirmed"
else
    print_error "Not in project root directory"
    echo "Please run this script from /root/ocr-invoice-reader-main"
    exit 1
fi

# Test 2: Check git status
echo ""
echo "Test 2: Checking git version..."
CURRENT_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$CURRENT_COMMIT" = "$REMOTE_COMMIT" ]; then
    print_success "Code is up to date with GitHub"
else
    print_error "Code is not up to date"
    echo "  Current: ${CURRENT_COMMIT:0:8}"
    echo "  Remote:  ${REMOTE_COMMIT:0:8}"
    echo ""
    echo "Attempting to pull latest changes..."
    git pull origin main
    if [ $? -eq 0 ]; then
        print_success "Successfully pulled latest changes"
    else
        print_error "Failed to pull changes"
        exit 1
    fi
fi

# Test 3: Check if new files exist
echo ""
echo "Test 3: Checking new files..."

if [ -f "scripts/fix_ollama_gpu.sh" ]; then
    print_success "GPU setup script exists"
else
    print_error "GPU setup script not found"
fi

if [ -f "docs/OLLAMA_GPU_SETUP.md" ]; then
    print_success "GPU documentation exists"
else
    print_error "GPU documentation not found"
fi

# Test 4: Check Python package version
echo ""
echo "Test 4: Checking Python package..."

python -c "
import sys
sys.path.insert(0, '.')
try:
    from ocr_invoice_reader.utils.llm_processor import LLMProcessor

    # Test timeout parameter
    processor = LLMProcessor('qwen2.5:14b')

    if hasattr(processor, 'timeout'):
        print('✓ Timeout attribute exists')
        print(f'  14B model timeout: {processor.timeout}s')
        if processor.timeout == 180:
            print('✓ Timeout is correct (180s for 14B)')
        else:
            print(f'✗ Timeout is {processor.timeout}s, expected 180s')
    else:
        print('✗ Timeout attribute not found')
        sys.exit(1)

    # Test different model sizes
    p_small = LLMProcessor('qwen2.5:0.5b')
    p_7b = LLMProcessor('qwen2.5:7b')

    print(f'  0.5B model timeout: {p_small.timeout}s')
    print(f'  7B model timeout: {p_7b.timeout}s')

    if p_small.timeout == 60 and p_7b.timeout == 120:
        print('✓ All model timeouts configured correctly')
    else:
        print('✗ Model timeouts not configured correctly')
        sys.exit(1)

except Exception as e:
    print(f'✗ Error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    ((TESTS_PASSED += 3))
else
    ((TESTS_FAILED += 3))
fi

# Test 5: Check GPU availability
echo ""
echo "Test 5: Checking GPU..."

if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader)
    print_success "NVIDIA GPU detected"
    echo "  GPU: $GPU_INFO"

    # Check CUDA
    if command -v nvcc &> /dev/null; then
        CUDA_VERSION=$(nvcc --version | grep "release" | awk '{print $5}' | sed 's/,//')
        print_success "CUDA installed: $CUDA_VERSION"
    else
        print_info "CUDA compiler not found (may still work with runtime)"
    fi
else
    print_error "No NVIDIA GPU found"
    echo "  GPU acceleration will not be available"
fi

# Test 6: Check Ollama status
echo ""
echo "Test 6: Checking Ollama..."

if command -v ollama &> /dev/null; then
    print_success "Ollama is installed"

    # Check if Ollama is running
    if curl -s http://localhost:11434 > /dev/null 2>&1; then
        print_success "Ollama service is running"

        # Check available models
        MODELS=$(ollama list 2>/dev/null)
        if [ $? -eq 0 ]; then
            print_success "Can query Ollama models"
            echo ""
            echo "Available models:"
            echo "$MODELS" | grep -E "qwen2.5|NAME" || echo "  No qwen2.5 models found"
            echo ""

            # Check if recommended model is available
            if echo "$MODELS" | grep -q "qwen2.5:7b\|qwen2.5:14b"; then
                print_success "Recommended model installed"
            else
                print_info "No qwen2.5:7b or 14b model found"
                echo "  Run: ollama pull qwen2.5:7b"
            fi
        fi
    else
        print_error "Ollama service not running"
        echo "  Starting Ollama..."
        nohup ollama serve > /tmp/ollama.log 2>&1 &
        sleep 3
        if curl -s http://localhost:11434 > /dev/null 2>&1; then
            print_success "Ollama started successfully"
        else
            print_error "Failed to start Ollama"
        fi
    fi
else
    print_error "Ollama not installed"
    echo "  Install: curl -fsSL https://ollama.ai/install.sh | sh"
fi

# Test 7: Check if Ollama is using GPU
echo ""
echo "Test 7: Checking Ollama GPU usage..."

if [ -f /tmp/ollama.log ]; then
    if grep -qi "nvidia gpu detected" /tmp/ollama.log; then
        print_success "Ollama detected NVIDIA GPU"
        CUDA_CAP=$(grep -i "cuda compute capability" /tmp/ollama.log | tail -1)
        if [ ! -z "$CUDA_CAP" ]; then
            echo "  $CUDA_CAP"
        fi
    else
        print_info "GPU detection uncertain"
        echo "  Check /tmp/ollama.log for details"
        echo "  Last 5 lines:"
        tail -5 /tmp/ollama.log | sed 's/^/    /'
    fi
else
    print_info "Ollama log not found at /tmp/ollama.log"
fi

# Test 8: Test OCR command (dry run check)
echo ""
echo "Test 8: Checking OCR command..."

if command -v ocr-enhanced &> /dev/null; then
    print_success "ocr-enhanced command is available"
else
    print_error "ocr-enhanced command not found"
    echo "  Run: pip install -e ."
fi

# Test 9: Run actual OCR test if sample file exists
echo ""
echo "Test 9: Running OCR test..."

SAMPLE_FILE="examples/INVOICE.pdf"
if [ -f "$SAMPLE_FILE" ]; then
    print_success "Sample file found: $SAMPLE_FILE"

    # Check if we should run the test
    echo ""
    echo "Ready to run actual OCR test with LLM."
    echo "This will process 1 page to verify the timeout fix."
    echo ""
    read -p "Run test? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "Running OCR test..."
        echo "Command: ocr-enhanced --image $SAMPLE_FILE --lang ch --use-llm --llm-model qwen2.5:7b"
        echo ""

        # Create a temporary test with just 1 page
        START_TIME=$(date +%s)

        timeout 200 ocr-enhanced --image "$SAMPLE_FILE" --lang ch --use-llm --llm-model qwen2.5:7b 2>&1 | tee /tmp/ocr_test_output.log

        EXIT_CODE=${PIPESTATUS[0]}
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))

        echo ""
        if [ $EXIT_CODE -eq 0 ]; then
            print_success "OCR test completed successfully in ${DURATION}s"

            # Check if LLM files were created
            LATEST_RESULT=$(ls -td results/*/ 2>/dev/null | head -1)
            if [ ! -z "$LATEST_RESULT" ]; then
                LLM_FILES=$(find "$LATEST_RESULT" -name "*_llm.json" 2>/dev/null | wc -l)
                if [ $LLM_FILES -gt 0 ]; then
                    print_success "LLM JSON files generated ($LLM_FILES files)"
                    echo "  Latest results: $LATEST_RESULT"

                    # Show sample LLM output
                    SAMPLE_LLM=$(find "$LATEST_RESULT" -name "*_llm.json" 2>/dev/null | head -1)
                    if [ -f "$SAMPLE_LLM" ]; then
                        echo ""
                        echo "Sample LLM output:"
                        cat "$SAMPLE_LLM" | python -m json.tool 2>/dev/null | head -20 || cat "$SAMPLE_LLM" | head -20
                    fi
                else
                    print_error "No LLM JSON files found"
                fi
            fi

            # Check for timeout errors in output
            if grep -qi "timeout" /tmp/ocr_test_output.log; then
                print_error "Timeout errors still present in output"
                echo "  Check /tmp/ocr_test_output.log"
            else
                print_success "No timeout errors detected"
            fi
        elif [ $EXIT_CODE -eq 124 ]; then
            print_error "Test timed out after 200s"
        else
            print_error "OCR test failed with exit code $EXIT_CODE"
            echo "  Check /tmp/ocr_test_output.log for details"
        fi
    else
        print_info "OCR test skipped"
    fi
else
    print_info "Sample file not found, skipping OCR test"
    echo "  Place a PDF at $SAMPLE_FILE to test"
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. If GPU not configured: bash scripts/fix_ollama_gpu.sh"
    echo "2. If model not installed: ollama pull qwen2.5:7b"
    echo "3. Run full test: ocr-enhanced --image examples/INVOICE.pdf --lang ch --use-llm --llm-model qwen2.5:7b"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Update code: git pull origin main && pip install -e ."
    echo "2. Setup GPU: bash scripts/fix_ollama_gpu.sh"
    echo "3. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "4. Install model: ollama pull qwen2.5:7b"
    echo ""
    echo "For detailed help, see docs/OLLAMA_GPU_SETUP.md"
    echo ""
    exit 1
fi
