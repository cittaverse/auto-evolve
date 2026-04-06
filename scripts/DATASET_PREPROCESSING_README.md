# 数据集预处理 Pipeline v3.0

**Cron 任务**: #7744d4c5 - 数据集预处理  
**维护者**: Hulk 🟢  
**最后更新**: 2026-04-02

---

## 快速开始

```bash
# 完整处理所有数据集
bash scripts/dataset_preprocess_v3.sh

# 仅处理 AISHELL
bash scripts/dataset_preprocess_v3.sh aishell

# 仅处理老年语音
bash scripts/dataset_preprocess_v3.sh elderly

# 验证处理结果
bash scripts/dataset_preprocess_v3.sh validate

# 重新处理（覆盖已有数据）
bash scripts/dataset_preprocess_v3.sh aishell --reprocess
```

---

## 功能特性

### 1. 音频清洗
- ✅ 重采样到 16kHz（统一采样率）
- ✅ 音量归一化（RMS 标准化）
- ✅ 单声道转换
- ✅ 格式统一（WAV）

### 2. 数据集分割
- ✅ 80% 训练集 / 10% 验证集 / 10% 测试集
- ✅ 随机种子固定（seed=42，可复现）
- ✅ 分层抽样（保持说话者分布）

### 3. 特征提取
提取的声学特征：

| 特征 | 维度 | 说明 |
|------|------|------|
| MFCC | 13 | 梅尔频率倒谱系数，语音识别核心特征 |
| Mel 频谱 | 40 | 梅尔尺度频谱图 |
| Spectral Contrast | 7 | 频谱对比度 |
| Zero Crossing Rate | 1 | 过零率 |
| Chroma | 12 | 色度特征 |

**总特征维度**: 73 维（每帧统计均值 + 标准差）

### 4. 标注加载
- ✅ 支持 AISHELL 格式标注
- ✅ 自动关联音频 ID 与文本
- ✅ 无标注时留空字段（不影响特征提取）

---

## 输出结构

```
data/processed/
├── audio/                      # 标准化音频文件
│   ├── BAC009S0757W0261_norm.wav
│   └── ...
├── train/
│   └── manifest.jsonl          # 训练集清单
├── val/
│   └── manifest.jsonl          # 验证集清单
├── test/
│   └── manifest.jsonl          # 测试集清单
├── features/
│   ├── train/                  # 训练集特征 (.npz)
│   ├── val/                    # 验证集特征 (.npz)
│   └── test/                   # 测试集特征 (.npz)
├── processing_report.json      # 处理报告
└── validation_report.json      # 验证报告
```

### Manifest 格式

每行一个 JSON 对象：

```json
{
  "audio_path": "/path/to/audio.wav",
  "audio_id": "BAC009S0757W0261",
  "duration": 4.643,
  "transcript": "人工智能将改变世界",
  "language": "zh-CN",
  "split": "train"
}
```

### 特征文件格式

`.npz` 文件包含：

- `mfcc_mean`: 13 维 MFCC 均值
- `mfcc_std`: 13 维 MFCC 标准差
- `mel_mean`: 40 维 Mel 频谱均值
- `mel_std`: 40 维 Mel 频谱标准差
- `contrast_mean`: 7 维频谱对比度均值
- `zcr_mean`: 过零率均值
- `chroma_mean`: 12 维色度均值
- `duration`: 音频时长（秒）
- `sample_rate`: 采样率

---

## 支持的数据集

### AISHELL-1
- **语言**: 中文普通话
- **说话者**: 400 人
- **音频文件**: ~17,000 条
- **总时长**: ~178 小时
- **许可**: 开源可商用

### 老年语音数据集
- **语言**: 中文（方言混合）
- **年龄段**: 60+ 岁
- **音频文件**: ~8,500 条
- **场景**: 日常对话、回忆叙述

---

## 依赖安装

### Python 依赖

```bash
pip install librosa soundfile numpy pandas matplotlib scipy tqdm
```

### 系统依赖

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg libsndfile1
```

**验证安装:**
```bash
python3 -c "import librosa, soundfile, numpy, pandas, matplotlib, scipy; print('✓ 所有依赖已安装')"
```

---

## Cron 配置

### 每周日凌晨 2 点执行

```bash
# 编辑 crontab
crontab -e

