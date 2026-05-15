"""
Setup configuration for OCR Invoice Reader - IMPROVED
"""
from setuptools import setup, find_packages
import os
import sys

# Add package to path to import version
sys.path.insert(0, os.path.abspath('.'))
from ocr_invoice_reader import __version__

# Read long description from README
def read_long_description():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "OCR-based document information extraction system"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except:
        return []

setup(
    name="ocr-invoice-reader",
    version=__version__,  # Now properly imported
    author="Your Name",
    author_email="your.email@example.com",
    description="Document information extraction system using PaddleOCR and PP-Structure",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/SyuuKasinn/ocr-invoice-reader",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
        "llm": [
            "anthropic>=0.18.0",
            "openai>=1.0.0",
        ],
        "api": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "python-multipart>=0.0.6",
            "psutil>=5.9.0",  # For health check
        ],
    },
    entry_points={
        "console_scripts": [
            "ocr-extract=ocr_invoice_reader.cli.main:main",
            "ocr-simple=ocr_invoice_reader.cli.simple_cli:main",
            "ocr-raw=ocr_invoice_reader.cli.raw_structure:main",
            "ocr-enhanced=ocr_invoice_reader.cli.enhanced_extract:main",
            "ocr-enhanced-parallel=ocr_invoice_reader.cli.enhanced_extract_parallel:main",
            "ocr-api=ocr_invoice_reader.cli.api_server:main",
            "ocr-setup-ollama=ocr_invoice_reader.cli.setup_ollama:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
