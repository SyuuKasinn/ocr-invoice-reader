# OCR Invoice Reader Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies and Chinese fonts
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    wget \
    fontconfig \
    # Install Chinese fonts
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Alternative: Download Microsoft YaHei font (optional, for better quality)
# Note: Ensure you have proper license for font usage
RUN mkdir -p /usr/share/fonts/truetype/msyh && \
    wget -q https://github.com/SyuuKasinn/ocr-invoice-reader/releases/download/fonts/msyh.ttc \
    -O /usr/share/fonts/truetype/msyh/msyh.ttc 2>/dev/null || \
    echo "Using system fonts instead"

# Refresh font cache
RUN fc-cache -fv

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package
RUN pip install -e .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Create output directory
RUN mkdir -p /app/results

# Expose volume for input/output
VOLUME ["/app/data", "/app/results"]

# Default command
CMD ["bash"]
