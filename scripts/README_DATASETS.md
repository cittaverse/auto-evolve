# 数据集预处理工具

> 用于 AISHELL 及其他语音数据集的清洗、分割、特征提取

## 快速开始

```bash
# 完整流程（检查 + 安装 + 运行）
./scripts/preprocess-datasets.sh all

# 仅运行预处理
./scripts/preprocess-datasets.sh run --dataset aishell

# 检查环境和数据
./scripts/preprocess-datasets.sh check
```

## 功能

### 1. 数据清洗
- 解压 AISHELL 的 tar.gz 压缩文件
- 统一音频格式（WAV）
- 重采样到目标采样率（默认 16kHz）
- 音量归一化

### 2. 数据分割
- 自动分割为训练集/验证集/测试集
- 默认比例：80% / 10% / 10%
- 可复现的随机分割（seed=42）

### 3. 特征提取
- **MFCC**: 13 维梅尔频率倒谱系数
- **Mel 频谱图**: 40 维梅尔频谱
- **频谱对比度**: 7 个八度的频谱对比
- **过零率**: 音频信号的过零率

## 输出结构

```
data/processed/
├── audio/              # 标准化后的音频文件
├── train/
│   └── manifest.jsonl  # 训练集清单
├── val/
│   └── manifest.jsonl  # 验证集清单
├── test/
│   └── manifest.jsonl  # 测试集清单
├── features/
│   ├── train/          # 训练集特征 (.npz)
│   ├── val/            # 验证集特征
│   └── test/           # 测试集特征
└── processing_report.json  # 处理报告
```

## Manifest 格式

每行一个 JSON 对象：

```json
{
  "audio_path": "/path/to/audio.wav",
  "audio_id": "BAC009S0764W0121",
  "duration": 2.34,
  "transcript": "人工智能是未来的发展方向",
  "language": "zh-CN"
}
```

## Python API

```python
from scripts.preprocess_datasets import DatasetPreprocessor

preprocessor = DatasetPreprocessor(
    dataset_name='aishell',
    raw_dir='/path/to/raw/data',
    output_dir='/path/to/output',
    sample_rate=16000,
    test_split=0.1,
    val_split=0.1
)

# 处理 AISHELL
success = preprocessor.process_aishell()

# 单独提取特征
features = preprocessor.extract_features(audio_path)
# features['mfcc'], features['mel_spec'], etc.
```

## 依赖

```bash
pip install librosa numpy pandas soundfile tqdm
```

## 支持的数据集

| 数据集 | 语言 | 状态 | 备注 |
|--------|------|------|------|
| AISHELL | 中文 | ✓ 支持 | 400 说话者，~10GB |
| Common Voice | 多语言 | 计划中 | Mozilla 开源 |
| ST-CMDS | 中文 | 计划中 | 单说话者 |
| 老年语音 | 中文 | 计划中 | 自建数据集 |

## 命令行参数

```bash
python scripts/preprocess_datasets.py \
  --dataset aishell \
  --raw-dir /path/to/raw \
  --output-dir /path/to/output \
  --sample-rate 16000 \
  --test-split 0.1 \
  --val-split 0.1 \
  --extract-features
```

## 处理报告

处理完成后会生成 `processing_report.json`，包含：

- 处理文件总数
- 各分割集文件数
- 标注加载数量
- 采样率配置
- 处理时间戳

## 故障排查

### librosa 安装失败
```bash
# 需要 ffmpeg
sudo apt-get install ffmpeg
pip install librosa
```

### 内存不足
- 减少批量处理大小
- 关闭特征提取（`--skip-features`）
- 使用更少的 workers

### 标注文件未找到
确认 AISHELL 数据结构：
```
data_aishell/
├── wav/        # 音频压缩文件
└── transcript/ # 标注文件
    └── aishell_transcript_v0.8.txt
```

## 下一步

1. 运行预处理：`./scripts/preprocess-datasets.sh all`
2. 检查输出：`ls -lh data/processed/`
3. 查看清单：`head data/processed/train/manifest.jsonl`
4. 训练模型：使用处理后的数据训练 ASR 模型

---

**创建者**: Hulk 🟢  
**版本**: 1.0  
**日期**: 2026-03-25
