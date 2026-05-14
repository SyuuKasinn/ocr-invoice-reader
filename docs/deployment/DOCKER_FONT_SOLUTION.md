# Docker 环境中文字体解决方案

## 📋 问题概述

第三方 Docker 容器可能没有安装中文字体，导致可视化结果中中文显示为方块（□）。

## ✅ 完整解决方案

### 方案 1: 使用项目提供的 Dockerfile（推荐）⭐

项目已经提供了预配置的 Dockerfile，自动安装开源中文字体：

```bash
# 直接构建并运行
docker-compose up --build
```

**优点**：
- ✅ 开箱即用，无需额外配置
- ✅ 使用开源字体（WenQuanYi），无版权问题
- ✅ 字体已集成到镜像中

**字体详情**：
- WenQuanYi Micro Hei（文泉驿微米黑）- GPL v2 授权
- WenQuanYi Zen Hei（文泉驿正黑）- GPL v2 授权

### 方案 2: 在现有 Docker 镜像中安装字体

如果使用第三方 Docker 镜像，可以在 Dockerfile 中添加：

```dockerfile
FROM your-base-image:latest

# 安装中文字体
RUN apt-get update && apt-get install -y \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fontconfig \
    && fc-cache -fv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 其他配置...
```

### 方案 3: 挂载字体目录

将宿主机的字体目录挂载到容器中：

```bash
docker run -it --rm \
  -v /usr/share/fonts:/usr/share/fonts:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  your-image:latest \
  ocr-enhanced --image /app/data/invoice.pdf --visualize --use-cpu
```

### 方案 4: 使用项目 fonts 目录

1. 下载开源中文字体到 `fonts/` 目录：

```bash
# 下载 WenQuanYi Micro Hei
cd fonts/
wget http://sourceforge.net/projects/wqy/files/wqy-microhei/0.2.0-beta/wqy-microhei-0.2.0-beta.tar.gz
tar -xzf wqy-microhei-0.2.0-beta.tar.gz
cp wqy-microhei/wqy-microhei.ttc WenQuanYiMicroHei.ttf
```

2. 挂载 fonts 目录到容器：

```bash
docker run -it --rm \
  -v $(pwd)/fonts:/app/fonts:ro \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  your-image:latest
```

应用程序会自动检测 `/app/fonts/` 目录中的字体。

### 方案 5: 运行时安装字体

在容器启动时安装字体：

```bash
docker run -it --rm your-image:latest bash -c "
  apt-get update && \
  apt-get install -y fonts-wqy-microhei && \
  fc-cache -fv && \
  ocr-enhanced --image /app/data/invoice.pdf --visualize --use-cpu
"
```

## 🔍 字体加载顺序

应用程序按以下顺序尝试加载字体：

1. **项目 fonts/ 目录**
   - `fonts/WenQuanYiMicroHei.ttf`
   - `fonts/msyh.ttc`

2. **Linux 系统字体**（Docker 常用）
   - `/usr/share/fonts/truetype/wqy/wqy-microhei.ttc`
   - `/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc`
   - `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`
   - `/usr/share/fonts/truetype/arphic/uming.ttc`

3. **Windows 系统字体**
   - `C:/Windows/Fonts/msyh.ttc`（微软雅黑）
   - `C:/Windows/Fonts/simhei.ttf`（黑体）
   - `C:/Windows/Fonts/simsun.ttc`（宋体）

4. **macOS 系统字体**
   - `/System/Library/Fonts/PingFang.ttc`
   - `/System/Library/Fonts/STHeiti Light.ttc`

5. **降级方案**
   - PIL 默认字体（中文显示为方块，但不影响 OCR 功能）

## 🧪 验证字体安装

### 方法 1: 检查系统字体

```bash
docker run -it --rm your-image:latest fc-list :lang=zh
```

应该看到类似输出：
```
/usr/share/fonts/truetype/wqy/wqy-microhei.ttc: WenQuanYi Micro Hei
```

