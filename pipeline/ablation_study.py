#!/usr/bin/env python3
"""
L0/VSNC 模型消融实验主脚本

执行单组件消融、组合消融、极端配置对比实验
测量各组件对评分质量、稳定性、一致性的贡献

使用方法:
    python3 ablation_study.py --experiment single      # 单组件消融 (8 配置)
    python3 ablation_study.py --experiment grouped     # 组合消融 (16 配置)
    python3 ablation_study.py --experiment extreme     # 极端配置 (5 配置)
    python3 ablation_study.py --experiment all         # 全部实验 (128 配置)

输出:
    - results/ablation_results_{timestamp}.json
    - results/ablation_summary_{timestamp}.md
"""

import os
import sys
import json
import time
import argparse
import statistics
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path

# 添加 pipeline 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================================
# 配置
# ============================================================================

@dataclass
class AblationConfig:
    """消融配置 (v0.6 基线：C2/C6 已移除)"""
    name: str
    description: str
    # 组件开关
    enable_arousal: bool = True          # C1: 情绪唤醒度检测
    enable_dynamic_ratio: bool = False   # C2: 动态理想比例 (v0.6: 默认关闭，使用固定 60/40)
    enable_llm_event_extract: bool = True  # C3: LLM 事件提取
    enable_full_l0: bool = True          # C4: 完整 L0 六维评分
    enable_multi_agent: bool = True      # C5: 多 Agent 评委
    enable_voting: bool = False          # C6: 投票加权 (v0.6: 默认关闭，使用简单平均)
    enable_arbitration: bool = True      # C7: 仲裁机制


# 单组件消融配置 (8 种)
# v0.6 基线：C2/C6 已移除，C7 阈值从 15 上调至 20
SINGLE_COMPONENT_ABLATIONS = [
    AblationConfig(
        name="full_v0.6",
        description="L0 v0.6 简化架构 (C2/C6 移除，C7 阈值 20)",
        enable_arousal=True,
        enable_dynamic_ratio=False,  # C2 移除
        enable_llm_event_extract=True,
        enable_full_l0=True,
        enable_multi_agent=True,
        enable_voting=False,  # C6 移除
        enable_arbitration=True
    ),
    AblationConfig(
        name="full_v0.5",
        description="完整系统 v0.5 (所有组件开启，用于对比)",
        enable_arousal=True,
        enable_dynamic_ratio=True,
        enable_llm_event_extract=True,
        enable_full_l0=True,
        enable_multi_agent=True,
        enable_voting=True,
        enable_arbitration=True
    ),
    AblationConfig(
        name="w/o_C1_arousal",
        description="关闭情绪唤醒度检测",
        enable_arousal=False,
        enable_dynamic_ratio=False,  # 依赖 C1
        enable_llm_event_extract=True,
        enable_full_l0=True,
        enable_multi_agent=True,
        enable_voting=True,
        enable_arbitration=True
    ),
    AblationConfig(
        name="w/o_C2_dynamic_ratio",
        description="关闭动态理想比例 (使用固定 60/40)",
        enable_arousal=True,
        enable_dynamic_ratio=False,
        enable_llm_event_extract=True,
        enable_full_l0=True,
        enable_multi_agent=True,
        enable_voting=True,
        enable_arbitration=True
    ),
    AblationConfig(
        name="w/o_C3_llm_event",
        description="关闭 LLM 事件提取 (使用规则启发式)",
        enable_arousal=True,
        enable_dynamic_ratio=True,
        enable_llm_event_extract=False,
        enable_full_l0=True,
        enable_multi_agent=True,
        enable_voting=True,
        enable_arbitration=True
    ),
    AblationConfig(
        name="w/o_C4_simplified_l0",
        description="简化 L0 评分 (仅 3 维)",
        enable_arousal=True,
        enable_dynamic_ratio=True,
        enable_llm_event_extract=True,
        enable_full_l0=False,
        enable_multi_agent=True,
        enable_voting=True,
        enable_arbitration=True
    ),
    AblationConfig(
        name="w/o_C5_single_judge",
        description="单一评委 (非多 Agent)",
        enable_arousal=True,
        enable_dynamic_ratio=True,
        enable_llm_event_extract=True,
        enable_full_l0=True,
        enable_multi_agent=False,
        enable_voting=False,  # 依赖 C5
        enable_arbitration=False,  # 依赖 C5
    ),
    AblationConfig(
        name="w/o_C6_simple_average",
        description="简单平均 (非置信度加权)",
        enable_arousal=True,
        enable_dynamic_ratio=True,
        enable_llm_event_extract=True,
        enable_full_l0=True,
        enable_multi_agent=True,
        enable_voting=False,
        enable_arbitration=True
    ),
    AblationConfig(
        name="w/o_C7_no_arbitration",
        description="无仲裁机制",
        enable_arousal=True,
        enable_dynamic_ratio=True,
        enable_llm_event_extract=True,
        enable_full_l0=True,
        enable_multi_agent=True,
        enable_voting=True,
        enable_arbitration=False
    ),
]


