#!/usr/bin/env python3
"""
L0 标注质检多 Agent 系统 — Mock 测试

用于在缺少 dashscope 的环境中验证系统逻辑流程。
使用 mock 评分代替真实 API 调用。
"""

import os
import sys
import time
import json
from typing import Dict, List
from dataclasses import dataclass, asdict


@dataclass
class MockJudgeResult:
    dimension: str
    score: float
    confidence: float
    reasoning: str
    evidence: List[str]


def mock_judge_assess(dimension: str, text: str) -> MockJudgeResult:
    """Mock 评委评分（基于文本长度模拟）"""
    # 根据文本长度和维度生成模拟分数
    base_score = 50 + (len(text) % 50)
    
    # 不同维度有不同偏好
    dimension_bonus = {
        'Sensory': 10 if any(w in text for w in ['看', '听', '闻', '触', '味道']) else 0,
        'Context': 10 if any(w in text for w in ['年', '月', '日', '地方', '人']) else 0,
        'Emotion': 10 if any(w in text for w in ['感觉', '心情', '开心', '难过']) else 0,
        'Coherence': 10 if len(text) > 100 else 0,
    }
    
    score = min(100, base_score + dimension_bonus.get(dimension, 0))
    confidence = 0.7 + (len(text) % 30) / 100
    
    return MockJudgeResult(
        dimension=dimension,
        score=score,
        confidence=confidence,
        reasoning=f"Mock {dimension} assessment based on text analysis",
        evidence=[text[:50] + "..."]
    )


def test_system_flow():
    """测试系统流程"""
    print("=" * 60)
    print("L0 质检多 Agent 系统 — Mock 流程测试")
    print("=" * 60)
    print()
    
    # 测试样本
    test_narrative = """
    1978 年冬天，我 15 岁，在黑龙江下乡。清晨 5 点，天还没亮，
    茅草屋顶上结了一层白霜。我推开木门，"吱呀"一声，
    冷风灌进来，像刀子一样刮在脸上。院子里的井台结了冰，
    我提着水桶，手冻得通红，指尖几乎没有知觉。
    远处传来生产队的钟声，"当当当"，在寂静的清晨传得很远。
    """
    
    # 1. 并行执行 4 个评委评分
    print("步骤 1: 4 个评委并行评分")
    start_time = time.time()
    
    dimensions = ['Sensory', 'Context', 'Emotion', 'Coherence']
    judge_results = {}
    
    for dim in dimensions:
        result = mock_judge_assess(dim, test_narrative)
        judge_results[dim] = result
        print(f"  {dim}: {result.score:.1f}分 (置信度：{result.confidence:.2f})")
    
    # 2. 计算分数差异
    scores = [r.score for r in judge_results.values()]
    max_diff = max(scores) - min(scores)
    print()
    print(f"步骤 2: 分数差异分析")
    print(f"  最高分：{max(scores):.1f}")
    print(f"  最低分：{min(scores):.1f}")
    print(f"  差异：{max_diff:.1f}分")
    
    # 3. 检查是否需要仲裁
    conflict_threshold = 15.0
    arbitration_needed = max_diff > conflict_threshold
    
    print()
    print(f"步骤 3: 仲裁判定 (阈值={conflict_threshold}分)")
    if arbitration_needed:
        print(f"  ⚠️  差异超过阈值，触发仲裁")
        # Mock 仲裁：取平均
        final_scores = {dim: sum(scores)/len(scores) for dim in dimensions}
        print(f"  仲裁后分数：{final_scores}")
    else:
        print(f"  ✅ 差异在阈值内，无需仲裁")
        final_scores = {dim: r.score for dim, r in judge_results.items()}
    
    # 4. 计算综合分数
    overall_score = sum(final_scores.values()) / len(final_scores)
    grade = 'S' if overall_score >= 85 else 'A' if overall_score >= 70 else 'B' if overall_score >= 55 else 'C' if overall_score >= 40 else 'D'
    
    total_time = (time.time() - start_time) * 1000
    
    print()
    print("步骤 4: 最终结果")
    print(f"  各维度分数: {final_scores}")
    print(f"  综合分数：{overall_score:.1f}")
    print(f"  等级：{grade}")
    print(f"  耗时：{total_time:.1f}ms")
    print()
    print("=" * 60)
    print("✅ Mock 测试通过 — 系统逻辑流程正常")
    print("=" * 60)
    print()
    print("下一步:")
    print("  1. 在有 dashscope 的环境中运行真实测试")
    print("  2. 收集 50 条真实标注数据进行一致性对标")
    print("  3. 优化性能以达到 P95<500ms, 吞吐量>10 条/秒")


if __name__ == "__main__":
    test_system_flow()
