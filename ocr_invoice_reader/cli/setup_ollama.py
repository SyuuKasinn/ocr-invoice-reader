"""
Ollama设置命令行工具
"""
import argparse
import sys
from ocr_invoice_reader.utils.ollama_manager import OllamaManager


def main():
    """Ollama设置CLI"""
    parser = argparse.ArgumentParser(
        prog="ocr-setup-ollama",
        description="Setup Ollama for OCR Invoice Reader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 交互式设置（推荐）
  ocr-setup-ollama

  # 自动设置（无提示）
  ocr-setup-ollama --auto

  # 使用特定模型
  ocr-setup-ollama --model phi3:mini

  # 只检查状态
  ocr-setup-ollama --status
        """
    )

    parser.add_argument(
        '--model',
        type=str,
        default='qwen2.5:3b',
        help='LLM model to use (default: qwen2.5:3b)'
    )

    parser.add_argument(
        '--auto',
        action='store_true',
        help='Automatic setup without prompts'
    )

    parser.add_argument(
        '--status',
        action='store_true',
        help='Check Ollama status only'
    )

    args = parser.parse_args()

    manager = OllamaManager()

    # Status check mode
    if args.status:
        print("\n" + "=" * 60)
        print("Ollama Status")
        print("=" * 60)

        status = manager.get_status()

        print(f"\nInstallation: {'✓ Installed' if status['installed'] else '✗ Not installed'}")
        print(f"Service running: {'✓ Running' if status['service_running'] else '✗ Not running'}")

        if status['models']:
            print(f"\nDownloaded models:")
            for model in status['models']:
                print(f"  - {model}")
        else:
            print(f"\nDownloaded models: None")

        print("\n" + "=" * 60)

        # Return status code
        if status['installed'] and status['service_running'] and status['models']:
            print("✓ Ollama is ready")
            return 0
        else:
            print("✗ Ollama is not fully configured")
            print("\nRun the following command to complete setup:")
            print("  ocr-setup-ollama")
            return 1

    # Setup mode
    print("\n" + "=" * 60)
    print("Ollama Automatic Setup Tool")
    print("=" * 60)
    print(f"\nTarget model: {args.model}")

    if args.auto:
        print("Mode: Automatic (no prompts)")
    else:
        print("Mode: Interactive")

    success, message = manager.setup(args.model, auto_confirm=args.auto)

    if success:
        print("\n" + "=" * 60)
        print("✓ Setup complete!")
        print("=" * 60)
        print("\nYou can now use LLM features:")
        print(f"  ocr-enhanced --image invoice.pdf --use-llm")
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ Setup failed")
        print("=" * 60)
        print(f"\nReason: {message}")
        print("\nPlease refer to the following documentation:")
        print("  - OLLAMA_SETUP_QUICK.md")
        print("  - LLM_INTEGRATION_GUIDE.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
