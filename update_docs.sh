#!/bin/bash
# Script to update documentation references from Ollama to Qwen Direct

echo "Updating documentation..."

# Replace old model naming with new
find docs guides -type f -name "*.md" -exec sed -i 's/qwen2\.5:14b/14b/g' {} \;
find docs guides -type f -name "*.md" -exec sed -i 's/qwen2\.5:7b/7b/g' {} \;
find docs guides -type f -name "*.md" -exec sed -i 's/qwen2\.5:3b/3b/g' {} \;
find docs guides -type f -name "*.md" -exec sed -i 's/qwen2\.5:0\.5b/3b/g' {} \;

# Replace --auto-setup-ollama with new approach
find docs guides -type f -name "*.md" -exec sed -i 's/--auto-setup-ollama//g' {} \;

# Update version references
find docs guides -type f -name "*.md" -exec sed -i 's/Version\*\*: 2\.3\.1/Version**: 2.3.2/g' {} \;

echo "✓ Documentation updated"
echo ""
echo "Manual review recommended for:"
echo "  - docs/COMPLETE_GUIDE.md"
echo "  - docs/OLLAMA_GPU_SETUP.md (mark as deprecated)"
echo "  - guides/QUICK_START_HYBRID.md"