# 添加任务
0 2 * * 0 cd /Users/moondy/.openclaw/workspace-hulk && bash scripts/dataset_preprocess_v3.sh >> output/cron_dataset.log 2>&1
```

### 每日轻量级处理（预览）

```bash
# 每日凌晨 3 点处理 1000 个样本
0 3 * * * cd /Users/moondy/.openclaw/workspace-hulk && python3 scripts/preprocess_audio_datasets.py --dataset aishell --limit 1000 >> output/cron_lite.log 2>&1
```

---

## 标注文件获取

### AISHELL 标注

标注文件应放置在：
```
data_aishell/transcript/aishell_transcript_v0.8.txt
```

**获取方式:**

1. **OpenSLR** (推荐)
   - 访问：https://www.openslr.org/33/
   - 下载：`data_aishell.tgz` (包含音频 + 标注)

2. **GitHub 镜像**
   - 搜索：`AISHELL-1 transcript`
   - 下载：`aishell_transcript_v0.8.txt`

3. **联系 AISHELL**
   - 学术：aishell.foundation@gmail.com
   - 商业：bd@aishelldata.com

### 重新加载标注

下载标注后重新处理：
```bash
bash scripts/dataset_preprocess_v3.sh aishell --reprocess
```

---

## 验证与调试

### 验证处理结果

```bash
bash scripts/dataset_preprocess_v3.sh validate
```

输出示例：
```
✅ 验证处理结果
========================================
  ✓ 音频文件：12970
  ✓ train manifest: 10376 条
  ✓ val manifest: 1297 条
  ✓ test manifest: 1297 条
  ✓ 特征文件：10376
  ✓ 标注加载：10376 条

  ✅ 所有检查通过
```

### 查看处理报告

```bash
cat data/processed/processing_report.json | python3 -m json.tool
cat data/processed/validation_report.json | python3 -m json.tool
```

### 常见问题

**Q: 特征提取失败**
```
A: 检查 ffmpeg 是否安装
   brew install ffmpeg  # macOS
   sudo apt-get install ffmpeg  # Ubuntu
```

**Q: 内存不足**
```
A: 分批处理或增加 swap
   或使用 --limit 参数限制单次处理数量
```

**Q: 标注未加载**
```
A: 检查标注文件路径和格式
   确认文件位于 data_aishell/transcript/aishell_transcript_v0.8.txt
   格式应为：音频 ID 空格 文本
```

---

## 性能参考

| 数据集 | 文件数 | 处理时间 | 特征提取 |
|--------|--------|----------|----------|
| AISHELL 全量 | ~17,000 | 30-60 分钟 | 20-40 分钟 |
| AISHELL 预览 | 1,000 | ~1 分钟 | ~30 秒 |
| 老年语音 | ~8,500 | 15-30 分钟 | 10-20 分钟 |

*基于 M1 Mac, 16GB RAM*

---

## 扩展开发

### 添加新数据集

1. 在 `preprocess_audio_datasets.py` 中添加处理方法
2. 继承 `AudioPreprocessor` 类
3. 实现 `process_xxx()` 方法
4. 在 `main()` 中注册

### 添加新特征

```python
def extract_custom_features(self, y, sr):
    # 提取自定义特征
    feature = your_feature_extraction(y, sr)
    return feature
```

### 数据增强

```python
# 添加噪声
y_noisy = y + noise * alpha

# 速度变化
y_stretched = librosa.effects.time_stretch(y, rate=1.1)

# 音高变化
y_pitched = librosa.effects.pitch_shift(y, sr=sr, n_steps=2)
```

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v3.0 | 2026-04-02 | 重构为独立脚本，完善特征提取 |
| v2.0 | 2026-03-28 | 添加老年语音支持 |
| v1.0 | 2026-03-25 | 初始版本 (AISHELL) |

---

## 联系

**执行者**: Hulk 🟢  
**项目**: CittaVerse - 语音数据处理 Pipeline  
**文档**: `scripts/DATASET_PREPROCESSING_README.md`
