#!/usr/bin/env python3
"""
叙事评分算法 v0.5 - 集成情绪唤醒度检测
基于：LLM-Based Scoring of Narrative Memories (ResearchGate, Mar 14, 2026)
核心发现：情绪唤醒增强中心信息但牺牲外围信息

版本：v0.5
日期：2026-03-16
作者：Hulk 🟢

变更：
- 集成 EmotionalArousalDetector
- 新增情绪唤醒度字段
- 使用唤醒度感知的理想比例算法
- 使用唤醒度感知的引导策略映射
"""

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# 导入情绪唤醒度检测器
from emotional_arousal_detector import EmotionalArousalDetector, ArousalResult, get_ideal_central_ratio, get_guidance_strategy as get_arousal_guidance_strategy

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
    """叙事评分结果 v0.5"""
    event_richness: float  # 0-100
    temporal_coherence: float  # 0-100
    causal_coherence: float  # 0-100
    emotional_depth: float  # 0-100
    identity_integration: float  # 0-100
    information_density: float  # 0-100
    
    # 信息密度分布详情
    central_count: int = 0
    peripheral_count: int = 0
    central_ratio: float = 0.0
    peripheral_ratio: float = 0.0
    distribution_type: str = "unknown"  # "central_dominant", "balanced", "peripheral_dominant"
    
    # 情绪唤醒度 (v0.5 新增)
    emotional_arousal: float = 0.0  # 1-5 分
    arousal_level: str = "未知"  # "极低"|"低"|"中"|"高"|"极高"
    arousal_confidence: float = 0.0  # 0-1 置信度
    ideal_central_ratio: float = 0.5  # 理想中心比例 (基于唤醒度)
    arousal_evidence: Dict = None  # 情绪检测证据
    
    # 综合结果
    total_score: float = 0.0
    grade: str = "N/A"  # S/A/B/C/D
    
    # 引导建议
    guidance_strategy: str = "standard"
    guidance_prompts: List[str] = None
    
    def __post_init__(self):
        if self.guidance_prompts is None:
            self.guidance_prompts = []
        if self.arousal_evidence is None:
            self.arousal_evidence = {}


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

def score_narrative_v0_5(
    text: str,
    events: List[Event],
    strategy: str = "default",
    metamemory_profile: Optional[Dict] = None
) -> NarrativeScore:
    """
    叙事评分 v0.5 - 集成情绪唤醒度检测
    
    参数:
        text: 口述文本
        events: LLM 提取的事件列表（含 type 标注）
        strategy: 权重策略 ("default", "emc_phase", "therapy_phase", "mci_screening")
        metamemory_profile: 元记忆画像（可选）
    
    返回:
        NarrativeScore: 评分结果 (v0.5)
    """
    # 1. 加载权重配置
    weights = load_weights_config(strategy)
    
    # 2. 计算各维度评分
    event_richness = calculate_event_richness(events)
    temporal_coherence = calculate_temporal_coherence(events)
    causal_coherence = calculate_causal_coherence(events)
    emotional_depth = calculate_emotional_depth(text)
    identity_integration = calculate_identity_integration(text)
    
    # 3. 计算信息密度分布 (v0.4)
    density_result = calculate_information_density(events)
    information_density = density_result["density_score"]
    
    # 4. 情绪唤醒度检测 (v0.5 新增)
    arousal_detector = EmotionalArousalDetector()
    arousal_result = arousal_detector.detect(text)
    
    # 5. 计算唤醒度感知的理想比例
    ideal_central, ideal_peripheral, tolerance = get_ideal_central_ratio(arousal_result.score)
    
    # 6. 计算加权总分
    scores = {
        "event_richness": event_richness,
        "temporal_coherence": temporal_coherence,
        "causal_coherence": causal_coherence,
        "emotional_depth": emotional_depth,
        "identity_integration": identity_integration,
        "information_density": information_density
    }
    total_score = calculate_total_score(scores, weights)
    
    # 7. 分配等级
    grade = assign_grade(total_score)
    
    # 8. 选择引导策略 (v0.5: 使用唤醒度感知的策略)
    guidance_strategy = get_arousal_guidance_strategy(arousal_result.level, density_result["central_ratio"])
    
    # 9. 生成引导 prompts (基于策略)
    guidance = select_guidance_strategy(density_result["distribution_type"], metamemory_profile)
    guidance_prompts = guidance["prompt_templates"]
    
    # 10. 构建结果
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
        emotional_arousal=arousal_result.score,
        arousal_level=arousal_result.level,
        arousal_confidence=arousal_result.confidence,
        ideal_central_ratio=ideal_central,
        arousal_evidence=arousal_result.evidence,
        total_score=total_score,
        grade=grade,
        guidance_strategy=guidance_strategy,
        guidance_prompts=guidance_prompts
    )
    
    return result


# v0.4 兼容性别名
score_narrative_v0_4 = score_narrative_v0_5


# ============================================================================
# Mock 测试
# ============================================================================

