# Docker Deployment Guide

This guide explains how to deploy OCR Invoice Reader in Docker containers with proper Chinese font support.

## 🐳 Quick Start

### Method 1: Using Docker Compose (Recommended)

```bash
# Build and run
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Method 2: Using Docker CLI

```bash
# Build image
docker build -t ocr-invoice-reader:latest .

# Run container
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  ocr-invoice-reader:latest \
  ocr-enhanced --image /app/data/invoice.pdf --visualize --use-cpu
```

## 📝 Chinese Font Support

The application uses a multi-tier font loading strategy:

### Tier 1: System Fonts (Installed in Docker)

The Dockerfile automatically installs open-source Chinese fonts:
- **WenQuanYi Micro Hei** (`fonts-wqy-microhei`)
- **WenQuanYi Zen Hei** (`fonts-wqy-zenhei`)

These fonts provide good Chinese character coverage and are freely redistributable.

### Tier 2: Bundled Fonts (Optional)

You can place custom font files in the `fonts/` directory:

```bash
fonts/
├── WenQuanYiMicroHei.ttf   # Recommended for Docker
└── msyh.ttc                 # Microsoft YaHei (if licensed)
```

**Note**: Ensure you have proper licenses for any proprietary fonts.

### Tier 3: Fallback

If no suitable fonts are found, the application will:
1. Display a warning message
2. Use PIL's default font (text may appear as squares)
3. Continue processing normally

## 🔧 Font Installation Options

### Option A: Build-time Installation (Recommended)

Fonts are installed during Docker image build (already configured in Dockerfile):

```dockerfile
RUN apt-get update && apt-get install -y \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    && apt-get clean
```

### Option B: Volume-mounted Fonts

Mount your local fonts directory:

```bash
docker run -it --rm \
  -v $(pwd)/fonts:/usr/share/fonts/custom:ro \
  ocr-invoice-reader:latest
```

### Option C: Download at Build Time

Uncomment the font download section in `Dockerfile`:

```dockerfile
RUN wget -q https://github.com/.../msyh.ttc \
    -O /usr/share/fonts/truetype/msyh/msyh.ttc
```

## 🚀 Usage Examples

### Process Single PDF

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  ocr-invoice-reader:latest \
  ocr-enhanced \
    --image /app/data/invoice.pdf \
    --output-dir /app/results \
    --visualize \
    --use-cpu \
    --lang ch
```

### Batch Processing

```bash
docker run -it --rm \
  -v $(pwd)/invoices:/app/data \
  -v $(pwd)/results:/app/results \
  ocr-invoice-reader:latest \
  bash -c "for f in /app/data/*.pdf; do \
    ocr-enhanced --image \$f --output-dir /app/results --visualize --use-cpu; \
  done"
```

### Interactive Shell

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  ocr-invoice-reader:latest \
  bash
```

Then run commands inside the container:
```bash
ocr-enhanced --image /app/data/invoice.pdf --visualize --use-cpu
```

## 🖥️ GPU Support

For GPU acceleration, use the NVIDIA Docker runtime:

```bash
docker run -it --rm --gpus all \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  ocr-invoice-reader:latest \
  ocr-enhanced --image /app/data/invoice.pdf --visualize
```

Or with Docker Compose, uncomment the GPU section in `docker-compose.yml`.

## 🔍 Verification

### Check Font Installation

```bash
docker run -it --rm ocr-invoice-reader:latest fc-list :lang=zh
```

Expected output:
```
/usr/share/fonts/truetype/wqy/wqy-microhei.ttc: WenQuanYi Micro Hei
/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc: WenQuanYi Zen Hei
```

### Test Font Rendering

```bash
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  ocr-invoice-reader:latest \
  python -c "
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 20)
img = Image.new('RGB', (200, 50), 'white')
draw = ImageDraw.Draw(img)
draw.text((10, 10), '中文测试', fill='black', font=font)
img.save('/app/results/font_test.png')
print('Font test saved to results/font_test.png')
"
```

## 📦 Available Commands

All CLI commands are available in the Docker container:

| Command | Description |
|---------|-------------|
| `ocr-enhanced` | Enhanced extraction (recommended) |
| `ocr-raw` | PP-Structure raw output |
| `ocr-extract` | Structured field extraction |
| `ocr-simple` | Simple text extraction |

## 🐛 Troubleshooting

### Issue: Chinese characters show as squares

**Solution 1**: Verify fonts are installed
```bash
docker exec <container-id> fc-list :lang=zh
```

**Solution 2**: Rebuild image with fonts
```bash
docker-compose build --no-cache
```

**Solution 3**: Mount font directory
```bash
docker run -v /usr/share/fonts:/usr/share/fonts:ro ...
```

### Issue: Permission denied writing results

**Solution**: Fix volume permissions
```bash
chmod -R 777 results/
```

Or run with user permissions:
```bash
docker run --user $(id -u):$(id -g) ...
```

### Issue: Out of memory

**Solution**: Increase Docker memory limit
```bash
docker run --memory=4g --memory-swap=8g ...
```

## 📚 Additional Resources

- **Main README**: [README.md](README.md)
- **Deployment Instructions**: [DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)
- **Font Licenses**:
  - WenQuanYi: GPL v2 with Font Exception
  - See [fonts/LICENSE](fonts/LICENSE) for details

## 🆘 Support

If you encounter font-related issues:

1. Check the application logs for font loading messages
2. Verify font installation: `docker exec <container> fc-list`
3. Open an issue: https://github.com/SyuuKasinn/ocr-invoice-reader/issues
