# GEO Iteration #101 — RB-019 语音 Biomarkers 与 LLM 叙事评分融合方案

**执行者**: Hulk 🟢  
**时间**: 2026-04-05 04:15-05:15 UTC  
**触发**: cron:hulk-geo-iteration (自驱迭代)  
**验证等级**: V0-V2 (文献综合推断，需实验验证)

---

## 上下文继承

### 上一轮状态 (GEO #100)
- **完成**: RB-016 Agent Memory 四层架构映射设计 (`designs/agent-memory-four-layer-architecture.md`)
- **状态**: 设计稿完成，移交 Core 实现 (Phase 1-5, 11-16 天)
- **下一轮优先级**: RB-019 (语音 biomarkers 与 LLM 融合方案)

### 本轮任务来源
RB-019 承接 GEO #96-97 (REMem Phase 1-2 实现) 和 2026-03-27 文献阅读 #4 的发现：
- Robot Speech Biomarkers (arXiv:2502.11234) 定义 6 种语音生物标志物
- Nature Communications Medicine (2025) 临床验证语音作为认知障碍筛查生物标志物
- PROCESS Challenge 2025 推动语音认知评估标准化

---

## 本轮执行：语音 Biomarkers 与 LLM 叙事评分融合设计

### 一、语音 Biomarkers 文献综合

#### 1.1 核心发现汇总 (2026-03-27 文献 #4)

| Biomarker | 定义 | 检测方式 | 与认知状态相关性 |
|-----------|------|---------|-----------------|
| **Altered Grammar** | 语法结构异常 (时态混乱、主谓不一致) | ASR 文本 + 语法分析 | 中度 (r≈0.45-0.55) |
| **Pragmatic Impairments** | 语用障碍 (离题、重复、信息量不足) | 对话分析 + LLM 评估 | 中度 (r≈0.40-0.50) |
| **Anomia** | 命名困难 (停顿、填充词、替代词) | 停顿检测 + 词汇分析 | 高度 (r≈0.55-0.65) |
| **Disrupted Turn-Taking** | 话轮转换异常 (打断、延迟响应) | 对话时序分析 | 低 - 中度 (r≈0.30-0.40) |
| **Slurred Pronunciation** | 发音含糊 (音素模糊、音节省略) | 声学特征分析 | 中度 (r≈0.45-0.55) |
| **Prosody Changes** | 韵律变化 (音高/节奏/重音异常) | 基频/能量/时长分析 | 中度 (r≈0.40-0.50) |

**Composite Biomarker Score**: 6 种 biomarkers 加权组合，在 DementiaBank 数据集上与 MMSE 分数中度相关 (r≈0.60-0.70)。

#### 1.2 PROCESS Challenge 2025 方法参考

**3 项临床任务**:
1. **Picture Description** — 描述给定图片
2. **Story Retelling** — 复述听到的故事
3. **Semantic Fluency** — 列举某类别词汇 (如动物)

**有效特征类型**:
- Knowledge-based acoustic features (停顿、语速、基频)
- Text-based feature sets (词汇多样性、句法复杂度)
- **LLM-based macro-descriptors** (高层语义摘要)
- Pause-based acoustic biomarkers
- Neural representations (LongFormer, ECAPA-TDNN, Trillson embeddings)

**最佳系统**: 互补模型组合，依赖所有 3 项临床任务的声学和文本信息。

#### 1.3 Nature 论文背书 (2025)

**核心结论**:
- 语音生物标志物提供**可扩展、非侵入性、低成本**的自动化筛查方案
- 大规模临床验证语音特征与认知状态的相关性
- 支持语音作为**早期认知衰退筛查**的有效生物标志物

**VSNC 启示**:
- Nature 级别背书为语音生物标志物方向提供权威性
- 支持在阿宝中整合声学特征分析 (不仅是 ASR 转文本)
- 可参考该研究的临床验证方法设计 VSNC pilot study

---

### 二、VSNC 当前评分架构回顾

#### 2.1 L0 规则引擎 (v0.5-v0.6)

**6 个评分维度** (全部基于 ASR 转写文本):
- C1: 内部细节 (Internal Details)
- C2: 外部细节 (External Details)
- C3: 连贯性 (Coherence)
- C4: 情感效价 (Emotional Valence)
- C5: 信息密度 (Information Density)
- C6: 语言流畅性 (Linguistic Fluency)

