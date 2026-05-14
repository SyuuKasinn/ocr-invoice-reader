# 自动安装集成指南

## 🎯 概述

现在Ollama已经集成到项目中，支持**自动安装和配置**！

## 🚀 三种使用方式

### 方式1：完全自动（推荐）

**一条命令完成所有设置**：

```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm --auto-setup-ollama
```

**特点**：
- ✅ 自动检测Ollama是否安装
- ✅ 如未安装，自动下载并安装
- ✅ 自动启动Ollama服务
- ✅ 自动下载模型
- ✅ **无需任何手动操作**

**首次运行流程**：
```
1. 检测到Ollama未安装
2. 自动下载安装程序（~200MB）
3. 启动安装向导（点击"下一步"完成安装）
4. 自动启动Ollama服务
5. 自动下载模型（qwen2.5:0.5b，~300MB）
6. 开始OCR + LLM处理
```

---

### 方式2：交互式设置

```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm
```

**首次运行时会提示**：
```
✗ LLM not available

Ollama服务未运行或未安装
选项:
  1. 自动设置Ollama（推荐）
  2. 查看手动设置说明
  3. 跳过LLM功能，继续OCR

请选择 (1/2/3):
```

选择 `1` 即可自动设置。

---

### 方式3：独立设置命令

**先设置，再使用**：

```bash
# 第一步：设置Ollama
ocr-setup-ollama

# 第二步：使用LLM功能
ocr-enhanced --image invoice.pdf --lang ch --use-llm
```

---

## 📋 详细命令说明

### 1. `ocr-setup-ollama` - 独立设置工具

#### 基本用法

```bash
# 交互式设置（推荐）
ocr-setup-ollama

# 完全自动（无提示）
ocr-setup-ollama --auto

# 使用特定模型
ocr-setup-ollama --model gemma2:2b

# 只检查状态
ocr-setup-ollama --status
```

#### 检查状态

```bash
ocr-setup-ollama --status
```

**输出示例**：
```
============================================================
Ollama状态
============================================================

安装状态: ✓ 已安装
服务运行: ✓ 运行中

已下载模型:
  - qwen2.5:0.5b
  - gemma2:2b

============================================================
✓ Ollama已就绪
```

### 2. `ocr-enhanced` - 主命令（带自动设置）

#### 完全自动模式

```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm --auto-setup-ollama
```

- ✅ 遇到问题自动解决
- ✅ 不会中断处理流程
- ✅ 适合批处理和脚本

#### 交互模式（默认）

```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm
```

- ✅ 遇到问题时询问用户
- ✅ 可选择手动或自动设置
- ✅ 适合首次使用

---

## 🔧 安装流程详解

### 自动安装做什么？

#### Windows

1. **检测安装状态**
   ```
   [1/4] 检查Ollama服务...
   ✗ Ollama服务未运行
   
   [2/4] 检查Ollama安装...
   ✗ Ollama未安装
   ```

2. **下载安装程序**
   ```
   正在下载Ollama安装程序...
   下载进度: 45.2%
   下载完成！
   ```

3. **运行安装向导**
   ```
   正在运行安装程序...
   请按照安装向导完成安装
   
   安装程序已启动
   安装完成后，Ollama会自动启动
   ```

4. **启动服务**
   ```
   [3/4] 启动Ollama服务...
   等待服务启动... (1/10)
   等待服务启动... (2/10)
   Ollama服务启动成功！
   ```

5. **下载模型**
   ```
   [4/4] 检查模型 qwen2.5:0.5b...
   ✗ 模型 qwen2.5:0.5b 未下载
   
   模型大小: 300MB
   开始下载模型 qwen2.5:0.5b...
   pulling manifest
   pulling 8a2a7e3... 100%
   verifying sha256 digest
   writing manifest
   success
   
   模型 qwen2.5:0.5b 下载成功！
   ```

6. **完成**
   ```
   ============================================================
   ✓ Ollama设置完成！
   ============================================================
   ```

#### Linux

```bash
# 使用官方脚本自动安装
正在使用官方脚本安装Ollama...
>>> Installing ollama to /usr/local/bin...
>>> Creating ollama user...
>>> Starting ollama service...
安装成功！
```

#### macOS

```
macOS建议使用Homebrew安装:
  brew install ollama

或手动下载: https://ollama.ai/download
```

---

## 💡 使用场景

### 场景1：首次使用

```bash
# 一键完成所有设置
ocr-enhanced --image invoice.pdf --lang ch --use-llm --auto-setup-ollama
```

**结果**：
- Ollama自动安装
- 模型自动下载
- OCR + LLM完整处理
- 生成所有文件（包括LLM CSV）

---

### 场景2：批处理脚本

```python
import subprocess
import glob

# 批量处理所有PDF
for pdf_file in glob.glob('invoices/*.pdf'):
    cmd = [
        'ocr-enhanced',
        '--image', pdf_file,
        '--lang', 'ch',
        '--use-llm',
        '--auto-setup-ollama',  # 首次运行会自动设置
        '--output-dir', 'results'
    ]
    
    subprocess.run(cmd)
```