# 极端配置对比 (5 种)
EXTREME_CONFIGURATIONS = [
    AblationConfig(
        name="full",
        description="完整系统",
        enable_arousal=True,
        enable_dynamic_ratio=True,
        enable_llm_event_extract=True,
        enable_full_l0=True,
        enable_multi_agent=True,
        enable_voting=True,
        enable_arbitration=True
    ),
    AblationConfig(
        name="minimal",
        description="最小系统 (规则事件 + 简化评分 + 简单平均)",
        enable_arousal=False,
        enable_dynamic_ratio=False,
        enable_llm_event_extract=False,
        enable_full_l0=False,
        enable_multi_agent=False,
        enable_voting=False,
        enable_arbitration=False
    ),
    AblationConfig(
        name="llm_only",
        description="仅 LLM 组件 (LLM 事件提取 + 多 Agent)",
        enable_arousal=False,
        enable_dynamic_ratio=False,
        enable_llm_event_extract=True,
        enable_full_l0=False,
        enable_multi_agent=True,
        enable_voting=True,
        enable_arbitration=True
    ),
    AblationConfig(
        name="rule_only",
        description="仅规则组件 (情绪 + 动态比例 + 规则评分)",
        enable_arousal=True,
        enable_dynamic_ratio=True,
        enable_llm_event_extract=False,
        enable_full_l0=False,
        enable_multi_agent=False,
        enable_voting=False,
        enable_arbitration=False
    ),
    AblationConfig(
        name="hybrid",
        description="混合系统 (情绪 + 动态比例 + LLM 事件 + 简化评分 + 简单平均)",
        enable_arousal=True,
        enable_dynamic_ratio=True,
        enable_llm_event_extract=True,
        enable_full_l0=False,
        enable_multi_agent=False,
        enable_voting=False,
        enable_arbitration=False
    ),
]


# ============================================================================
# 测试数据集
# ============================================================================

def load_test_dataset() -> List[Dict]:
    """加载 50 条标准测试集"""
    
    # 如果测试集文件存在，从文件加载
    testset_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'data', 'ablation_testset_50.jsonl'
    )
    
    if os.path.exists(testset_path):
        with open(testset_path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f]
    
    # 否则生成 Mock 测试集 (基于鲁棒性测试用例)
    return generate_mock_testset()


