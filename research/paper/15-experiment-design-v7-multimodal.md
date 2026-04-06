# 实验设计方案 v7.0 (多模态融合版)

**版本**: v7.0 (2026-04-05 Multimodal Update)  
**日期**: 2026-04-05 17:45 UTC  
**作者**: Hulk 🟢  
**验证等级**: V2-V3 (文献综合 + 静态复核 — 整合 v6.0 + GEO #101 语音 Biomarkers 融合设计)  
**用途**: arXiv 论文 Section 3 (Methods) 补充材料 + 多模态验证实验设计 + Core 实现参考

---

## 执行摘要

本方案在 v6.0 基础上进行关键扩展：**整合语音 Biomarkers 与 LLM 叙事评分的多模态融合设计** (GEO #101, RB-019)。

### 核心更新概览

| 维度 | v6.0 | v7.0 | 更新理由 |
|------|------|------|----------|
| **验证层次** | 6 层 (L1a-L1d, L2, L3) | **7 层 (+L1e)** | 多模态融合需独立效度验证 |
| **评分模态** | 文本单模态 | **文本 + 声学双模态** | 语音 biomarkers 提供互补证据 |
| **变量控制** | 5 层 (含抗堆砌) | **6 层 (+声学质控)** | 音频质量影响 biomarker 检测 |
| **对比组** | L0 vs. L0+L1 | **+ 单模态 vs. 多模态** | 量化多模态增量价值 |
| **评估指标** | 抗堆砌效度 | **+ 多模态效度 + 声学 biomarkers** | 验证融合策略有效性 |
| **样本量** | N=200 (L1d) | **N=300 (+100 多模态验证)** | 多模态亚组分析需求 |

---

## 1. 验证层次扩展 (Six → Seven Layers)

### 1.1 七层验证体系总览

```
┌─────────────────────────────────────────────────────────────────┐
│                  七层验证体系 (Seven-Layer Validation)           │
├─────────────────────────────────────────────────────────────────┤
│ L1a → Mock 测试         → 算法正确性          → ✅ 已完成 (V4)  │
│ L1b → Benchmark 验证     → 评分一致性          → 🟡 待执行      │
│ L1c → 事件边界检测       → 事件提取准确率       → 🟡 待执行      │
│ L1d → 多 Agent 效度验证  → L0+L1 vs. L0 单独   → 🟡 设计中      │
│ L1e → 多模态效度验证     → 文本 + 声学 vs. 文本  → 🟢 新增 (v7.0)│
│ L2  → Pilot RCT          → 临床有效性          → 🟡 待执行      │
│ L3  → A/B 测试           → 元记忆策略增量价值   → 🟡 待执行      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 L1e 多模态效度验证设计 (新增)

#### 1.2.1 核心假设

| 假设 | 检验方式 | 目标值 | 依据 |
|------|----------|--------|------|
| **H1**: 多模态效度 > 单模态 | r(multimodal) > r(text-only) | Δr > 0.05 | PROCESS Challenge 2025 |
| **H2**: 声学抗堆砌有效 | 堆砌样本声学评分下降 | >15 分 | 声学特征难以伪造 |
| **H3**: 冲突检测准确 | 不一致样本检出率 | >80% | 融合设计预期 |
| **H4**: 融合置信度校准 | 高置信度样本效度 > 低置信度 | Δr > 0.10 | 不确定性量化 |

#### 1.2.2 样本设计

**总样本量**: N = 300 条叙事文本 + 音频

| 层级 | 样本量 | 占比 | 说明 |
|------|--------|------|------|
| **正常叙述** | 210 | 70% | 无明显问题的自然叙述 |
| **边界案例** | 60 | 20% | L0 置信度 < 0.6 或评分 55-75 分 |
| **堆砌样本** | 30 | 10% | 人工构造的关键词堆砌文本 (含音频表演) |

**音频质量分层**:
| 质量 | SNR | 样本量 | 用途 |
|------|-----|--------|------|
| **高** | >30dB | 150 | 理想条件效度 |
| **中** | 20-30dB | 100 | 典型使用条件 |
| **低** | 10-20dB | 50 | 噪声鲁棒性测试 |

#### 1.2.3 对比组设置

| 组别 | 样本 | 评分方式 | 用途 |
|------|------|---------|------|
| **Group A (金标准)** | 全部 300 条 | 人工标注 (2 人 + 仲裁) | 效度验证基准 |
| **Group B (文本单模态)** | 全部 300 条 | L0+L1 文本评分 | 基线性能 |
| **Group C (多模态融合)** | 全部 300 条 | 文本 + 声学融合评分 | 核心验证 |
| **Group D (声学单模态)** | 全部 300 条 | 声学 biomarkers 单独评分 | 声学效度独立验证 |
| **Group E (堆砌对照)** | 30 条堆砌样本 | 文本 vs. 多模态对比 | 抗堆砌效度 |

#### 1.2.4 主要统计检验

```r
# H1: 多模态效度 > 单模态
cor_text <- cor.test(text_scores, human_scores, method = "pearson")
cor_multimodal <- cor.test(multimodal_scores, human_scores, method = "pearson")

# Fisher's z 检验相关系数差异
fisher_z_test(cor_text$r, cor_multimodal$r, n = 300)

# H2: 抗堆砌效度
t.test(text_gaming_penalty, multimodal_gaming_penalty, paired = TRUE)

# H3: 冲突检测准确率
confusion_matrix(
  predicted = fusion_result$is_consistent,
  actual = human_flagged_inconsistency
)

# H4: 置信度校准
cor_high_conf <- cor.test(
  multimodal_scores[confidence > 0.7],
  human_scores[confidence > 0.7]
)
cor_low_conf <- cor.test(
  multimodal_scores[confidence <= 0.7],
  human_scores[confidence <= 0.7]
)
```

---

## 2. 变量控制矩阵扩展 (Five → Six Layers)

### 2.1 控制策略总览 (v7.0 更新)

| 控制层级 | 控制对象 | 主要方法 | 负责人 | 容差标准 | 监测频率 |
|----------|----------|----------|--------|----------|----------|
| **受试者层** | 纳入/排除/协变量 | 标准化筛查 + 随机化分层 | 研究协调员 | 纳入标准±0 | 每受试者 |
| **干预层** | 剂量/内容/保真度 | 系统日志 + 10% 人工抽检 | 干预执行者 | 时长 25-45min | 每会话 |
| **评估层** | 评估者/时点/盲法 | 统一培训 + 盲法检验 | 评估主管 | ICC>0.90 | 每周 |
| **数据层** | 录入/缺失/锁定 | 双人录入 + 统计调整 | 数据管理员 | 差异>5% 重核 | 每日 |
| **抗堆砌层** | 关键词堆砌检测 | L0 密度检测 + L1 语义一致性 | 系统自动 | 堆砌率<2% | 实时 |
| **声学质控层** | 音频质量/SNR/设备 | 音频质量自动检测 + 设备标准化 | 系统自动 | SNR>20dB | 每会话 (新增) |

---

### 2.2 声学质控层 (新增)

#### 2.2.1 音频质量标准

| 参数 | 标准值 | 容差范围 | 监测方式 | 纠偏措施 |
|------|--------|----------|----------|----------|
| **信噪比 (SNR)** | >30dB | ≥20dB | 系统自动检测 | <20dB 标记"低质量"，评分置信度降级 |
| **采样率** | 16kHz | ±0 | 系统配置 | 固定配置，异常报警 |
| **位深** | 16-bit | ±0 | 系统配置 | 固定配置 |
| **声道** | Mono | ±0 | 系统配置 | 固定配置 |
| **最大音量** | -3dBFS | -6 to -1dBFS | 系统检测 | 削波标记，人工复核 |
| **最小音量** | >-60dBFS | >-70dBFS | 系统检测 | 过低标记，提示用户调整 |

#### 2.2.2 设备标准化

| 设备类型 | 推荐设备 | 备选设备 | 控制方式 |
|----------|----------|----------|----------|
| **麦克风** | iPhone 内置麦克风 | Android 旗舰机内置 | 设备型号记录，作为协变量 |
| **耳机** | 有线耳机 (3.5mm) | 蓝牙耳机 (低延迟) | 类型记录，作为协变量 |
| **环境** | 安静室内 (<40dB) | 可接受一般噪音 | 环境噪音检测，作为协变量 |

#### 2.2.3 音频质量自动检测算法

```python
class AudioQualityChecker:
    """
    音频质量自动检测
    
    输入：语音波形
    输出：质量评分 + 标记
    """
    
    def __init__(self):
        self.sr = 16000
        self.snr_threshold_good = 30  # dB
        self.snr_threshold_acceptable = 20  # dB
    
    def check_quality(self, audio_path: str) -> Dict:
        """检测音频质量"""
        waveform, sr = librosa.load(audio_path, sr=self.sr)
        
        # === 1. 信噪比估计 ===
        snr = self._estimate_snr(waveform)
        
        # === 2. 削波检测 ===
        clipping_ratio = np.sum(np.abs(waveform) >= 0.99) / len(waveform)
        
        # === 3. 静音比例 ===
        silence_ratio = self._detect_silence_ratio(waveform)
        
        # === 4. 音量水平 ===
        rms = np.sqrt(np.mean(waveform ** 2))
        
        # === 5. 综合质量评分 ===
        quality_score = self._compute_quality_score(
            snr, clipping_ratio, silence_ratio, rms
        )
        
        # === 6. 质量分级 ===
        if quality_score >= 80 and snr >= self.snr_threshold_good:
            quality_level = 'HIGH'
        elif quality_score >= 60 and snr >= self.snr_threshold_acceptable:
            quality_level = 'MEDIUM'
        else:
            quality_level = 'LOW'
        
        return {
            'quality_score': quality_score,
            'quality_level': quality_level,
            'snr_db': snr,
            'clipping_ratio': clipping_ratio,
            'silence_ratio': silence_ratio,
            'rms': rms,
            'usable': quality_level != 'LOW'
        }
    
    def _estimate_snr(self, waveform: np.ndarray) -> float:
        """估计信噪比 (dB)"""
        # 简化方法：信号能量 / 噪声能量
        # 噪声估计：最低 10% 能量的帧
        energy = librosa.feature.rms(y=waveform)[0]
        noise_energy = np.percentile(energy, 10)
        signal_energy = np.percentile(energy, 90)
        
        if noise_energy <= 0:
            return 100.0
        
        snr = 10 * np.log10(signal_energy / noise_energy)
        return snr
```

#### 2.2.4 音频质量对评分的影响处理

| 质量等级 | 处理方式 | 置信度调整 | 备注 |
|----------|----------|------------|------|
| **HIGH** | 正常评分 | 无调整 | 理想条件 |
| **MEDIUM** | 正常评分 + 标记 | 置信度 × 0.85 | 典型使用条件 |
| **LOW** | 评分仅供参考 + 强烈标记 | 置信度 × 0.60 | 建议重新录制 |

---

## 3. 对比组设计扩展

### 3.1 L1e 多模态效度验证对比组 (新增)

```
┌─────────────────────────────────────────────────────────┐
│           L1e: 多模态效度验证 (EXP-002)                  │
│  ┌─────────────────┐    ┌─────────────────┐            │
│  │ 文本单模态 (n=300)│    │多模态融合 (n=300)│            │
│  │   L0+L1 文本     │    │  文本 + 声学融合  │            │
│  └────────┬────────┘    └────────┬────────┘            │
│           │                      │                      │
│           └──────────┬───────────┘                      │
│                      ↓                                  │
│         比较：与人工标注的相关系数 (Pearson r)           │
│         目标：Δr > 0.05 (multimodal > text-only)        │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│              音频质量分层分析                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ HIGH (n=150) │  │MEDIUM (n=100)│  │ LOW (n=50)   │  │
│  │   SNR>30dB   │  │ SNR 20-30dB  │  │ SNR 10-20dB  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                      ↓                                  │
│         检验：多模态优势在不同质量下是否稳健             │
└─────────────────────────────────────────────────────────┘
```

### 3.2 与 L1d 的关系

| 维度 | L1d (多 Agent) | L1e (多模态) | 关系 |
|------|---------------|-------------|------|
| **验证目标** | L0+L1 vs. L0 单独 | 多模态 vs. 文本单模态 | 互补 |
| **样本量** | N=200 | N=300 | L1e 更大 (需音频质量分层) |
| **核心假设** | L1 仲裁提升效度 | 声学融合提升效度 | 独立验证 |
| **执行顺序** | Phase 1 | Phase 2 | L1d 先执行 (无需音频) |

---

## 4. 评估指标扩展

### 4.1 技术验证指标 (新增多模态指标)

| 指标 | 计算方法 | 目标值 | 依据 | 解释标准 |
|------|----------|--------|------|----------|
| **多模态 vs 人工相关** | Pearson r (融合 vs. 人工) | >0.80 | PROCESS Challenge 2025 | ≥0.80=Excellent |
| **文本 vs 人工相关** | Pearson r (文本 vs. 人工) | >0.75 | v6.0 目标 | 基线对照 |
| **多模态增量效度** | Δr = r(multi) - r(text) | >0.05 | 文献预期 | 量化融合价值 |
| **声学 vs 人工相关** | Pearson r (声学 vs. 人工) | >0.65 | DementiaBank 研究 | 声学独立效度 |
| **冲突检测准确率** | 不一致样本检出率 | >80% | 融合设计预期 | — |
| **置信度校准** | 高置信度效度 - 低置信度效度 | >0.10 | 不确定性量化 | — |
| **音频质量影响** | r(HIGH) - r(LOW) | <0.15 | 鲁棒性要求 | 越小越好 |
| **抗堆砌效度 (声学)** | 堆砌样本声学评分下降 | >15 分 | 声学难以伪造 | — |

### 4.2 声学 Biomarkers 指标 (新增)

| Biomarker | 操作化定义 | 测量方式 | 预期与认知相关性 |
|-----------|------------|----------|-----------------|
| **停顿率** | 停顿时长 / 总时长 | 能量阈值检测 | r≈-0.45 (负相关) |
| **平均停顿时长** | 连续静音段平均时长 | 静音段分析 | r≈-0.40 |
| **基频变异系数** | F0 std / F0 mean | 基频提取 | r≈-0.35 |
| **能量变异系数** | Energy std / Energy mean | 能量分析 | r≈-0.30 |
| **语速** | 音节数 / 时长 | 过零率近似 | r≈+0.40 |
| **发音清晰度** | 频谱平坦度逆指标 | STFT 分析 | r≈+0.45 |
| **Composite Audio Score** | 6 biomarkers 加权 | 加权平均 | r≈+0.60-0.70 |

---

## 5. 多模态融合架构 (方法学核心)

### 5.1 并行处理流水线

```
用户语音输入 (叙事录音，30s-5min)
            ↓
    ┌───────────────┐
    │  并行处理流水线 │
    └───────────────┘
        ↓           ↓
┌───────────────┐   ┌───────────────┐
│  文本分支      │   │  声学分支      │
│               │   │               │
│ 1. ASR 转写    │   │ 1. 音频质量检测│
│ 2. L0 评分     │   │ 2. 特征提取    │
│ 3. C1-C6 维度  │   │ 3. 6 Biomarkers│
│ 4. 置信度      │   │ 4. Audio Score│
└───────┬───────┘   └───────┬───────┘
        ↓                   ↓
    ┌───────────────────────────┐
    │      融合层                │
    │                           │
    │ - 加权融合 (0.6 文本 +0.4 声学)│
    │ - 一致性检验 (差异>15 分标记)  │
    │ - 冲突解决 (触发 L1 仲裁)     │
    └─────────────┬─────────────┘
                  ↓
    ┌───────────────────────────┐
    │      L1 仲裁层 (增强版)      │
    │                           │
    │ 输入：文本 + 声学 + 融合结果  │
    │ 输出：调整量 + 推理 + 最终分  │
    └─────────────┬─────────────┘
                  ↓
    ┌───────────────────────────┐
    │      最终评分输出           │
    │  Final Score + 置信度       │
    └───────────────────────────┘
```

### 5.2 融合策略伪代码

```python
class MultimodalFusion:
    """
    多模态融合器 (文本 + 声学)
    """
    
    def __init__(self, text_weight: float = 0.6, audio_weight: float = 0.4):
        self.text_weight = text_weight
        self.audio_weight = audio_weight
        self.consistency_threshold = 15  # 分数差异>15 分视为不一致
    
    def fuse(self, text_result: Dict, audio_result: Dict, audio_quality: Dict) -> Dict:
        """融合文本和声学评分"""
        text_score = text_result['final_score']
        audio_score = audio_result['audio_score']
        
        # === 1. 加权融合 ===
        fused_score = (
            self.text_weight * text_score +
            self.audio_weight * audio_score
        )
        
        # === 2. 一致性检验 ===
        score_diff = abs(text_score - audio_score)
        is_consistent = score_diff <= self.consistency_threshold
        
        # === 3. 置信度融合 ===
        text_conf = text_result.get('confidence', 0.7)
        audio_conf = audio_result.get('confidence', 0.75)
        
        # 音频质量调整置信度
        if audio_quality['quality_level'] == 'MEDIUM':
            audio_conf *= 0.85
        elif audio_quality['quality_level'] == 'LOW':
            audio_conf *= 0.60
        
        fused_confidence = 0.5 * (text_conf + audio_conf)
        
        # 如果不一致，降低置信度
        if not is_consistent:
            fused_confidence *= 0.7
        
        # === 4. 触发 L1 仲裁条件 ===
        requires_l1 = (
            not is_consistent or 
            fused_confidence < 0.6 or
            text_result.get('confidence', 1.0) < 0.6
        )
        
        return {
            'final_score': fused_score,
            'confidence': fused_confidence,
            'is_consistent': is_consistent,
            'score_diff': score_diff,
            'text_score': text_score,
            'audio_score': audio_score,
            'requires_l1_arbitration': requires_l1,
            'audio_quality': audio_quality['quality_level']
        }
```

---

## 6. 统计分析计划扩展

### 6.1 L1e 多模态效度验证分析 (新增)

**主要效度检验**:
```r
# Pearson 相关系数
cor_text <- cor.test(text_scores, human_scores, method = "pearson")
cor_multimodal <- cor.test(multimodal_scores, human_scores, method = "pearson")
cor_audio_only <- cor.test(audio_scores, human_scores, method = "pearson")

# 相关系数差异检验 (Fisher's z)
# H1: 多模态 > 文本
fisher_z_test(cor_text$r, cor_multimodal$r, n = 300)

# H2: 多模态 > 声学
fisher_z_test(cor_audio_only$r, cor_multimodal$r, n = 300)
```

**抗堆砌效度检验**:
```r
# 堆砌样本 vs. 正常样本的评分差异 (多模态)
t.test(multimodal_gaming_scores, multimodal_normal_scores, paired = FALSE)

# 文本 vs. 多模态对堆砌样本的惩罚差异
wilcox.test(text_gaming_penalty, multimodal_gaming_penalty, paired = TRUE)
```

**音频质量分层分析**:
```r
# 按音频质量分层计算效度
cor_high <- cor.test(
  multimodal_scores[audio_quality == 'HIGH'],
  human_scores[audio_quality == 'HIGH']
)
cor_medium <- cor.test(
  multimodal_scores[audio_quality == 'MEDIUM'],
  human_scores[audio_quality == 'MEDIUM']
)
cor_low <- cor.test(
  multimodal_scores[audio_quality == 'LOW'],
  human_scores[audio_quality == 'LOW']
)

# 检验效度差异
anova_result <- aov(score ~ audio_quality * scoring_method, data = data)
```

**置信度校准分析**:
```r
# 高置信度 vs. 低置信度效度
cor_high_conf <- cor.test(
  multimodal_scores[confidence > 0.7],
  human_scores[confidence > 0.7]
)
cor_low_conf <- cor.test(
  multimodal_scores[confidence <= 0.7],
  human_scores[confidence <= 0.7]
)

# 校准曲线
calibration_plot <- ggplot(data, aes(x = predicted_score, y = human_score)) +
  geom_point(alpha = 0.3) +
  geom_smooth(method = 'lm') +
  facet_wrap(~confidence_level)
```

### 6.2 L1e 样本量计算 (新增)

```
目标：检测 Δr = 0.05 的相关系数差异 (r=0.75 → r=0.80)

使用 G*Power 3.1:
- Test family: t tests
- Statistical test: Correlation: Difference from constant
- Type of power analysis: A priori
- Effect size: q = 0.05 (Fisher's z transformation)
- α err prob: 0.05
- Power (1-β err prob): 0.80

输出：N = 287 → 300 (考虑音频质量分层需求)

音频质量分层样本量:
- HIGH (SNR>30dB): 50% → 150
- MEDIUM (SNR 20-30dB): 33% → 100
- LOW (SNR 10-20dB): 17% → 50
```

---

## 7. 实现路线图 (Core 参考)

| 阶段 | 任务 | 预计工作量 | 依赖 | 产出物 | 关联实验 |
|------|------|-----------|------|--------|---------|
| **Phase 1** | 声学特征提取器实现 | 2-3 天 | librosa, scipy | `pipeline/src/services/audio_feature_extractor.py` + 测试 | L1e |
| **Phase 2** | 6 种 Biomarkers 检测器 | 3-4 天 | Phase 1 完成 | `pipeline/src/services/speech_biomarker_detector.py` | L1e |
| **Phase 3** | Composite Audio Scorer | 1-2 天 | Phase 2 完成 | `pipeline/src/services/composite_audio_scorer.py` | L1e |
| **Phase 4** | 多模态融合器 | 2-3 天 | Phase 3 完成 | `pipeline/src/services/multimodal_fusion.py` | L1e |
| **Phase 5** | L1 仲裁增强 + 端到端测试 | 2-3 天 | Phase 4 完成 | 整合测试 + 基准报告 | L1d+L1e |
| **Phase 6** | EXP-002 实验执行 | 5-7 天 | Phase 5 完成 | 300 样本标注 + 分析报告 | L1e |

**总计**: 15-22 天

**依赖项**:
- ✅ 文献基础：Robot Speech Biomarkers, PROCESS Challenge, Nature 论文
- ✅ 设计稿：`designs/speech-biomarkers-fusion-v0.7.md` (GEO #101)
- 🔴 ASR API Key：讯飞/阿里 (需 V 提供)
- 🔴 音频测试数据：300 条老年叙事录音 (需 Core/V 收集，可用 DementiaBank 先行验证)

---

## 8. 与论文章节对应

| 论文章节 | 对应内容 | v7.0 新增 |
|----------|----------|----------|
| Section 3.1 | Study Design Overview | 七层验证体系概览 |
| Section 3.2 | Variable Control Matrix | + 声学质控层 |
| Section 3.3 | Comparison Groups | + L1e 多模态对比组 |
| Section 3.4 | Outcome Measures | + 多模态指标 + 声学 biomarkers |
| Section 3.5 | Statistical Analysis | + L1e 统计分析 |
| **Section 3.6** | **Multimodal Fusion Architecture** | **🟢 全新章节** |
| Section 5.1 | L1a Mock Test | 已完成 (V4) |
| Section 5.2 | L1b Benchmark | 设计中 |
| Section 5.3 | L1c Event Detection | 设计中 |
| Section 5.4 | L1d Multi-Agent Validation | 设计中 |
| **Section 5.5** | **L1e Multimodal Validation** | **🟢 新增** |
| Section 5.6 | L2 Pilot RCT | 设计中 |
| Section 5.7 | L3 A/B Test | 设计中 |

---

## 9. 补充材料扩展 (v7.0)

以下材料将作为补充材料提交:

1. **Supplementary Table S1**: 数据字典 (完整变量列表)
2. **Supplementary Table S2**: AI 提示语标准库 (干预组)
3. **Supplementary Table S3**: 认知训练任务列表 (对照组)
4. **Supplementary Figure S1**: 六维评分框架速查卡
5. **Supplementary Figure S2**: 评估者培训流程图
6. **Supplementary Figure S3**: 抗堆砌检测算法流程图
7. **Supplementary Figure S4**: 多模态融合架构流程图 (新增)
8. **Supplementary Figure S5**: 音频质量检测算法流程图 (新增)
9. **Supplementary Appendix A**: 知情同意书模板
10. **Supplementary Appendix B**: 变量控制执行清单
11. **Supplementary Appendix C**: R 分析代码框架
12. **Supplementary Appendix D**: EXP-001 实验方案 (L1d)
13. **Supplementary Appendix E**: EXP-002 实验方案 (L1e, 新增)
14. **Supplementary Appendix F**: 6 种 Speech Biomarkers 检测协议 (新增)

---

## 10. 版本历史

| 版本 | 日期 | 更新内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-03-24 | 初始设计 | Hulk |
| v2.0 | 2026-03-26 | 强化变量控制 | Hulk |
| v3.0 | 2026-03-27 | 五层验证 + 时间线 | Hulk |
| v4.0 | 2026-03-29 | 精炼执行版 | Hulk |
| v5.0 | 2026-03-30 | arXiv Methods 终稿 | Hulk |
| v6.0 | 2026-04-04 | 整合 EXP-001 + 抗堆砌机制 | Hulk |
| **v7.0** | **2026-04-05** | **整合多模态融合 (语音 Biomarkers)** | **Hulk** |

---

## 11. 与 v6.0 对比总结

| 要素 | v6.0 | v7.0 | 更新理由 |
|------|------|------|----------|
| **验证层次** | 6 层 | 7 层 (+L1e) | 多模态融合需独立验证 |
| **评分模态** | 文本单模态 | 文本 + 声学双模态 | 语音 biomarkers 提供互补证据 |
| **变量控制** | 5 层 | 6 层 (+声学质控) | 音频质量影响 biomarker 检测 |
| **对比组** | L0 vs. L0+L1 | + 单模态 vs. 多模态 | 量化多模态增量价值 |
| **评估指标** | 抗堆砌效度 | + 多模态效度 + 声学 biomarkers | 验证融合策略有效性 |
| **样本量** | N=200 (L1d) | N=300 (L1e) | 多模态亚组分析需求 |
| **统计分析** | L1d 分析 | + L1e 分析 + 音频质量分层 | 支撑多模态验证 |
| **补充材料** | 12 项 | 14 项 | 新增多模态 + biomarkers |
| **论文章节** | Section 3.1-3.5 | + Section 3.6 + 5.5 | 方法学完整性 |

---

## 12. 文档用途定位

| 文档 | 主要用途 | 次要用途 | 状态 |
|------|----------|----------|------|
| `15-experiment-design-v7-multimodal.md` (v7.0) | **多模态验证实验设计** | arXiv Supplementary Materials v3 | ✅ 就绪 |
| `14-experiment-design-v6-updated.md` (v6.0) | **单模态最新版** | arXiv Supplementary Materials v2 | ✅ 就绪 |
| `12-experiment-design-arxiv-final.md` (v5.0) | arXiv 提交 + 伦理审批 + 预注册 | 实验执行参考 | ✅ 就绪 |
| `designs/speech-biomarkers-fusion-v0.7.md` | Core 实现参考 | L1e 实验设计素材 | ✅ 就绪 |

---

## 13. 下一步建议

| # | 任务 | 优先级 | 负责人 | 预计耗时 |
|---|------|--------|--------|----------|
| 1 | **arXiv 提交 (v5.0 对齐)** | 高 | V | 95 分钟 |
| 2 | **伦理审批提交** | 高 | V/PI | 见上 |
| 3 | **EXP-001 实验启动 (L1d)** | 高 | Core | 协调标注人员，5 天完成 |
| 4 | **多模态 Phase 1-5 实现** | 中 | Core | 15-22 天 (如 RB-019 优先级提升) |
| 5 | **EXP-002 实验设计细化** | 中 | Hulk | 3-5 天 (如 Core 确认实现路线图) |
| 6 | **Section 3.6 整合 (可选)** | 低 | Hulk | 如 V 确认 arXiv v2 需要 |

---

## 14. 验证等级汇总

| 要素 | v6.0 验证等级 | v7.0 验证等级 | 验证方式 |
|------|----------|----------|----------|
| 变量控制 | V3 | V3 | CONSORT/SPIRIT + 音频质控文献交叉确认 |
| 对比组设计 | V3 | V2 | RCT 最佳实践 + PROCESS Challenge 参考 |
| 评估指标 | V3 | V2 | CONSORT + 语音 biomarkers 文献 |
| 多模态融合架构 | N/A | V2 | GEO #101 文献综合 + 架构推断 |
| 统计分析 | V3 | V2 | G*Power 计算 + 文献先例 |
| 声学 biomarkers | N/A | V2 | Robot Speech Biomarkers + DementiaBank |

---

**文档状态**: v7.0 Multimodal Ready (多模态验证实验设计就绪)  
**验证等级**: V2-V3 (文献综合 + 静态复核)  
**下一步**: Core 评审实现路线图 + V 确认 arXiv v2 整合需求

---

*Hulk 🟢 — 2026-04-05 17:45 UTC*  
*密度即价值*
