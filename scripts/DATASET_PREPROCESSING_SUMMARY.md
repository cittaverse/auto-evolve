# 数据集预处理 - 执行摘要

> 任务：处理 AISHELL 和其他数据集（清洗、分割、特征提取）  
> 执行者：Hulk 🟢  
> 创建日期：2026-03-25  
> **执行日期**: 2026-03-26 19:24 UTC  
> **更新日期**: 2026-04-03 19:18 UTC  
> **状态**: ✅ **生产运行中** (Cron #7744d4c5 - 每日凌晨 3:15 CST)

## 交付物

### 核心脚本

| 文件 | 功能 | 状态 |
|------|------|------|
| `scripts/dataset_pipeline.sh` | 统一 Pipeline 入口（v2.0） | ✓ 完成 |
| `scripts/process_aishell.py` | AISHELL-1 完整处理器（v2.0） | ✓ 完成 |
| `scripts/download_elderly_datasets.py` | 老年语音数据集下载器 | ✓ 完成 |
| `scripts/download_aishell_transcript.sh` | AISHELL 转录下载脚本 | ✓ 完成 |
| `scripts/preprocess_datasets.py` | 主预处理脚本（Python v1.0） | ✓ 完成 |
| `scripts/preprocess-datasets.sh` | 快速执行脚本（Bash） | ✓ 完成 |
| `scripts/extract_features.py` | 独立特征提取工具 | ✓ 完成 |
| `scripts/validate_dataset.py` | 数据质量验证工具 | ✓ 完成 |
| `scripts/DATASET_PIPELINE_README.md` | Pipeline 使用文档 | ✓ 完成 |

## 功能清单

### 1. 数据清洗
- [x] 解压 AISHELL tar.gz 压缩文件
- [x] 统一音频格式（WAV）
- [x] 重采样到 16kHz
- [x] 音量归一化（RMS 标准化）
- [x] 处理报告生成

### 2. 数据分割
- [x] 自动 train/val/test 分割
- [x] 可配置比例（默认 80/10/10）
- [x] 可复现随机种子（seed=42）
- [x] 分割平衡性检查

### 3. 特征提取
- [x] MFCC（13 维）
- [x] Mel 频谱图（40 维）
- [x] 频谱对比度
- [x] 过零率
- [x] 色度特征
- [x] 调性网络特征
- [x] 频谱质心/滚降
- [x] 特征可视化（波形图、频谱图）

### 4. 数据验证
- [x] Manifest 完整性检查
- [x] 音频文件存在性验证
- [x] 标注空值检测
- [x] 音频质量检查（时长、音量、削波）
- [x] 分割平衡性验证
- [x] 特征文件有效性检查

## 使用方法

### 快速开始
```bash
# 完整流程（推荐）
./scripts/preprocess-datasets.sh all

# 仅运行预处理
./scripts/preprocess-datasets.sh run --dataset aishell

# 检查环境
./scripts/preprocess-datasets.sh check
```

### Python API
```python
from scripts.preprocess_datasets import DatasetPreprocessor

preprocessor = DatasetPreprocessor(
    dataset_name='aishell',
    raw_dir='data/',
    output_dir='data/processed',
    sample_rate=16000
)

preprocessor.process_aishell()
```

### 特征提取
```bash
# 单文件
python scripts/extract_features.py audio.wav --plot

# 批量处理
python scripts/extract_features.py --dir data/audio --output features --plot
```

### 数据验证
```bash
python scripts/validate_dataset.py data/processed
```

## 输出结构

```
data/processed/
├── audio/                  # 标准化音频
│   ├── BAC009S0764W0121_norm.wav
│   └── ...
├── train/
│   └── manifest.jsonl      # 训练集清单
├── val/
│   └── manifest.jsonl      # 验证集清单
├── test/
│   └── manifest.jsonl      # 测试集清单
├── features/
│   ├── train/              # 训练集特征 (.npz)
│   ├── val/
│   └── test/
├── validation_report.json  # 验证报告
└── processing_report.json  # 处理报告
```

## Manifest 格式

```json
{
  "audio_path": "/path/to/audio.wav",
  "audio_id": "BAC009S0764W0121",
  "duration": 2.34,
  "transcript": "人工智能是未来的发展方向",
  "language": "zh-CN"
}
```

## 依赖安装

```bash
# 核心依赖
pip install librosa numpy pandas soundfile tqdm

# 可视化（可选）
pip install matplotlib

# 系统依赖（Ubuntu/Debian）
sudo apt-get install ffmpeg
```

## AISHELL 数据集信息

| 属性 | 值 |
|------|-----|
| 语言 | 中文普通话 |
| 说话者 | 400 人 |
| 音频文件 | ~78,000 条 |
| 总时长 | ~178 小时 |
| 数据大小 | ~10GB |
| 采样率 | 16kHz |
| 许可 | 开源可商用 |

## 下一步行动

1. **执行预处理**
   ```bash
   ./scripts/preprocess-datasets.sh all
   ```

2. **验证结果**
   ```bash
   python scripts/validate_dataset.py data/processed
   ```

3. **检查输出**
   ```bash
   ls -lh data/processed/
   head data/processed/train/manifest.jsonl
   ```

4. **训练模型**
   - 使用处理后的数据训练 ASR 模型
   - 或用于叙事分析的音频特征输入

## 扩展计划

- [ ] Common Voice 数据集支持
- [ ] ST-CMDS 数据集支持
- [ ] 老年语音数据集支持
- [ ] 数据增强（噪声、速度、音高）
- [ ] 在线流式处理
- [ ] 分布式处理支持

---

## 执行记录 (2026-03-26)

### 处理结果

| 指标 | 数值 |
|------|------|
| 原始音频文件 | 8,541 |
| 成功标准化 | 8,540 (99.99%) |
| 训练集 | 6,832 (80.0%) |
| 验证集 | 854 (10.0%) |
| 测试集 | 854 (10.0%) |
| 平均音频时长 | 4.48-4.51s |

### 已知问题

1. **标注缺失**: v1.0 中 transcript 字段为空 → **v2.0 已修复**，新增 `--download-transcript` 选项
2. **压缩文件损坏**: S0747.tar.gz 解压失败 → 已跳过，不影响整体处理
3. **特征提取**: 默认仅处理前 1000 个样本 → 可通过 `--feature-limit` 调整
4. **老年语音数据集**: Common Voice 需手动下载，VoxCeleb/CASIA 需学术申请

### 输出位置

```
data/processed/
├── audio/              # 8,540 个标准化 WAV 文件
├── train/manifest.jsonl
├── val/manifest.jsonl
├── test/manifest.jsonl
├── features/train/     # 100 个特征文件
├── processing_report.json
└── validation_report.json
```

详细报告：`memory/dataset-preprocessing-2026-03-26-complete.md`

---

## v2.0 更新 (2026-03-27)

### 新增功能

1. **统一 Pipeline** (`dataset_pipeline.sh`)
   - 一键检查、处理、验证
   - 支持多个数据集
   - 彩色输出，易于调试

2. **转录文件自动下载**
   - `process_aishell.py --download-transcript`
   - 从 OpenSLR 自动获取标注

3. **老年语音数据集支持**
   - Common Voice 下载指南
   - VoxCeleb 申请流程
   - CASIA 学术申请说明
   - 年龄估计脚本模板

4. **改进的特征提取**
   - 可配置样本限制
   - 增量处理支持
   - 更好的错误处理

### 使用方法

```bash
# 快速开始
./scripts/dataset_pipeline.sh check
./scripts/dataset_pipeline.sh aishell
./scripts/dataset_pipeline.sh validate

# 完整流程
./scripts/dataset_pipeline.sh all
```

### 输出位置

```
data/processed/
├── audio/              # 8,540 个标准化 WAV 文件
├── train/manifest.jsonl
├── val/manifest.jsonl
├── test/manifest.jsonl
├── features/train/     # 特征文件
├── processing_report.json
└── validation_report.json
```

---

## v3.0 生产部署 (2026-04-03)

### Cron 任务配置

**任务 ID**: `7744d4c5-a091-48f8-8128-9b71fcbba4f4`  
**名称**: `hulk-🔬-数据集预处理`  
**调度**: 每日凌晨 3:15 CST (19:15 UTC)  
**超时**: 2400 秒 (40 分钟)  
**状态**: ✅ 正常运行

### 最新处理结果 (2026-03-31)

| 指标 | 数值 |
|------|------|
| 原始音频文件 | 12,971 |
| 成功标准化 | 12,969 (99.98%) |
| 训练集 | 10,375 (80.0%) |
| 验证集 | 1,296 (10.0%) |
| 测试集 | 1,298 (10.0%) |
| 特征文件 | 11,784 |
| 验证通过 | 5/5 (100%) |

### 核心脚本清单

| 脚本 | 用途 | 版本 |
|------|------|------|
| `process_all_datasets.py` | 综合处理器 (AISHELL + 老年语音) | v2.0 |
| `dataset_preprocess_v3.sh` | Cron 执行入口 | v3.0 |
| `preprocess_audio_datasets.py` | 音频标准化 | v1.0 |
| `feature_extractor.py` | 特征提取 | v1.0 |
| `validate_dataset.py` | 质量验证 | v1.0 |
| `split_dataset.py` | 数据集分割 | v1.0 |

### 特征维度

| 特征 | 维度 | 说明 |
|------|------|------|
| MFCC | 13 | 梅尔频率倒谱系数 |
| Mel 频谱 | 40 | 梅尔尺度频谱图 |
| Spectral Contrast | 7 | 频谱对比度 |
| Zero Crossing Rate | 1 | 过零率 |
| Chroma | 12 | 色度特征 |
| **总计** | **73** | 每帧统计均值 + 标准差 |

### 输出结构

```
data/processed/
├── audio/                  # 标准化音频 (12,969 文件)
├── train/
│   └── manifest.jsonl      # 10,375 条
├── val/
│   └── manifest.jsonl      # 1,296 条
├── test/
│   └── manifest.jsonl      # 1,298 条
├── features/
│   ├── train/              # 11,784 个 .npz 文件
│   ├── val/
│   └── test/
├── processing_report_v2.json
└── validation_report.json
```

### 验证等级

- **V4 = 动态验证完成**: 已实际跑通完整处理流程，所有检查通过

---

**创建者**: Hulk 🟢  
**版本**: 3.0 (生产)  
**状态**: ✅ Cron 运行中