def generate_mock_testset() -> List[Dict]:
    """生成 Mock 测试集 (50 条)"""
    
    testset = []
    
    # 类别 1: 高情绪唤醒 (10 条)
    for i in range(10):
        testset.append({
            "id": f"high_arousal_{i:02d}",
            "category": "high_arousal",
            "text": f"那一刻，我感到前所未有的喜悦，眼泪止不住地流下来。阳光如此温暖，心里充满了幸福。这是我最珍贵的回忆，至今想起来仍然心潮澎湃。",
            "expected_arousal": 4.5 + (i % 6) / 10,
            "expected_grade": "A" if i < 5 else "S",
            "metadata": {"source": "robustness_test_C01"}
        })
    
    # 类别 2: 低情绪唤醒 (10 条)
    for i in range(10):
        testset.append({
            "id": f"low_arousal_{i:02d}",
            "category": "low_arousal",
            "text": f"那天我去了公园。天气不错，我在公园散步。看到一些人在锻炼。然后我回家了。",
            "expected_arousal": 1.5 + (i % 6) / 10,
            "expected_grade": "C" if i < 5 else "D",
            "metadata": {"source": "robustness_test_B01"}
        })
    
    # 类别 3: 高连贯性 (10 条)
    for i in range(10):
        testset.append({
            "id": f"high_coherence_{i:02d}",
            "category": "high_coherence",
            "text": f"1985 年春天，我在杭州西湖边第一次见到她。那天阳光明媚，我们沿着苏堤漫步，聊了很多关于未来的梦想。那次相遇改变了我的一生。",
            "expected_arousal": 3.0 + (i % 4) / 10,
            "expected_grade": "A",
            "metadata": {"source": "mock_test_TC03"}
        })
    
    # 类别 4: 低连贯性 (10 条)
    for i in range(10):
        testset.append({
            "id": f"low_coherence_{i:02d}",
            "category": "low_coherence",
            "text": f"嗯...那个...好像是...记不太清了...可能是在...反正就是...大概吧...不太确定...",
            "expected_arousal": 2.0,
            "expected_grade": "D",
            "metadata": {"source": "mock_test_TC06"}
        })
    
    # 类别 5: 边界案例 (10 条)
    boundary_cases = [
        {"id": "boundary_empty", "text": "", "category": "boundary"},
        {"id": "boundary_whitespace", "text": "   \n\t  ", "category": "boundary"},
        {"id": "boundary_short", "text": "好。", "category": "boundary"},
        {"id": "boundary_emoji", "text": "😀😃😄😊🎉", "category": "boundary"},
        {"id": "boundary_numbers", "text": "12345 67890", "category": "boundary"},
        {"id": "boundary_punctuation", "text": "！！！？？？……", "category": "boundary"},
        {"id": "boundary_repetition", "text": "开心开心开心开心开心开心开心开心开心开心", "category": "boundary"},
        {"id": "boundary_mixed", "text": "Hello 你好こんにちは안녕하세요", "category": "boundary"},
        {"id": "boundary_unicode", "text": "\u200b\u200c\u200d\uFEFF", "category": "boundary"},
        {"id": "boundary_long", "text": "那天" * 500, "category": "boundary"},
    ]
    
    for i, case in enumerate(boundary_cases):
        testset.append({
            "id": case["id"],
            "category": "boundary",
            "text": case["text"],
            "expected_arousal": 1.0 if case["id"] in ["boundary_empty", "boundary_whitespace"] else 2.0,
            "expected_grade": "D",
            "metadata": {"source": "robustness_test_boundary"}
        })
    
    return testset


# ============================================================================
# Mock 评分系统 (模拟 L0/VSNC 各组件)
# ============================================================================

