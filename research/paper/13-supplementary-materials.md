# Supplementary Materials — CittaVerse Narrative Scorer

**版本**: v1.0  
**日期**: 2026-03-31 00:45 UTC  
**作者**: Hulk 🟢  
**用途**: arXiv 论文 Appendix 直接素材 (app:prompts, app:scales)

---

## Appendix A: Prompt Templates (for LLM-enhanced version)

### A.1 Event Boundary Detection Prompt (Chinese)

```
你是一位专业的叙事分析助手。请分析以下口述文本，识别事件边界。

【输入文本】
{transcript}

【任务】
1. 识别文本中的事件边界（事件转换点）
2. 为每个事件分配一个简短标签
3. 输出格式：JSON

【事件边界判断标准】
- 时间变化（如"后来"、"第二天"、"那年夏天"）
- 地点变化（如"到了学校"、"回到家"）
- 人物变化（如"我和同事"、"后来我一个人"）
- 主题/活动变化（如"开始工作后"、"下班后"）
- 情感/态度转折（如"但是"、"然而"、"没想到"）

【输出格式】
{
  "events": [
    {
      "event_id": 1,
      "start_char": 0,
      "end_char": 150,
      "label": "童年回忆 - 上学第一天",
      "boundary_cues": ["时间词", "地点词"],
      "text_snippet": "我记得那天早上..."
    },
    ...
  ],
  "total_events": 5,
  "avg_event_length_chars": 120
}

【注意】
- 事件长度通常在 50-300 字之间
- 不要过度分段，保持事件的自然完整性
- 如果文本很短（<200 字），可能只有 1-2 个事件
```

---

### A.2 Six-Dimension Scoring Prompt (Chinese)

```
你是一位专业的叙事质量评估专家。请根据以下六维框架评估口述文本的质量。

【输入文本】
{transcript}

【六维评估框架】

1. **具体性 (Specificity)**
   - 评估：是否包含具体的感官细节、时间、地点、人物
   - 高分特征：视觉/听觉/嗅觉/触觉细节，具体日期/年龄，明确地点
   - 低分特征：概括性陈述，模糊时间（"那时候"、"以前"）

2. **情感性 (Emotionality)**
   - 评估：是否表达情感体验及其变化
   - 高分特征：明确情感词汇，情感变化过程，情感与事件关联
   - 低分特征：纯事实陈述，无情感表达

3. **连贯性 (Coherence)**
   - 评估：事件之间的逻辑连接和因果关系
   - 高分特征：清晰的时间线，因果连接词，主题一致
   - 低分特征：跳跃式叙述，缺乏连接，主题散乱

4. **反思性 (Reflectiveness)**
   - 评估：是否对经历进行意义建构和自我反思
   - 高分特征："我意识到"、"这让我明白"、"现在想来"，成长/变化描述
   - 低分特征：纯事件罗列，无意义建构

5. **生动性 (Vividness)**
   - 评估：叙述的生动程度和画面感
   - 高分特征：对话引用，动作描写，场景再现
   - 低分特征：抽象概括，缺乏画面感

6. **完整性 (Completeness)**
   - 评估：事件是否有清晰的开始、经过、结束
   - 高分特征：完整的事件结构，有头有尾
   - 低分特征：片段式叙述，缺少关键部分

【输出格式】
{
  "scores": {
    "specificity": {"score": 4.2, "evidence": ["包含具体日期", "描述了房间布置"]},
    "emotionality": {"score": 3.5, "evidence": ["表达了紧张情绪", "情感变化清晰"]},
    "coherence": {"score": 4.0, "evidence": ["时间线清晰", "因果连接充分"]},
    "reflectiveness": {"score": 3.8, "evidence": ["有自我反思", "描述了成长"]},
    "vividness": {"score": 4.5, "evidence": ["有对话引用", "场景描写生动"]},
    "completeness": {"score": 4.0, "evidence": ["事件结构完整", "有头有尾"]}
  },
  "overall_score": 4.0,
  "strengths": ["生动性高", "具体性好"],
  "areas_for_improvement": ["可增加更多反思"],
  "word_count": 450
}

【评分标准】
- 1 分：完全缺失该维度特征
- 2 分：少量特征，不明显
- 3 分：中等水平，基本达标
- 4 分：良好，特征清晰
- 5 分：优秀，特征突出且丰富
```

---

### A.3 Meta-memory Strategy Prompt (Chinese)

