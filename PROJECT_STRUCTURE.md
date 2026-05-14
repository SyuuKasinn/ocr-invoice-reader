# 项目结构说明

## 📁 目录结构

```
ocr-invoice-reader/
├── ocr_invoice_reader/          # 核心代码
│   ├── api/                     # REST API实现
│   │   ├── app.py              # FastAPI应用
│   │   └── models.py           # API数据模型
│   ├── cli/                     # 命令行工具
│   │   ├── main.py             # ocr-enhanced命令
│   │   └── api_server.py       # ocr-api命令
│   ├── models/                  # 数据模型
│   │   └── base.py             # Document基础模型
│   ├── processors/              # 核心处理器
│   │   ├── enhanced_structure_analyzer.py  # 增强结构分析（主引擎）
│   │   ├── structure_analyzer.py           # 基础结构分析
│   │   ├── file_handler.py                 # 文件处理（PDF/图片）
│   │   └── document_processor.py           # 文档处理流程
│   └── utils/                   # 工具模块
│       ├── text_processor.py    # 文本后处理
│       └── image_optimizer.py   # 图像优化（可选）
│
├── docs/                        # 文档目录
│   ├── API_USAGE.md            # API使用指南 ⭐
│   ├── QUICKSTART_API_CSV.md   # 快速入门（API+CSV） ⭐
│   ├── QUICK_START_GUIDE.md    # 基础快速入门
│   ├── DOCUMENT_EXTRACTION_GUIDE.md  # 文档提取指南
│   ├── development/             # 开发文档
│   │   ├── OCR_IMPROVEMENTS.md           # OCR改进说明
│   │   ├── TABLE_DETECTION_FIX.md        # 表格检测修复
│   │   ├── PAGE8_FIX.md                  # Page 8问题修复
│   │   ├── VERIFICATION_RESULTS.md       # 验证测试结果
│   │   ├── CPU_OPTIMIZATION_REALISTIC.md # CPU性能优化实测 ⭐
│   │   ├── NEW_FEATURES.md               # 新功能说明
│   │   └── IMPROVEMENTS_SUMMARY.md       # 改进总结
│   └── deployment/              # 部署文档
│       ├── DOCKER_DEPLOYMENT.md     # Docker部署指南
│       ├── DOCKER_FONT_SOLUTION.md  # Docker字体解决方案
│       └── DEPLOY_INSTRUCTIONS.md   # 部署说明
│
├── examples/                    # 示例文件
│   ├── INVOICE.pdf             # 测试发票PDF
│   └── sample_invoice.jpg      # 示例图片
│
├── fonts/                       # 字体文件（Docker用）
│   └── simhei.ttf              # 黑体字体
│
├── images/                      # 文档图片资源
│   └── ...                     # README中的示例图片
│
├── tests/                       # 测试代码（待完善）
│
├── README.md                    # 项目主文档 ⭐
├── CHANGELOG.md                # 版本更新日志
├── PERFORMANCE_OPTIMIZATION.md # 性能优化完整指南 ⭐
├── VISUAL_EXAMPLES.md          # 可视化示例
├── LICENSE                     # MIT许可证
├── requirements.txt            # Python依赖
├── setup.py                    # 安装配置
├── Dockerfile                  # Docker镜像配置
└── docker-compose.yml          # Docker Compose配置
```

## 📖 文档导航

### 新用户入门

1. **README.md** - 项目概述、快速开始
2. **docs/QUICKSTART_API_CSV.md** - 最新功能快速入门（API + CSV）
3. **docs/API_USAGE.md** - REST API完整使用指南

### 开发者

1. **docs/development/OCR_IMPROVEMENTS.md** - 了解OCR改进
2. **docs/development/CPU_OPTIMIZATION_REALISTIC.md** - 性能优化实测
3. **PERFORMANCE_OPTIMIZATION.md** - 完整性能优化方案

### 部署运维

1. **docs/deployment/DOCKER_DEPLOYMENT.md** - Docker部署
2. **requirements.txt** - 依赖列表
3. **Dockerfile** - 容器配置

## 🎯 核心文件说明

### 代码模块

