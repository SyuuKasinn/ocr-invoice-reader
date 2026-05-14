"""
Setup configuration for OCR Invoice Reader
"""
from setuptools import setup, find_packages
import os

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
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Document information extraction system using PaddleOCR and PP-Structure",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ocr-invoice-reader",
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
        ],
    },
    entry_points={
        "console_scripts": [
            "ocr-extract=ocr_invoice_reader.cli.main:main",
            "ocr-simple=ocr_invoice_reader.cli.simple_cli:main",
            "ocr-raw=ocr_invoice_reader.cli.raw_structure:main",
            "ocr-enhanced=ocr_invoice_reader.cli.enhanced_extract:main",
            "ocr-api=ocr_invoice_reader.cli.api_server:main",
            "ocr-setup-ollama=ocr_invoice_reader.cli.setup_ollama:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
