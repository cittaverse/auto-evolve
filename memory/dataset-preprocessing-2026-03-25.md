# 数据集预处理工具创建

**日期**: 2026-03-25  
**执行者**: Hulk 🟢  
**任务**: 处理 AISHELL 和其他数据集（清洗、分割、特征提取）

## 背景

为 CittaVerse 语音识别/叙事分析 pipeline 准备标准化的语音数据集。需要处理 AISHELL 等开源数据集，进行清洗、分割和特征提取。

## 交付物

### 脚本文件

1. **preprocess_datasets.py** (14KB)
   - 主预处理脚本
   - 支持 AISHELL 数据集
   - 功能：解压、标准化、分割、特征提取、清单生成

2. **preprocess-datasets.sh** (4.8KB)
   - Bash 快速执行脚本
   - 一键检查/安装/运行流程
   - 彩色输出和进度提示

3. **extract_features.py** (7.9KB)
   - 独立特征提取工具
   - 支持 8 种声学特征
   - 可视化输出（波形图、频谱图）

4. **validate_dataset.py** (12KB)
   - 数据质量验证工具
   - 检查 manifest 完整性
   - 音频质量检查
   - 分割平衡性验证

### 文档

- **README_DATASETS.md**: 详细使用文档
- **DATASET_PREPROCESSING_SUMMARY.md**: 执行摘要

## 功能特性

### 数据清洗
- 解压 tar.gz 压缩文件
- 重采样到 16kHz
- RMS 音量归一化
- 统一 WAV 格式

### 数据分割
- 自动 train/val/test 分割
- 默认 80/10/10 比例
- 可复现随机种子 (seed=42)

### 特征提取
- MFCC (13 维)
- Mel 频谱图 (40 维)
- 频谱对比度
- 过零率
- 色度特征
- 调性网络
- 频谱质心/滚降

### 数据验证
- Manifest 完整性
- 音频文件存在性
- 标注空值检测
- 音频质量（时长、音量、削波）
- 分割平衡性

## 使用方法

```bash
# 完整流程
./scripts/preprocess-datasets.sh all

# 单独运行
./scripts/preprocess-datasets.sh run --dataset aishell

# 特征提取
python scripts/extract_features.py audio.wav --plot

# 数据验证
python scripts/validate_dataset.py data/processed
```

## 依赖

```bash
pip install librosa numpy pandas soundfile tqdm matplotlib
sudo apt-get install ffmpeg  # 系统依赖
```

## 输出结构

```
data/processed/
├── audio/              # 标准化音频
├── train/manifest.jsonl
├── val/manifest.jsonl
├── test/manifest.jsonl
├── features/           # 特征文件 (.npz)
├── validation_report.json
└── processing_report.json
```

## AISHELL 数据集

- 语言：中文普通话
- 说话者：400 人
- 音频文件：~78,000 条
- 总时长：~178 小时
- 数据大小：~10GB
- 许可：开源可商用

## 下一步

1. 执行预处理：`./scripts/preprocess-datasets.sh all`
2. 验证结果：`python scripts/validate_dataset.py data/processed`
3. 用于模型训练或特征分析

## 扩展计划

- [ ] Common Voice 支持
- [ ] ST-CMDS 支持
- [ ] 老年语音数据集支持
- [ ] 数据增强（噪声、速度、音高）
- [ ] 分布式处理

---

**状态**: ✓ 脚本就绪，等待执行  
**验证等级**: V3 (静态复核完成)
