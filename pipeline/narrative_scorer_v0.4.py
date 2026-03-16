#!/usr/bin/env python3
"""
叙事评分算法 v0.4 - 新增信息密度分布维度
基于：LLM-Based Scoring of Narrative Memories (ResearchGate, Mar 14, 2026)
核心发现：情绪唤醒增强中心信息但牺牲外围信息

版本：v0.4
日期：2026-03-16
作者：Hulk 🟢
"""

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# ============================================================================
# 配置加载
# ============================================================================

def load_weights_config(strategy: str = "default") -> Dict[str, float]:
    """加载权重配置"""
    
    strategies = {
        "default": {
            "event_richness": 0.15,
            "temporal_coherence": 0.15,
            "causal_coherence": 0.15,
            "emotional_depth": 0.20,
            "identity_integration": 0.15,
            "information_density": 0.20
        },
        "emc_phase": {
            "event_richness": 0.10,
            "temporal_coherence": 0.10,
            "causal_coherence": 0.10,
            "emotional_depth": 0.20,
            "identity_integration": 0.10,
            "information_density": 0.40
        },
        "therapy_phase": {
            "event_richness": 0.15,
            "temporal_coherence": 0.15,
            "causal_coherence": 0.15,
            "emotional_depth": 0.20,
            "identity_integration": 0.15,
            "information_density": 0.20
        },
        "mci_screening": {
            "event_richness": 0.10,
            "temporal_coherence": 0.25,
            "causal_coherence": 0.25,
            "emotional_depth": 0.15,
            "identity_integration": 0.10,
            "information_density": 0.15
        }
    }
    
    return strategies.get(strategy, strategies["default"])


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class Event:
    """事件数据结构"""
    description: str
    time: Optional[str] = None
    people: List[str] = None
    event_type: str = "central"  # "central" or "peripheral"
    
    def __post_init__(self):
        if self.people is None:
            self.people = []


@dataclass
class NarrativeScore:
    """叙事评分结果"""
    event_richness: float  # 0-100
    temporal_coherence: float  # 0-100
    causal_coherence: float  # 0-100
    emotional_depth: float  # 0-100
    identity_integration: float  # 0-100
    information_density: float  # 0-100 (新增)
    
    # 信息密度分布详情
    central_count: int = 0
    peripheral_count: int = 0
    central_ratio: float = 0.0
    peripheral_ratio: float = 0.0
    distribution_type: str = "unknown"  # "central_dominant", "balanced", "peripheral_dominant"
    
    # 综合结果
    total_score: float = 0.0
    grade: str = "N/A"  # S/A/B/C/D
    
    # 引导建议
    guidance_strategy: str = "standard"
    guidance_prompts: List[str] = None
    
    def __post_init__(self):
        if self.guidance_prompts is None:
            self.guidance_prompts = []


# ============================================================================
# 信息密度分布计算 (v0.4 新增核心功能)
# ============================================================================

def calculate_information_density(events: List[Event]) -> Dict:
    """
    计算信息密度分布
    
    输入：LLM 提取的事件列表（每个事件包含 type 字段）
    输出：中心/外围信息比例 + 分布评分
    
    理想比例：中心 60% ± 15%, 外围 40% ± 15%
    """
    central_count = sum(1 for e in events if e.event_type == "central")
    peripheral_count = sum(1 for e in events if e.event_type == "peripheral")
    
    total = central_count + peripheral_count
    if total == 0:
        return {
            "central_count": 0,
            "peripheral_count": 0,
            "central_ratio": 0.0,
            "peripheral_ratio": 0.0,
            "balance_score": 0.0,
            "distribution_type": "unknown",
            "density_score": 0
        }
    
    central_ratio = central_count / total
    peripheral_ratio = peripheral_count / total
    
    # 理想比例：中心 60%, 外围 40%
    ideal_central = 0.6
    ideal_peripheral = 0.4
    
    # 计算偏离度（0-1，1 表示完美平衡）
    central_deviation = abs(central_ratio - ideal_central)
    peripheral_deviation = abs(peripheral_ratio - ideal_peripheral)
    balance_score = 1 - (central_deviation + peripheral_deviation) / 2
    
    # 判定分布类型
    if central_ratio > 0.75:
        distribution_type = "central_dominant"  # 中心主导（可能缺乏细节）
    elif peripheral_ratio > 0.55:
        distribution_type = "peripheral_dominant"  # 外围主导（可能缺乏主线）
    else:
        distribution_type = "balanced"  # 平衡
    
    # 计算密度评分 (0-100)
    density_score = round(balance_score * 100, 1)
    
    return {
        "central_count": central_count,
        "peripheral_count": peripheral_count,
        "central_ratio": round(central_ratio, 2),
        "peripheral_ratio": round(peripheral_ratio, 2),
        "balance_score": round(balance_score, 2),
        "distribution_type": distribution_type,
        "density_score": density_score
    }


