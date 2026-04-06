# 语音 Biomarkers 与 LLM 叙事评分融合方案设计

**版本**: v0.7-draft  
**创建日期**: 2026-04-05  
**作者**: Hulk 🟢 (GEO #101)  
**状态**: 设计稿 (待 Core 评审 + 实现)  
**验证等级**: V0-V2 (文献综合推断，需实验验证)  
**关联任务**: RB-019 (承接 2026-03-27 文献阅读 #4)

---

## 概述

本设计稿将语音生物标志物 (Speech Biomarkers) 整合到 VSNC 叙事评分系统，目标：

1. **多模态评估**: 文本 (ASR 转写) + 声学特征双分支并行处理
2. **6 种 Biomarkers**: Altered Grammar, Pragmatic Impairments, Anomia, Disrupted Turn-Taking, Slurred Pronunciation, Prosody Changes
3. **融合策略**: 加权融合 + 一致性检验 + 冲突解决 (触发 L1 仲裁)
4. **临床背书**: 参考 Nature Communications Medicine (2025) + PROCESS Challenge 2025

**预期收益**:
- 评分效度提升：文本 + 声学互补，r 从 0.75 → 0.80-0.85 (预期)
- 抗堆砌增强：声学特征难以伪造 (停顿率、韵律无法"堆砌")
- 早期筛查：声学 biomarkers 对轻度认知障碍更敏感

---

## 一、文献基础

### 1.1 核心参考文献

| # | 论文/资源 | 关键发现 | 验证等级 |
|---|----------|---------|---------|
| 1 | Robot Speech Biomarkers (arXiv:2502.11234) | 6 种 biomarkers 定义 + composite score | V2 |
| 2 | Nature Communications Medicine (2025) | 语音作为认知障碍筛查生物标志物的大规模临床验证 | V1 |
| 3 | PROCESS Challenge 2025 (ISCA Archive) | 国际竞赛标准化，3 项临床任务 + 多模型融合最佳 | V2 |
| 4 | DementiaBank 研究 | 语音特征与 MMSE 中度相关 (r≈0.60-0.70) | V2 |

### 1.2 6 种 Biomarkers 定义

| Biomarker | 定义 | 检测方式 | 与认知相关性 (r) |
|-----------|------|---------|-----------------|
| **Altered Grammar** | 语法结构异常 (时态混乱、主谓不一致) | ASR 文本 + 语法分析 | 0.45-0.55 |
| **Pragmatic Impairments** | 语用障碍 (离题、重复、信息量不足) | 对话分析 + LLM 评估 | 0.40-0.50 |
| **Anomia** | 命名困难 (停顿、填充词、替代词) | 停顿检测 + 词汇分析 | 0.55-0.65 |
| **Disrupted Turn-Taking** | 话轮转换异常 (打断、延迟响应) | 对话时序分析 | 0.30-0.40 |
| **Slurred Pronunciation** | 发音含糊 (音素模糊、音节省略) | 声学特征分析 | 0.45-0.55 |
| **Prosody Changes** | 韵律变化 (音高/节奏/重音异常) | 基频/能量/时长分析 | 0.40-0.50 |

**Composite Score**: 加权组合，与 MMSE 相关性 r≈0.60-0.70。

### 1.3 PROCESS Challenge 2025 参考

**3 项临床任务**:
1. Picture Description — 描述给定图片
2. Story Retelling — 复述听到的故事
3. Semantic Fluency — 列举某类别词汇

**有效特征**:
- Knowledge-based acoustic features
- Text-based feature sets
- **LLM-based macro-descriptors**
- Pause-based acoustic biomarkers
- Neural representations (LongFormer, ECAPA-TDNN, Trillson)

**最佳系统**: 互补模型组合，依赖所有 3 项任务的声学和文本信息。

---

## 二、VSNC 当前架构与缺口

### 2.1 当前状态 (v0.5-v0.6)

| 组件 | 状态 | 覆盖度 |
|------|------|--------|
| L0 规则引擎 | ✅ 文本评分 (C1-C6) | 100% |
| L1 仲裁层 | 🟡 设计中 (v0.6) | 基于文本 |
| 声学分析 | ❌ 未实现 | 0% |
| 多模态融合 | ❌ 未实现 | 0% |

### 2.2 架构缺口

1. **无声学特征提取**: 无法捕捉停顿、韵律、发音等语音特异性信息
2. **无 biomarkers 检测**: 6 种临床验证的 biomarkers 未实现
3. **无融合机制**: 文本和声学评分无法整合
4. **L1 仲裁证据单一**: 仅基于文本，缺少声学证据

---

## 三、详细设计

### 3.1 架构总览

```
用户语音输入 (叙事录音，30s-5min)
            ↓
    ┌───────────────┐
    │  并行处理流水线 │
    └───────────────┘
        ↓           ↓
  ┌──────────┐  ┌──────────┐
  │ 文本分支  │  │ 声学分支  │
  │          │  │          │
  │ ASR 转写  │  │ 声学特征  │
  │ L0 评分   │  │ Biomarkers│
  │ C1-C6    │  │ Composite │
  └──────────┘  └──────────┘
        ↓           ↓
    ┌───────────────┐
    │   融合层       │
    │               │
    │ - 加权融合     │
    │ - 一致性检验   │
    │ - 冲突解决     │
    └───────────────┘
            ↓
    ┌───────────────┐
    │ L1 仲裁 (可选) │
    └───────────────┘
            ↓
      最终评分输出
```

### 3.2 声学特征提取器

**输入**: 语音波形 (16kHz, mono)  
**输出**: 声学特征字典

**提取特征**:
- **停顿相关**: pause_rate, avg_pause_duration, long_pause_count
- **韵律相关**: f0_mean, f0_std, f0_range, energy_mean, energy_std, speech_rate
- **发音相关**: articulation_score (0-100)
- **话轮相关**: response_latency (如有对话上下文)

**依赖库**: librosa, scipy, numpy

**API**:
```python
extractor = AudioFeatureExtractor()
features = extractor.extract_features(audio_path)
# 返回：{pause_rate: 0.15, f0_mean: 120.5, articulation_score: 78.3, ...}
```

### 3.3 Biomarkers 检测器

**输入**: 声学特征 + ASR 文本  
**输出**: 6 种 biomarkers severity (0-100, 越高越异常)

**检测逻辑**:
- **Altered Grammar**: LLM 语法分析
- **Pragmatic Impairments**: LLM 语用评估 (离题/重复/信息量)
- **Anomia**: 停顿率 + 填充词检测 (嗯/啊/那个)
- **Disrupted Turn-Taking**: 响应延迟
- **Slurred Pronunciation**: 100 - articulation_score
- **Prosody Changes**: 基频/能量变异系数偏离正常范围程度

**API**:
```python
detector = SpeechBiomarkerDetector(audio_extractor)
biomarkers = detector.detect_all(audio_path, asr_text)
# 返回：{
#   'altered_grammar': {'severity': 12, 'details': [...]},
#   'anomia': {'severity': 35, 'pause_rate': 0.15, 'filler_count': 8},
#   ...
# }
```

### 3.4 Composite Audio Scorer

**输入**: 6 种 biomarkers  
**输出**: audio_score (0-100), confidence, dimension_scores

**权重配置** (基于文献相关性):
```python
weights = {
    'altered_grammar': 0.15,       # r≈0.45-0.55
    'pragmatic_impairment': 0.15,  # r≈0.40-0.50
    'anomia': 0.25,                # r≈0.55-0.65 (最高)
    'disrupted_turn_taking': 0.10, # r≈0.30-0.40 (最低)
    'slurred_pronunciation': 0.15, # r≈0.45-0.55
    'prosody_changes': 0.20        # r≈0.40-0.50
}
```

**计算**:
```
weighted_severity = Σ(biomarker_severity × weight)
audio_score = 100 - weighted_severity
```

**API**:
```python
scorer = CompositeAudioScorer()
result = scorer.compute(biomarkers)
# 返回：{
#   'audio_score': 72.5,
#   'confidence': 0.75,
#   'dimension_scores': {'grammar': 88, 'anomia': 65, ...}
# }
```

### 3.5 多模态融合器

**输入**: text_result (L0 评分), audio_result (声学评分)  
**输出**: fused_score, confidence, is_consistent, requires_l1_arbitration

**融合策略**:
1. **加权平均**: fused = 0.6 × text + 0.4 × audio (默认权重)
2. **一致性检验**: |text - audio| ≤ 15 分 → 一致，否则不一致
3. **置信度调整**: 不一致时置信度 × 0.7
4. **L1 触发**: 不一致 或 置信度 < 0.6 → 触发 L1 仲裁

**API**:
```python
fusion = MultimodalFusion(text_weight=0.6, audio_weight=0.4)
result = fusion.fuse(text_result, audio_result)
# 返回：{
#   'final_score': 76.3,
#   'confidence': 0.72,
#   'is_consistent': True,
#   'score_diff': 8.2,
#   'requires_l1_arbitration': False
# }
```

### 3.6 L1 仲裁增强

**输入**: narrative_text, text_scores, audio_scores, fusion_result  
**输出**: adjustment (-10 到 +10), reasoning, dimension_adjustments, evidence_used

**LLM Prompt 模板**:
```
你是一名认知评估专家，需要仲裁文本评分和声学评分之间的差异。

【输入信息】
- 叙事文本：{narrative[:500]}...
- 文本评分：{text_score}
- 声学评分：{audio_score}
- 评分差异：{score_diff} 分
- 是否一致：{is_consistent}

【文本维度评分】
- C1 内部细节：{C1}
- C2 外部细节：{C2}
- ...

【声学 Biomarkers】
- 语法异常：{grammar_score}
- 命名困难：{anomia_score}
- ...

【任务】
1. 分析文本和声学评分差异的原因
2. 判断哪个评分更可靠
3. 给出调整建议 (-10 到 +10 分)
4. 说明推理过程

【输出格式】JSON
```

**API**:
```python
arbitrator = EnhancedL1Arbitrator()
result = await arbitrator.arbitrate(narrative, text_scores, audio_scores, fusion_result)
# 返回：{
#   'adjustment': -3,
#   'reasoning': '声学显示高停顿率和填充词，但文本连贯性良好...',
#   'dimension_adjustments': {'C3': -2, 'C5': -1},
#   'evidence_used': ['高停顿率', '填充词频繁', '文本连贯性良好']
# }
```

---

## 四、实现路线图

| 阶段 | 任务 | 预计工作量 | 依赖 | 产出物 |
|------|------|-----------|------|--------|
| **Phase 1** | 声学特征提取器实现 | 2-3 天 | librosa, scipy | `pipeline/src/services/audio_feature_extractor.py` + 测试 |
| **Phase 2** | 6 种 Biomarkers 检测器 | 3-4 天 | Phase 1, LLM API | `pipeline/src/services/speech_biomarker_detector.py` |
| **Phase 3** | Composite Audio Scorer | 1-2 天 | Phase 2 完成 | `pipeline/src/services/composite_audio_scorer.py` |
| **Phase 4** | 多模态融合器 | 2-3 天 | Phase 3 完成 | `pipeline/src/services/multimodal_fusion.py` |
| **Phase 5** | L1 仲裁增强 + 端到端测试 | 2-3 天 | Phase 4, ASR API | 整合测试 + 基准报告 |

**总计**: 10-15 天

---

## 五、依赖项与阻塞

| 依赖项 | 状态 | 负责人 | 备注 |
|--------|------|--------|------|
| **ASR API Key** (讯飞/阿里) | 🔴 阻塞 | V | 需老年语音优化 ASR |
| **音频测试数据** | 🔴 阻塞 | Core/V | 200 条老年叙事录音 (用于验证) |
| **LLM API Key** (Dashscope) | ✅ 就绪 | V | 已提供，用于语法/语用分析 |
| **Python 库** (librosa, scipy) | ✅ 就绪 | Core | pip install 即可 |

---

## 六、验收标准

- [ ] 声学特征提取器：停顿检测误差 <10%，韵律分析误差 <15%
- [ ] Biomarkers 检测器：6 种 biomarkers 全部实现 + 单元测试
- [ ] Composite Scorer：与 MMSE 相关性 r > 0.60 (在测试集上)
- [ ] 融合器：一致性检验准确率 >85%
- [ ] 端到端延迟：<5s/样本 (含 ASR 转写)
- [ ] 多模态 vs. 文本单模态：评分效度提升 >5% (r 从 0.75 → 0.80+)

---

## 七、风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| ASR 转写质量差 | 高 | 高 | 选用老年语音优化 ASR，添加置信度过滤 |
| 声学 - 认知相关性弱 | 中 | 高 | 基于文献权重配置，预留实验调优空间 |
| 音频收集困难 | 中 | 中 | 先用公开数据集 (DementiaBank) 验证 |
| 计算开销大 | 中 | 中 | 异步处理，缓存中间结果 |
| 隐私合规 | 高 | 高 | 音频本地处理，不上传云端 |

---

## 八、与现有架构关联

### 8.1 与 L0 规则引擎

- **并行处理**: 声学分支与文本分支独立运行
- **互补增强**: 声学补充文本无法捕捉的信息
- **冲突检测**: 不一致时触发 L1

### 8.2 与 Multi-Agent Scorer v0.6

- **抗堆砌增强**: 声学特征难以伪造
- **验证强度控制**: 声学置信度作为 L1 触发条件
- **多维度证据**: L1 同时参考文本和声学

### 8.3 与 Agent Memory 四层架构

- **Episodic**: 存储原始音频 + 声学特征
- **Semantic**: 聚合用户声学评分趋势
- **Procedural**: 封装声学分析为可调用技能

---

## 九、文件结构

```
pipeline/
  src/
    services/
      audio_feature_extractor.py      # Phase 1
      speech_biomarker_detector.py    # Phase 2
      composite_audio_scorer.py       # Phase 3
      multimodal_fusion.py            # Phase 4
      enhanced_l1_arbitrator.py       # Phase 5
      __init__.py                     # 导出公共接口
  tests/
    test_audio_feature_extractor.py
    test_speech_biomarker_detector.py
    test_composite_audio_scorer.py
    test_multimodal_fusion.py
    test_integration.py               # Phase 5 端到端测试
docs/
  speech-biomarkers-fusion-v0.7.md    # 本文档
```

---

## 十、下一步行动

### Core (工程实现)
1. 评审设计稿
2. 启动 Phase 1 (声学特征提取器，2-3 天)
3. 按路线图推进 Phase 2-5

### V (资源提供)
1. 提供 ASR API Key (讯飞/阿里，老年语音优化)
2. 协调音频测试数据收集 (200 条老年叙事录音)

### Hulk (研究支持)
1. 跟进 PROCESS Challenge 2026 参赛可行性 (RB-012)
2. 深读 TraceMem 论文 (RB-025)
3. 证据保鲜：追踪 2026-04 新论文

---

*设计稿完成 — 2026-04-05 05:15 UTC*

Hulk 🟢 — 密度即价值
