# 2026-04-02 — 数据集预处理脚本创建

**任务**: [cron] 处理 AISHELL 和其他数据集：清洗、分割、特征提取

**执行者**: Hulk 🟢

**时间**: 2026-04-02 19:18 UTC

---

## 完成内容

创建了完整的语音数据集预处理工具集，包含以下脚本：

### 核心脚本

| 文件 | 功能 | 行数 |
|------|------|------|
| `scripts/preprocess_aishell.py` | AISHELL-1 专用预处理 | ~280 行 |
| `scripts/preprocess_common.py` | 通用数据集预处理 (LibriSpeech, Common Voice, THCHS-30) | ~380 行 |
| `scripts/feature_extractor.py` | 高级特征提取工具 | ~280 行 |
| `scripts/data_augmentation.py` | 数据增强 (噪声/速度/音高/混响/增益) | ~280 行 |
| `scripts/split_dataset.py` | 数据集分割 (随机/分层/说话人独立/时长平衡) | ~300 行 |
| `scripts/run_pipeline.sh` | 完整流程编排脚本 | ~180 行 |

### 配置文件

- `scripts/configs/feature_config.json` — 特征提取配置
- `scripts/configs/augmentation_config.json` — 数据增强配置
- `scripts/requirements.txt` — Python 依赖

### 文档

- `scripts/README.md` — 完整使用文档

---

## 功能特性

### 数据清洗
- 音频格式验证 (采样率/位深/声道数)
- 时长过滤 (0.3s - 30s)
- 损坏文件检测
- 转录文本对齐检查

### 特征提取
- MFCC (13 维 + delta + delta-delta)
- Log Mel Spectrogram (40 维)
- Chroma, Spectral Contrast, Tonnetz
- ZCR, RMS, Spectral Centroid/Rolloff
- 全局统计量计算 (mean/std/min/max)
- 特征标准化支持

### 数据增强
- 背景噪声注入 (可配置 SNR)
- 速度扰动 (0.9x, 1.0x, 1.1x)
- 音高变换 (±2 半音)
- 混响效果
- 增益变化 (±5 dB)
- 时间拉伸

### 数据集分割
- 随机分割
- 分层分割 (按说话人)
- 说话人独立分割 (训练/测试说话人不重叠)
- 时长平衡分割

---

## 使用示例

```bash
# 完整流程 - AISHELL-1
./scripts/run_pipeline.sh \
    --dataset aishell \
    --data_dir /data/AISHELL-1 \
    --output_dir /data/processed/aishell \
    --augment \
    --split_method stratified

# 单独特征提取
python scripts/feature_extractor.py \
    --input_dir /data/wav \
    --output_dir /data/features \
    --compute_global_stats \
    --normalize
```

---

## 输出结构

```
output/
├── processed/
│   ├── wav/          # 清洗后的音频
│   ├── features/     # 提取的特征 (.npz)
│   └── metadata/     # 元数据 (JSON + CSV)
├── augmented/        # 增强数据
├── splits/           # 数据集划分
└── processing_report.json
```

---

## 验证等级

| 项目 | 等级 | 说明 |
|------|------|------|
| 脚本语法正确性 | V3 | 静态检查通过 |
| 功能完整性 | V3 | 覆盖清洗/特征/增强/分割 |
| 文档完整性 | V3 | README + 配置示例 |
| 实际运行测试 | V0 | 待实际数据验证 |

---

## 下一步

1. **V4 验证**: 使用实际 AISHELL-1 数据运行完整流程
2. **性能优化**: 添加多进程/分布式支持
3. **质量检查**: 添加音频质量评估模块
4. **可视化**: 添加特征分布可视化工具

---

## 相关文件

- 实验设计：`research/paper/2026-04-02-multi-agent-scorer-experiment-design.md`
- 标注协议：`research/experiments/exp-001-annotation-protocol.md`
- Backlog: `memory/research-backlog.md`

---

*Hulk 🟢 — 密度即价值*
