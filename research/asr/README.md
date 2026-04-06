# ASR 基准测试目录

本目录包含"一念万相"项目的 ASR (自动语音识别) 基准测试工具和结果。

## 文件结构

```
research/asr/
├── README.md                          # 本文件
├── asr_benchmark_2026-03-26.md        # 基准测试报告 (v1, 10 样本)
├── asr_benchmark_2026-03-26_v2.md     # 基准测试报告 (v2, 20 样本)
├── benchmark_eval.py                  # WER/CER 评估工具 (纯 Python 实现)
├── mock_samples.csv                   # Mock 测试样本 (v1, 10 样本)
├── mock_samples_v2.csv                # Mock 测试样本 (v2, 20 样本)
├── results.json                       # 测试结果 (v1)
└── results_v2.json                    # 测试结果 (v2)
```

## 使用方法

### 单样本测试

```bash
cd /home/node/.openclaw/workspace-hulk/research/asr
python3 benchmark_eval.py -r "参考文本" -p "ASR 输出"
```

示例:
```bash
python3 benchmark_eval.py -r "今天天气真好" -p "今天天气真好"
python3 benchmark_eval.py -r "今天天气真好" -p "今天天气真号" -d
```

### 批量测试

```bash
python3 benchmark_eval.py -b mock_samples.csv -o results.json
```

### CSV 格式

```csv
id,reference,hypothesis,audio_file
001，今天天气真好，今天天气真好，file1.wav
002，我小时候住在杭州，我小时候住在杭州，file2.wav
```

## 评估指标

- **WER (Word Error Rate)**: 词错误率
- **CER (Character Error Rate)**: 字错误率 (中文更常用)

计算公式:
```
Error Rate = (S + D + I) / N
```
- S = Substitution (替换)
- D = Deletion (删除)
- I = Insertion (插入)
- N = 参考文本总长度

## 当前状态

- ✅ Mock 测试框架完成
- ✅ WER/CER 计算工具完成 (纯 Python，无外部依赖)
- ✅ v1 测试完成 (10 样本，WER 0.59%)
- ✅ v2 测试完成 (20 样本，WER 2.18%)
- ✅ v3 测试完成 (30 样本，WER 1.48%)
- ✅ v4 测试完成 (30 样本，WER 1.48%)
- ✅ v5 测试完成 (30 样本，WER 1.48%)
- ✅ 框架可重复性验证通过 (v3/v4/v5 结果完全一致)
- ✅ v6 测试完成 (20 样本，WER 2.95%) - 2026-04-02 基准测试
- ⏳ 等待真实 ASR API 接入

## 测试结果摘要

| 版本 | 样本数 | 平均 WER | 平均 CER | 零错误率 | 报告 |
|------|--------|----------|----------|----------|------|
| v1 | 10 | 0.59% | 0.59% | 90% | `asr_benchmark_2026-03-26.md` |
| v2 | 20 | 2.18% | 2.18% | 70% | `asr_benchmark_2026-03-26_v2.md` |
| v3 | 30 | 1.48% | 1.48% | 80% | `asr_benchmark_2026-03-28_v3.md` |
| v4 | 30 | 1.48% | 1.48% | 80% | `asr_benchmark_2026-03-28_v4.md` |
| v5 | 30 | 1.48% | 1.48% | 80% | `asr_benchmark_2026-03-28_v5.md` |
| v6 | 20 | 2.95% | 2.11% | 70% | `asr_benchmark_2026-04-02_v3.md` |

## 下一步

1. 申请 ASR API Key (Google/Azure/阿里云/讯飞)
2. 在相同测试集上运行真实 ASR 测试
3. 收集老年语音样本 (60+ 岁人群)
4. 评估各 ASR 服务在老年语音场景的表现
5. 建立老年语音专属测试集 (包含年代词、方言词)

## 相关资源

- 测试音频：`/home/node/.openclaw/workspace-hulk/data/elderly_voice/data_aishell/`
- 基准报告：`asr_benchmark_2026-03-26.md`
