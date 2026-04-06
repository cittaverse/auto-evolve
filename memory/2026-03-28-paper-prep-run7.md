# 2026-03-28 — 学术论文准备 (Paper Prep Cron Run #7)

**时间**: 2026-03-28 02:45 UTC  
**触发**: cron hulk-paper-prep-001  
**状态**: ✅ 完成

---

## 断点确认

从 Run #6 (2026-03-27) 留下的 TODO 继续：
1. LaTeX 版本同步 (paper.tex v1.0→v1.1) — 本轮完成
2. C 级引用继续验证 — 延至 Run #8（等 API 额度恢复）
3. arXiv 提交执行 — 待 V 操作
4. Pilot RCT 伦理审批提交 — 待 V 执行

---

## 本轮产出

### 1. LaTeX 论文正文升级 (`paper.tex` v1.0→v1.1)

**文件**: `research/arxiv-paper/paper.tex`  
**变更**: 465 行 → ~550 行，同步 paper-draft-v1.1.md v0.6 内容

#### 1.1 核心升级

| 章节 | 变更 |
|------|------|
| **标题** | v0.5 → v0.6, 添加 "with Event Boundary Detection" |
| **Abstract** | 添加事件边界检测 v2 描述 (F1 > 0.75)、8-week intervention |
| **§1.3 Contribution** | 添加第 4 点：Event boundary detection v2 |
| **§2.3 LLM-Based Evaluation** | 新增 4 段：CheckEval 范式、LLM 事件分割、Context Sequentiality、PD Narrative NLP |
| **§2.6 Gap Analysis** | 添加 Rememo 行、Rememo 深度对比、Dolphin 方言 ASR 对比 |
| **§3.4 Event Boundary Detection v2** | 新增完整算法描述 (4 步流程、性能目标、验证方法) |
| **§4.4 Output Format** | 添加 event_boundaries 字段说明 |
| **§5.2 Validation Metrics** | 添加 Event detection accuracy (F1 > 0.75) |
| **§7.1 Limitations** | 添加 Event boundary detection v2 requires further validation |
| **§7.2 Future Directions** | 添加 Checklist-based LLM scoring、Cognitive dimension extraction |
| **Conclusion** | 更新为 v0.6，提及事件边界检测 |
| **Appendix Version** | v0.5 → v0.6 |
| **References** | 引用 key 修正 (diamond2013, mcadams2013, fraser2015) |

#### 1.2 事件边界检测 v2 描述 (§3.4)

完整算法描述包含 4 步流程：
1. Sentence-level feature extraction (temporal marker, location change, subject/agent change, verb tense/aspect change, topic keyword shift)
2. Topic transition detection (sentence embeddings, cosine similarity < 0.65)
3. Boundary smoothing (merge within 2-sentence window, enforce min event length ≥2 sentences)
4. Output: Binary boundary labels per sentence

**性能目标**:
- Precision: > 0.75
- Recall: > 0.75
- F1: > 0.75 (vs human annotation)
- Boundary tolerance F1 (±1 sentence): > 0.80

**验证方法**: 2 名训练评估者独立标注，Cohen's κ > 0.70

#### 1.3 新增文献整合 (§2.3, §2.6, §7.2)

**CheckEval 范式** [checkeval2024, autochecklist2026, healthcare_llm_judge2025]:
- 二元 checklist 分解替代直接 Likert 评分
- ICC 提升 +0.45，方差降低
- Healthcare LLM-Judge ICC=0.818
- 直接指导 v0.7 LLM 增强层设计

**LLM 事件分割** [llm_narrative_seg2023, llm_event_seg2025]:
- Michelmann et al. (2023): LLM 事件分割与人类一致性
- Event Segmentation + Recall (arXiv:2502.13349): LLM chat completion 自动识别事件边界，一致性 > 人类 - 人类
- 为 v0.6 事件边界检测器提供方法论支撑

**Context Sequentiality** [sequentiality2025]:
- Sentence-to-sentence 叙事流畅度特征 (topic + contextual term)
- Context-only 优于 topic-only 和 zero-shot LLM
- 可作为 hybrid scoring 规则层可解释特征

**PD Narrative NLP** [pd_narrative_nlp2025]:
- 7 类认知维度自动提取 (thought, emotion, social interaction, location, time...)
- Fine-tuned Llama-3-8B (QLoRA) F1=0.74 micro
- 验证 instruction-tuned LLM > BERT
- 7 类与 VSNC 六维度高度重叠

**Rememo 深度对比** [rememo2026]:
- CHI 2026, arXiv:2602.17083
- Therapist-first (B2B) vs CittaVerse B2B2C
- GenAI 图像触发 vs 叙事 NLP+ 六维评分
- 互相验证非直接竞争

**Dolphin 方言 ASR** [dolphin2025]:
- 22 种中文方言支持 (含粤语、吴语)
- 开源，v0.6 方言 ASR 首选候选
- 需老年人口语场景验证 WER/CER

#### 1.4 引用 key 修正

| 旧 key | 新 key | 原因 |
|--------|--------|------|
| goldmanrakic2024 | diamond2013 | 作者已故 (2003), 原条目无效 |
| mcadams2024 | mcadams2013 | 经典论文实际年份 2013 |
| fraser2024 | fraser2015 | Semantic Scholar V4 验证实际年份 2015 |

### 2. 状态看板更新

`research/paper/00-paper-prep-status.md` 同步更新 Run #7 完成状态。

---

## 待完成事项

| 事项 | 优先级 | 依赖 | 预计 Run |
|------|--------|------|----------|
| LaTeX 编译测试 (pdflatex/xelatex) | 高 | 本地 TeX 环境 | Run #8 |
| C 级引用继续验证 | 低 | Serper/S2 API 额度恢复 | Run #8+ |
| arXiv 提交执行 | 高 | V 操作账号 | 待 V 确认 |
| Pilot RCT 伦理审批提交 | 高 | V 审阅 | 待 V 执行 |

---

## 验证等级

| 产出 | 验证等级 | 说明 |
|------|----------|------|
| LaTeX 升级 | V3 | 静态复核 — 与 paper-draft-v1.1.md v0.6 交叉确认 |
| 事件边界检测 v2 描述 | V3 | 基于文献 [llm_narrative_seg2023, llm_event_seg2025] 方法论，算法描述已复核 |
| 文献整合 | V2 | 多来源交叉确认 (arXiv API 验证 4 条) |
| 引用 key 修正 | V4 | Semantic Scholar API 动态验证 (fraser2015) |

---

## 下一步 (Run #8 优先级)

1. **LaTeX 编译测试** — 验证 paper.tex 可成功编译为 PDF
2. **C 级引用继续验证** — 等 API 额度恢复
3. **arXiv 提交执行** — 待 V 确认时间
4. **Pilot RCT 伦理审批提交** — 待 V 执行

---

*Hulk 🟢 — Paper Prep Run #7 完成*