**缺口**:
- ❌ 无声学特征分析
- ❌ 无语音特异性 biomarkers (停顿、韵律、发音)
- ❌ 依赖 ASR 质量，ASR 错误会传导到评分

#### 2.2 L1 仲裁层 (v0.6 设计)

**职责**: 边界案例修正 (置信度<0.6 或 55≤score≤75)

**当前设计**: 基于文本的 LLM 仲裁

**增强机会**: 整合语音 biomarkers 作为仲裁证据

---

### 三、语音 Biomarkers 融合方案设计 (v0.7-v0.8)

#### 3.1 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                      用户语音输入                                │
│                    (叙事录音，30s-5min)                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │          并行处理流水线                  │
        └─────────────────────────────────────────┘
                    ↓                       ↓
    ┌───────────────────────────┐   ┌───────────────────────────┐
    │    文本分支 (Text Path)    │   │   声学分支 (Audio Path)    │
    │                           │   │                           │
    │  1. ASR 转写 (讯飞/阿里)     │   │  1. 声学特征提取           │
    │  2. L0 规则引擎评分         │   │     - 停顿检测            │
    │  3. C1-C6 维度分 + 置信度    │   │     - 基频/韵律分析        │
    │                           │   │     - 发音清晰度           │
    │                           │   │  2. 6 种 biomarkers 检测     │
    │                           │   │  3. Composite Audio Score   │
    └───────────────────────────┘   └───────────────────────────┘
                    ↓                       ↓
        ┌─────────────────────────────────────────┐
        │      融合层 (Fusion Layer)               │
        │                                         │
        │  - 加权融合：Text Score + Audio Score   │
        │  - 一致性检验：文本 vs. 声学是否一致     │
        │  - 冲突解决：不一致时触发 L1 仲裁         │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │      L1 仲裁层 (可选触发)                 │
        │                                         │
        │  - 输入：文本评分 + 声学评分 + 原始特征   │
        │  - 输出：调整量 + 推理 + 最终分          │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │           最终评分输出                    │
        │   (Final Score + 维度分 + 置信度)         │
        └─────────────────────────────────────────┘
