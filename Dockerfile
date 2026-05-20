FROM python:3.10-slim

WORKDIR /app

# System libraries required by PaddleOCR / OpenCV / PaddlePaddle at runtime.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Image targets CPU by default — paddlepaddle (CPU build) is installed
# explicitly because pyproject.toml no longer pins it (install.sh chooses
# CPU vs GPU at install time, but Docker builds don't see GPUs).
# For GPU, build from an nvidia/cuda base image and re-run install.sh.
COPY requirements.txt .
RUN pip install --no-cache-dir "paddlepaddle>=3.2.0" \
    && pip install --no-cache-dir -r requirements.txt

# Copy the package and install in editable mode (entry point: ocr-extract).
COPY . .
RUN pip install --no-cache-dir --no-build-isolation -e .

ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN mkdir -p /app/data /app/results
VOLUME ["/app/data", "/app/results"]

# Device auto-detection picks GPU when paddlepaddle-gpu is installed,
# otherwise CPU. Override with --cpu for debugging.
CMD ["ocr-extract", "--help"]
