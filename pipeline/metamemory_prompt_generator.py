#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
元记忆 (Metamemory) 引导问题生成器
版本：1.0 (阶段 3 代码实现)
创建日期：2026-03-14
作者：Hulk 🟢

功能：根据叙事内容和用户状态，动态生成个性化的元记忆引导问题
整合：与 narrative_scorer 和 L0 质检系统协同工作
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from metamemory_selector import MetamemorySelector, UserState, MemorySegment, Prompt


class NarrativeFeature(Enum):
    """叙事特征类型"""
    TEMPORAL = "temporal"           # 时间线索
    SPATIAL = "spatial"             # 空间线索
    SENSORY = "sensory"             # 感官细节
    EMOTIONAL = "emotional"         # 情感表达
    SOCIAL = "social"               # 社会互动
    CAUSAL = "causal"               # 因果关系
    REFLECTIVE = "reflective"       # 反思性内容


@dataclass
class NarrativeAnalysis:
    """叙事分析结果"""
    text: str
    word_count: int = 0
    sentence_count: int = 0
    features: Dict[NarrativeFeature, int] = None
    confidence_estimate: float = 5.0
    coherence_score: float = 0.5
    detail_richness: float = 0.5
    
    def __post_init__(self):
        if self.features is None:
            self.features = {f: 0 for f in NarrativeFeature}


class PromptGenerator:
    """元记忆引导问题生成器"""
    
    # 特征关键词映射
    FEATURE_KEYWORDS = {
        NarrativeFeature.TEMPORAL: [
            "那年", "当时", "后来", "之后", "之前", "现在", "过去", "时候", 
            "年", "月", "日", "季节", "天气"
        ],
        NarrativeFeature.SPATIAL: [
            "地方", "地点", "这里", "那里", "房间", "家", "学校", "工作",
            "位置", "周围", "环境"
        ],
        NarrativeFeature.SENSORY: [
            "看到", "听到", "闻到", "尝到", "摸到", "感觉", "声音", "颜色",
            "气味", "味道", "温度", "光线"
        ],
        NarrativeFeature.EMOTIONAL: [
            "开心", "难过", "紧张", "害怕", "兴奋", "感动", "心情", "情绪",
            "感觉", "喜欢", "讨厌", "担心", "希望"
        ],
        NarrativeFeature.SOCIAL: [
            "谁", "人", "一起", "朋友", "家人", "同事", "孩子", "父母",
            "老师", "同学", "他们", "我们"
        ],
        NarrativeFeature.CAUSAL: [
            "因为", "所以", "导致", "结果", "原因", "为什么", "因此", "于是"
        ],
        NarrativeFeature.REFLECTIVE: [
            "意义", "影响", "改变", "学会", "明白", "懂得", "成长", "重要",
            "价值", "教训", "经验"
        ]
    }
    
    # 信心指示词
    CONFIDENCE_LOW = ["好像", "可能", "也许", "大概", "记不清", "模糊", "不太确定"]
    CONFIDENCE_HIGH = ["清楚", "记得", "肯定", "一定", "明确", "深刻"]
    
    def __init__(self, selector: Optional[MetamemorySelector] = None):
        """
        初始化生成器
        
        Args:
            selector: MetamemorySelector 实例，默认创建新实例
        """
        self.selector = selector or MetamemorySelector()
    
    def analyze_narrative(self, text: str) -> NarrativeAnalysis:
        """
        分析叙事文本特征
        
        Args:
            text: 用户叙事文本
        
        Returns:
            NarrativeAnalysis 结果
        """
        analysis = NarrativeAnalysis(text=text)
        
        # 基础统计
        analysis.word_count = len(text)
        analysis.sentence_count = text.count('。') + text.count('！') + text.count('？')
        
        # 特征提取
        for feature, keywords in self.FEATURE_KEYWORDS.items():
            count = sum(text.count(kw) for kw in keywords)
            analysis.features[feature] = count
        
        # 信心估计 (基于信心指示词)
        low_conf_count = sum(text.count(kw) for kw in self.CONFIDENCE_LOW)
        high_conf_count = sum(text.count(kw) for kw in self.CONFIDENCE_HIGH)
        
        if low_conf_count + high_conf_count > 0:
            analysis.confidence_estimate = 5.0 + (high_conf_count - low_conf_count) * 0.5
            analysis.confidence_estimate = max(1.0, min(10.0, analysis.confidence_estimate))
        
        # 细节丰富度 (基于特征总数)
        total_features = sum(analysis.features.values())
        analysis.detail_richness = min(1.0, total_features / 20.0)
        
        # 连贯性估计 (基于因果和反思内容)
        causal_reflective = analysis.features[NarrativeFeature.CAUSAL] + \
                           analysis.features[NarrativeFeature.REFLECTIVE]
        analysis.coherence_score = min(1.0, causal_reflective / 5.0)
        
        return analysis
    
    def extract_user_state(self, analysis: NarrativeAnalysis) -> UserState:
        """
        从叙事分析结果提取用户状态
        
        Args:
            analysis: NarrativeAnalysis 结果
        
        Returns:
            UserState 对象
        """
        return UserState(
            confidence=analysis.confidence_estimate,
            detail_count=sum(analysis.features.values()),
            source_unclear=analysis.features[NarrativeFeature.SPATIAL] < 2,
            emotional_rich=analysis.features[NarrativeFeature.EMOTIONAL] >= 3,
            narrative_fragmented=analysis.coherence_score < 0.3,
            segment_count=analysis.sentence_count
        )
    
    def generate_prompt(self, text: str, 
                        context: Optional[str] = None) -> Tuple[Prompt, NarrativeAnalysis]:
        """
        根据叙事内容生成引导问题
        
        Args:
            text: 用户叙事文本
            context: 对话上下文 (可选)
        
        Returns:
            (Prompt, NarrativeAnalysis) 元组
        """
        # 分析叙事
        analysis = self.analyze_narrative(text)
        
        # 提取用户状态
        user_state = self.extract_user_state(analysis)
        
        # 创建记忆片段
        memory_segment = MemorySegment(
            text=text,
            details=sum(analysis.features.values()),
            source_unclear=user_state.source_unclear,
            emotional_content=analysis.features[NarrativeFeature.EMOTIONAL] / 10.0,
            coherence=analysis.coherence_score
        )
        
        # 选择 prompt
        prompt = self.selector.select_prompt(user_state, memory_segment)
        
        return prompt, analysis
    
    def generate_follow_up(self, prompt: Prompt, 
                           user_response: str) -> Optional[str]:
        """
        根据用户回答生成追问
        
        Args:
            prompt: 已使用的 prompt
            user_response: 用户回答
        
        Returns:
            追问问题 (如果没有合适的追问则返回 None)
        """
        if not prompt.follow_up:
            return None
        
        # 简单策略：轮流使用追问
        # 更复杂的实现可以分析用户回答内容，选择最相关的追问
        return prompt.follow_up[0]
    
    def generate_session_plan(self, initial_text: str, 
                               num_turns: int = 5) -> List[Dict]:
        """
        为一次完整会话生成引导计划
        
        Args:
            initial_text: 初始叙事
            num_turns: 计划轮次
        
        Returns:
            引导计划列表
        """
        plan = []
        current_text = initial_text
        
        # 获取会话级 prompts
        analysis = self.analyze_narrative(initial_text)
        user_state = self.extract_user_state(analysis)
        prompts = self.selector.select_prompts_for_session(user_state, num_prompts=num_turns)
        
        for i, prompt in enumerate(prompts):
            plan.append({
                "turn": i + 1,
                "prompt_id": prompt.id,
                "category": prompt.category,
                "question": prompt.question,
                "follow_ups": prompt.follow_up,
                "rationale": prompt.rationale,
                "expected_outcome": prompt.expected_outcome
            })
        
        return plan
    
    def ab_test_assignment(self, user_id: str) -> str:
        """
        A/B 测试分组
        
        Args:
            user_id: 用户 ID
        
        Returns:
            "A" (对照组) 或 "B" (实验组)
        """
        # 简单哈希分组 (实际应使用更严谨的随机化)
        hash_val = hash(user_id) % 100
        return "B" if hash_val < 50 else "A"  # 50/50 分配
    
    def get_ab_test_prompts(self, group: str, text: str) -> Tuple[Prompt, NarrativeAnalysis]:
        """
        根据 A/B 测试分组获取 prompt
        
        Args:
            group: "A" 或 "B"
            text: 用户叙事
        
        Returns:
            (Prompt, NarrativeAnalysis) 元组
        """
        prompt, analysis = self.generate_prompt(text)
        
        if group == "A":
            # 对照组：使用标准叙事引导 (不带元记忆提示)
            # 这里简化处理，实际应使用不同的 prompt 集
            return prompt, analysis
        else:
            # 实验组：使用元记忆增强 prompt
            # 已经在 generate_prompt 中实现了元记忆策略
            return prompt, analysis