class MockScorer:
    """Mock 评分系统 - 模拟不同配置下的评分行为"""
    
    def __init__(self, config: AblationConfig):
        self.config = config
    
    def score(self, text: str) -> Dict:
        """
        评分主函数
        
        根据配置模拟不同组件开启/关闭时的评分行为
        """
        start_time = time.time()
        
        # 基础特征提取
        features = self._extract_features(text)
        
        # C1: 情绪唤醒度检测
        arousal_score = self._compute_arousal(text, features) if self.config.enable_arousal else 3.0
        
        # C2: 动态理想比例
        ideal_ratio = self._compute_ideal_ratio(arousal_score) if self.config.enable_dynamic_ratio else 0.6
        
        # C3: 事件提取
        events = self._extract_events(text, features) if self.config.enable_llm_event_extract else self._rule_extract_events(text)
        
        # C4: L0 评分
        l0_scores = self._compute_l0_scores(text, events, features) if self.config.enable_full_l0 else self._simplified_l0_scores(text, features)
        
        # C5: 多 Agent 评委
        judge_scores = self._multi_agent_scores(text, l0_scores, arousal_score) if self.config.enable_multi_agent else self._single_judge_score(text, l0_scores)
        
        # C6: 投票加权
        if self.config.enable_multi_agent and self.config.enable_voting:
            weighted_score = self._weighted_vote(judge_scores)
        else:
            weighted_score = statistics.mean([s["score"] for s in judge_scores.values()]) if judge_scores else 50.0
        
        # C7: 仲裁机制
        arbitration_triggered = False
        final_score = weighted_score
        
        if self.config.enable_multi_agent and self.config.enable_arbitration:
            score_values = [s["score"] for s in judge_scores.values()]
            if len(score_values) >= 2 and (max(score_values) - min(score_values)) > 15:
                arbitration_triggered = True
                final_score = self._arbitrate(text, judge_scores)
        
        # 计算等级
        grade = self._assign_grade(final_score)
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "total_score": final_score,
            "grade": grade,
            "arousal_score": arousal_score,
            "ideal_ratio": ideal_ratio,
            "l0_scores": l0_scores,
            "judge_scores": {k: v["score"] for k, v in judge_scores.items()},
            "arbitration_triggered": arbitration_triggered,
            "latency_ms": latency_ms,
            "config": self.config.name
        }
    
    def _extract_features(self, text: str) -> Dict:
        """基础特征提取"""
        return {
            "length": len(text),
            "word_count": len(text.split()),
            "sentence_count": text.count("。") + text.count("！") + text.count("？"),
            "exclamation_count": text.count("！") + text.count("!"),
            "question_count": text.count("？") + text.count("?"),
            "has_emotion_words": any(w in text for w in ["开心", "难过", "激动", "悲伤", "高兴", "痛苦"]),
        }
    
    def _compute_arousal(self, text: str, features: Dict) -> float:
        """C1: 情绪唤醒度检测 (Mock)"""
        if not text.strip():
            return 1.0
        
        # 基于特征简单模拟
        score = 3.0
        if features["exclamation_count"] > 2:
            score += 0.5
        if features["has_emotion_words"]:
            score += 0.5
        if features["length"] > 100:
            score += 0.3
        
        return min(5.0, max(1.0, score))
    
    def _compute_ideal_ratio(self, arousal_score: float) -> float:
        """C2: 动态理想比例"""
        # 根据唤醒度调整理想中心比例
        return 0.50 + (arousal_score - 3) * 0.05
    
    def _extract_events(self, text: str, features: Dict) -> List[Dict]:
        """C3: LLM 事件提取 (Mock)"""
        # 简单模拟：基于句号分割
        sentences = [s.strip() for s in text.split("。") if s.strip()]
        events = []
        for i, sent in enumerate(sentences[:10]):  # 最多 10 个事件
            events.append({
                "id": f"e{i}",
                "description": sent,
                "type": "central" if len(sent) > 10 else "peripheral"
            })
        return events
    
    def _rule_extract_events(self, text: str) -> List[Dict]:
        """C3 Fallback: 规则启发式事件提取"""
        # 更简单的规则：基于固定长度切分
        chunks = [text[i:i+50] for i in range(0, len(text), 50)]
        return [{"id": f"e{i}", "description": chunk, "type": "peripheral"} for i, chunk in enumerate(chunks) if chunk]
    
    def _compute_l0_scores(self, text: str, events: List[Dict], features: Dict) -> Dict:
        """C4: 完整 L0 六维评分"""
        return {
            "temporal": min(5.0, 2.5 + len([e for e in events if "年" in e["description"] or "月" in e["description"]]) * 0.5),
            "spatial": min(5.0, 2.5 + len([e for e in events if "在" in e["description"]]) * 0.5),
            "person": min(5.0, 2.5 + len([e for e in events if any(p in e["description"] for p in ["我", "你", "他", "她"])]) * 0.5),
            "sensory": min(5.0, 2.0 + features["word_count"] / 50),
            "emotional": min(5.0, 2.5 + (1 if features["has_emotion_words"] else 0)),
            "coherence": min(5.0, 3.0 + features["sentence_count"] / 10),
        }
    
    def _simplified_l0_scores(self, text: str, features: Dict) -> Dict:
        """C4 Fallback: 简化 L0 评分 (仅 3 维)"""
        return {
            "temporal": 3.0,
            "emotional": 3.0 + (1 if features["has_emotion_words"] else 0),
            "coherence": min(5.0, 3.0 + features["sentence_count"] / 10),
        }
    
    def _multi_agent_scores(self, text: str, l0_scores: Dict, arousal_score: float) -> Dict:
        """C5: 多 Agent 评委 (Mock 4 个评委)"""
        base_score = sum(l0_scores.values()) / len(l0_scores) * 20  # 转成 0-100
        
        return {
            "sensory": {"score": base_score * (0.9 + arousal_score * 0.05), "confidence": 0.8},
            "context": {"score": base_score * (0.95 + len(l0_scores) * 0.01), "confidence": 0.85},
            "emotion": {"score": base_score * (0.85 + arousal_score * 0.1), "confidence": 0.9},
            "coherence": {"score": base_score * l0_scores.get("coherence", 3) / 5, "confidence": 0.8},
        }
    
    def _single_judge_score(self, text: str, l0_scores: Dict) -> Dict:
        """C5 Fallback: 单一评委"""
        base_score = sum(l0_scores.values()) / len(l0_scores) * 20
        return {"single_judge": {"score": base_score, "confidence": 0.7}}
    
    def _weighted_vote(self, judge_scores: Dict) -> float:
        """C6: 置信度加权投票"""
        total_weight = sum(s["confidence"] for s in judge_scores.values())
        if total_weight == 0:
            return 50.0
        return sum(s["score"] * s["confidence"] for s in judge_scores.values()) / total_weight
    
    def _arbitrate(self, text: str, judge_scores: Dict) -> float:
        """C7: 仲裁机制 (Mock)"""
        # 简单模拟：取中位数
        scores = [s["score"] for s in judge_scores.values()]
        return statistics.median(scores)
    
    def _assign_grade(self, score: float) -> str:
        """分配等级"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"


# ============================================================================
# 实验执行
# ============================================================================

@dataclass
class ExperimentResult:
    """实验结果"""
    config_name: str
    config_description: str
    sample_count: int
    avg_score: float
    score_std: float  # 稳定性指标
    avg_latency_ms: float
    arbitration_rate: float
    grade_distribution: Dict[str, int]
    category_results: Dict[str, Dict]


def run_experiment(configs: List[AblationConfig], testset: List[Dict]) -> List[ExperimentResult]:
    """运行实验"""
    
    results = []
    
    for config in configs:
        print(f"\n{'='*60}")
        print(f"Running: {config.name}")
        print(f"Description: {config.description}")
        print(f"{'='*60}")
        
        scorer = MockScorer(config)
        all_scores = []
        all_latencies = []
        arbitration_count = 0
        grade_counts = {"S": 0, "A": 0, "B": 0, "C": 0, "D": 0}
        category_results = {}
        
        for sample in testset:
            result = scorer.score(sample["text"])
            all_scores.append(result["total_score"])
            all_latencies.append(result["latency_ms"])
            
            if result["arbitration_triggered"]:
                arbitration_count += 1
            
            grade = result["grade"]
            if grade in grade_counts:
                grade_counts[grade] += 1
            
            # 按类别聚合
            category = sample["category"]
            if category not in category_results:
                category_results[category] = {"scores": [], "count": 0}
            category_results[category]["scores"].append(result["total_score"])
            category_results[category]["count"] += 1
        
        # 计算统计量
        avg_score = statistics.mean(all_scores)
        score_std = statistics.stdev(all_scores) if len(all_scores) > 1 else 0
        avg_latency = statistics.mean(all_latencies)
        arbitration_rate = arbitration_count / len(testset)
        
        # 类别级别统计
        category_stats = {}
        for cat, data in category_results.items():
            category_stats[cat] = {
                "avg_score": statistics.mean(data["scores"]),
                "std_score": statistics.stdev(data["scores"]) if len(data["scores"]) > 1 else 0,
                "count": data["count"]
            }
        
        result = ExperimentResult(
            config_name=config.name,
            config_description=config.description,
            sample_count=len(testset),
            avg_score=avg_score,
            score_std=score_std,
            avg_latency_ms=avg_latency,
            arbitration_rate=arbitration_rate,
            grade_distribution=grade_counts,
            category_results=category_stats
        )
        
        results.append(result)
        print(f"Completed: avg_score={avg_score:.2f}, std={score_std:.2f}, latency={avg_latency:.2f}ms")
    
    return results


# ============================================================================
# 结果分析
# ============================================================================

def analyze_results(results: List[ExperimentResult], baseline_name: str = "full") -> Dict:
    """分析实验结果"""
    
    # 找到基线
    baseline = next((r for r in results if r.config_name == baseline_name), None)
    if not baseline:
        print(f"Warning: Baseline '{baseline_name}' not found")
        return {}
    
    analysis = {
        "baseline": {
            "name": baseline.config_name,
            "avg_score": baseline.avg_score,
            "score_std": baseline.score_std,
            "latency_ms": baseline.avg_latency_ms
        },
        "component_contributions": [],
        "rankings": []
    }
    
    # 计算各组件的贡献
    for result in results:
        if result.config_name == baseline_name:
            continue
        
        score_diff = result.avg_score - baseline.avg_score
        std_diff = result.score_std - baseline.score_std
        latency_diff = result.avg_latency_ms - baseline.avg_latency_ms
        
        contribution = {
            "config": result.config_name,
            "description": result.config_description,
            "score_change": score_diff,
            "stability_change": std_diff,
            "latency_change": latency_diff,
            "impact": "positive" if score_diff > 0 else "negative"
        }
        analysis["component_contributions"].append(contribution)
    
    # 按影响排序
    analysis["rankings"] = sorted(
        analysis["component_contributions"],
        key=lambda x: abs(x["score_change"]),
        reverse=True
    )
    
    return analysis


def generate_report(results: List[ExperimentResult], analysis: Dict, output_dir: str):
    """生成 Markdown 报告"""
    
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(output_dir, f"ablation_summary_{timestamp}.md")
    
    baseline = analysis.get("baseline", {})
    
    report = f"""# L0/VSNC 消融实验报告