| 文件 | 功能 | 重要性 |
|------|------|--------|
| `processors/enhanced_structure_analyzer.py` | OCR主引擎，表格检测 | ⭐⭐⭐⭐⭐ |
| `processors/file_handler.py` | PDF/图片处理 | ⭐⭐⭐⭐⭐ |
| `api/app.py` | REST API服务 | ⭐⭐⭐⭐ |
| `models/base.py` | 数据模型（支持CSV导出） | ⭐⭐⭐⭐ |
| `utils/text_processor.py` | 文本质量改进 | ⭐⭐⭐ |
| `cli/main.py` | 命令行工具 | ⭐⭐⭐⭐⭐ |

### 关键文档

| 文档 | 内容 | 受众 |
|------|------|------|
| **README.md** | 项目介绍、安装、基本使用 | 所有人 ⭐⭐⭐⭐⭐ |
| **QUICKSTART_API_CSV.md** | 新功能快速入门 | 新用户 ⭐⭐⭐⭐⭐ |
| **API_USAGE.md** | API完整文档 | API用户 ⭐⭐⭐⭐ |
| **PERFORMANCE_OPTIMIZATION.md** | 性能优化指南 | 性能关注者 ⭐⭐⭐⭐ |
| **CPU_OPTIMIZATION_REALISTIC.md** | CPU优化实测 | 无GPU用户 ⭐⭐⭐⭐ |

## 🔧 配置文件

| 文件 | 用途 |
|------|------|
| `requirements.txt` | Python依赖包 |
| `setup.py` | 项目安装配置 |
| `.gitignore` | Git忽略规则 |
| `Dockerfile` | Docker镜像构建 |
| `docker-compose.yml` | Docker服务编排 |
| `MANIFEST.in` | 打包清单 |

## 📦 安装包结构

安装后的包结构（`pip install .`）：

```
site-packages/
└── ocr_invoice_reader/
    ├── api/
    ├── cli/
    ├── models/
    ├── processors/
    └── utils/
```

命令行工具：
- `ocr-enhanced` - 核心OCR处理
- `ocr-api` - REST API服务器

## 🗂️ 临时文件

运行时生成（已在.gitignore中）：

```
results/              # OCR处理结果
output/               # 输出目录
temp/                 # 临时文件
.paddleocr/          # PaddleOCR模型缓存
__pycache__/         # Python字节码
*.egg-info/          # 安装信息
```

## 🚀 快速查找

### 想要...

- **开始使用项目** → `README.md`
- **使用REST API** → `docs/API_USAGE.md`
- **导出CSV** → `docs/QUICKSTART_API_CSV.md`
- **提升性能** → `PERFORMANCE_OPTIMIZATION.md`
- **修复问题** → `docs/development/` 查看修复文档
- **部署到服务器** → `docs/deployment/DOCKER_DEPLOYMENT.md`
- **了解更新** → `CHANGELOG.md`

### 我是...

- **新用户** → 从 `README.md` 开始
- **开发者** → 看 `docs/development/` 目录
- **API用户** → 看 `docs/API_USAGE.md`
- **运维人员** → 看 `docs/deployment/` 目录

## 📊 项目统计

### 代码量

- Python代码: ~3,500 行
- 文档: ~50,000 字
- 测试覆盖: 待完善

### 版本历史

- v1.x: 基础OCR功能
- v2.0: PP-Structure集成
- v2.1: 增强表格检测
- v2.2: API + CSV支持，性能优化
- **当前**: v2.2.6

## 🔄 维护指南

### 添加新功能

1. 代码放在 `ocr_invoice_reader/` 对应模块
2. 文档放在 `docs/development/`
3. 更新 `CHANGELOG.md`
4. 更新 `README.md` (如果是重要功能)

### 添加新文档

1. 用户文档 → `docs/`
2. 开发文档 → `docs/development/`
3. 部署文档 → `docs/deployment/`
4. 更新本文件的文档导航

### 发布新版本

1. 更新 `setup.py` 版本号
2. 更新 `CHANGELOG.md`
3. 创建 Git tag: `git tag v2.x.x`
4. 推送: `git push --tags`

---

**最后更新**: 2026-05-14  
**当前版本**: v2.2.6  
**维护者**: SyuuKasinn
