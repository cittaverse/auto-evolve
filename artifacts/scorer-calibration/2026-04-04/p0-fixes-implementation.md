# P0 修复实施计划

**优先级**: P0 (高)  
**预计总工作量**: 7 小时  
**目标完成**: 2026-04-05

---

## 修复 1: 风险词假阳性 (2 小时)

**文件**: `pipeline/emotional_arousal_detector.py` 或独立风险检测模块

**当前问题**:
```python
# 当前实现：简单关键词匹配
if "不想活了" in text:
    risk_level = "high"  # ❌ 忽略语境
```

**修复方案**:

```python
# 新增：语境否定检测
RISK_KEYWORDS = [
    "不想活了", "死了算了", "活着受罪", "活够了",
    "没意思", "太累了", "撑不下去了"
]

NEGATION_PATTERNS = [
    r"开玩笑的", r"只是说说", r"别当真", r"哈哈哈",
    r"这是歌词", r"电影台词", r"开玩笑", r"逗你玩",
    r"随口一说", r"说着玩的", r"不是真的"
]

def assess_suicide_risk(text):
    """
    评估自杀风险 (语境感知)
    
    Returns:
        dict: {"level": "none"|"low"|"medium"|"high", "reason": str}
    """
    has_risk_keyword = any(kw in text for kw in RISK_KEYWORDS)
    
    if not has_risk_keyword:
        return {"level": "none", "reason": "无风险词"}
    
    # 检查否定/玩笑语境
    has_negation = any(re.search(p, text, re.IGNORECASE) for p in NEGATION_PATTERNS)
    
    # 检查上下文距离 (风险词和否定词是否在同一个句子)
    sentences = re.split(r'[。！？!?]', text)
    risk_in_same_sentence_as_negation = False
    
    for sentence in sentences:
        has_kw = any(kw in sentence for kw in RISK_KEYWORDS)
        has_neg = any(re.search(p, sentence, re.IGNORECASE) for p in NEGATION_PATTERNS)
        if has_kw and has_neg:
            risk_in_same_sentence_as_negation = True
            break
    
    if has_negation and risk_in_same_sentence_as_negation:
        return {"level": "low", "reason": "风险词出现在玩笑/否定语境"}
    elif has_negation:
        return {"level": "medium", "reason": "风险词但存在否定信号 (跨句)"}
    else:
        return {"level": "high", "reason": "风险词无语境否定"}
```

**测试用例**:
```python
test_cases = [
    ("我不想活了...开玩笑的", "low"),
    ("死了算了...哈哈哈这是歌词", "low"),
    ("活着受罪...电影台词而已", "low"),
    ("我不想活了，太痛苦了", "high"),
    ("活着没意思，每天都这样", "high"),
]
```

---

## 修复 2: LREF 关键词堆砌欺骗 (3 小时)

**文件**: `github-repos/narrative-scorer/src/llm_feature_extractor.py` 或 LREF 判定模块

**当前问题**:
```python
# 当前实现：基于关键词频率
l3_keywords = ["现在想想", "后来才懂", "意义", "人生", "总结", "传承"]
count = sum(text.count(kw) for kw in l3_keywords)
if count >= 5:
    lref_stage = "L4"  # ❌ 容易被堆砌欺骗
```

**修复方案**:

```python
def check_keyword_stuffing(text, keywords_found):
    """
    检测关键词堆砌
    
    Returns:
        bool: True if stuffing detected
    """
    if len(keywords_found) < 3:
        return False
    
    # 1. 关键词密度检查
    total_keyword_chars = sum(len(kw) for kw in keywords_found)
    keyword_density = total_keyword_chars / max(len(text), 1)
    
    if keyword_density > 0.5:  # 关键词占文本 50% 以上
        return True
    
    # 2. 关键词重复模式检查
    from collections import Counter
    counter = Counter(keywords_found)
    most_common_count = counter.most_common(1)[0][1]
    
    if most_common_count > 3:  # 任一关键词重复>3 次
        return True
    
    # 3. 语义连贯性检查 (连接词比例)
    connectors = ["的", "了", "是", "在", "和", "与", "及", "而", "但", "或"]
    connector_count = sum(text.count(c) for c in connectors)
    connector_ratio = connector_count / max(len(text), 1)
    
    if connector_ratio < 0.05:  # 连接词比例<5%
        return True
    
    # 4. 语法完整性检查 (标点符号比例)
    punctuation = "，。！？；：、"
    punct_count = sum(text.count(p) for p in punctuation)
    punct_ratio = punct_count / max(len(text), 1)
    
    if punct_ratio < 0.02:  # 标点比例<2%
        return True
    
    return False

def determine_lref_stage(text, features):
    """
    判定 LREF 阶段 (防堆砌版本)
    
    Returns:
        str: "L0"|"L1"|"L2"|"L3"|"L4"
    """
    # 提取关键词
    keywords_found = extract_lref_keywords(text)
    
    # 检查堆砌
    if check_keyword_stuffing(text, keywords_found):
        # 强制降级到 L2
        return min(calculate_stage_from_keywords(keywords_found), "L2")
    
    # 正常判定流程
    return calculate_stage_from_keywords(keywords_found)
```