**执行时间**: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}  
**测试样本**: {results[0].sample_count if results else 0} 条  
**实验配置**: {len(results)} 种

---

## 执行摘要

### 基线性能 (Full Model)

| 指标 | 值 |
|------|-----|
| 平均评分 | {baseline.get('avg_score', 0):.2f} |
| 评分稳定性 (std) | {baseline.get('score_std', 0):.2f} |
| 平均延迟 | {baseline.get('latency_ms', 0):.2f} ms |

---

## 单组件消融结果

### 各组件贡献排名

| 排名 | 组件 | 描述 | 评分变化 | 稳定性变化 | 延迟变化 |
|------|------|------|----------|------------|----------|
"""
    
    for i, item in enumerate(analysis.get("rankings", [])[:7], 1):
        report += f"| {i} | `{item['config']}` | {item['description']} | {item['score_change']:+.2f} | {item['stability_change']:+.2f} | {item['latency_change']:+.2f}ms |\n"
    
    report += f"""
### 详细结果

| 配置 | 平均评分 | 稳定性 (std) | 延迟 (ms) | 仲裁率 |
|------|----------|-------------|-----------|--------|
"""
    
    for result in results:
        report += f"| `{result.config_name}` | {result.avg_score:.2f} | {result.score_std:.2f} | {result.avg_latency_ms:.2f} | {result.arbitration_rate:.1%} |\n"
    
    report += f"""