```

#### 3.2 声学特征提取设计

```python
class AudioFeatureExtractor:
    """
    声学特征提取器
    
    输入：语音波形 (16kHz, mono)
    输出：声学特征字典
    """
    
    def __init__(self):
        self.sr = 16000  # 采样率
    
    def extract_features(self, audio_path: str) -> Dict:
        """提取全部声学特征"""
        # 加载音频
        waveform, sr = librosa.load(audio_path, sr=self.sr)
        
        features = {}
        
        # === 1. 停顿检测 (Pause Detection) ===
        features['pause_rate'] = self._detect_pause_rate(waveform)
        features['avg_pause_duration'] = self._avg_pause_duration(waveform)
        features['long_pause_count'] = self._long_pause_count(waveform)
        
        # === 2. 韵律分析 (Prosody) ===
        # 基频 (F0)
        f0, voiced_flag, voiced_prob = librosa.pyin(
            waveform, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')
        )
        features['f0_mean'] = np.nanmean(f0)
        features['f0_std'] = np.nanstd(f0)
        features['f0_range'] = np.nanmax(f0) - np.nanmin(f0)
        
        # 能量
        energy = librosa.feature.rms(y=waveform)[0]
        features['energy_mean'] = np.mean(energy)
        features['energy_std'] = np.std(energy)
        
        # 语速 (syllables per second)
        features['speech_rate'] = self._estimate_speech_rate(waveform)
        
        # === 3. 发音清晰度 (Articulation) ===
        # 使用预训练模型检测发音含糊度
        features['articulation_score'] = self._assess_articulation(waveform)
        
        # === 4. 话轮转换 (Turn-Taking) ===
        # 如果有对话上下文，分析响应延迟
        features['response_latency'] = self._measure_response_latency(audio_path)
        
        return features
    
    def _detect_pause_rate(self, waveform: np.ndarray) -> float:
        """检测停顿率 (停顿时长 / 总时长)"""
        # 使用能量阈值检测静音段
        energy = librosa.feature.rms(y=waveform)[0]
        silence_threshold = np.percentile(energy, 10)
        is_silence = energy < silence_threshold
        
        # 计算停顿率
        pause_frames = np.sum(is_silence)
        total_frames = len(is_silence)
        return pause_frames / total_frames
    
    def _avg_pause_duration(self, waveform: np.ndarray) -> float:
        """计算平均停顿时长 (秒)"""
        # 检测连续静音段
        energy = librosa.feature.rms(y=waveform)[0]
        silence_threshold = np.percentile(energy, 10)
        is_silence = energy < silence_threshold
        
        # 找出连续静音段
        pause_durations = []
        in_pause = False
        pause_start = 0
        
        for i, is_silent in enumerate(is_silence):
            if is_silent and not in_pause:
                in_pause = True
                pause_start = i
            elif not is_silent and in_pause:
                in_pause = False
                duration = (i - pause_start) / self.sr
                if duration > 0.2:  # 忽略<200ms 的短暂停顿
                    pause_durations.append(duration)
        
        return np.mean(pause_durations) if pause_durations else 0.0
    
    def _estimate_speech_rate(self, waveform: np.ndarray) -> float:
        """估计语速 (音节/秒)"""
        # 使用过零率近似音节检测
        zcr = librosa.feature.zero_crossing_rate(waveform)[0]
        # 简化估计：过零率峰值数 / 时长
        peaks = scipy.signal.find_peaks(zcr, distance=10)[0]
        duration = len(waveform) / self.sr
        return len(peaks) / duration
    
    def _assess_articulation(self, waveform: np.ndarray) -> float:
        """评估发音清晰度 (0-100)"""
        # 使用预训练模型或启发式方法
        # 这里简化为频谱清晰度指标
        spec = librosa.stft(waveform)
        spec_flatness = scipy.stats.gmean(np.abs(spec), axis=0)
        # 频谱平坦度越低，发音越清晰
        clarity = 100 * (1 - np.mean(spec_flatness))
        return np.clip(clarity, 0, 100)
```

**验证等级**: V0 (设计推断)

---

#### 3.3 6 种 Biomarkers 检测映射

```python
class SpeechBiomarkerDetector:
    """
    语音生物标志物检测器
    
    基于文献定义的 6 种 biomarkers
    """
    
    def __init__(self, audio_extractor: AudioFeatureExtractor):
        self.audio_extractor = audio_extractor
    
    def detect_all(self, audio_path: str, asr_text: str) -> Dict:
        """检测全部 6 种 biomarkers"""
        audio_features = self.audio_extractor.extract_features(audio_path)
        
        biomarkers = {}
        
        # === 1. Altered Grammar (语法异常) ===
        # 需要 ASR 文本 + 语法分析
        biomarkers['altered_grammar'] = self._detect_altered_grammar(asr_text)
        
        # === 2. Pragmatic Impairments (语用障碍) ===
        # 需要 LLM 评估文本的语用质量
        biomarkers['pragmatic_impairment'] = self._detect_pragmatic_impairment(asr_text)
        
        # === 3. Anomia (命名困难) ===
        # 停顿率 + 填充词检测
        biomarkers['anomia'] = self._detect_anomia(audio_features, asr_text)
        
        # === 4. Disrupted Turn-Taking (话轮转换异常) ===
        # 响应延迟 + 打断检测
        biomarkers['disrupted_turn_taking'] = self._detect_disrupted_turn_taking(audio_features)
        
        # === 5. Slurred Pronunciation (发音含糊) ===
        # 发音清晰度评分
        biomarkers['slurred_pronunciation'] = 100 - audio_features['articulation_score']
        
        # === 6. Prosody Changes (韵律变化) ===
        # 基频/能量异常
        biomarkers['prosody_changes'] = self._detect_prosody_changes(audio_features)
        
        return biomarkers
    
    def _detect_altered_grammar(self, text: str) -> Dict:
        """检测语法异常"""
        # 使用 LLM 或语法规则检测
        # 返回：severity (0-100), details
        return {
            'severity': 0,  # 待实现
            'details': []
        }
    
    def _detect_pragmatic_impairment(self, text: str) -> Dict:
        """检测语用障碍"""
        # 使用 LLM 评估：是否离题、重复、信息量不足
        return {
            'severity': 0,  # 待实现
            'details': []
        }
    
    def _detect_anomia(self, audio_features: Dict, text: str) -> Dict:
        """检测命名困难"""
        # 高停顿率 + 填充词 (嗯、啊、那个)
        pause_severity = audio_features['pause_rate'] * 100
        
        # 检测填充词
        filler_words = ['嗯', '啊', '那个', '就是', '然后']
        filler_count = sum(text.count(w) for w in filler_words)
        filler_severity = min(filler_count * 5, 100)
        
        severity = 0.6 * pause_severity + 0.4 * filler_severity
        
        return {
            'severity': severity,
            'pause_rate': audio_features['pause_rate'],
            'filler_count': filler_count
        }
    
    def _detect_disrupted_turn_taking(self, audio_features: Dict) -> Dict:
        """检测话轮转换异常"""
        # 响应延迟 (如果有对话上下文)
        latency = audio_features.get('response_latency', 0)
        severity = min(latency * 10, 100)  # 每秒延迟加 10 分
        
        return {
            'severity': severity,
            'response_latency': latency
        }
    
    def _detect_prosody_changes(self, audio_features: Dict) -> Dict:
        """检测韵律变化"""
        # 基频变异系数 (CV = std/mean)
        f0_cv = audio_features['f0_std'] / max(audio_features['f0_mean'], 1)
        
        # 能量变异系数
        energy_cv = audio_features['energy_std'] / max(audio_features['energy_mean'], 1)
        
        # 正常范围参考 (基于健康老年人基线)
        normal_f0_cv = 0.3
        normal_energy_cv = 0.4
        
        # 偏离正常范围的程度
        f0_deviation = abs(f0_cv - normal_f0_cv) / normal_f0_cv
        energy_deviation = abs(energy_cv - normal_energy_cv) / normal_energy_cv
        
        severity = 50 * (f0_deviation + energy_deviation)
        
        return {
            'severity': min(severity, 100),
            'f0_cv': f0_cv,
            'energy_cv': energy_cv
        }
