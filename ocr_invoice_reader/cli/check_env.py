#!/usr/bin/env python3
"""
Environment checker - Diagnose hardware and dependencies
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ocr_invoice_reader.utils.environment import EnvironmentConfig


def main():
    """Main entry point"""
    print()
    print("="*70)
    print(" "*20 + "Environment Diagnostic Tool")
    print("="*70)
    print()

    env = EnvironmentConfig()

    # Hardware Info
    print("📊 Hardware Information")
    print("-"*70)
    print(f"Platform: {env.platform}")
    print(f"CPU Cores: {env.cpu_count}")
    print()

    if env.gpu_available:
        print(f"GPU: ✓ Available")
        print(f"  Name: {env.gpu_name}")
        print(f"  Memory: {env.gpu_memory:.1f} GB")
        print(f"  CUDA: {'✓ Available' if env.cuda_available else '✗ Not available'}")

        # Test GPU
        try:
            import torch
            if torch.cuda.is_available():
                print(f"  PyTorch CUDA: ✓ Working")
                print(f"  CUDA Version: {torch.version.cuda}")

                # Test tensor creation
                test_tensor = torch.tensor([1.0], device='cuda')
                print(f"  GPU Test: ✓ Passed")
            else:
                print(f"  PyTorch CUDA: ✗ Not working")
        except Exception as e:
            print(f"  GPU Test: ✗ Failed ({e})")
    else:
        print(f"GPU: ✗ Not available")
        print(f"  Will use CPU for all operations")

    print()

    # Dependencies Check
    print("📦 Dependencies Check")
    print("-"*70)

    deps = {
        'PaddlePaddle': 'paddle',
        'PaddleOCR': 'paddleocr',
        'PyTorch': 'torch',
        'Transformers': 'transformers',
        'Accelerate': 'accelerate',
        'BitsAndBytes': 'bitsandbytes',
        'FastAPI': 'fastapi',
        'PyMuPDF': 'fitz',
        'OpenCV': 'cv2',
    }

    for name, module in deps.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', 'unknown')
            print(f"✓ {name:20s} {version}")

            # Special check for PaddlePaddle CUDA support
            if name == 'PaddlePaddle' and env.gpu_available:
                try:
                    import paddle
                    has_cuda = paddle.is_compiled_with_cuda()
                    if has_cuda:
                        print(f"  └─ CUDA support: ✓ Enabled")
                    else:
                        print(f"  └─ CUDA support: ✗ Not compiled with CUDA")
                        print(f"     Run: bash scripts/fix_paddle_gpu.sh")
                except:
                    pass
        except ImportError:
            optional = name in ['BitsAndBytes', 'FastAPI']
            prefix = '⚠' if optional else '✗'
            suffix = ' (optional)' if optional else ' (required)'
            print(f"{prefix} {name:20s} Not installed{suffix}")

    print()

    # Recommended Configuration
    print("⚙️  Recommended Configuration")
    print("-"*70)

    config = env.get_recommended_llm_config()
    print(f"Backend: {config['backend']}")
    print(f"Model Size: {config['model_size']}")
    print(f"Device: {config['device']}")
    if config.get('quantization'):
        print(f"Quantization: {config['quantization']}")
    print()

    # Installation Instructions
    ok, missing = env.check_dependencies()

    if not ok:
        print("🔧 Installation Required")
        print("-"*70)
        print("Missing dependencies detected. Install with:")
        print()

        if env.gpu_available:
            print("# GPU Version (recommended)")
            print("bash scripts/install.sh")
            print()
            print("# Or manually:")
            print(env.get_install_command())
            print("pip install transformers accelerate bitsandbytes")
            print("pip install paddlepaddle-gpu")
        else:
            print("# CPU Version")
            print("bash scripts/install.sh")
            print()
            print("# Or manually:")
            print(env.get_install_command())
            print("pip install transformers accelerate")
            print("pip install paddlepaddle")

        print()

    # Usage Examples
    print("💡 Usage Examples")
    print("-"*70)

    if env.gpu_available:
        print("# With GPU (recommended)")
        print(f"ocr-enhanced --image invoice.pdf --use-llm --llm-model {config['model_size']}")
        print()
        print("# Monitor GPU usage")
        print("watch -n 1 nvidia-smi")
    else:
        print("# With CPU")
        print(f"ocr-enhanced --image invoice.pdf --use-llm --llm-model {config['model_size']}")
        print()
        print("# Note: CPU inference is slower than GPU")

    print()

    # Environment Variables
    print("🔐 Environment Variables")
    print("-"*70)
    import os
    env_vars = {
        'OMP_NUM_THREADS': os.environ.get('OMP_NUM_THREADS', 'not set'),
        'MKL_NUM_THREADS': os.environ.get('MKL_NUM_THREADS', 'not set'),
        'CUDA_VISIBLE_DEVICES': os.environ.get('CUDA_VISIBLE_DEVICES', 'not set'),
        'HF_ENDPOINT': os.environ.get('HF_ENDPOINT', 'not set (using default)'),
    }

    for key, value in env_vars.items():
        print(f"{key:25s} = {value}")

    print()

    # Summary
    print("="*70)
    if ok and env.gpu_available:
        print("✅ System ready for GPU-accelerated OCR + LLM!")
    elif ok:
        print("✅ System ready for CPU-based OCR + LLM")
    else:
        print("⚠️  Please install missing dependencies")

    print("="*70)
    print()

    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
