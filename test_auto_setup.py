#!/usr/bin/env python
"""Test automatic Ollama setup"""

from ocr_invoice_reader.utils.ollama_manager import OllamaManager

def main():
    manager = OllamaManager()

    print("Testing Ollama auto-setup...")
    print("="*60)

    # Test with auto_confirm=True
    success, message = manager.setup("qwen2.5:0.5b", auto_confirm=True)

    print("\n" + "="*60)
    if success:
        print("✓ Setup successful!")
    else:
        print(f"✗ Setup failed: {message}")

    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
