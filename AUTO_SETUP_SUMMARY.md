# 自动安装和 LLM 集成总结

## ✅ 完成的功能

### 1. Ollama 自动安装
- **Windows 路径检测**：自动查找 Ollama 安装路径
- **静默安装**：支持 `/SILENT` 参数自动安装
- **服务启动**：自动启动 Ollama 服务
- **模型下载**：自动下载 qwen2.5:0.5b 模型（300MB）
- **编码修复**：解决 Windows cp932 编码问题

### 2. LLM 处理流程
```
OCR 识别（8页） → LLM 后处理（每页） → 保存结果
```

**处理阶段：**
1. OCR 识别所有页面（不受 LLM 影响）
2. 提取所有文本
3. LLM 处理（在保存前）：
   - 文本纠错（修正 OCR 错误）
   - 文档分类（invoice, receipt, waybill 等）
   - 字段提取（发票号、日期、金额、公司等）

### 3. 输出文件

每页生成：
- `*_page_*.json` - 完整的结构化数据（含 LLM 结果）
- `*_page_*.txt` - 原始 OCR 文本
- `*_page_*_llm.txt` - LLM 纠正和分析结果
- `*_page_*_llm.csv` - 可导入数据库的字段（如果是发票）

## 📝 使用方法

### 自动模式（推荐）
```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm --auto-setup-ollama
```

这个命令会：
1. 检查 Ollama 是否已安装
2. 自动安装 Ollama（如果需要）
3. 启动 Ollama 服务
4. 下载模型 qwen2.5:0.5b
5. 运行 OCR + LLM 处理

### 手动检查状态
```bash
ocr-setup-ollama --status
```

### 只安装不运行
```bash
ocr-setup-ollama --auto
```

## 🔧 技术改进

### Windows 兼容性修复
1. **路径检测**：
   ```python
   C:\Users\{username}\AppData\Local\Programs\Ollama\ollama.exe
   C:\Program Files\Ollama\ollama.exe
   ```

2. **编码处理**：
   ```python
   # subprocess 使用 utf-8 编码
   encoding='utf-8', errors='replace'
   ```

3. **Unicode 字符替换**：
   - `✓` → `[OK]`
   - `✗` → `[X]`

### LLM 处理优化
1. **独立处理**：OCR 和 LLM 分离，不影响识别速度
2. **错误容忍**：单页 LLM 失败不影响其他页
3. **超时处理**：30 秒超时，自动跳过

## 📊 示例输出

### 原始 OCR（page_0002.txt）
```
INVOICE
Tracking No: | 506-538-938-065
S E M I C O N D U C T O R PACKAGING
```

### LLM 纠正（page_0002_llm.txt）
```
[Corrected Text]
INVOICE
Tracking No: 506-538-938-065
SEMICONDUCTOR PACKAGING

[Document Classification]
Type: invoice
Confidence: high

[Extracted Fields]
Invoice No: 506-538-938-065
Date: 24-Sep-25
Company: SANEI SANSYOU CORPORATION
```

## ⚠️ 已知问题

1. **LLM 超时**：大文本可能超时（目前限制 2000 字符）
2. **模型能力**：qwen2.5:0.5b 较小，纠错能力有限
3. **处理速度**：每页 LLM 处理需要 3-10 秒

## 🚀 未来优化

1. 支持更大的模型（qwen2.5:1.5b, phi3:mini）
2. 批量处理模式（一次处理多页）
3. 增加超时配置参数
4. 改进提示词（prompt）提高纠错质量