def run_mock_tests():
    """运行 Mock 数据测试 (v0.5)"""
    print("=" * 60)
    print("叙事评分 v0.5 - Mock 测试 (集成情绪唤醒度)")
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
    
    text_tc01 = "我和老伴去了西湖，我们结婚了，孩子出生了，我升职了，买了第一套房子，父母搬来同住，退休了，老伴去世了，搬到了杭州，开始学习书法。"
    result_tc01 = score_narrative_v0_5(text_tc01, events_tc01)
    print(f"\nTC-01: 纯中心信息 (10 中心/0 外围)")
    print(f"  分布类型：{result_tc01.distribution_type}")
    print(f"  信息密度评分：{result_tc01.information_density}")
    print(f"  情绪唤醒度：{result_tc01.emotional_arousal} ({result_tc01.arousal_level})")
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
    
    text_tc02 = "那天阳光很好，湖面有薄雾，我穿了一件蓝色旗袍，心里很紧张，空气中有桂花香，远处有鸟叫声，温度大概 25 度，墙壁是白色的，桌上有束花，音乐很轻柔。"
    result_tc02 = score_narrative_v0_5(text_tc02, events_tc02)
    print(f"\nTC-02: 纯外围信息 (0 中心/10 外围)")
    print(f"  分布类型：{result_tc02.distribution_type}")
    print(f"  信息密度评分：{result_tc02.information_density}")
    print(f"  情绪唤醒度：{result_tc02.emotional_arousal} ({result_tc02.arousal_level})")
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
    
    text_tc03 = "我和老伴去了西湖，那天阳光很好，我们结婚了，湖面有薄雾，孩子出生了，我穿了一件蓝色旗袍，我升职了，心里很紧张，买了第一套房子，空气中有桂花香。"
    result_tc03 = score_narrative_v0_5(text_tc03, events_tc03)
    print(f"\nTC-03: 平衡分布 (5 中心/5 外围)")
    print(f"  分布类型：{result_tc03.distribution_type}")
    print(f"  信息密度评分：{result_tc03.information_density}")
    print(f"  情绪唤醒度：{result_tc03.emotional_arousal} ({result_tc03.arousal_level})")
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
    
    text_tc04 = "我和老伴去了西湖，那天阳光很好，我们结婚了，孩子出生了，我升职了，买了第一套房子，心里很紧张，空气中有桂花香。"
    result_tc04 = score_narrative_v0_5(text_tc04, events_tc04)
    print(f"\nTC-04: 轻微中心偏向 (6 中心/2 外围)")
    print(f"  分布类型：{result_tc04.distribution_type}")
    print(f"  信息密度评分：{result_tc04.information_density}")
    print(f"  中心比例：{result_tc04.central_ratio}")
    print(f"  情绪唤醒度：{result_tc04.emotional_arousal} ({result_tc04.arousal_level})")
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
    
    text_tc05 = "我和老伴去了西湖，那天阳光很好，我们结婚了，湖面有薄雾，孩子出生了，我穿了一件蓝色旗袍，心里很紧张，空气中有桂花香，远处有鸟叫声，温度大概 25 度。"
    result_tc05 = score_narrative_v0_5(text_tc05, events_tc05)
    print(f"\nTC-05: 轻微外围偏向 (3 中心/7 外围)")
    print(f"  分布类型：{result_tc05.distribution_type}")
    print(f"  信息密度评分：{result_tc05.information_density}")
    print(f"  外围比例：{result_tc05.peripheral_ratio}")
    print(f"  情绪唤醒度：{result_tc05.emotional_arousal} ({result_tc05.arousal_level})")
    print(f"  预期：peripheral_dominant (>55% 外围), ~40-60, event_structure_enhancement")
    
    # TC-06: 高情绪唤醒 - 喜悦
    events_tc06 = [
        Event(description="得知孩子考上大学", event_type="central"),
        Event(description="全家喜出望外", event_type="peripheral"),
        Event(description="激动得热泪盈眶", event_type="peripheral"),
        Event(description="心里乐开了花", event_type="peripheral"),
    ]
    text_tc06 = "得知孩子考上大学的那天，全家喜出望外！我激动得热泪盈眶，心里乐开了花！真是太高兴了！"
    result_tc06 = score_narrative_v0_5(text_tc06, events_tc06)
    print(f"\nTC-06: 高情绪唤醒 - 喜悦")
    print(f"  情绪唤醒度：{result_tc06.emotional_arousal} ({result_tc06.arousal_level})")
    print(f"  理想中心比例：{result_tc06.ideal_central_ratio:.0%}")
    print(f"  引导策略：{result_tc06.guidance_strategy}")
    print(f"  预期：高唤醒 (≥3.5), peripheral_context ✓" if result_tc06.emotional_arousal >= 3.5 else "  ✗ 唤醒度偏低")
    
    # TC-07: 高情绪唤醒 - 悲伤
    events_tc07 = [
        Event(description="老伴去世", event_type="central"),
        Event(description="泣不成声", event_type="peripheral"),
        Event(description="心如刀割", event_type="peripheral"),
        Event(description="眼泪止不住", event_type="peripheral"),
    ]
    text_tc07 = "老伴走的那天，我泣不成声，心如刀割，眼泪止不住地流。痛不欲生，感觉天都塌了。"
    result_tc07 = score_narrative_v0_5(text_tc07, events_tc07)
    print(f"\nTC-07: 高情绪唤醒 - 悲伤")
    print(f"  情绪唤醒度：{result_tc07.emotional_arousal} ({result_tc07.arousal_level})")
    print(f"  理想中心比例：{result_tc07.ideal_central_ratio:.0%}")
    print(f"  引导策略：{result_tc07.guidance_strategy}")
    print(f"  预期：高唤醒 (≥3.5), emotional_integration ✓" if result_tc07.emotional_arousal >= 3.5 else "  ✗ 唤醒度偏低")
    
    # TC-08: 中等情绪唤醒 - 温暖回忆
    events_tc08 = [
        Event(description="第一次约会", event_type="central"),
        Event(description="心里暖暖的", event_type="peripheral"),
        Event(description="很幸福", event_type="peripheral"),
        Event(description="难忘的经历", event_type="peripheral"),
    ]
    text_tc08 = "第一次约会的时候，阳光很好，我们去了西湖。心里暖暖的，感觉很幸福。至今记得很清楚，真是难忘的经历。"
    result_tc08 = score_narrative_v0_5(text_tc08, events_tc08)
    print(f"\nTC-08: 中等情绪唤醒 - 温暖回忆")
    print(f"  情绪唤醒度：{result_tc08.emotional_arousal} ({result_tc08.arousal_level})")
    print(f"  理想中心比例：{result_tc08.ideal_central_ratio:.0%}")
    print(f"  引导策略：{result_tc08.guidance_strategy}")
    print(f"  预期：中唤醒 (2.5-3.5), standard ✓" if 2.5 <= result_tc08.emotional_arousal <= 3.5 else "  ⚠ 唤醒度边界")
    
    # TC-09: 低情绪唤醒 - 平淡叙述
    events_tc09 = [
        Event(description="早上起床", event_type="central"),
        Event(description="吃了早饭", event_type="central"),
        Event(description="去公园散步", event_type="central"),
        Event(description="回家休息", event_type="central"),
    ]
    text_tc09 = "早上起床，吃了早饭，然后去公园散步。天气还可以，走了大概一个小时就回家了。没什么特别的，就是日常。"
    result_tc09 = score_narrative_v0_5(text_tc09, events_tc09)
    print(f"\nTC-09: 低情绪唤醒 - 平淡叙述")
    print(f"  情绪唤醒度：{result_tc09.emotional_arousal} ({result_tc09.arousal_level})")
    print(f"  理想中心比例：{result_tc09.ideal_central_ratio:.0%}")
    print(f"  引导策略：{result_tc09.guidance_strategy}")
    print(f"  预期：低唤醒 (≤2.5), standard_emotional_exploration ✓" if result_tc09.emotional_arousal <= 2.5 else "  ✗ 唤醒度偏高")
    
    # TC-10: 情绪爆发 - 极度愤怒
    events_tc10 = [
        Event(description="被骗光积蓄", event_type="central"),
        Event(description="暴怒", event_type="peripheral"),
        Event(description="浑身发抖", event_type="peripheral"),
        Event(description="火冒三丈", event_type="peripheral"),
    ]
    text_tc10 = "得知被骗光积蓄的那一刻，我暴怒！火冒三丈！浑身发抖，气得说不出话！太气人了！简直忍无可忍！"
    result_tc10 = score_narrative_v0_5(text_tc10, events_tc10)
    print(f"\nTC-10: 情绪爆发 - 极度愤怒")
    print(f"  情绪唤醒度：{result_tc10.emotional_arousal} ({result_tc10.arousal_level})")
    print(f"  理想中心比例：{result_tc10.ideal_central_ratio:.0%}")
    print(f"  引导策略：{result_tc10.guidance_strategy}")
    print(f"  预期：极高唤醒 (≥4.0), emotional_integration ✓" if result_tc10.emotional_arousal >= 4.0 else "  ⚠ 唤醒度略低")
    
    print("\n" + "=" * 60)
    print("Mock 测试完成 (10/10 用例)")
    print("=" * 60)
    
    return {
        "tc01": result_tc01,
        "tc02": result_tc02,
        "tc03": result_tc03,
        "tc04": result_tc04,
        "tc05": result_tc05,
        "tc06": result_tc06,
        "tc07": result_tc07,
        "tc08": result_tc08,
        "tc09": result_tc09,
        "tc10": result_tc10
    }


# ============================================================================
# CLI 入口
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_mock_tests()
    else:
        print("叙事评分算法 v0.5 - 集成情绪唤醒度检测")
        print("用法：python narrative_scorer_v0.4.py --test")
        print("\n核心功能:")
        print("  - 6 维度评分 + 信息密度分布")
        print("  - 情绪唤醒度检测 (1-5 分)")
        print("  - 唤醒度感知的理想比例算法")
        print("  - 唤醒度感知的引导策略映射")
        print("  - 中心/外围信息显式建模")
        print("  - 可配置权重策略")
        print("\n依据：LLM-Based Scoring of Narrative Memories (ResearchGate, Mar 14, 2026)")