# ============================================================================
# 引导策略映射 (v0.4 新增)
# ============================================================================

def select_guidance_strategy(distribution_type: str, metamemory_profile: Optional[Dict] = None) -> Dict:
    """
    根据信息密度分布选择引导策略
    
    返回：策略配置（包含 prompt 模板和元记忆提示）
    """
    strategies = {
        "central_dominant": {
            "strategy": "sensory_enhancement",
            "prompt_templates": [
                "那天的天气怎么样？",
                "您当时穿的是什么衣服？",
                "周围有什么声音或气味吗？",
                "您能看到什么特别的景物吗？",
                "当时的温度感觉如何？"
            ],
            "metamemory_hint": "您当时是如何注意到这些细节的？",
            "rationale": "中心信息过多，需补充感官细节和环境背景"
        },
        "peripheral_dominant": {
            "strategy": "event_structure_enhancement",
            "prompt_templates": [
                "这件事是怎么开始的？",
                "后来发生了什么？",
                "这对您有什么影响？",
                "您为什么会记得这么清楚？",
                "这件事的核心是什么？"
            ],
            "metamemory_hint": "这件事对您意味着什么？",
            "rationale": "外围信息过多，需补充事件主线和因果关系"
        },
        "balanced": {
            "strategy": "standard",
            "prompt_templates": [
                "能再多说说当时的情况吗？",
                "您当时是什么感受？",
                "还有谁在场？",
                "这件事发生在什么地方？",
                "这对您来说意味着什么？"
            ],
            "metamemory_hint": None,
            "rationale": "信息分布平衡，保持标准引导策略"
        },
        "unknown": {
            "strategy": "standard",
            "prompt_templates": [
                "能再多说说当时的情况吗？",
                "您当时是什么感受？"
            ],
            "metamemory_hint": None,
            "rationale": "无法判定分布类型，使用标准策略"
        }
    }
    
    base_strategy = strategies.get(distribution_type, strategies["unknown"])
    
    # 如提供元记忆画像，可进一步细化策略
    if metamemory_profile:
        # 未来扩展：根据元记忆画像调整策略
        pass
    
    return base_strategy


# ============================================================================
# 评分维度计算 (v0.3 保留 + v0.4 扩展)
# ============================================================================

def calculate_event_richness(events: List[Event]) -> float:
    """事件丰富度评分 (0-100)"""
    count = len(events)
    # 10 个事件为满分，线性映射
    score = min(count / 10.0, 1.0) * 100
    return round(score, 1)


def calculate_temporal_coherence(events: List[Event]) -> float:
    """时间连贯性评分 (0-100)"""
    events_with_time = sum(1 for e in events if e.time)
    if len(events) == 0:
        return 0
    ratio = events_with_time / len(events)
    # 时间信息覆盖率 * 100
    score = ratio * 100
    return round(score, 1)


def calculate_causal_coherence(events: List[Event]) -> float:
    """因果连贯性评分 (0-100)"""
    # 简化版：基于事件数量和人物关联
    # 完整版：需要 LLM 分析事件间因果关系
    if len(events) < 2:
        return 0
    # 假设有 3+ 事件且有人物关联则给高分
    people_count = len(set(p for e in events for p in e.people))
    score = min((len(events) + people_count) / 10.0, 1.0) * 100
    return round(score, 1)


def calculate_emotional_depth(text: str) -> float:
    """情感深度评分 (0-100)"""
    # 简化版：基于情感词汇密度
    # 完整版：需要 LLM 分析情感层次
    emotional_words = ["高兴", "难过", "激动", "紧张", "温暖", "感动", "骄傲", "遗憾", "幸福", "悲伤"]
    count = sum(text.count(word) for word in emotional_words)
    # 每 100 字有 1 个情感词为基准
    density = count / max(len(text) / 100, 1)
    score = min(density * 20, 100)
    return round(score, 1)


def calculate_identity_integration(text: str) -> float:
    """自我认同整合评分 (0-100)"""
    # 简化版：基于自我指涉词汇
    # 完整版：需要 LLM 分析意义反思深度
    self_ref_words = ["我", "我的", "自己", "我觉得", "我认为", "对我", "我自己"]
    meaning_words = ["意义", "重要", "影响", "改变", "成长", "学会", "明白", "懂得"]
    
    self_count = sum(text.count(word) for word in self_ref_words)
    meaning_count = sum(text.count(word) for word in meaning_words)
    
    # 自我指涉 + 意义反思
    score = min((self_count + meaning_count * 2) / 10.0, 1.0) * 100
    return round(score, 1)


# ============================================================================
# 综合评分与分级
# ============================================================================