def demo():
    """演示用法"""
    print("=" * 60)
    print("元记忆引导问题生成器 - 演示")
    print("=" * 60)
    
    generator = PromptGenerator()
    
    # 测试样本 1: 简短模糊的叙事
    print("\n【样本 1】简短模糊的叙事")
    text1 = "我记得小时候有一次出去玩，好像是在一个公园里，具体记不清了。"
    prompt1, analysis1 = generator.generate_prompt(text1)
    print(f"字数：{analysis1.word_count}")
    print(f"信心估计：{analysis1.confidence_estimate:.1f}/10")
    print(f"细节丰富度：{analysis1.detail_richness:.2f}")
    print(f"选择策略：{prompt1.category}")
    print(f"问题：{prompt1.question}")
    
    # 测试样本 2: 详细的叙事
    print("\n【样本 2】详细的叙事")
    text2 = "那是 1985 年的夏天，我 10 岁。那天天气特别热，我和爸爸妈妈一起去西湖玩。我记得湖边有很多柳树，风吹过来很凉爽。我们坐在长椅上吃冰淇淋，爸爸给我讲了他小时候的故事。那时候我觉得特别开心，希望时间能停下来。"
    prompt2, analysis2 = generator.generate_prompt(text2)
    print(f"字数：{analysis2.word_count}")
    print(f"信心估计：{analysis2.confidence_estimate:.1f}/10")
    print(f"细节丰富度：{analysis2.detail_richness:.2f}")
    print(f"连贯性：{analysis2.coherence_score:.2f}")
    print(f"特征分布：{dict((k.value, v) for k, v in analysis2.features.items())}")
    print(f"选择策略：{prompt2.category}")
    print(f"问题：{prompt2.question}")
    
    # 测试样本 3: A/B 测试计划
    print("\n【样本 3】会话引导计划生成")
    text3 = "我记得第一次上班的那天，很紧张。"
    plan = generator.generate_session_plan(text3, num_turns=4)
    print(f"初始叙事：{text3}")
    print(f"计划轮次：{len(plan)}")
    for turn in plan:
        print(f"  第{turn['turn']}轮 [{turn['category']}]: {turn['question'][:40]}...")
    
    # 测试样本 4: A/B 测试分组
    print("\n【样本 4】A/B 测试分组")
    for user_id in ["user_001", "user_002", "user_003", "user_004"]:
        group = generator.ab_test_assignment(user_id)
        print(f"  {user_id} → 组别 {group}")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demo()
