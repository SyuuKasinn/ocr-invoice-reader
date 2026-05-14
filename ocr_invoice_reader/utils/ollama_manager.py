"""
Ollama automatic installation and management module
"""
import os
import sys
import subprocess
import platform
import tempfile
import time
import requests
from pathlib import Path
from typing import Optional, Tuple, List


class OllamaManager:
    """Ollama service manager - automatic installation, startup and configuration"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.system = platform.system()

    def check_service(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(self.base_url, timeout=2)
            return response.status_code == 200
        except (requests.RequestException, requests.Timeout):
            # Service not available
            return False
        except Exception as e:
            # Unexpected error
            print(f"Unexpected error checking service: {e}")
            return False

    def _find_ollama_executable(self) -> Optional[str]:
        """Find ollama executable path on the system"""
        # Try common paths
        if self.system == "Windows":
            # Windows common installation paths
            possible_paths = [
                r"C:\Users\{}\AppData\Local\Programs\Ollama\ollama.exe".format(os.environ.get('USERNAME', '')),
                r"C:\Program Files\Ollama\ollama.exe",
                r"C:\Program Files (x86)\Ollama\ollama.exe",
                "ollama.exe",  # Try in PATH
                "ollama"  # Try without extension
            ]
        else:
            # Linux/macOS paths
            possible_paths = [
                "/usr/local/bin/ollama",
                "/usr/bin/ollama",
                "ollama"  # Try in PATH
            ]

        # Test each path
        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, '--version'],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return path
            except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
                continue

        return None

    def is_installed(self) -> bool:
        """Check if Ollama is installed"""
        return self._find_ollama_executable() is not None

    def get_install_url(self) -> Optional[str]:
        """Get Ollama installation URL for current system"""
        if self.system == "Windows":
            return "https://ollama.ai/download/OllamaSetup.exe"
        elif self.system == "Darwin":  # macOS
            return "https://ollama.ai/download/Ollama-darwin.zip"
        elif self.system == "Linux":
            return None  # Linux uses script installation
        return None

    def auto_install(self, auto_confirm: bool = False) -> bool:
        """
        Automatically install Ollama

        Args:
            auto_confirm: Whether to auto-confirm installation (no user prompt)

        Returns:
            Whether installation succeeded
        """
        if self.is_installed():
            print("Ollama is already installed")
            return True

        print("=" * 60)
        print("Ollama is not installed")
        print("=" * 60)

        if not auto_confirm:
            response = input("Do you want to install Ollama automatically? (y/n): ").strip().lower()
            if response != 'y':
                print("Installation cancelled")
                print(f"Please install manually: https://ollama.ai/download")
                return False

        print("\nStarting Ollama installation...")

        try:
            if self.system == "Windows":
                return self._install_windows()
            elif self.system == "Darwin":
                return self._install_macos()
            elif self.system == "Linux":
                return self._install_linux()
            else:
                print(f"Unsupported system: {self.system}")
                return False
        except Exception as e:
            print(f"Installation failed: {e}")
            return False

    def _install_windows(self) -> bool:
        """Windows automatic installation"""
        print("Downloading Ollama installer...")

        url = self.get_install_url()
        temp_dir = tempfile.gettempdir()
        installer_path = os.path.join(temp_dir, "OllamaSetup.exe")

        try:
            # Download installer
            response = requests.get(url, stream=True, timeout=300)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rDownload progress: {percent:.1f}%", end='', flush=True)

            print("\nDownload complete!")
            print("Running installer with silent mode...")

            # Run installer with silent installation flag
            process = subprocess.run(
                [installer_path, '/SILENT'],
                timeout=300
            )

            if process.returncode == 0:
                print("Installation completed!")

                # Wait a bit for Ollama to initialize
                print("Waiting for Ollama to initialize...")
                time.sleep(5)

                # Check if installed successfully
                if self.is_installed():
                    print("✓ Ollama installed successfully")
                    return True
                else:
                    print("✗ Installation may have failed, please verify")
                    return False
            else:
                print("Installation may have failed")
                print("Please try manual installation from: https://ollama.ai/download")
                return False

        except subprocess.TimeoutExpired:
            print("\nInstallation timeout")
            print("The installer may still be running in the background")
            print("Please wait for it to complete, then re-run this command")
            return False
        except Exception as e:
            print(f"\nInstallation failed: {e}")
            print(f"Please download and install manually: {url}")
            return False

    def _install_macos(self) -> bool:
        """macOS automatic installation"""
        print("For macOS, we recommend using Homebrew:")
        print("  brew install ollama")
        print("\nOr download manually: https://ollama.ai/download")
        return False

    def _install_linux(self) -> bool:
        """Linux automatic installation"""
        print("Installing Ollama using official script...")

        try:
            # Use official installation script
            result = subprocess.run(
                ['curl', '-fsSL', 'https://ollama.ai/install.sh'],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                install_script = result.stdout

                # Execute installation script
                process = subprocess.Popen(
                    ['sh'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                stdout, stderr = process.communicate(input=install_script, timeout=300)

                if process.returncode == 0:
                    print("Installation successful!")
                    return True
                else:
                    print(f"Installation failed: {stderr}")
                    return False
            else:
                print("Failed to download installation script")
                return False

        except Exception as e:
            print(f"Installation failed: {e}")
            print("Please run manually: curl -fsSL https://ollama.ai/install.sh | sh")
            return False

    def start_service(self) -> bool:
        """Start Ollama service"""
        if self.check_service():
            print("Ollama service is already running")
            return True

        if not self.is_installed():
            print("Ollama is not installed, cannot start")
            return False

        print("Starting Ollama service...")

        try:
            ollama_cmd = self._find_ollama_executable()
            if not ollama_cmd:
                print("Cannot find ollama executable")
                return False

            if self.system == "Windows":
                # Windows: Start Ollama service in background
                subprocess.Popen(
                    [ollama_cmd, 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
                )
            else:
                # Linux/Mac: start in background
                subprocess.Popen(
                    [ollama_cmd, 'serve'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            # Wait for service to start
            for i in range(10):
                time.sleep(1)
                if self.check_service():
                    print("Ollama service started successfully!")
                    return True
                print(f"Waiting for service to start... ({i+1}/10)")

            print("Service startup timeout")
            return False

        except Exception as e:
            print(f"Startup failed: {e}")
            return False

    def check_model(self, model: str) -> bool:
        """Check if model is downloaded"""
        try:
            ollama_cmd = self._find_ollama_executable()
            if not ollama_cmd:
                return False

            result = subprocess.run(
                [ollama_cmd, 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return model in result.stdout
            return False
        except (subprocess.SubprocessError, subprocess.TimeoutExpired, FileNotFoundError):
            # Ollama not available or command failed
            return False
        except Exception as e:
            print(f"Unexpected error checking model: {e}")
            return False

    def pull_model(self, model: str, auto_confirm: bool = False) -> bool:
        """
        Download model

        Args:
            model: Model name (e.g. qwen2.5:0.5b)
            auto_confirm: Whether to auto-confirm download

        Returns:
            Whether download succeeded
        """
        if self.check_model(model):
            print(f"Model {model} already exists")
            return True

        print("=" * 60)
        print(f"Model {model} is not downloaded")
        print("=" * 60)

        # Show model size information
        model_sizes = {
            'qwen2.5:0.5b': '300MB',
            'qwen2.5:1.5b': '1GB',
            'gemma2:2b': '1.5GB',
            'phi3:mini': '2GB'
        }
        size = model_sizes.get(model, 'unknown size')
        print(f"Model size: {size}")

        if not auto_confirm:
            response = input(f"Do you want to download model {model}? (y/n): ").strip().lower()
            if response != 'y':
                print("Download cancelled")
                return False

        print(f"\nStarting download of model {model}...")
        print("This may take a few minutes, please wait...")

        try:
            # Find ollama executable path
            ollama_cmd = self._find_ollama_executable()
            if not ollama_cmd:
                print("\nError: Cannot find ollama executable")
                print("Please make sure Ollama is installed and in PATH")
                print("Or try installing: https://ollama.ai/download")
                return False

            # Use subprocess to show download progress in real-time
            process = subprocess.Popen(
                [ollama_cmd, 'pull', model],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in process.stdout:
                print(line, end='', flush=True)

            process.wait()

            if process.returncode == 0:
                print(f"\nModel {model} downloaded successfully!")
                return True
            else:
                print(f"\nModel download failed")
                return False

        except FileNotFoundError:
            print("\nError: Ollama command not found")
            print("Please install Ollama from: https://ollama.ai/download")
            return False
        except Exception as e:
            print(f"\nDownload failed: {e}")
            return False

    def setup(self, model: str = "qwen2.5:0.5b", auto_confirm: bool = False) -> Tuple[bool, str]:
        """
        Complete Ollama setup process

        Args:
            model: Model to use
            auto_confirm: Whether to auto-confirm all operations

        Returns:
            (success, status message)
        """
        print("\n" + "=" * 60)
        print("Ollama Automatic Setup")
        print("=" * 60)

        # 1. Check service
        print("\n[1/4] Checking Ollama service...")
        if self.check_service():
            print("✓ Ollama service is running")
        else:
            print("✗ Ollama service is not running")

            # 2. Check if installed
            print("\n[2/4] Checking Ollama installation...")
            if not self.is_installed():
                print("✗ Ollama is not installed")
                if not self.auto_install(auto_confirm):
                    return False, "Ollama installation failed or cancelled"
                print("✓ Ollama installation complete")
            else:
                print("✓ Ollama is installed")

            # 3. Start service
            print("\n[3/4] Starting Ollama service...")
            if not self.start_service():
                return False, "Failed to start Ollama service"
            print("✓ Ollama service is running")

        # 4. Check and download model
        print(f"\n[4/4] Checking model {model}...")
        if not self.check_model(model):
            print(f"✗ Model {model} is not downloaded")
            if not self.pull_model(model, auto_confirm):
                return False, f"Failed to download model {model} or cancelled"
            print(f"✓ Model {model} is ready")
        else:
            print(f"✓ Model {model} already exists")

        print("\n" + "=" * 60)
        print("✓ Ollama setup complete!")
        print("=" * 60)

        return True, "Setup successful"

    def get_status(self) -> dict:
        """Get Ollama status information"""
        status = {
            'installed': self.is_installed(),
            'service_running': self.check_service(),
            'models': []
        }

        if status['installed']:
            try:
                ollama_cmd = self._find_ollama_executable()
                if ollama_cmd:
                    result = subprocess.run(
                        [ollama_cmd, 'list'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')[1:]  # Skip header
                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if len(parts) >= 1:
                                    status['models'].append(parts[0])
            except (subprocess.SubprocessError, subprocess.TimeoutExpired, IndexError):
                # Failed to get model list, return empty models list
                pass
            except Exception as e:
                print(f"Unexpected error getting model list: {e}")
                pass

        return status


def create_ollama_manager(base_url: str = "http://localhost:11434") -> OllamaManager:
    """Create OllamaManager instance"""
    return OllamaManager(base_url)


if __name__ == "__main__":
    # Command line test
    manager = OllamaManager()

    print("Ollama Status:")
    status = manager.get_status()
    print(f"  Installed: {status['installed']}")
    print(f"  Service running: {status['service_running']}")
    print(f"  Downloaded models: {status['models']}")

    if len(sys.argv) > 1:
        if sys.argv[1] == "setup":
            model = sys.argv[2] if len(sys.argv) > 2 else "qwen2.5:0.5b"
            success, message = manager.setup(model, auto_confirm=False)
            print(f"\n{message}")
            sys.exit(0 if success else 1)
