# 2026-04-04 — 数据集预处理流水线 v2 (Cron 任务)

**任务**: [cron:7744d4c5-a091-48f8-8128-9b71fcbba4f4] 处理 AISHELL 和其他数据集：清洗、分割、特征提取。脚本存入 scripts/。

**执行者**: Hulk 🟢

**时间**: 2026-04-04 19:16 UTC

**状态**: ✅ 脚本创建完成，待实际运行

---

## 完成内容

### 新增脚本

| 文件 | 功能 | 状态 |
|------|------|------|
| `scripts/preprocess_aishell_v2.py` | AISHELL 完整预处理 (清洗 + 分割 + 特征) | ✅ 完成 |
| `scripts/fix_aishell_transcript.py` | 标注文件修复 (从 HuggingFace 下载) | ✅ 完成 |
| `scripts/dataset_pipeline_v2.sh` | 流程编排脚本 | ✅ 完成 |
| `scripts/DATASET_PREPROCESSING_PIPELINE.md` | 完整文档 | ✅ 完成 |

### 已有脚本 (复用)

| 文件 | 功能 |
|------|------|
| `scripts/feature_extractor.py` | 高级特征提取 (108 维) |
| `scripts/data_augmentation.py` | 数据增强 (噪声/速度/音高) |
| `scripts/split_dataset.py` | 数据集分割工具 |
| `scripts/validate_dataset.py` | 质量验证工具 |

---

## 关键修复

### 1. 标注文件修复

**问题**: `aishell_transcript_v0.8.txt` 被下载为 HTML 格式

**解决**: 
- 创建 `fix_aishell_transcript.py` 自动从 HuggingFace 下载正确标注
- URL: `https://huggingface.co/datasets/AISHELL/AISHELL-1/raw/main/data_aishell/transcript/aishell_transcript_v0.8.txt`
- 已验证：141,600 条标注

### 2. librosa API 兼容性

**问题**: `librosa.output.write_wav` 在新版中已移除

**解决**: 改用 `soundfile.write()`

---

## 功能特性

### 数据清洗
- ✅ 音频格式验证 (采样率/位深/声道数)
- ✅ 时长过滤 (0.3s - 20s)
- ✅ 损坏文件检测
- ✅ 音量归一化

### 特征提取
- ✅ MFCC (13 维 + delta + delta-delta)
- ✅ Log Mel Spectrogram (40 维)
- ✅ Chroma (12 维)
- ✅ Spectral Contrast (7 维)
- ✅ Tonnetz (6 维)
- ✅ ZCR, RMS, Spectral Centroid/Rolloff
- ✅ 全局统计量 (mean/std/min/max)

### 数据集分割
- ✅ 随机分割 (80/10/10)
- ✅ 分层分割 (按说话人)
- ⏳ 说话人独立分割 (待测试)
- ⏳ 时长平衡分割 (待测试)

### 数据增强
- ⏳ 背景噪声注入 (脚本存在，待集成)
- ⏳ 速度扰动 (脚本存在，待集成)
- ⏳ 音高变换 (脚本存在，待集成)

---

## 使用方法

### 轻量级预览 (推荐先测试)

```bash
cd /Users/moondy/.openclaw/workspace-hulk
bash scripts/dataset_pipeline_v2.sh --dataset aishell --mode lite
```

输出：
- 1,000 样本
- ~2 分钟
- `data/processed_aishell_lite/`

### 完整处理

```bash
bash scripts/dataset_pipeline_v2.sh --dataset aishell --mode full
```

输出：
- 12,971 样本
- ~30-60 分钟
- `data/processed_aishell_v2/`

---

## 输出结构

```
data/processed_aishell_v2/
├── audio/              # 标准化音频
├── features/
│   ├── train/
│   ├── val/
│   └── test/
├── train/manifest.jsonl
├── val/manifest.jsonl
├── test/manifest.jsonl
├── processing_report.json
└── quality_report.md
```

---

## 验证等级

| 项目 | 等级 | 说明 |
|------|------|------|
| 脚本语法 | V3 | Python 语法检查通过 |
| 依赖安装 | V3 | librosa, soundfile, numpy, tqdm 已验证 |
| 标注下载 | V4 | 实际测试成功 (141,600 条) |
| lite 模式 | V1 | 流程跑通，因 librosa 输出问题需重试 |
| full 模式 | V0 | 待实际运行 |

---

## 已知限制

1. **多进程**: 当前为单进程，全量处理需 30-60 分钟
2. **数据增强**: 脚本存在但未集成到主流程
3. **其他数据集**: LibriSpeech/Common Voice/THCHS-30 待实现

---

## 下一步行动

### P0 - 立即执行

1. **运行 lite 模式验证**
   ```bash
   bash scripts/dataset_pipeline_v2.sh --dataset aishell --mode lite
   ```

2. **验证输出质量**
   ```bash
   python scripts/validate_dataset.py data/processed_aishell_lite
   ```

### P1 - 后续优化

3. **添加多进程支持**
   - 使用 `multiprocessing` 或 `joblib`
   - 目标：全量处理 <10 分钟

4. **集成数据增强**
   - 在主流程中添加 `--augment` 选项
   - 生成 3x 扩充数据

5. **扩展数据集支持**
   - LibriSpeech
   - Common Voice (中文)
   - 老年语音全量处理

---

## Cron 任务信息

- **Job ID**: `7744d4c5-a091-48f8-8128-9b71fcbba4f4`
- **名称**: `hulk-🔬-数据集预处理`
- **状态**: 脚本就绪，待执行
- **下次运行**: 按 cron 调度

---

## 相关文档

- 完整文档：`scripts/DATASET_PREPROCESSING_PIPELINE.md`
- 配置：`scripts/configs/feature_config.json`
- 历史日志：`memory/dataset-preprocessing-*.md`

---

*Hulk 🟢 — 密度即价值*