### 方法 2: 测试应用程序字体加载

```bash
docker run -it --rm your-image:latest python -c "
from ocr_invoice_reader.utils.visualizer import OCRVisualizer
viz = OCRVisualizer()
print('✓ Font loaded successfully!')
"
```

成功输出：
```
  ✓ Loaded font: WenQuanYi Micro Hei
✓ Font loaded successfully!
```

### 方法 3: 运行完整测试

```bash
# 使用项目提供的测试脚本
bash test-docker.sh
```

## 📚 推荐字体

### 开源字体（可自由分发）

| 字体名称 | 许可证 | 文件名 | 下载地址 |
|---------|--------|--------|----------|
| WenQuanYi Micro Hei | GPL v2 + Font Exception | wqy-microhei.ttc | http://wenq.org/wqy2/index.cgi?MicroHei |
| WenQuanYi Zen Hei | GPL v2 + Font Exception | wqy-zenhei.ttc | http://wenq.org/wqy2/index.cgi?ZenHei |
| Noto Sans CJK | OFL 1.1 | NotoSansCJK-Regular.ttc | https://www.google.com/get/noto/#sans-hans |
| Source Han Sans | OFL 1.1 | SourceHanSans.ttc | https://github.com/adobe-fonts/source-han-sans |
| AR PL UMing | Arphic Public License | uming.ttc | http://www.freedesktop.org/wiki/Software/CJKUnifonts |

### 商业字体（需要许可证）

| 字体名称 | 许可证 | 备注 |
|---------|--------|------|
| Microsoft YaHei | 专有 | Windows 自带，需要 Windows 许可证 |
| SimHei | 专有 | Windows 自带 |
| SimSun | 专有 | Windows 自带 |

⚠️ **重要提示**：不要在 Docker 镜像中分发商业字体，除非你有相应的许可证。

## 🔧 故障排除

### 问题 1: 中文仍然显示为方块

**诊断**：
```bash
# 检查字体列表
docker exec <container-id> fc-list :lang=zh

# 查看应用程序日志
docker logs <container-id> | grep -i font
```

**解决方案**：
- 确保字体已正确安装
- 重新构建镜像：`docker-compose build --no-cache`
- 确认字体文件权限：`chmod 644 fonts/*.ttf`

### 问题 2: Docker 构建失败

**错误**: `apt-get: fonts-wqy-microhei: Package not found`

**解决方案**：
```dockerfile
# 更新包列表
RUN apt-get update && apt-get install -y \
    fonts-wqy-microhei || \
    echo "Font package not available, using alternative..."
```

### 问题 3: 字体加载但中文仍然乱码

**原因**: 字体文件损坏或编码问题

**解决方案**：
```bash
# 重新下载字体
rm -rf fonts/*.ttf
wget <font-download-url>

# 或使用系统包管理器
apt-get install --reinstall fonts-wqy-microhei
```

### 问题 4: 性能问题

**问题**: 字体加载缓慢

**解决方案**：
```dockerfile
# 在 Dockerfile 中预先缓存字体
RUN fc-cache -fv
```

## 🎯 最佳实践

1. **生产环境**：使用方案 1（预配置的 Dockerfile）
2. **开发环境**：使用方案 3（挂载系统字体）
3. **离线环境**：使用方案 4（fonts/ 目录）
4. **CI/CD**：在构建阶段安装字体（方案 2）

## 📖 相关文档

- [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - 完整 Docker 部署指南
- [fonts/README.md](fonts/README.md) - 字体安装和许可说明
- [README.md](README.md) - 项目主文档

## 🆘 获取帮助

如果遇到字体相关问题：

1. 查看应用程序日志中的字体加载信息
2. 使用 `fc-list :lang=zh` 验证字体安装
3. 参考 [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) 故障排除部分
4. 在 GitHub 上提交 Issue: https://github.com/SyuuKasinn/ocr-invoice-reader/issues