```
你是一位温暖的回忆引导助手。基于用户的叙事质量评分，提供个性化的元记忆策略建议。

【输入】
- 用户六维评分：{scores_json}
- 用户当前主题：{current_theme}
- 历史表现：{history_summary}

【任务】
生成 1-2 条具体、可操作的元记忆策略建议，帮助用户提升叙事质量。

【策略库】

**针对具体性低**:
- "试着回忆当时的具体场景：你看到了什么？听到了什么？闻到了什么？"
- "能说说那天是星期几吗？大概几点钟？天气怎么样？"
- "当时还有谁在场？他们穿了什么衣服？说了什么话？"

**针对情感性低**:
- "那时候你心里是什么感觉？紧张？兴奋？还是害怕？"
- "这件事对你的情绪有什么影响？你后来想起来会怎么感受？"

**针对连贯性低**:
- "这件事是怎么开始的？后来发生了什么？最后怎么样了？"
- "这两件事之间有什么联系吗？为什么会从这件事说到那件事？"

**针对反思性低**:
- "现在回想起来，这件事对你有什么意义？"
- "经历了这件事后，你有什么变化或收获吗？"
- "如果重来一次，你会有什么不同的做法吗？"

**针对生动性低**:
- "当时你们有对话吗？能模仿一下当时的语气吗？"
- "能描述一下当时的动作吗？比如你是怎么做的？"

**针对完整性低**:
- "这件事最开始是怎么发生的？"
- "后来呢？这件事最后怎么样了？"

【输出格式】
{
  "strategies": [
    {
      "dimension": "具体性",
      "current_score": 2.5,
      "suggestion": "试着回忆当时的具体场景：你看到了什么？听到了什么？",
      "rationale": "当前叙述以概括为主，缺少感官细节"
    }
  ],
  "encouragement": "您的叙述在生动性方面表现很好，继续保持！",
  "next_theme_suggestion": "童年友谊"
}

【语气要求】
- 温暖、支持性，避免评判性语言
- 具体、可操作，避免抽象建议
- 先肯定优势，再提出改进建议
```

---

## Appendix B: Assessment Scales (Chinese translations)

### B.1 System Usability Scale (SUS) — 中文版

**来源**: Brooke, J. (1996). SUS: A "quick and dirty" usability scale.

**指导语**: 请根据您的实际使用体验，对以下陈述进行评分。1=非常不同意，5=非常同意。

| 题号 | 题目 | 1 | 2 | 3 | 4 | 5 |
|------|------|---|---|---|---|---|
| 1 | 我愿意经常使用这个系统 | ○ | ○ | ○ | ○ | ○ |
| 2 | 我觉得这个系统过于复杂 | ○ | ○ | ○ | ○ | ○ |
| 3 | 我觉得这个系统很容易使用 | ○ | ○ | ○ | ○ | ○ |
| 4 | 我觉得需要技术人员帮助才能使用这个系统 | ○ | ○ | ○ | ○ | ○ |
| 5 | 我觉得这个系统的各项功能整合得很好 | ○ | ○ | ○ | ○ | ○ |
| 6 | 我觉得这个系统有太多不一致的地方 | ○ | ○ | ○ | ○ | ○ |
| 7 | 我想大多数人会很快学会使用这个系统 | ○ | ○ | ○ | ○ | ○ |
| 8 | 我觉得这个系统用起来很麻烦 | ○ | ○ | ○ | ○ | ○ |
| 9 | 使用这个系统让我感到自信 | ○ | ○ | ○ | ○ | ○ |
| 10 | 在使用这个系统之前，我需要学习很多东西 | ○ | ○ | ○ | ○ | ○ |

**计分方法**:
1. 奇数题 (1,3,5,7,9): 得分 = 选项值 - 1
2. 偶数题 (2,4,6,8,10): 得分 = 5 - 选项值
3. 总分 = 所有题目得分之和 × 2.5
4. 总分范围：0-100

**解释**:
- ≥68: 高于平均水平 (及格)
- ≥80.3: 良好 (A 级)
- ≥85.5: 优秀 (A+ 级)

---

### B.2 Net Promoter Score (NPS) — 中文版

**来源**: Reichheld, F. F. (2003). The one number you need to grow. Harvard Business Review.

**问题**: 您向朋友或同事推荐这个系统的可能性有多大？

| 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 完全不可能 | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ○ | 极有可能 |

**计分方法**:
- 贬损者 (Detractors): 0-6 分
- 被动者 (Passives): 7-8 分
- 推荐者 (Promoters): 9-10 分

**NPS 计算**:
```
NPS = (推荐者人数 / 总人数) × 100 - (贬损者人数 / 总人数) × 100
```

**NPS 范围**: -100 到 +100

**解释**:
- >0: 良好
- ≥30: 优秀
- ≥50: 极佳
- ≥70: 世界级

---

### B.3 Technology Anxiety Scale — 技术焦虑量表 (中文版)

**来源**: 改编自 Meier, S. T. (1985). Toward a psychology of computers.

