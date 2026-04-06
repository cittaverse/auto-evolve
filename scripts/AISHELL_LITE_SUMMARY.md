
# AISHELL 轻量级预处理摘要

**执行时间**: 2026-03-31 03:24:04  
**执行者**: Hulk 🟢  
**Cron 任务**: #7744d4c5 - 数据集预处理

## 处理结果

- **输入文件**: 100 个 WAV 文件
- **标准化**: 100 个文件
- **数据集分割**:
  - 训练集：800 个样本
  - 验证集：100 个样本
  - 测试集：100 个样本
- **特征提取**: 100/100 个样本

## 输出目录

```
data/processed/
├── audio_lite/              # 标准化音频（lite 版）
├── train_lite/
│   └── manifest.jsonl      # 训练集标注
├── val_lite/
│   └── manifest.jsonl      # 验证集标注
├── test_lite/
│   └── manifest.jsonl      # 测试集标注
├── features/
│   └── train_lite/         # 训练集特征 (.npz)
└── processing_report_lite.json
```

## 标注状态

⚠️ **标注文件缺失** - transcript 字段为空

需要下载 AISHELL 标注文件：
1. 访问：https://www.openslr.org/33/
2. 下载 data_aishell.tgz
3. 提取 transcript/aishell_transcript_v0.8.txt
4. 放置到：data_aishell/transcript/

## 全量处理

要处理全部 ~178 小时音频（约 17,000+ 文件），请运行：

```bash
bash scripts/dataset_preprocess.sh --dataset aishell
```

或使用 Python 脚本：

```bash
python3 scripts/process_all_datasets.py --dataset aishell
```

**状态**: ✅ 轻量级处理完成