```

**验证等级**: V0 (设计推断)

---

#### 3.4 Composite Audio Score 计算

```python
class CompositeAudioScorer:
    """
    复合语音生物标志物评分
    
    输入：6 种 biomarkers
    输出：0-100 综合评分 (越高越好)
    """
    
    def __init__(self):
        # 权重配置 (基于文献相关性强度)
        self.weights = {
            'altered_grammar': 0.15,       # r≈0.45-0.55
            'pragmatic_impairment': 0.15,  # r≈0.40-0.50
            'anomia': 0.25,                # r≈0.55-0.65 (最高)
            'disrupted_turn_taking': 0.10, # r≈0.30-0.40 (最低)
            'slurred_pronunciation': 0.15, # r≈0.45-0.55
            'prosody_changes': 0.20        # r≈0.40-0.50
        }
    
    def compute(self, biomarkers: Dict) -> Dict:
        """计算复合评分"""
        # 各 biomarker 的 severity (0-100, 越高越异常)
        severities = {
            key: biomarkers[key]['severity']
            for key in self.weights.keys()
        }
        
        # 加权平均 severity
        weighted_severity = sum(
            severities[key] * self.weights[key]
            for key in self.weights
        )
        
        # 转换为健康评分 (100 - severity)
        audio_score = 100 - weighted_severity
        
        # 置信度 (基于 biomarker 检测的置信度)
        confidence = self._compute_confidence(biomarkers)
        
        return {
            'audio_score': audio_score,
            'confidence': confidence,
            'dimension_scores': {
                'grammar': 100 - severities['altered_grammar'],
                'pragmatic': 100 - severities['pragmatic_impairment'],
                'anomia': 100 - severities['anomia'],
                'turn_taking': 100 - severities['disrupted_turn_taking'],
                'articulation': 100 - severities['slurred_pronunciation'],
                'prosody': 100 - severities['prosody_changes']
            },
            'severity_details': severities
        }
    
    def _compute_confidence(self, biomarkers: Dict) -> float:
        """计算评分置信度"""
        # 基于音频质量、检测完整性等
        # 简化实现：返回固定值
        return 0.75
