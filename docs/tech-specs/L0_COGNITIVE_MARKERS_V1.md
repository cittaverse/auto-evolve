# L0 认知特征提取规范 v1.0

> **战略定位**：整个技术体系的制高点  
> **合规红线**：筛查/监测 ≠ 诊断（不做 NMPA 医疗器械）  
> **创建时间**：2026-03-11  
> **版本**：v1.0

---

## 📐 六维度认知特征

### 1. 时间定向力 (Temporal Orientation)

**定义**：对时间、日期、季节的认知准确性

**提取指标**：
| 指标 | 说明 | 评分 |
|------|------|------|
| 时间提及准确率 | 提及年月日/季节/节日的准确性 | 0-10 分 |
| 时间顺序逻辑 | 事件先后顺序是否清晰 | 0-10 分 |
| 时间模糊度 | "那时候/前几天"等模糊词频率 | 频率越高，分越低 |

**示例**：
```
✅ 高分："1965 年春天，我在人民公社干活"
❌ 低分："记不清了，好像是前些年吧"
```

---

### 2. 事件连贯性 (Event Coherence)

**定义**：叙事中事件的逻辑连接和完整性

**提取指标**：
| 指标 | 说明 | 评分 |
|------|------|------|
| 事件分段数 | 可识别的独立事件数量 | 适中为佳 |
| 连接词使用 | "然后/后来/因为所以"等 | 适度使用 |
| 因果逻辑 | 事件间因果关系清晰度 | 0-10 分 |

**示例**：
```
✅ 高分："那年大炼钢铁，因为要交铁锅，所以把家里的锅都砸了"
❌ 低分："大炼钢铁...铁锅...记不清了"
```

---

### 3. 细节丰富度 (Detail Richness)

**定义**：叙事中具体细节的数量和质量

**提取指标**：
| 指标 | 说明 | 评分 |
|------|------|------|
| 人名/地名提及 | 具体人名、地名数量 | 计数 |
| 感官细节 | 视觉/听觉/嗅觉/味觉描述 | 0-10 分 |
| 情感细节 | 当时的心情、感受描述 | 0-10 分 |

**示例**：
```
✅ 高分："杭州下沙的稻田，金黄色的，我跟我哥两个人割稻子，手上都磨出血泡"
❌ 低分："就在地里干活，挺累的"
```

---

### 4. 情感一致性 (Emotional Consistency)

**定义**：情感表达与事件内容的匹配度

**提取指标**：
| 指标 | 说明 | 评分 |
|------|------|------|
| 情感极性匹配 | 正面/负面事件与情感表达一致 | 0-10 分 |
| 情感波动幅度 | 单次对话内情感变化范围 | 过大可能异常 |
| 情感麻木信号 | 重大事件无情感表达 | 警示信号 |

**示例**：
```
✅ 正常："我儿子考上大学，高兴得不得了"（正面事件 + 正面情感）
⚠️ 警示："我老伴走了...唉...就这样吧"（重大负面事件 + 情感平淡）
```

---

### 5. 语言流畅度 (Language Fluency)

**定义**：语言表达的流畅性和完整性

**提取指标**：
| 指标 | 说明 | 评分 |
|------|------|------|
| 平均句长 | 每句话平均字数 | 过短可能异常 |
| 中断频率 | "呃/那个/嗯"等填充词 | 频率越高，分越低 |
| 重复率 | 相同内容重复提及 | 过高可能异常 |

**示例**：
```
✅ 正常："我年轻时候在工厂上班，干了三十多年，一直到退休"
❌ 异常："那个...呃...就是...在厂里...嗯...上班"
```

---

### 6. 自我认知 (Self-Awareness)

**定义**：对自身状态和能力的认知

**提取指标**：
| 指标 | 说明 | 评分 |
|------|------|------|
| 自我肯定 | "我记得/我知道"等肯定表达 | 适度为佳 |
| 自我否定 | "我老了/没用了"等消极表达 | 频率过高警示 |
| 记忆自信 | 对自身记忆的信任度 | 0-10 分 |

**示例**：
```
✅ 正常："我记得很清楚，那时候..."
⚠️ 警示："老了，记性不行了，说过的话就忘"
```

