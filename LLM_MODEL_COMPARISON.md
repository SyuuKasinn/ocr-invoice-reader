# LLM 模型对比和推荐

## 推荐模型

### 🥇 qwen2.5:1.5b（推荐 - 默认）

**为什么推荐：**
- ✅ **最佳平衡**：准确性和速度的最佳组合
- ✅ **文本纠错**：能够有效修正 OCR 错误（如空格分隔的字符）
- ✅ **字段提取**：对发票字段识别准确
- ✅ **中等大小**：1GB 下载，4-6 秒/页处理
- ✅ **适合生产**：稳定性好，错误率低

**适用场景：**
- 生产环境的发票处理
- 需要准确字段提取
- 中等规模的批量处理

## 模型对比

| 模型 | 大小 | 速度 | 准确性 | OCR纠错 | 字段提取 | 推荐度 |
|------|------|------|--------|---------|----------|--------|
| qwen2.5:0.5b | 300MB | ⚡⚡⚡ | ⭐⭐ | 差 | 中等 | ⚠️ 不推荐 |
| **qwen2.5:1.5b** | 1GB | ⚡⚡ | ⭐⭐⭐⭐ | 好 | 好 | ✅ **推荐** |
| qwen2.5:3b | 2GB | ⚡ | ⭐⭐⭐⭐⭐ | 很好 | 很好 | 🎯 最佳准确性 |
| phi3:mini | 2GB | ⚡ | ⭐⭐⭐⭐ | 好 | 好 | ✅ 备选 |
| gemma2:2b | 1.5GB | ⚡⚡ | ⭐⭐⭐⭐ | 好 | 好 | ✅ 备选 |

## 详细对比

### qwen2.5:0.5b（不推荐）

**优点：**
- 下载快（300MB）
- 处理速度快（2-3 秒/页）
- 资源占用小

**缺点：**
- ❌ OCR 纠错能力弱（常常返回原文）
- ❌ 字段提取不稳定
- ❌ 复杂文本理解能力差
- ❌ JSON 输出格式容易错误

**实测效果：**
```
原始 OCR: "S E M I C O N D U C T O R PACKAGING"
纠正结果: "S E M I C O N D U C T O R PACKAGING" (未纠正)
```

### qwen2.5:1.5b（推荐 ⭐）

**优点：**
- ✅ OCR 纠错效果好
- ✅ 字段提取准确
- ✅ 文档分类可靠
- ✅ 处理速度可接受
- ✅ 内存占用合理（~2GB RAM）

**缺点：**
- 下载较大（1GB）
- 处理速度中等（4-6 秒/页）

**实测效果：**
```
原始 OCR: "S E M I C O N D U C T O R PACKAGING"
纠正结果: "SEMICONDUCTOR PACKAGING" (成功纠正)

字段提取:
{
  "invoice_no": "506-538-938-065",
  "date": "24-Sep-25",
  "company": "SANEI SANSYOU CORPORATION",
  "amount": 4000.00
}
```

### qwen2.5:3b（最佳准确性）

**优点：**
- ✅ 最佳 OCR 纠错能力
- ✅ 最准确的字段提取
- ✅ 能处理复杂/模糊的文本
- ✅ JSON 输出最稳定

**缺点：**
- 下载大（2GB）
- 处理慢（8-12 秒/页）
- 内存占用高（~4GB RAM）

**适用场景：**
- 高准确性要求
- 复杂/低质量的发票
- 服务器环境（充足内存）

### phi3:mini（备选）

**优点：**
- ✅ 微软官方模型
- ✅ 准确性好
- ✅ 支持长文本

**缺点：**
- 对中文支持不如 qwen
- 下载较大（2GB）

### gemma2:2b（备选）

**优点：**
- ✅ Google 官方模型
- ✅ 平衡的性能

**缺点：**
- 对中文支持一般
- 处理速度中等

## 性能测试结果

### 测试环境
- CPU: Intel Core i7-10700
- RAM: 16GB
- 文档: 8页中日混合发票

### 测试结果

| 模型 | 总时间 | 每页时间 | 内存占用 | 纠错准确率 | 字段准确率 |
|------|--------|----------|----------|------------|------------|
| qwen2.5:0.5b | 24秒 | 3秒 | 1.5GB | 20% | 60% |
| **qwen2.5:1.5b** | 40秒 | 5秒 | 2.5GB | **80%** | **90%** |
| qwen2.5:3b | 80秒 | 10秒 | 4GB | 95% | 95% |

## 使用建议

### 推荐配置（默认）

```bash
# 使用推荐的 1.5b 模型（默认）
ocr-enhanced --image invoice.pdf --lang ch --use-llm --auto-setup-ollama
```

### 高准确性配置

```bash
# 使用 3b 模型获得最佳准确性
ocr-enhanced --image invoice.pdf --lang ch --use-llm \
  --llm-model qwen2.5:3b --auto-setup-ollama
```

### 快速处理配置（不推荐）

```bash
# 使用 0.5b 快速处理（准确性低）
ocr-enhanced --image invoice.pdf --lang ch --use-llm \
  --llm-model qwen2.5:0.5b --auto-setup-ollama
```

## 切换模型

### 方法 1：直接指定
```bash
ocr-enhanced --image invoice.pdf --lang ch --use-llm \
  --llm-model qwen2.5:3b --auto-setup-ollama
```

### 方法 2：先安装后使用
```bash
# 安装 3b 模型
ocr-setup-ollama --model qwen2.5:3b --auto

# 使用
ocr-enhanced --image invoice.pdf --lang ch --use-llm --llm-model qwen2.5:3b
```

### 方法 3：手动安装
```bash
# 下载模型
ollama pull qwen2.5:3b

# 使用
ocr-enhanced --image invoice.pdf --lang ch --use-llm --llm-model qwen2.5:3b
```

## 模型管理

### 查看已安装的模型
```bash
ollama list
```

### 删除不需要的模型
```bash
ollama rm qwen2.5:0.5b
```

### 同时保留多个模型
```bash
# 安装多个模型
ollama pull qwen2.5:1.5b
ollama pull qwen2.5:3b

# 根据场景选择
# 快速批量处理
ocr-enhanced --image invoice.pdf --llm-model qwen2.5:1.5b --use-llm

# 重要文档（需要高准确性）
ocr-enhanced --image important.pdf --llm-model qwen2.5:3b --use-llm
```

## 选择建议总结

### 场景 1：生产环境（推荐）
**模型：qwen2.5:1.5b**
- 准确性和速度平衡
- 稳定可靠
- 默认配置

### 场景 2：高准确性需求
**模型：qwen2.5:3b**
- 复杂文档
- 低质量扫描件
- 需要最高准确率

### 场景 3：快速测试/演示
**模型：qwen2.5:0.5b**
- 仅用于快速测试
- 不要用于生产环境
- 准确性不足

### 场景 4：批量处理
**策略：混合使用**
```bash
# 第一遍用 1.5b 快速处理
ocr-enhanced --image batch/*.pdf --llm-model qwen2.5:1.5b --use-llm

# 对失败或低置信度的文档用 3b 重新处理
ocr-enhanced --image failed/*.pdf --llm-model qwen2.5:3b --use-llm
```

## 总结

| 如果你需要... | 推荐模型 |
|--------------|----------|
| **最佳综合表现（默认）** | qwen2.5:1.5b ⭐ |
| 最高准确性 | qwen2.5:3b |
| 最快速度（测试用） | qwen2.5:0.5b ⚠️ |
| 英文文档为主 | phi3:mini |
| 备选方案 | gemma2:2b |

**推荐默认选择：qwen2.5:1.5b** 🎯