def calculate_total_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """计算加权总分"""
    total = 0
    for key, weight in weights.items():
        total += scores.get(key, 0) * weight
    return round(total, 1)


def assign_grade(total_score: float) -> str:
    """根据总分分配等级"""
    if total_score >= 90:
        return "S"
    elif total_score >= 80:
        return "A"
    elif total_score >= 70:
        return "B"
    elif total_score >= 60:
        return "C"
    else:
        return "D"


# ============================================================================
# 主评分函数 (v0.4)
# ============================================================================

def score_narrative_v0_4(
    text: str,
    events: List[Event],
    strategy: str = "default",
    metamemory_profile: Optional[Dict] = None
) -> NarrativeScore:
    """
    叙事评分 v0.4
    
    参数:
        text: 口述文本
        events: LLM 提取的事件列表（含 type 标注）
        strategy: 权重策略 ("default", "emc_phase", "therapy_phase", "mci_screening")
        metamemory_profile: 元记忆画像（可选）
    
    返回:
        NarrativeScore: 评分结果
    """
    # 1. 加载权重配置
    weights = load_weights_config(strategy)
    
    # 2. 计算各维度评分
    event_richness = calculate_event_richness(events)
    temporal_coherence = calculate_temporal_coherence(events)
    causal_coherence = calculate_causal_coherence(events)
    emotional_depth = calculate_emotional_depth(text)
    identity_integration = calculate_identity_integration(text)
    
    # 3. 计算信息密度分布 (v0.4 新增)
    density_result = calculate_information_density(events)
    information_density = density_result["density_score"]
    
    # 4. 计算加权总分
    scores = {
        "event_richness": event_richness,
        "temporal_coherence": temporal_coherence,
        "causal_coherence": causal_coherence,
        "emotional_depth": emotional_depth,
        "identity_integration": identity_integration,
        "information_density": information_density
    }
    total_score = calculate_total_score(scores, weights)
    
    # 5. 分配等级
    grade = assign_grade(total_score)
    
    # 6. 选择引导策略
    guidance = select_guidance_strategy(density_result["distribution_type"], metamemory_profile)
    
    # 7. 构建结果
    result = NarrativeScore(
        event_richness=event_richness,
        temporal_coherence=temporal_coherence,
        causal_coherence=causal_coherence,
        emotional_depth=emotional_depth,
        identity_integration=identity_integration,
        information_density=information_density,
        central_count=density_result["central_count"],
        peripheral_count=density_result["peripheral_count"],
        central_ratio=density_result["central_ratio"],
        peripheral_ratio=density_result["peripheral_ratio"],
        distribution_type=density_result["distribution_type"],
        total_score=total_score,
        grade=grade,
        guidance_strategy=guidance["strategy"],
        guidance_prompts=guidance["prompt_templates"]
    )
    
    return result


# ============================================================================
# Mock 测试
# ============================================================================