**指导语**: 请根据您使用电子设备/APP 时的感受，对以下陈述进行评分。1=非常不同意，5=非常同意。

| 题号 | 题目 | 1 | 2 | 3 | 4 | 5 |
|------|------|---|---|---|---|---|
| 1 | 我担心会不小心弄坏这个系统 | ○ | ○ | ○ | ○ | ○ |
| 2 | 使用新系统让我感到紧张 | ○ | ○ | ○ | ○ | ○ |
| 3 | 我担心按错按钮会导致问题 | ○ | ○ | ○ | ○ | ○ |
| 4 | 学习使用新系统让我感到有压力 | ○ | ○ | ○ | ○ | ○ |
| 5 | 我担心系统会"死机"或出错 | ○ | ○ | ○ | ○ | ○ |
| 6 | 使用电子设备时我感到不自在 | ○ | ○ | ○ | ○ | ○ |

**计分方法**:
- 总分 = 所有题目得分之和
- 总分范围：6-30
- 分数越高，技术焦虑程度越高

**解释**:
- 6-12: 低焦虑
- 13-20: 中等焦虑
- 21-30: 高焦虑

---

### B.4 Privacy Concerns Scale — 隐私关注量表 (中文版)

**来源**: 改编自 Iivari, M., & Iivari, N. (2013). The relationship between age and user behavior.

**指导语**: 请根据您对个人信息保护的关注程度，对以下陈述进行评分。1=非常不同意，5=非常同意。

| 题号 | 题目 | 1 | 2 | 3 | 4 | 5 |
|------|------|---|---|---|---|---|
| 1 | 我担心我的个人信息会被泄露 | ○ | ○ | ○ | ○ | ○ |
| 2 | 我担心系统会记录我的隐私对话 | ○ | ○ | ○ | ○ | ○ |
| 3 | 我不确定我的数据会被如何使用 | ○ | ○ | ○ | ○ | ○ |
| 4 | 我希望有更多关于数据使用的透明度 | ○ | ○ | ○ | ○ | ○ |
| 5 | 我担心我的故事会被他人看到 | ○ | ○ | ○ | ○ | ○ |
| 6 | 我对分享个人回忆感到不安 | ○ | ○ | ○ | ○ | ○ |

**计分方法**:
- 总分 = 所有题目得分之和
- 总分范围：6-30
- 分数越高，隐私关注程度越高

**解释**:
- 6-12: 低关注
- 13-20: 中等关注
- 21-30: 高关注

---

## Appendix C: Source Code Repository

**GitHub**: https://github.com/cittaverse/narrative-scorer  
**License**: MIT  
**Version**: v0.6  
**DOI**: [To be added after arXiv submission]

### C.1 Repository Structure

```
narrative-scorer/
├── README.md                 # 项目说明与安装指南
├── LICENSE                   # MIT License
├── requirements.txt          # Python 依赖
├── setup.py                  # 安装脚本
├── narrative_scorer/
│   ├── __init__.py
│   ├── scorer.py             # 六维评分核心算法
│   ├── event_segmentation.py # 事件边界检测 (v2)
│   ├── prompts/              # Prompt 模板
│   │   ├── event_boundary.txt
│   │   ├── six_dimension.txt
│   │   └── meta_memory.txt
│   └── utils/
│       ├── preprocessing.py  # 文本预处理
│       └── metrics.py        # 评估指标计算
├── tests/
│   ├── test_scorer.py
│   └── test_event_segmentation.py
├── examples/
│   ├── sample_transcript.txt
│   └── sample_output.json
└── docs/
    ├── api.md                # API 文档
    └── user_guide.md         # 用户指南
```

### C.2 Installation

```bash
# 从 GitHub 安装
pip install git+https://github.com/cittaverse/narrative-scorer.git

# 或本地安装
git clone https://github.com/cittaverse/narrative-scorer.git
cd narrative-scorer
pip install -e .
```

### C.3 Usage Example

```python
from narrative_scorer import SixDimensionScorer

# 初始化评分器
scorer = SixDimensionScorer(model="qwen-plus")

# 评分
transcript = "我记得那天早上，阳光透过窗帘照进来..."
result = scorer.score(transcript)

# 输出
print(f"Overall Score: {result['overall_score']}")
print(f"Dimension Scores: {result['scores']}")
```

### C.4 Citation

```bibtex
@software{narrative_scorer_2026,
  author = {CittaVerse Team},
  title = {CittaVerse Narrative Scorer: Six-Dimension Assessment for Chinese Autobiographical Memory Quality},
  version = {0.6},
  year = {2026},
  url = {https://github.com/cittaverse/narrative-scorer},
  license = {MIT}
}
```

---

*Hulk 🟢 — Supplementary Materials v1.0 — 2026-03-31 00:45 UTC*
