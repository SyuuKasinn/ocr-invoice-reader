# Fonts Directory

This directory is for optional custom fonts to support Chinese character rendering in Docker environments.

## 📝 Recommended Fonts

### For Docker/Linux

**WenQuanYi Micro Hei** (文泉驿微米黑)
- **License**: GPL v2 with Font Exception (Free to use and redistribute)
- **Download**: http://wenq.org/wqy2/index.cgi?MicroHei
- **File**: `WenQuanYiMicroHei.ttf`
- **Installation**:
  ```bash
  # Debian/Ubuntu
  apt-get install fonts-wqy-microhei
  
  # Or download and place here
  wget http://sourceforge.net/projects/wqy/files/wqy-microhei/0.2.0-beta/wqy-microhei-0.2.0-beta.tar.gz
  ```

### For Windows

**Microsoft YaHei** (微软雅黑)
- **License**: Proprietary (included with Windows)
- **File**: `msyh.ttc` from `C:\Windows\Fonts\msyh.ttc`
- **Note**: Only use if you have a valid Windows license

**SimHei** (黑体)
- **License**: Proprietary
- **File**: `simhei.ttf` from `C:\Windows\Fonts\simhei.ttf`

## 🚀 Usage

### Option 1: System Installation (Recommended for Docker)

The Dockerfile automatically installs WenQuanYi fonts:
```dockerfile
RUN apt-get install fonts-wqy-microhei fonts-wqy-zenhei
```

### Option 2: Manual Placement

Place font files directly in this directory:
```
fonts/
├── WenQuanYiMicroHei.ttf    # Recommended
├── msyh.ttc                  # Optional
└── README.md
```

The application will automatically detect and use fonts from this directory.

### Option 3: Volume Mount

Mount your system fonts into the Docker container:
```bash
docker run -v /usr/share/fonts:/usr/share/fonts:ro ...
```

## ⚖️ License Compliance

**Important**: Ensure you have proper licenses for any fonts you use:

- ✅ **Open Source Fonts** (WenQuanYi, Noto Sans CJK, etc.): Free to redistribute
- ⚠️ **Proprietary Fonts** (Microsoft YaHei, SimHei, etc.): Require valid licenses
  - Do NOT distribute proprietary fonts with the application
  - Users must provide their own licensed fonts

## 🔍 Font Detection Order

The application tries fonts in this order:

1. **Bundled fonts** in this directory
2. **System fonts** (Windows/macOS/Linux)
3. **Fallback** to PIL default font (limited Chinese support)

## 📚 Additional Open Source Fonts

Alternative fonts with good Chinese support:

| Font | License | Download |
|------|---------|----------|
| Noto Sans CJK | OFL 1.1 | https://www.google.com/get/noto/#sans-hans |
| Source Han Sans | OFL 1.1 | https://github.com/adobe-fonts/source-han-sans |
| WenQuanYi Zen Hei | GPL v2 | http://wenq.org/wqy2/index.cgi?ZenHei |
| AR PL UMing | Arphic Public License | http://www.freedesktop.org/wiki/Software/CJKUnifonts |

## 🆘 Troubleshooting

### Font not loading?

1. Check file permissions:
   ```bash
   chmod 644 fonts/*.ttf fonts/*.ttc
   ```

2. Verify font format:
   ```bash
   file fonts/*.ttf
   ```

3. Test font loading:
   ```python
   from PIL import ImageFont
   font = ImageFont.truetype('fonts/WenQuanYiMicroHei.ttf', 20)
   ```

### Still seeing squares?

- Ensure the font file supports Chinese characters
- Try a different font from the list above
- Check application logs for font loading messages
