#!/bin/bash
# Quick Docker test script

set -e

echo "🐳 Testing Docker deployment..."
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✓ Docker is installed"
echo

# Build image
echo "📦 Building Docker image..."
docker build -t ocr-invoice-reader:test .
echo "✓ Image built successfully"
echo

# Test font installation
echo "🔍 Checking Chinese fonts in container..."
docker run --rm ocr-invoice-reader:test fc-list :lang=zh | head -5
echo

# Test font loading in Python
echo "🐍 Testing font loading in Python..."
docker run --rm ocr-invoice-reader:test python -c "
from ocr_invoice_reader.utils.visualizer import OCRVisualizer
viz = OCRVisualizer()
print('Font loaded successfully!')
"
echo

echo "✅ Docker deployment test passed!"
echo
echo "To run the application:"
echo "  docker-compose up"
echo
echo "Or with a file:"
echo "  docker run -it --rm \\"
echo "    -v \$(pwd)/data:/app/data \\"
echo "    -v \$(pwd)/results:/app/results \\"
echo "    ocr-invoice-reader:test \\"
echo "    ocr-enhanced --image /app/data/invoice.pdf --visualize --use-cpu"