---

## 等级分布对比

| 配置 | S | A | B | C | D |
|------|---|---|---|---|---|
"""
    
    for result in results:
        d = result.grade_distribution
        report += f"| `{result.config_name}` | {d['S']} | {d['A']} | {d['B']} | {d['C']} | {d['D']} |\n"
    
    report += f"""
---

## 关键发现

### 高影响组件 (评分变化 >5 分)

"""
    
    high_impact = [item for item in analysis.get("rankings", []) if abs(item["score_change"]) > 5]
    if high_impact:
        for item in high_impact:
            report += f"- **{item['config']}**: {item['description']} → 评分变化 {item['score_change']:+.2f}分\n"
    else:
        report += "无显著高影响组件 (所有变化 <5 分)\n"
    
    report += f"""
### 低影响组件 (评分变化 <2 分)

"""
    
    low_impact = [item for item in analysis.get("rankings", []) if abs(item["score_change"]) < 2]
    if low_impact:
        for item in low_impact:
            report += f"- **{item['config']}**: {item['description']} → 评分变化 {item['score_change']:+.2f}分\n"
    else:
        report += "无显著低影响组件 (所有变化 ≥2 分)\n"
    
    report += f"""
---

## 建议

### 可考虑简化的组件

"""
    
    simplifiable = [item for item in analysis.get("rankings", []) if abs(item["score_change"]) < 2 and item["latency_change"] < -5]
    if simplifiable:
        for item in simplifiable:
            report += f"- `{item['config']}`: 贡献<2 分，但可降低{abs(item['latency_change']):.1f}ms 延迟\n"
    else:
        report += "无明确可简化组件\n"
    
    report += f"""
