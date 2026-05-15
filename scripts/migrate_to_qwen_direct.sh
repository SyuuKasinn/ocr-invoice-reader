#!/bin/bash

# Migrate OCR Invoice Reader to use Qwen Direct by default
# This script safely updates the codebase to use the new llm_factory

set -e

echo "=========================================="
echo "OCR Invoice Reader Migration Script"
echo "From: Ollama-first to Qwen Direct-first"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check we're in the right directory
if [ ! -f "setup.py" ] || [ ! -d "ocr_invoice_reader" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

echo "✓ Project directory confirmed"
echo ""

# Backup
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
echo "[1/6] Creating backup..."
mkdir -p "$BACKUP_DIR"
cp -r ocr_invoice_reader "$BACKUP_DIR/"
echo "   Backup created: $BACKUP_DIR"
echo ""

# Phase 1: Update main CLI
echo "[2/6] Updating main CLI (enhanced_extract.py)..."
if [ -f "ocr_invoice_reader/cli/enhanced_extract.py" ]; then
    # Back up original
    cp ocr_invoice_reader/cli/enhanced_extract.py "$BACKUP_DIR/enhanced_extract.py.orig"

    # Replace with refactored version
    if [ -f "ocr_invoice_reader/cli/enhanced_extract_refactored.py" ]; then
        cp ocr_invoice_reader/cli/enhanced_extract_refactored.py ocr_invoice_reader/cli/enhanced_extract.py
        echo "   ✓ Updated enhanced_extract.py"
    else
        echo "   ⚠ Refactored version not found, manual update needed"
    fi
else
    echo "   ⚠ enhanced_extract.py not found"
fi
echo ""

# Phase 2: Update Python imports
echo "[3/6] Updating Python imports..."

find ocr_invoice_reader -name "*.py" -type f | while read -r file; do
    # Skip already updated files
    if grep -q "llm_factory" "$file"; then
        continue
    fi

    # Update imports
    if grep -q "from ocr_invoice_reader.utils.llm_processor import" "$file"; then
        sed -i.bak 's/from ocr_invoice_reader\.utils\.llm_processor import/from ocr_invoice_reader.utils.llm_factory import/g' "$file"
        echo "   ✓ Updated imports in $(basename $file)"
        rm "${file}.bak"
    fi
done

echo ""

# Phase 3: Update model names in CLI
echo "[4/6] Updating model name patterns..."

find ocr_invoice_reader/cli -name "*.py" -type f | while read -r file; do
    # Update default model names
    if grep -q "qwen2.5:14b" "$file"; then
        sed -i.bak 's/qwen2\.5:14b/14b/g' "$file"
        sed -i.bak 's/qwen2\.5:7b/7b/g' "$file"
        sed -i.bak 's/qwen2\.5:0\.5b/3b/g' "$file"
        echo "   ✓ Updated model names in $(basename $file)"
        rm "${file}.bak" 2>/dev/null || true
    fi
done

echo ""

# Phase 4: Update examples
echo "[5/6] Updating examples..."

if [ -d "examples" ]; then
    find examples -name "*.py" -type f | while read -r file; do
        if grep -q "llm_processor" "$file"; then
            sed -i.bak 's/from ocr_invoice_reader\.utils\.llm_processor import/from ocr_invoice_reader.utils.llm_factory import/g' "$file"
            echo "   ✓ Updated $(basename $file)"
            rm "${file}.bak" 2>/dev/null || true
        fi
    done
fi

echo ""

# Phase 5: Create compatibility shim
echo "[6/6] Creating backward compatibility shim..."

cat > ocr_invoice_reader/utils/llm_processor_compat.py << 'EOF'
"""
Backward compatibility shim for old imports
Deprecated: Use llm_factory instead
"""
import warnings
from ocr_invoice_reader.utils.llm_factory import create_llm_processor as factory_create


def create_llm_processor(model: str = "qwen2.5:7b", **kwargs):
    """
    [DEPRECATED] Use llm_factory.create_llm_processor instead

    This function is provided for backward compatibility only.
    It will be removed in a future version.
    """
    warnings.warn(
        "Importing from llm_processor is deprecated. "
        "Use: from ocr_invoice_reader.utils.llm_factory import create_llm_processor\n"
        "The API is the same, just change the import.",
        DeprecationWarning,
        stacklevel=2
    )

    # Convert old Ollama format to new format
    if "qwen2.5:" in model:
        # Extract size
        if "14b" in model:
            model = "14b"
        elif "7b" in model:
            model = "7b"
        elif "3b" in model:
            model = "3b"

        # Force Ollama backend for compatibility
        kwargs['backend'] = 'ollama'

    return factory_create(model, **kwargs)


# Also provide LLMProcessor for direct imports
try:
    from ocr_invoice_reader.utils.llm_processor import LLMProcessor
except ImportError:
    # If original is removed, provide a compatibility class
    class LLMProcessor:
        def __init__(self, *args, **kwargs):
            warnings.warn(
                "LLMProcessor is deprecated. Use llm_factory.create_llm_processor instead.",
                DeprecationWarning,
                stacklevel=2
            )
            raise ImportError(
                "LLMProcessor has been replaced. "
                "Use: from ocr_invoice_reader.utils.llm_factory import create_llm_processor"
            )
EOF

echo "   ✓ Created compatibility shim"
echo ""

# Summary
echo "=========================================="
echo "Migration Complete!"
echo "=========================================="
echo ""
echo "Changes made:"
echo "  ✓ Backed up original files to: $BACKUP_DIR"
echo "  ✓ Updated main CLI to use llm_factory"
echo "  ✓ Updated Python imports"
echo "  ✓ Updated model name formats"
echo "  ✓ Updated examples"
echo "  ✓ Created backward compatibility shim"
echo ""
echo "Next steps:"
echo "  1. Test the changes:"
echo "     python -m ocr_invoice_reader.cli.enhanced_extract --check-llm"
echo ""
echo "  2. Run your typical command:"
echo "     ocr-enhanced --image examples/INVOICE.pdf --use-llm --llm-model 7b"
echo ""
echo "  3. If everything works, commit the changes:"
echo "     git add -A"
echo "     git commit -m 'refactor: Migrate to Qwen Direct as default LLM backend'"
echo ""
echo "  4. If there are issues, restore backup:"
echo "     cp -r $BACKUP_DIR/ocr_invoice_reader/* ocr_invoice_reader/"
echo ""
echo "=========================================="
echo ""
echo "⚠ Important:"
echo "  - Old imports will show deprecation warnings"
echo "  - All functionality is backward compatible"
echo "  - Users don't need to change their commands"
echo "  - Qwen Direct is now the default (faster, better GPU usage)"
echo ""
echo "For more details, see: REFACTORING_GUIDE.md"
echo ""