**优点**：
- 首次运行自动设置Ollama
- 后续运行直接使用
- 无需手动干预

---

### 场景3：CI/CD集成

```yaml
# .github/workflows/process-invoices.yml
name: Process Invoices

on: [push]

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Process invoices
        run: |
          ocr-enhanced \
            --image invoices/sample.pdf \
            --lang ch \
            --use-llm \
            --auto-setup-ollama
```

---

## 🔍 故障排除

### 问题1：下载失败

**症状**：
```
下载失败: Connection timeout
```

**解决**：
1. 检查网络连接
2. 重试命令
3. 手动下载：https://ollama.ai/download

---

### 问题2：安装失败

**症状**：
```
安装失败: Permission denied
```

**解决**（Windows）：
1. 以管理员身份运行命令行
2. 重新运行安装命令

**解决**（Linux）：
```bash
sudo ocr-setup-ollama
```

---

### 问题3：服务启动失败

**症状**：
```
服务启动超时
```

**解决**：
```bash
# 手动启动Ollama
ollama serve

# 另一个终端窗口运行OCR
ocr-enhanced --image invoice.pdf --use-llm
```

---

### 问题4：模型下载中断

**症状**：
```
模型下载失败
```

**解决**：
```bash
# 单独下载模型
ollama pull qwen2.5:0.5b

# 验证
ollama list
```

---

## 📊 完整工作流程

### 新用户首次使用

```bash
# 1. 安装项目
pip install -e .

# 2. 运行OCR（自动设置Ollama）
ocr-enhanced --image invoice.pdf --lang ch --use-llm --auto-setup-ollama

# 首次运行输出：
# ============================================================
# Enhanced Document Extraction
# ============================================================
# 
# Processing PDF: invoice.pdf
#   Pages: 5
# 
# Initializing LLM processor...
# ✗ LLM not available
# 
# 自动设置模式（--auto-setup-ollama）
# 
# ============================================================
# Ollama自动设置
# ============================================================
# 
# [1/4] 检查Ollama服务...
# ✗ Ollama服务未运行
# 
# [2/4] 检查Ollama安装...
# ✗ Ollama未安装
# 
# 正在下载Ollama安装程序...
# 下载进度: 100.0%
# 下载完成！
# 正在运行安装程序...
# （安装向导窗口打开，按提示完成安装）
# 
# [3/4] 启动Ollama服务...
# Ollama服务启动成功！
# 
# [4/4] 检查模型 qwen2.5:0.5b...
# ✗ 模型 qwen2.5:0.5b 未下载
# 开始下载模型...
# 模型下载成功！
# 
# ============================================================
# ✓ Ollama设置完成！
# ============================================================
# 
# ✓ LLM设置成功
# 
# Processing page 1/5...
#   ✓ LLM classified as: invoice (confidence: high)
#   ✓ LLM extracted 8 fields
# ...
# 
# Individual page files:
#   Page 1 LLM TXT: invoice_page_0001_llm.txt    ⭐
#   Page 1 LLM CSV: invoice_page_0001_llm.csv    ⭐
# 
# Combined files:
#   LLM Analysis: invoice_llm_analysis.txt        ⭐
#   LLM CSV: invoice_llm.csv                      ⭐
```

### 后续使用

```bash
# 不需要 --auto-setup-ollama，直接使用
ocr-enhanced --image invoice2.pdf --lang ch --use-llm
```

---

## 🎨 推荐配置

### 快速处理（CPU）

```bash
ocr-enhanced \
  --image invoice.pdf \
  --lang ch \
  --use-cpu \
  --use-llm \
  --llm-model qwen2.5:0.5b \
  --auto-setup-ollama
```

- 模型：300MB
- 速度：~3秒/页
- 内存：~1.5GB

### 高质量处理

```bash
ocr-enhanced \
  --image invoice.pdf \
  --lang ch \
  --use-llm \
  --llm-model gemma2:2b \
  --auto-setup-ollama
```

- 模型：1.5GB
- 速度：~5秒/页（CPU）
- 内存：~3GB

---

## 📚 相关文档

- **[OLLAMA_SETUP_QUICK.md](OLLAMA_SETUP_QUICK.md)** - Ollama快速启动
- **[LLM_INTEGRATION_GUIDE.md](LLM_INTEGRATION_GUIDE.md)** - LLM完整指南
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 快速参考

---

## ✅ 总结

### 自动集成优势

✅ **零配置**：无需手动安装Ollama  
✅ **自动化**：一条命令完成所有设置  
✅ **智能检测**：自动判断需要哪些步骤  
✅ **容错处理**：失败时提供清晰指引  
✅ **跨平台**：支持Windows、Linux、macOS

### 推荐使用方式

**首次使用**：
```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm --auto-setup-ollama
```

**日常使用**：
```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm
```

**检查状态**：
```bash
ocr-setup-ollama --status
```

---

**版本**: v2.3.0  
**最后更新**: 2026-05-14  
**状态**: ✅ 完全自动化集成