### 需优先优化的组件

"""
    
    critical = [item for item in analysis.get("rankings", []) if item["score_change"] < -10]
    if critical:
        for item in critical:
            report += f"- `{item['config']}`: 移除后评分下降{abs(item['score_change']):.2f}分，需保留并优化\n"
    else:
        report += "无关键组件 (所有组件移除后评分下降 <10 分)\n"
    
    report += f"""
---

## 原始数据

详细 JSON 结果：`ablation_results_{timestamp}.json`

---

*Report generated by ablation_study.py*
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")
    return report_path


# ============================================================================
# 主函数
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="L0/VSNC 消融实验")
    parser.add_argument(
        "--experiment",
        choices=["single", "grouped", "extreme", "all"],
        default="single",
        help="实验类型"
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results"),
        help="输出目录"
    )
    
    args = parser.parse_args()
    
    # 选择配置
    if args.experiment == "single":
        configs = SINGLE_COMPONENT_ABLATIONS
    elif args.experiment == "extreme":
        configs = EXTREME_CONFIGURATIONS
    elif args.experiment == "all":
        configs = SINGLE_COMPONENT_ABLATIONS + EXTREME_CONFIGURATIONS[1:]  # 避免重复 full
    else:
        print(f"Error: Experiment type '{args.experiment}' not implemented yet")
        sys.exit(1)
    
    # 加载测试集
    print(f"Loading test dataset...")
    testset = load_test_dataset()
    print(f"Loaded {len(testset)} samples")
    
    # 运行实验
    print(f"\nStarting {args.experiment} ablation experiment...")
    results = run_experiment(configs, testset)
    
    # 分析结果
    print(f"\nAnalyzing results...")
    analysis = analyze_results(results)
    
    # 生成报告
    print(f"\nGenerating report...")
    report_path = generate_report(results, analysis, args.output_dir)
    
    # 保存 JSON 结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = os.path.join(args.output_dir, f"ablation_results_{timestamp}.json")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "experiment_type": args.experiment,
            "config_count": len(configs),
            "sample_count": len(testset),
            "results": [asdict(r) for r in results],
            "analysis": analysis
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nJSON results saved to: {json_path}")
    print(f"\n{'='*60}")
    print("Experiment Complete!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
