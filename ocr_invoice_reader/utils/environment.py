"""
Environment configuration and auto-detection
Handles CPU/GPU compatibility, environment variables, and dependencies
"""
import os
import sys
import platform
import warnings
from typing import Dict, Optional, Tuple


class EnvironmentConfig:
    """Environment configuration manager"""

    def __init__(self):
        self.platform = platform.system()
        self.gpu_available = False
        self.cuda_available = False
        self.gpu_name = None
        self.gpu_memory = None
        self.cpu_count = os.cpu_count() or 1

        # Detect hardware
        self._detect_gpu()
        self._configure_environment()

    def _detect_gpu(self):
        """Detect GPU availability"""
        try:
            import torch
            self.gpu_available = torch.cuda.is_available()
            self.cuda_available = self.gpu_available

            if self.gpu_available:
                self.gpu_name = torch.cuda.get_device_name(0)
                self.gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        except ImportError:
            pass

    def _configure_environment(self):
        """Configure environment variables based on hardware"""

        # PaddlePaddle OpenBLAS threading
        # Set to 1 for single-threaded operation (avoids warning)
        if 'OMP_NUM_THREADS' not in os.environ:
            os.environ['OMP_NUM_THREADS'] = '1'

        if 'MKL_NUM_THREADS' not in os.environ:
            os.environ['MKL_NUM_THREADS'] = '1'

        # For CPU-only: optimize number of threads
        if not self.gpu_available:
            # Use half of available CPU cores for inference
            optimal_threads = max(1, self.cpu_count // 2)
            os.environ['OMP_NUM_THREADS'] = str(optimal_threads)
            os.environ['MKL_NUM_THREADS'] = str(optimal_threads)

        # Disable some CUDA warnings if GPU available
        if self.gpu_available:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    def get_recommended_device(self) -> str:
        """Get recommended device for inference"""
        return 'gpu' if self.gpu_available else 'cpu'

    def get_recommended_llm_config(self) -> Dict:
        """Get recommended LLM configuration based on hardware"""

        if not self.gpu_available:
            # CPU configuration
            return {
                'backend': 'qwen_direct',
                'model_size': '3b',  # Small model for CPU
                'use_gpu': False,
                'quantization': None,  # CPU doesn't need quantization
                'device': 'cpu'
            }

        # GPU configuration based on VRAM
        if self.gpu_memory:
            if self.gpu_memory >= 16:
                # 16GB+: Can use 14B
                return {
                    'backend': 'qwen_direct',
                    'model_size': '14b',
                    'use_gpu': True,
                    'quantization': 'int4',
                    'device': 'cuda'
                }
            elif self.gpu_memory >= 8:
                # 8-16GB: Use 7B
                return {
                    'backend': 'qwen_direct',
                    'model_size': '7b',
                    'use_gpu': True,
                    'quantization': 'int4',
                    'device': 'cuda'
                }
            else:
                # 4-8GB: Use 3B
                return {
                    'backend': 'qwen_direct',
                    'model_size': '3b',
                    'use_gpu': True,
                    'quantization': 'int4',
                    'device': 'cuda'
                }

        # Default GPU config
        return {
            'backend': 'qwen_direct',
            'model_size': '7b',
            'use_gpu': True,
            'quantization': 'int4',
            'device': 'cuda'
        }

    def check_dependencies(self) -> Tuple[bool, list]:
        """Check if all required dependencies are installed"""
        missing = []

        # Core dependencies
        try:
            import torch
        except ImportError:
            missing.append('torch')

        try:
            import transformers
        except ImportError:
            missing.append('transformers')

        try:
            import accelerate
        except ImportError:
            missing.append('accelerate')

        # Optional: quantization support
        if self.gpu_available:
            try:
                import bitsandbytes
            except ImportError:
                missing.append('bitsandbytes (optional, for quantization)')

        return len(missing) == 0, missing

    def get_install_command(self) -> str:
        """Get appropriate pip install command for current system"""

        # Check if we have CUDA
        if self.gpu_available:
            try:
                import torch
                cuda_version = torch.version.cuda

                if cuda_version:
                    major, minor = cuda_version.split('.')[:2]
                    cuda_short = f"cu{major}{minor}"

                    return f"pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/{cuda_short}"

            except:
                pass

        # CPU or unknown CUDA
        return "pip install torch torchvision torchaudio"

    def print_status(self):
        """Print environment status"""
        print("="*60)
        print("Environment Configuration")
        print("="*60)
        print(f"Platform: {self.platform}")
        print(f"CPU Cores: {self.cpu_count}")
        print(f"GPU Available: {self.gpu_available}")

        if self.gpu_available:
            print(f"GPU Name: {self.gpu_name}")
            print(f"GPU Memory: {self.gpu_memory:.1f} GB")
            print(f"CUDA Available: {self.cuda_available}")

        print()
        print("Recommended Configuration:")
        config = self.get_recommended_llm_config()
        for key, value in config.items():
            print(f"  {key}: {value}")

        print()
        print("Dependencies:")
        ok, missing = self.check_dependencies()
        if ok:
            print("  ✓ All dependencies installed")
        else:
            print(f"  ✗ Missing: {', '.join(missing)}")
            print(f"\n  Install with:")
            print(f"  {self.get_install_command()}")
            print(f"  pip install transformers accelerate")
            if self.gpu_available:
                print(f"  pip install bitsandbytes")

        print("="*60)


def configure_paddle_environment(use_gpu: bool = None):
    """Configure PaddlePaddle environment variables

    Args:
        use_gpu: Force GPU on/off, None for auto-detect
    """
    env = EnvironmentConfig()

    if use_gpu is None:
        use_gpu = env.gpu_available

    # PaddlePaddle specific
    if use_gpu:
        os.environ['FLAGS_use_cuda'] = '1'
    else:
        os.environ['FLAGS_use_cuda'] = '0'

    return env


def configure_llm_environment(use_gpu: bool = None):
    """Configure LLM (transformers) environment

    Args:
        use_gpu: Force GPU on/off, None for auto-detect
    """
    env = EnvironmentConfig()

    if use_gpu is None:
        use_gpu = env.gpu_available

    # Transformers settings
    if not use_gpu:
        os.environ['CUDA_VISIBLE_DEVICES'] = ''

    return env


def get_optimal_workers() -> int:
    """Get optimal number of workers for parallel processing"""
    env = EnvironmentConfig()

    if env.gpu_available:
        # GPU: Limit workers to avoid memory issues
        # Rule: 1 worker per 8GB VRAM
        if env.gpu_memory:
            return max(1, int(env.gpu_memory // 8))
        return 1
    else:
        # CPU: Use based on CPU cores
        # Rule: Reserve 1-2 cores for system
        return max(1, env.cpu_count - 2)


def auto_configure():
    """Automatically configure environment on import"""
    env = EnvironmentConfig()
    return env


# Auto-configure on module import
_env = auto_configure()


def get_environment() -> EnvironmentConfig:
    """Get current environment configuration"""
    return _env


if __name__ == "__main__":
    # Test and display environment
    env = EnvironmentConfig()
    env.print_status()

    print("\nOptimal parallel workers:", get_optimal_workers())