---

## 📊 综合评分算法

```python
def calculate_cognitive_score(markers: dict) -> dict:
    """
    计算认知健康综合评分
    
    输入:
        markers: {
            "temporal_orientation": 8.5,
            "event_coherence": 7.2,
            "detail_richness": 6.8,
            "emotional_consistency": 8.0,
            "language_fluency": 7.5,
            "self_awareness": 8.2
        }
    
    输出:
        {
            "total_score": 7.7,  # 加权平均
            "risk_level": "low",  # low/medium/high
            "trend": "stable",  # stable/declining/improving
            "flags": []  # 警示信号
        }
    """
    
    # 权重配置（可调整）
    weights = {
        "temporal_orientation": 0.20,
        "event_coherence": 0.20,
        "detail_richness": 0.15,
        "emotional_consistency": 0.15,
        "language_fluency": 0.15,
        "self_awareness": 0.15
    }
    
    # 加权平均
    total = sum(markers[k] * weights[k] for k in markers)
    
    # 风险等级
    if total >= 7.0:
        risk_level = "low"
    elif total >= 5.0:
        risk_level = "medium"
    else:
        risk_level = "high"
    
    return {
        "total_score": round(total, 2),
        "risk_level": risk_level,
        "timestamp": datetime.now().isoformat()
    }
```

---

## ⚠️ 合规红线

### 允许使用的术语
- ✅ 认知健康筛查
- ✅ 认知变化监测
- ✅ 认知改善趋势
- ✅ 认知健康评分

### 严禁使用的术语
- ❌ 诊断
- ❌ 治疗
- ❌ 疗效
- ❌ 疾病（如"老年痴呆"）
- ❌ 医疗器械

### 产品文案规范
```
✅ 正确："您的认知健康评分为 7.5 分，处于良好水平"
❌ 错误："您没有老年痴呆症"

✅ 正确："连续 3 次对话显示记忆细节有所下降，建议关注"
❌ 错误："您可能患有轻度认知障碍"
```

---

## 📈 纵向追踪机制

### 认知快照 (Cognitive Snapshot)

每次对话生成一个快照：

```json
{
  "session_id": "20260311_143022_user123",
  "timestamp": "2026-03-11T14:30:22+08:00",
  "markers": {
    "temporal_orientation": 8.5,
    "event_coherence": 7.2,
    "detail_richness": 6.8,
    "emotional_consistency": 8.0,
    "language_fluency": 7.5,
    "self_awareness": 8.2
  },
  "total_score": 7.7,
  "risk_level": "low"
}
```

### 趋势分析

```python
def analyze_trend(snapshots: List[dict]) -> dict:
    """
    分析跨次对话的认知变化趋势
    
    输入：最近 5 次对话的认知快照
    输出：趋势分析结果
    """
    
    # 计算每个维度的斜率
    slopes = {}
    for dim in marker_keys:
        values = [s["markers"][dim] for s in snapshots]
        slopes[dim] = linear_regression_slope(values)
    
    # 判断趋势
    if all(s > 0.1 for s in slopes.values()):
        trend = "improving"
    elif all(s < -0.1 for s in slopes.values()):
        trend = "declining"
    else:
        trend = "stable"
    
    # 黄灯预警：连续 3 次某维度显著下降
    flags = []
    for dim, slope in slopes.items():
        if slope < -0.2 and len([s for s in snapshots if s["markers"][dim] < 6.0]) >= 3:
            flags.append(f"{dim}_declining")
    
    return {
        "trend": trend,
        "flags": flags,
        "recommendation": generate_recommendation(trend, flags)
    }
```

---

## 🔗 与现有系统集成

### narrative_scorer v0.3 → v0.4 升级路径

**当前状态**：v0.3 支持 5 维度内容评分

**升级任务**：
1. [ ] 扩展为 6 维度认知特征
2. [ ] 添加纵向追踪功能
3. [ ] 实现合规术语过滤

**预计完成**：2026-03-17

---

*文档版本：v1.0 | 创建：2026-03-11 13:45 | 负责人：Hulk 🟢*
