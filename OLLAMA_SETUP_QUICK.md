# Ollama 快速启动指南

## ⚠️ 问题：没有生成LLM文件

如果运行 `ocr-enhanced --use-llm` 后看到：

```
WARNING: Ollama service not available
✗ LLM not available, continuing without post-processing
```

**原因**：Ollama服务没有运行

---

## 🚀 快速解决方案

### Windows用户

#### 1️⃣ 检查Ollama是否已安装

打开PowerShell或CMD，运行：
```powershell
ollama list
```

**如果显示命令未找到**，说明没有安装，跳到步骤2。

**如果显示模型列表**（可能为空），说明已安装，跳到步骤3。

#### 2️⃣ 安装Ollama（如果未安装）

1. 访问：https://ollama.ai/download
2. 下载Windows版本
3. 安装（双击安装程序，一路下一步）
4. 安装完成后，Ollama会自动启动

#### 3️⃣ 启动Ollama服务

**方法1：自动启动**（推荐）
- Ollama安装后会作为Windows服务自动运行
- 检查系统托盘（右下角），应该能看到Ollama图标

**方法2：手动启动**
```powershell
# 打开新的PowerShell窗口
ollama serve
```

**方法3：通过开始菜单**
- 开始菜单 → 搜索 "Ollama"
- 点击启动

#### 4️⃣ 下载模型

第一次使用需要下载模型：

```powershell
# 推荐：小而快的模型（300MB，CPU友好）
ollama pull qwen2.5:0.5b

# 或者：质量更高的模型（1.5GB）
ollama pull gemma2:2b
```

#### 5️⃣ 验证服务运行

```powershell
# 测试Ollama是否运行
curl http://localhost:11434

# 应该返回：Ollama is running
```

或者在浏览器中打开：http://localhost:11434

#### 6️⃣ 重新运行OCR

```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm
```

现在应该能看到：
```
Initializing LLM processor...
✓ Using LLM model: qwen2.5:0.5b
```

---

## 🔍 故障排除

### 问题1：端口被占用

**症状**：
```
Error: listen tcp 127.0.0.1:11434: bind: address already in use
```

**解决**：
```powershell
# 查看占用11434端口的进程
netstat -ano | findstr :11434

# 关闭进程（替换<PID>为实际进程ID）
taskkill /PID <PID> /F

# 重新启动Ollama
ollama serve
```

### 问题2：模型下载失败

**症状**：下载中断或超时

**解决**：
```powershell
# 重新下载
ollama pull qwen2.5:0.5b

# 如果网络不稳定，使用更小的模型
ollama pull qwen2.5:0.5b
```

### 问题3：服务启动失败

**症状**：
```
Error: could not connect to ollama app
```

**解决**：
1. 重启电脑
2. 重新安装Ollama
3. 检查防火墙设置

---

## 📋 完整验证清单

运行以下命令，确保每一步都成功：

```powershell
# 1. 检查Ollama已安装
ollama --version
# 应该显示：ollama version x.x.x

# 2. 检查服务运行
curl http://localhost:11434
# 应该返回：Ollama is running

# 3. 列出已下载的模型
ollama list
# 应该看到至少一个模型（如qwen2.5:0.5b）

# 4. 测试模型
ollama run qwen2.5:0.5b "hello"
# 应该返回AI生成的回复

# 5. 运行OCR
ocr-enhanced --image invoice.pdf --lang ch --use-llm
# 应该看到：✓ Using LLM model: qwen2.5:0.5b
```

---

## 🎯 预期输出（LLM启用后）

### 控制台输出

```
Initializing LLM processor...
✓ Using LLM model: qwen2.5:0.5b
✓ LLM processor initialized

Processing page 1/8...
  ✓ LLM classified as: invoice (confidence: high)
  ✓ LLM extracted 8 fields

...

Individual page files:
  Page 1 JSON: invoice_page_0001.json
  Page 1 TXT: invoice_page_0001.txt
  Page 1 LLM TXT: invoice_page_0001_llm.txt    ⭐
  Page 1 LLM CSV: invoice_page_0001_llm.csv    ⭐

Combined files:
  Summary CSV: invoice_summary.csv
  LLM Analysis: invoice_llm_analysis.txt        ⭐
  LLM CSV: invoice_llm.csv                      ⭐
```

### 生成的文件

```
results/20260514_161130/
├── invoice_page_0001.json
├── invoice_page_0001.txt
├── invoice_page_0001_llm.txt          ⭐ LLM分析文本
├── invoice_page_0001_llm.csv          ⭐ LLM字段CSV
├── invoice_page_0002.json
├── invoice_page_0002.txt
├── invoice_page_0002_llm.txt          ⭐
├── invoice_page_0002_llm.csv          ⭐
├── ...
├── invoice_all_pages.json
├── invoice_all_pages.txt
├── invoice_all_tables.html
├── invoice_summary.csv
├── invoice_llm_analysis.txt           ⭐ LLM汇总文本
└── invoice_llm.csv                    ⭐ LLM汇总CSV（数据库导入用）
```

---

## 💡 推荐配置

### 快速处理（CPU）

```bash
# 使用最小模型
ollama pull qwen2.5:0.5b

ocr-enhanced --image invoice.pdf --lang ch --use-cpu --use-llm --llm-model qwen2.5:0.5b
```

**性能**：
- 模型大小：300MB
- 处理速度：~3秒/页
- 内存占用：~1.5GB

### 高质量处理（GPU可选）

```bash
# 使用更大的模型
ollama pull gemma2:2b

ocr-enhanced --image invoice.pdf --lang ch --use-llm --llm-model gemma2:2b
```

**性能**：
- 模型大小：1.5GB
- 处理速度：~5秒/页（CPU）、~2秒/页（GPU）
- 内存占用：~3GB

---

## 🔗 相关文档

- **[LLM_INTEGRATION_GUIDE.md](LLM_INTEGRATION_GUIDE.md)** - 完整LLM集成指南
- **[CSV_OUTPUT_GUIDE.md](CSV_OUTPUT_GUIDE.md)** - CSV格式说明
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 快速参考

---

## ❓ 常见问题

### Q: 为什么要用Ollama而不是其他方案？

**A**: 
- ✅ 本地运行，数据不离开本地
- ✅ 免费，无API费用
- ✅ 简单易用，一键安装
- ✅ 支持多种模型
- ✅ CPU友好的小模型

### Q: 可以不用LLM吗？

**A**: 可以！去掉 `--use-llm` 参数：

```bash
ocr-enhanced --image invoice.pdf --lang ch
```

只做OCR，不做AI分析。

### Q: LLM主要做什么？

**A**: 
1. **文档分类**：自动识别发票、收据、运单等
2. **字段提取**：自动提取发票号、日期、金额等
3. **文本纠错**：修正OCR识别错误
4. **结构化输出**：生成数据库友好的CSV文件

### Q: LLM处理需要多久？

**A**: 
- qwen2.5:0.5b（CPU）：~3秒/页
- gemma2:2b（CPU）：~5秒/页
- 完整8页PDF：~30-40秒

**对比**：
- 纯OCR：~15秒（8页）
- OCR + LLM：~45秒（8页）

**额外30秒换来**：自动分类、字段提取、数据库就绪的CSV

---

**版本**: v2.3.0  
**最后更新**: 2026-05-14
