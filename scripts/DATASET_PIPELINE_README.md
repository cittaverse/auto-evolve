# 数据集处理 Pipeline

**版本**: v2.0  
**维护者**: Hulk 🟢  
**Cron 任务**: #7744d4c5 - 数据集预处理

---

## 快速开始

```bash
# 1. 安装依赖
pip install librosa numpy pandas soundfile tqdm matplotlib

# 2. 轻量级预览（1 分钟）
python3 scripts/preprocess_aishell_lite.py

# 3. 全量处理（30-60 分钟）
bash scripts/dataset_preprocess.sh --dataset aishell

# 4. 验证结果
bash scripts/dataset_preprocess.sh --validate
```

---

## 脚本清单

| 脚本 | 用途 | 输入 | 输出 |
|------|------|------|------|
| `preprocess_aishell_lite.py` | 轻量级预览 | 100-1000 样本 | 标准化音频 + manifest + 特征 |
| `process_all_datasets.py` | 全量处理 | 全部音频 | 完整处理结果 |
| `dataset_preprocess.sh` | Bash 包装器 | 参数化调用 | 日志 + 处理结果 |
| `download_aishell_transcripts.sh` | 标注下载 | - | aishell_transcript_v0.8.txt |
| `extract_features.py` | 特征提取 | 音频文件 | .npz 特征文件 |

---

## 处理流程

```
原始音频 → 标准化 → 分割 → 特征提取 → Manifest
   ↓          ↓         ↓          ↓           ↓
WAV 文件   16kHz     train/    MFCC/Mel   JSONL
         归一化    val/test   Contrast
```

### 步骤详解

1. **音频标准化**
   - 重采样到 16kHz
   - 音量归一化
   - 输出：`audio/*.wav`

2. **数据集分割**
   - 80% train / 10% val / 10% test
   - 随机种子：42（可复现）
   - 输出：`train/val/test/manifest.jsonl`

3. **特征提取**
   - MFCC (13 维)
   - Mel 频谱图 (40 维)
   - Spectral Contrast (7 维)
   - Zero Crossing Rate (1 维)
   - Chroma (12 维)
   - 输出：`features/train/*.npz`

---

## 输出目录结构

```
data/processed/
├── audio/                  # 标准化音频文件
├── audio_lite/             # 轻量级标准化音频
├── train/                  # 训练集
│   └── manifest.jsonl     # 训练集标注
├── train_lite/             # 轻量级训练集
├── val/                    # 验证集
│   └── manifest.jsonl     # 验证集标注
├── val_lite/               # 轻量级验证集
├── test/                   # 测试集
│   └── manifest.jsonl     # 测试集标注
├── test_lite/              # 轻量级测试集
├── features/
│   ├── train/             # 训练集特征 (.npz)
│   └── train_lite/        # 轻量级特征
├── elderly_voice/          # 老年语音数据
├── processing_report.json  # 处理报告
├── processing_report_lite.json
└── validation_report.json  # 验证报告
```

---

## Manifest 格式

```jsonl
{
  "audio_path": "/path/to/audio.wav",
  "audio_id": "BAC009S0724W0314_lite",
  "duration": 2.87,
  "transcript": "标注文本（待填充）",
  "language": "zh-CN",
  "split": "train"
}
```

---

## 使用示例

### 轻量级预览

```bash
# 处理前 100 个样本（快速验证）
python3 scripts/preprocess_aishell_lite.py

# 修改样本数
# 编辑脚本：max_samples=100 → max_samples=1000
```

### 全量处理

```bash
# AISHELL 全量
bash scripts/dataset_preprocess.sh --dataset aishell

# 老年语音全量
bash scripts/dataset_preprocess.sh --dataset elderly

# 所有数据集
bash scripts/dataset_preprocess.sh --dataset all

# 重新处理（覆盖已有）
bash scripts/dataset_preprocess.sh --dataset aishell --reprocess
```

### 仅特征提取

```bash
bash scripts/dataset_preprocess.sh --extract-features
```

### 仅验证

```bash
bash scripts/dataset_preprocess.sh --validate
```

---

## 标注文件

### 当前状态

⚠️ **标注文件缺失** - transcript 字段为空

### 获取方式

**方案 A: OpenSLR**
```bash
# 访问 https://www.openslr.org/33/
# 下载 data_aishell.tgz (15GB)
```

**方案 B: 手动放置**
```bash
# 放置到 data_aishell/transcript/aishell_transcript_v0.8.txt
```

**方案 C: 联系 AISHELL**
- 学术：aishell.foundation@gmail.com
- 企业：bd@aishelldata.com

### 重新处理（加载标注后）

```bash
python3 scripts/process_all_datasets.py --dataset aishell --reprocess
```

---

## 数据增强（TODO）

计划功能：

- [ ] 添加背景噪声（街道、办公室、家庭）
- [ ] 速度变化 (0.9x - 1.1x)
- [ ] 音高变化 (±2 半音)
- [ ] 混响效果

---

## Cron 配置

### 每周全量处理

```cron
0 2 * * 0 cd /Users/moondy/.openclaw/workspace-hulk && bash scripts/dataset_preprocess.sh --dataset all >> output/cron_dataset.log 2>&1
```

### 每日轻量级预览

```cron
0 3 * * * cd /Users/moondy/.openclaw/workspace-hulk && python3 scripts/preprocess_aishell_lite.py >> output/cron_lite.log 2>&1
```

---

## 故障排查

### 问题：缺少 Python 依赖

```bash
pip install librosa numpy pandas soundfile tqdm matplotlib
```

### 问题：缺少 ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### 问题：标注文件缺失

参考「标注文件」章节获取。

### 问题：处理超时

使用轻量级脚本：
```bash
python3 scripts/preprocess_aishell_lite.py
```

---

## 性能基准

| 数据集 | 样本数 | 处理时间 | 特征维度 |
|--------|--------|----------|----------|
| AISHELL lite | 1,000 | ~44 秒 | 73 |
| AISHELL 全量 | ~17,000 | 30-60 分钟 | 73 |
| 老年语音 | ~8,500 | 15-30 分钟 | 73 |

---

## 相关文档

- `DATASET_PREPROCESSING_COMPLETE.md` - 完整处理报告
- `AISHELL_LITE_SUMMARY.md` - 轻量级摘要
- `memory/dataset-preprocessing-*.md` - 执行日志

---

**最后更新**: 2026-03-31  
**验证等级**: V4 (动态验证完成)