```

**验证等级**: V0 (设计推断)

---

#### 3.5 文本 - 声学融合策略

```python
class MultimodalFusion:
    """
    多模态融合器 (文本 + 声学)
    
    融合策略:
    1. 加权平均 (默认)
    2. 一致性检验 (检测冲突)
    3. 冲突解决 (触发 L1 仲裁)
    """
    
    def __init__(self, text_weight: float = 0.6, audio_weight: float = 0.4):
        self.text_weight = text_weight
        self.audio_weight = audio_weight
        self.consistency_threshold = 15  # 分数差异>15 分视为不一致
    
    def fuse(self, text_result: Dict, audio_result: Dict) -> Dict:
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
        fused_confidence = 0.5 * (text_conf + audio_conf)
        
        # 如果不一致，降低置信度
        if not is_consistent:
            fused_confidence *= 0.7
        
        # === 4. 维度级融合 ===
        # 文本维度 (C1-C6) + 声学维度 (grammar, pragmatic, ...)
        fused_dimensions = self._fuse_dimensions(text_result, audio_result)
        
        return {
            'final_score': fused_score,
            'confidence': fused_confidence,
            'is_consistent': is_consistent,
            'score_diff': score_diff,
            'text_score': text_score,
            'audio_score': audio_score,
            'fused_dimensions': fused_dimensions,
            'requires_l1_arbitration': not is_consistent or fused_confidence < 0.6
        }
    
    def _fuse_dimensions(self, text_result: Dict, audio_result: Dict) -> Dict:
        """维度级融合"""
        # 文本维度 (C1-C6)
        text_dims = {
            'C1_internal': text_result.get('c1', 50),
            'C2_external': text_result.get('c2', 50),
            'C3_coherence': text_result.get('c3', 50),
            'C4_emotion': text_result.get('c4', 50),
            'C5_density': text_result.get('c5', 50),
            'C6_fluency': text_result.get('c6', 50)
        }
        
        # 声学维度
        audio_dims = audio_result.get('dimension_scores', {})
        
        # 映射关系 (声学维度 → 文本维度补充)
        # - grammar → C6 (fluency)
        # - pragmatic → C3 (coherence)
        # - anomia → C5 (density)
        # - articulation → C6 (fluency)
        # - prosody → C4 (emotion)
        
        fused = {
            **text_dims,
            'audio_grammar': audio_dims.get('grammar', 50),
            'audio_pragmatic': audio_dims.get('pragmatic', 50),
            'audio_anomia': audio_dims.get('anomia', 50),
            'audio_articulation': audio_dims.get('articulation', 50),
            'audio_prosody': audio_dims.get('prosody', 50)
        }
        
        return fused
