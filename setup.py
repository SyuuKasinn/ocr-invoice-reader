"""Setup configuration for OCR Invoice Reader (PaddleOCR-VL 1.5)."""
import re
from pathlib import Path

from setuptools import find_packages, setup


def read_version() -> str:
    text = Path("ocr_invoice_reader/__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE)
    if not match:
        raise RuntimeError("Could not parse __version__ from ocr_invoice_reader/__init__.py")
    return match.group(1)


__version__ = read_version()


def read_long_description() -> str:
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return "Document parsing with PaddleOCR-VL 1.5."


def read_requirements() -> list[str]:
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            return [
                line.strip()
                for line in f
                if line.strip() and not line.startswith("#")
            ]
    except OSError:
        return []


setup(
    name="ocr-invoice-reader",
    version=__version__,
    description="Document parsing system built on PaddleOCR-VL 1.5",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/SyuuKasinn/ocr-invoice-reader",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ocr-extract=ocr_invoice_reader.cli.extract:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
    ],
    include_package_data=True,
    zip_safe=False,
)
