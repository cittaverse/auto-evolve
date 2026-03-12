# CittaVerse Pipeline - 使用指南

> 5 分钟快速上手神经符号叙事评估

---

## 快速开始

### 安装

```bash
git clone https://github.com/cittaverse/pipeline
cd pipeline
pip install -r requirements.txt
```

### 基础使用

```python
from src.assessor import NarrativeAssessor

# 初始化评估器
assessor = NarrativeAssessor()

# 评估叙事文本
narrative = "我退休那年开始学习书法，现在每天去公园练习。"
result = assessor.evaluate(narrative)

# 输出结果
print(f"连贯性分数：{result.coherence_score}")
print(f"质量等级：{result.quality_level}")
print(f"建议：{result.recommendations}")
```

### 命令行使用

```bash
python -m src.assessor --text "我退休那年开始学习书法..."
python -m src.assessor --file input.txt --output result.json
```

---

## 效果对比

### Before（无评估）

```
用户输入："我退休那年开始学习书法，现在每天去公园练习。"
输出：无结构化反馈
```

### After（使用 Pipeline）

```json
{
  "coherence_score": 0.33,
  "quality_level": "中",
  "events": [
    {"content": "退休那年开始学习书法", "time": "退休那年"},
    {"content": "每天去公园练习", "time": "现在"}
  ],
  "recommendations": [
    "叙事连贯性较低，建议引导老人补充事件间的关联"
  ]
}
```

---

## 常见场景

### 场景 1：临床评估

```python
assessor = NarrativeAssessor(clinical_mode=True)
result = assessor.evaluate(patient_narrative)
report = assessor.generate_clinical_report(result)
```

### 场景 2：批量处理

```python
narratives = load_narratives("data/")
results = [assessor.evaluate(n) for n in narratives]
assessor.export_results(results, "output.csv")
```

---

## FAQ

**Q: 支持哪些语言？**  
A: 目前优化中文，英文支持测试中。

**Q: 评估需要多长时间？**  
A: 单条叙事约 2-5 秒（取决于 LLM API 响应）。

**Q: 如何自定义评分标准？**  
A: 修改 `src/scoring.py` 中的权重配置。

---

*文档版本：v0.4 | 更新：2026-03-10*