def run_mock_tests():
    """运行 Mock 数据测试"""
    print("=" * 60)
    print("叙事评分 v0.4 - Mock 测试")
    print("=" * 60)
    
    # TC-01: 纯中心信息
    events_tc01 = [
        Event(description="我和老伴去了西湖", event_type="central"),
        Event(description="我们结婚了", event_type="central"),
        Event(description="孩子出生了", event_type="central"),
        Event(description="我升职了", event_type="central"),
        Event(description="买了第一套房子", event_type="central"),
        Event(description="父母搬来同住", event_type="central"),
        Event(description="退休了", event_type="central"),
        Event(description="老伴去世了", event_type="central"),
        Event(description="搬到了杭州", event_type="central"),
        Event(description="开始学习书法", event_type="central"),
    ]
    
    result_tc01 = score_narrative_v0_4("测试文本", events_tc01)
    print(f"\nTC-01: 纯中心信息 (10 中心/0 外围)")
    print(f"  分布类型：{result_tc01.distribution_type}")
    print(f"  信息密度评分：{result_tc01.information_density}")
    print(f"  引导策略：{result_tc01.guidance_strategy}")
    print(f"  预期：central_dominant, ~40, sensory_enhancement ✓" if result_tc01.distribution_type == "central_dominant" else "  ✗ 失败")
    
    # TC-02: 纯外围信息
    events_tc02 = [
        Event(description="那天阳光很好", event_type="peripheral"),
        Event(description="湖面有薄雾", event_type="peripheral"),
        Event(description="我穿了一件蓝色旗袍", event_type="peripheral"),
        Event(description="心里很紧张", event_type="peripheral"),
        Event(description="空气中有桂花香", event_type="peripheral"),
        Event(description="远处有鸟叫声", event_type="peripheral"),
        Event(description="温度大概 25 度", event_type="peripheral"),
        Event(description="墙壁是白色的", event_type="peripheral"),
        Event(description="桌上有束花", event_type="peripheral"),
        Event(description="音乐很轻柔", event_type="peripheral"),
    ]
    
    result_tc02 = score_narrative_v0_4("测试文本", events_tc02)
    print(f"\nTC-02: 纯外围信息 (0 中心/10 外围)")
    print(f"  分布类型：{result_tc02.distribution_type}")
    print(f"  信息密度评分：{result_tc02.information_density}")
    print(f"  引导策略：{result_tc02.guidance_strategy}")
    print(f"  预期：peripheral_dominant, ~40, event_structure_enhancement ✓" if result_tc02.distribution_type == "peripheral_dominant" else "  ✗ 失败")
    
    # TC-03: 平衡分布
    events_tc03 = [
        Event(description="我和老伴去了西湖", event_type="central"),
        Event(description="那天阳光很好", event_type="peripheral"),
        Event(description="我们结婚了", event_type="central"),
        Event(description="湖面有薄雾", event_type="peripheral"),
        Event(description="孩子出生了", event_type="central"),
        Event(description="我穿了一件蓝色旗袍", event_type="peripheral"),
        Event(description="我升职了", event_type="central"),
        Event(description="心里很紧张", event_type="peripheral"),
        Event(description="买了第一套房子", event_type="central"),
        Event(description="空气中有桂花香", event_type="peripheral"),
    ]
    
    result_tc03 = score_narrative_v0_4("测试文本", events_tc03)
    print(f"\nTC-03: 平衡分布 (5 中心/5 外围)")
    print(f"  分布类型：{result_tc03.distribution_type}")
    print(f"  信息密度评分：{result_tc03.information_density}")
    print(f"  引导策略：{result_tc03.guidance_strategy}")
    print(f"  预期：balanced, ~80-100, standard ✓" if result_tc03.distribution_type == "balanced" else "  ✗ 失败")
    
    # TC-04: 轻微中心偏向
    events_tc04 = [
        Event(description="我和老伴去了西湖", event_type="central"),
        Event(description="那天阳光很好", event_type="peripheral"),
        Event(description="我们结婚了", event_type="central"),
        Event(description="孩子出生了", event_type="central"),
        Event(description="我升职了", event_type="central"),
        Event(description="买了第一套房子", event_type="central"),
        Event(description="心里很紧张", event_type="peripheral"),
        Event(description="空气中有桂花香", event_type="peripheral"),
    ]
    
    result_tc04 = score_narrative_v0_4("测试文本", events_tc04)
    print(f"\nTC-04: 轻微中心偏向 (6 中心/2 外围)")
    print(f"  分布类型：{result_tc04.distribution_type}")
    print(f"  信息密度评分：{result_tc04.information_density}")
    print(f"  中心比例：{result_tc04.central_ratio}")
    print(f"  预期：balanced (75% 中心), ~70-90, standard")
    
    # TC-05: 轻微外围偏向
    events_tc05 = [
        Event(description="我和老伴去了西湖", event_type="central"),
        Event(description="那天阳光很好", event_type="peripheral"),
        Event(description="我们结婚了", event_type="central"),
        Event(description="湖面有薄雾", event_type="peripheral"),
        Event(description="孩子出生了", event_type="central"),
        Event(description="我穿了一件蓝色旗袍", event_type="peripheral"),
        Event(description="心里很紧张", event_type="peripheral"),
        Event(description="空气中有桂花香", event_type="peripheral"),
        Event(description="远处有鸟叫声", event_type="peripheral"),
        Event(description="温度大概 25 度", event_type="peripheral"),
    ]
    
    result_tc05 = score_narrative_v0_4("测试文本", events_tc05)
    print(f"\nTC-05: 轻微外围偏向 (3 中心/7 外围)")
    print(f"  分布类型：{result_tc05.distribution_type}")
    print(f"  信息密度评分：{result_tc05.information_density}")
    print(f"  外围比例：{result_tc05.peripheral_ratio}")
    print(f"  预期：peripheral_dominant (>55% 外围), ~40-60, event_structure_enhancement")
    
    print("\n" + "=" * 60)
    print("Mock 测试完成")
    print("=" * 60)
    
    return {
        "tc01": result_tc01,
        "tc02": result_tc02,
        "tc03": result_tc03,
        "tc04": result_tc04,
        "tc05": result_tc05
    }


# ============================================================================
# CLI 入口
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_mock_tests()
    else:
        print("叙事评分算法 v0.4")
        print("用法：python narrative_scorer_v0.4.py --test")
        print("\n核心功能:")
        print("  - 6 维度评分（新增信息密度分布）")
        print("  - 中心/外围信息显式建模")
        print("  - 可配置权重策略")
        print("  - 引导策略自动映射")
        print("\n依据：LLM-Based Scoring of Narrative Memories (ResearchGate, Mar 14, 2026)")