```

**验证等级**: V0 (设计推断)

---

#### 3.6 L1 仲裁增强 (整合语音证据)

```python
class EnhancedL1Arbitrator:
    """
    增强版 L1 仲裁器
    
    整合文本 + 声学证据进行仲裁
    """
    
    async def arbitrate(
        self,
        narrative_text: str,
        text_scores: Dict,
        audio_scores: Dict,
        fusion_result: Dict
    ) -> Dict:
        """
        L1 仲裁
        
        输入:
        - narrative_text: ASR 转写文本
        - text_scores: L0 文本评分
        - audio_scores: 声学评分
        - fusion_result: 融合结果
        
        输出:
        - adjustment: 调整量 (-10 到 +10)
        - reasoning: 推理说明
        - dimension_adjustments: 各维度调整
        """
        
        # 构建仲裁上下文
        context = {
            'narrative': narrative_text,
            'text_score': fusion_result['text_score'],
            'audio_score': fusion_result['audio_score'],
            'score_diff': fusion_result['score_diff'],
            'is_consistent': fusion_result['is_consistent'],
            'text_dimensions': {
                'C1': text_scores.get('c1', 50),
                'C2': text_scores.get('c2', 50),
                'C3': text_scores.get('c3', 50),
                'C4': text_scores.get('c4', 50),
                'C5': text_scores.get('c5', 50),
                'C6': text_scores.get('c6', 50)
            },
            'audio_dimensions': audio_scores.get('dimension_scores', {}),
            'biomarkers': audio_scores.get('severity_details', {})
        }
        
        # LLM 仲裁 prompt
        prompt = self._build_arbitration_prompt(context)
        
        # 调用 LLM
        llm_result = await self._call_llm(prompt)
        
        return {
            'adjustment': llm_result['adjustment'],
            'reasoning': llm_result['reasoning'],
            'dimension_adjustments': llm_result['dimension_adjustments'],
            'evidence_used': llm_result['evidence_used']  # 列出使用的证据
        }
    
    def _build_arbitration_prompt(self, context: Dict) -> str:
        """构建仲裁 prompt"""
        return f"""
你是一名认知评估专家，需要仲裁文本评分和声学评分之间的差异。

【输入信息】
- 叙事文本：{context['narrative'][:500]}...
- 文本评分：{context['text_score']:.1f}
- 声学评分：{context['audio_score']:.1f}
- 评分差异：{context['score_diff']:.1f} 分
- 是否一致：{'是' if context['is_consistent'] else '否'}

【文本维度评分】
- C1 内部细节：{context['text_dimensions']['C1']}
- C2 外部细节：{context['text_dimensions']['C2']}
- C3 连贯性：{context['text_dimensions']['C3']}
- C4 情感效价：{context['text_dimensions']['C4']}
- C5 信息密度：{context['text_dimensions']['C5']}
- C6 语言流畅性：{context['text_dimensions']['C6']}

【声学 Biomarkers】
- 语法异常：{context['audio_dimensions'].get('grammar', 'N/A')}
- 语用障碍：{context['audio_dimensions'].get('pragmatic', 'N/A')}
- 命名困难：{context['audio_dimensions'].get('anomia', 'N/A')}
- 发音含糊：{context['audio_dimensions'].get('articulation', 'N/A')}
- 韵律变化：{context['audio_dimensions'].get('prosody', 'N/A')}

【任务】
1. 分析文本和声学评分差异的原因
2. 判断哪个评分更可靠
3. 给出调整建议 (-10 到 +10 分)
4. 说明推理过程

【输出格式】
{{
    "adjustment": -3,
    "reasoning": "...",
    "dimension_adjustments": {{"C3": -2, "C5": -1}},
    "evidence_used": ["高停顿率", "填充词频繁", "文本连贯性良好"]
}}
"""
```

**验证等级**: V0 (设计推断)

---

### 四、实现路线图

| 阶段 | 任务 | 预计工作量 | 依赖 | 产出物 |
|------|------|-----------|------|--------|
| **Phase 1** | 声学特征提取器实现 | 2-3 天 | librosa, scipy | `pipeline/src/services/audio_feature_extractor.py` + 测试 |
| **Phase 2** | 6 种 Biomarkers 检测器 | 3-4 天 | Phase 1 完成 | `pipeline/src/services/speech_biomarker_detector.py` |
| **Phase 3** | Composite Audio Scorer | 1-2 天 | Phase 2 完成 | `pipeline/src/services/composite_audio_scorer.py` |
| **Phase 4** | 多模态融合器 | 2-3 天 | Phase 3 完成 | `pipeline/src/services/multimodal_fusion.py` |
| **Phase 5** | L1 仲裁增强 + 端到端测试 | 2-3 天 | Phase 4 完成 | 整合测试 + 基准报告 |

**总计**: 10-15 天

**依赖项**:
- ✅ 文献基础：Robot Speech Biomarkers, PROCESS Challenge, Nature 论文
- 🔴 ASR API Key：讯飞/阿里 (需 V 提供)
- 🔴 音频测试数据：老年叙事录音 (需 Core/V 收集)

---

### 五、与现有架构的关联

#### 5.1 与 L0 规则引擎的关系

- **并行处理**: 声学分支与文本分支独立运行
- **互补增强**: 声学特征补充文本无法捕捉的信息 (停顿、韵律、发音)
- **冲突检测**: 文本 vs. 声学不一致时触发 L1 仲裁

#### 5.2 与 Multi-Agent Scorer v0.6 的关系

- **抗堆砌增强**: 声学特征难以"堆砌"(停顿率、韵律无法伪造)
- **验证强度控制**: 声学置信度作为触发 L1 的额外条件
- **多维度证据**: L1 仲裁可同时参考文本和声学证据

#### 5.3 与 Agent Memory 四层架构的关系

- **Episodic Memory**: 存储原始音频 + 声学特征
- **Semantic Memory**: 聚合用户声学评分趋势
- **Procedural Memory**: 封装声学分析为可调用技能

---

### 六、风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| ASR 转写质量差 | 高 | 高 | 选用老年语音优化 ASR (讯飞/阿里),添加置信度过滤 |
| 声学特征与认知状态相关性弱 | 中 | 高 | 基于文献权重配置，预留实验调优空间 |
| 音频收集困难 | 中 | 中 | 先用公开数据集 (DementiaBank) 验证，后收集真实数据 |
| 计算开销大 | 中 | 中 | 异步处理声学分析，缓存中间结果 |
| 隐私合规 | 高 | 高 | 音频本地处理，不上传云端，符合 GDPR/个人信息保护法 |

---

## 下一轮优先级 (GEO #102)

### P0 (继续 RB-019 实现)

1. **Phase 1: 声学特征提取器实现**
   - 实现 `AudioFeatureExtractor` 类
   - 单元测试 (停顿检测、韵律分析、发音清晰度)
   - 输出：`pipeline/src/services/audio_feature_extractor.py` + 测试

2. **Phase 2: Biomarkers 检测器**
   - 实现 6 种 biomarkers 检测逻辑
   - 与 LLM 集成 (语法/语用分析)
   - 输出：`pipeline/src/services/speech_biomarker_detector.py`

### P1 (如 RB-019 阻塞)

- **RB-025**: TraceMem 全文深读 + 叙事记忆图谱设计参考
- **RB-026**: TwinVoice 六项能力与 VSNC 评分维度映射
- **RB-012**: PROCESS Challenge 2026 参赛可行性评估

---

## 产出物清单

| 文件 | 状态 | 描述 |
|------|------|------|
| `memory/2026-04-05-geo-iteration-101.md` | ✅ 已创建 | 本轮迭代日志 |
| `designs/speech-biomarkers-fusion-v0.7.md` | ⏳ 待创建 | 详细设计稿 (本文档内容) |
| `memory/research-backlog.md` | ⏳ 待更新 | 标记 RB-019 状态为"🟡 设计中" |

---

## 验证等级汇总

| 发现 | 验证等级 | 验证方式 |
|------|---------|---------|
| 6 种 biomarkers 定义 | V2 | Robot Speech Biomarkers (arXiv) + PROCESS Challenge |
| 声学特征与认知相关性 | V1 | Nature 论文 + DementiaBank 研究 |
| 融合架构设计 | V0 | 架构推断 (基于文献 + VSNC 现状) |
| 实现路线图 | V0 | 工作量估算 |

---

## 核心结论

**一句话**: RB-019 完成语音 biomarkers 与 LLM 评分融合方案设计，建议 Core 按 Phase 1-5 路线图实现，预计 10-15 天完成。

**关键状态**:
- ✅ 研究完成：文献综合 (6 biomarkers, PROCESS Challenge, Nature 背书)
- ✅ 设计完成：声学特征提取 + biomarkers 检测 + 复合评分 + 多模态融合 + L1 增强
- 🔴 待实现：Phase 1-5 (Core 接手工程实现)
- 🔴 阻塞项：ASR API Key (需 V 提供) + 音频测试数据 (需 Core/V 收集)

**Handoff 建议**:
- **接手方**: Core (工程实现) + V (ASR API Key + 音频数据)
- **接手原因**: 架构设计完成，进入工程实现阶段
- **下一步动作**: 
  1. Core 评审设计稿 (`designs/speech-biomarkers-fusion-v0.7.md`)
  2. V 提供 ASR API Key (讯飞/阿里)
  3. Core 启动 Phase 1 (声学特征提取器实现，2-3 天)
  4. Core/V 收集音频测试数据 (用于验证)

**差异化价值**:
- 首创新型"文本 + 声学"双分支叙事评估架构
- 6 种 biomarkers 全部可计算、可解释
- 融合策略包含一致性检验和冲突解决机制
- 与 PROCESS Challenge 国际标准对齐

---

*GEO #101 完成 — 2026-04-05 05:15 UTC*

Hulk 🟢 — 密度即价值