**测试用例**:
```python
test_cases = [
    # 堆砌案例 (应降级到 L2)
    ("现在想想当时不明白后来才懂后悔庆幸意义一生这辈子人生总结传承留给现在想想", "L2"),
    ("意义意义意义人生人生人生总结总结传承传承", "L2"),
    
    # 正常案例 (应正常判定)
    ("现在想想，那时候虽然不明白，但后来才懂得其中的意义。", "L3/L4"),
    ("这件事对我的人生影响很大，至今仍在思考。", "L3"),
]
```

---

## 修复 3: temporal_coherence 区分度优化 (2 小时)

**文件**: `github-repos/narrative-scorer/src/scorer.py`

**当前问题**:
```python
# 当前实现：仅基于时间标记覆盖率
def calculate_temporal_coherence(events):
    events_with_time = sum(1 for e in events if e.time_marker)
    ratio = events_with_time / len(events)
    return ratio * 100  # ❌ 所有完整叙事都接近 100
```

**修复方案**:

```python
def calculate_temporal_coherence_v2(events, text):
    """
    时间连贯性评分 v2 (增加区分度)
    
    评分维度:
    1. 时间标记覆盖率 (40%)
    2. 时间标记多样性 (30%)
    3. 时间线一致性 (30%)
    """
    if not events:
        return 0.0
    
    # 1. 覆盖率 (40 分)
    events_with_time = sum(1 for e in events if e.time_marker)
    coverage_score = (events_with_time / len(events)) * 40
    
    # 2. 多样性 (30 分)
    time_markers = [e.time_marker for e in events if e.time_marker]
    unique_markers = len(set(time_markers))
    
    # 多样性评分：基于唯一标记数量 (目标：5+ 种不同标记)
    diversity_score = min(unique_markers / 5.0, 1.0) * 30
    
    # 3. 一致性检查 (30 分)
    consistency_score = check_timeline_consistency(events)
    
    total_score = coverage_score + diversity_score + consistency_score
    return min(total_score, 100.0)

def check_timeline_consistency(events):
    """
    检查时间线一致性
    
    检测:
    - 时间跳跃 (无过渡)
    - 时间矛盾 (先后顺序冲突)
    - 时间模糊 (大量"那时候"等模糊标记)
    
    Returns:
        float: 0-30 分
    """
    if len(events) < 2:
        return 30.0  # 单事件无需检查一致性
    
    vague_markers = ["那时候", "当时", "后来", "之前", "之后"]
    specific_markers = ["1978 年", "3 月 15 日", "早上 8 点", "小学三年级", "退休后"]
    
    vague_count = 0
    specific_count = 0
    
    for e in events:
        if e.time_marker:
            if any(vm in e.time_marker for vm in vague_markers):
                vague_count += 1
            elif any(sm in e.time_marker for sm in specific_markers):
                specific_count += 1
    
    # 模糊标记过多扣分
    if len(events) > 0:
        vague_ratio = vague_count / len(events)
        if vague_ratio > 0.8:
            return 15.0  # 大部分时间标记模糊
        elif vague_ratio > 0.5:
            return 22.0  # 一半以上模糊
    
    return 30.0  # 时间线一致
```

**测试用例**:
```python
test_cases = [
    # 高区分度案例
    (
        [{"time": "1978 年"}, {"time": "3 月"}, {"time": "第二天"}, {"time": "现在"}],
        "expected: 85-95 (多样性好)"
    ),
    (
        [{"time": "那时候"}, {"time": "当时"}, {"time": "后来"}, {"time": "那时候"}],
        "expected: 50-65 (模糊标记过多)"
    ),
    (
        [{"time": None}, {"time": None}, {"time": None}],
        "expected: 0-30 (无时间标记)"
    ),
]
```

---

## 验证流程

### 单元测试

```bash
cd github-repos/narrative-scorer
python -m pytest tests/test_risk_detection.py -v
python -m pytest tests/test_keyword_stuffing.py -v
python -m pytest tests/test_temporal_coherence.py -v
```

### 集成测试

```bash
# 运行完整 L0 测试套件
python tests/l0_test_optimized.py

# 运行鲁棒性测试
python tests/test_robustness.py
```

### 验收标准

| 修复项 | 验收标准 | 验证方法 |
|-------|---------|---------|
| 风险词假阳性 | 假阳性率 < 5% | 10 个玩笑语境测试全部通过 |
| LREF 堆砌欺骗 | 检测准确率 > 90% | 10 个堆砌案例全部降级到 L2 |
| temporal_coherence | 标准差 > 5 | 5 种叙事类型分数差异明显 |

---

## 回滚计划

如修复引入新问题，回滚步骤：

1. Git 回滚到修复前版本：
   ```bash
   git checkout HEAD~3 -- pipeline/emotional_arousal_detector.py
   git checkout HEAD~3 -- github-repos/narrative-scorer/src/scorer.py
   ```

2. 重新运行测试验证：
   ```bash
   python tests/l0_test_optimized.py
   ```

3. 记录问题到 `memory/YYYY-MM-DD.md`

---

**负责人**: Hulk 🟢  
**审核人**: V  
**状态**: 待实施
