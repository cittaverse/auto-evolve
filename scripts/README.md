# 语音数据集预处理工具集

> 用于 CittaVerse 叙事质量评估系统的语音数据预处理流程
> 
> 作者：Hulk 🟢  
> 日期：2026-04-02

## 📁 目录结构

```
scripts/
├── README.md                          # 本文档
├── run_pipeline.sh                    # 主流程脚本
├── preprocess_aishell.py              # AISHELL 专用预处理
├── preprocess_common.py               # 通用数据集预处理
├── feature_extractor.py               # 高级特征提取
├── data_augmentation.py               # 数据增强
├── split_dataset.py                   # 数据集分割
└── configs/
    ├── feature_config.json            # 特征提取配置
    └── augmentation_config.json       # 数据增强配置
```

## 🚀 快速开始

### 完整流程（推荐）

```bash
# 处理 AISHELL-1 数据集
./run_pipeline.sh \
    --dataset aishell \
    --data_dir /path/to/AISHELL-1 \
    --output_dir /path/to/output

# 处理 LibriSpeech + 数据增强
./run_pipeline.sh \
    --dataset librispeech \
    --data_dir /path/to/LibriSpeech \
    --output_dir /path/to/output \
    --augment

# 说话人独立分割
./run_pipeline.sh \
    --dataset aishell \
    --data_dir /path/to/AISHELL-1 \
    --output_dir /path/to/output \
    --split_method speaker_independent
```

### 单步执行

```bash
# 1. 预处理 AISHELL
python preprocess_aishell.py \
    --data_dir /path/to/AISHELL-1 \
    --output_dir /path/to/output

# 2. 特征提取
python feature_extractor.py \
    --input_dir /path/to/wav \
    --output_dir /path/to/features \
    --compute_global_stats \
    --normalize

# 3. 数据增强
python data_augmentation.py \
    --input_dir /path/to/wav \
    --output_dir /path/to/augmented \
    --methods noise,gain,pitch \
    --n_copies 2

# 4. 数据集分割
python split_dataset.py \
    --metadata /path/to/metadata.json \
    --output_dir /path/to/splits \
    --method stratified
```

## 📊 支持的数据集

| 数据集 | 语言 | 说明 |
|--------|------|------|
| `aishell` | 中文 | AISHELL-1 普通话语音数据集 |
| `librispeech` | 英文 | LibriSpeech 英语朗读数据集 |
| `common_voice` | 多语言 | Mozilla Common Voice |
| `thchs30` | 中文 | THCHS-30 中文语音数据集 |

## 🔧 特征提取

### 提取的特征类型

- **MFCC** (13 维 + delta + delta-delta = 39 维)
- **Log Mel Spectrogram** (40 维)
- **Chroma** (12 维)
- **Spectral Contrast** (7 维)
- **Tonnetz** (6 维)
- **Zero Crossing Rate** (1 维)
- **RMS Energy** (1 维)
- **Spectral Centroid** (1 维)
- **Spectral Rolloff** (1 维)

### 统计特征

对每个特征自动计算：
- Mean
- Std
- Min
- Max

### 配置示例

```json
{
    "sample_rate": 16000,
    "n_mfcc": 13,
    "n_mels": 40,
    "extract_delta": true,
    "extract_stats": true,
    "features": ["mfcc", "log_mel", "chroma"]
}
```

## 🎛️ 数据增强

### 支持的增强方法

| 方法 | 说明 | 参数 |
|------|------|------|
| `noise` | 背景噪声注入 | SNR: 10-30 dB |
| `speed` | 速度扰动 | 因子：0.9, 1.0, 1.1 |
| `pitch` | 音高变换 | 半音：-2 到 +2 |
| `reverb` | 混响效果 | 延迟：50ms |
| `gain` | 增益变化 | 范围：-5 到 +5 dB |
| `stretch` | 时间拉伸 | 因子：0.8, 1.0, 1.2 |

### 使用示例

```bash
# 使用配置文件
python data_augmentation.py \
    --input_dir wav/ \
    --output_dir augmented/ \
    --config configs/augmentation_config.json \
    --n_copies 3

# 命令行指定方法
python data_augmentation.py \
    --input_dir wav/ \
    --output_dir augmented/ \
    --methods noise,pitch,gain \
    --n_copies 2
```

## 📐 数据集分割

### 分割方法

| 方法 | 说明 | 适用场景 |
|------|------|---------|
| `random` | 随机分割 | 快速原型 |
| `stratified` | 分层分割（按说话人） | 一般训练 |
| `speaker_independent` | 说话人独立 | 泛化能力测试 |
| `duration_balanced` | 时长平衡 | 公平性要求高 |

### 使用示例

```bash
# 分层分割
python split_dataset.py \
    --metadata metadata.json \
    --output_dir splits/ \
    --method stratified \
    --train_ratio 0.8 \
    --dev_ratio 0.1 \
    --test_ratio 0.1

# 说话人独立分割
python split_dataset.py \
    --metadata metadata.json \
    --output_dir splits/ \
    --method speaker_independent
```

## 📁 输出格式

### 目录结构

```
output/
├── processed/
│   ├── wav/              # 处理后的音频
│   ├── features/         # 提取的特征 (.npz)
│   └── metadata/
│       ├── train.json    # 训练集元数据
│       ├── dev.json      # 验证集元数据
│       ├── test.json     # 测试集元数据
│       ├── train.csv     # CSV 格式
│       ├── dev.csv
│       ├── test.csv
│       └── statistics.json
├── augmented/            # 增强数据（如启用）
├── splits/               # 分割结果
│   ├── train.json
│   ├── dev.json
│   ├── test.json
│   └── split_statistics.json
└── processing_report.json
```

### 元数据格式

```json
{
    "utterance_id": "BAC009S0764W0121",
    "speaker_id": "S0764",
    "dataset": "aishell",
    "split": "train",
    "duration": 2.345,
    "transcript": "人工智能改变世界",
    "wav_path": "/path/to/wav/BAC009S0764W0121.wav",
    "feature_path": "/path/to/features/BAC009S0764W0121.npz"
}
```

## 📦 依赖安装

```bash
# 核心依赖
pip install librosa soundfile numpy tqdm

# 可选：用于音频播放/可视化
pip install matplotlib ipywidgets

# 完整依赖
pip install -r requirements.txt
```

## 🔬 在 CittaVerse 中的使用

### 叙事录音预处理

```bash
# 处理用户叙事录音
./run_pipeline.sh \
    --dataset aishell \
    --data_dir /data/narrations/raw \
    --output_dir /data/narrations/processed \
    --augment \
    --split_method stratified
```

### 特征用于评分模型

```python
import numpy as np

# 加载特征
features = np.load('features/utterance_001.npz')

# MFCC 统计特征
mfcc_mean = features['mfcc_mean']  # 13 维
mfcc_std = features['mfcc_std']    # 13 维

# 用于叙事质量评估模型输入
model_input = np.concatenate([mfcc_mean, mfcc_std])
```

## 📝 注意事项

1. **内存使用**: 处理大数据集时建议分批处理
2. **并行处理**: 使用 `--n_jobs` 参数加速
3. **磁盘空间**: 特征文件约为原始音频的 2-3 倍
4. **采样率**: 统一使用 16kHz 以保持一致性

## 🤝 贡献

如需添加新数据集支持或改进特征提取，请：

1. 在 `preprocess_common.py` 中添加新的处理方法
2. 更新本文档
3. 添加测试用例

---

*Hulk 🟢 — 密度即价值*
