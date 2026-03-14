#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
元记忆 (Metamemory) 策略选择器
版本：1.0 (阶段 3 代码实现)
创建日期：2026-03-14
作者：Hulk 🟢

功能：根据用户状态和记忆片段特征，智能选择元记忆引导策略
来源：JMIR mHealth 2026-01 + MEMORY.md 研究洞察
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class MetamemoryCategory(Enum):
    """元记忆策略类别"""
    SOURCE_MONITORING = "source_monitoring"      # 来源监控
    CONFIDENCE_ASSESSMENT = "confidence_assessment"  # 信心评估
    STRATEGY_CUEING = "strategy_cueing"        # 策略提示
    MEANING_REFLECTION = "meaning_reflection"  # 意义反思


@dataclass
class UserState:
    """用户当前状态"""
    confidence: float = 5.0  # 记忆信心 (1-10 分)
    detail_count: int = 0    # 已提取的细节数量
    source_unclear: bool = False  # 来源是否模糊
    emotional_rich: bool = False  # 是否情感丰富
    narrative_fragmented: bool = False  # 叙事是否碎片化
    segment_count: int = 0   # 事件分段数


@dataclass
class MemorySegment:
    """记忆片段特征"""
    text: str
    details: int = 0         # 细节数量
    source_unclear: bool = False
    emotional_content: float = 0.0  # 情感强度 (0-1)
    coherence: float = 0.0   # 连贯性 (0-1)


@dataclass
class Prompt:
    """引导问题"""
    id: str
    category: str
    question: str
    follow_up: List[str]
    rationale: str
    expected_outcome: str
    trigger_keywords: Optional[List[str]] = None
    scale: Optional[Dict] = None
    options: Optional[List[str]] = None
    technique: Optional[str] = None


class MetamemorySelector:
    """元记忆策略选择器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化选择器
        
        Args:
            config_path: YAML 配置文件路径，默认使用 config/metamemory_prompts.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "metamemory_prompts.yaml"
        
        self.config_path = Path(config_path)
        self.prompts: Dict[str, Prompt] = {}
        self.category_prompts: Dict[MetamemoryCategory, List[Prompt]] = {
            cat: [] for cat in MetamemoryCategory
        }
        self._load_config()
    
    def _load_config(self):
        """加载 YAML 配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 YAML (处理多个文档)
        docs = yaml.safe_load_all(content)
        for doc in docs:
            if doc is None:
                continue
            
            # 遍历四个类别
            categories = {
                'source_monitoring': MetamemoryCategory.SOURCE_MONITORING,
                'confidence_assessment': MetamemoryCategory.CONFIDENCE_ASSESSMENT,
                'strategy_cueing': MetamemoryCategory.STRATEGY_CUEING,
                'meaning_reflection': MetamemoryCategory.MEANING_REFLECTION
            }
            
            for section_key, category in categories.items():
                # 查找对应的章节 (如 "一、来源监控")
                for key, value in doc.items() if isinstance(doc, dict) else []:
                    if isinstance(value, dict):
                        prompts_data = value.get('引导问题', {})
                        if isinstance(prompts_data, dict):
                            for prompt_id, prompt_data in prompts_data.items():
                                if isinstance(prompt_data, dict):
                                    prompt = self._parse_prompt(prompt_id, prompt_data, category)
                                    if prompt:
                                        self.prompts[prompt.id] = prompt
                                        self.category_prompts[category].append(prompt)
        
        print(f"Loaded {len(self.prompts)} prompts across {len(MetamemoryCategory)} categories")
    
    def _parse_prompt(self, prompt_id: str, data: dict, category: MetamemoryCategory) -> Optional[Prompt]:
        """解析单个 prompt 数据"""
        try:
            return Prompt(
                id=prompt_id,
                category=category.value,
                question=data.get('question', ''),
                follow_up=data.get('follow_up', []),
                rationale=data.get('rationale', ''),
                expected_outcome=data.get('expected_outcome', ''),
                trigger_keywords=data.get('trigger_keywords'),
                scale=data.get('scale'),
                options=data.get('options'),
                technique=data.get('technique')
            )
        except Exception as e:
            print(f"Error parsing prompt {prompt_id}: {e}")
            return None
    
    def select_prompt(self, user_state: UserState, memory_segment: Optional[MemorySegment] = None) -> Prompt:
        """
        根据用户状态选择最合适的元记忆引导问题
        
        选择策略 (基于 config 使用指南):
        1. 记忆模糊 (confidence < 5) → 信心评估 → 策略提示
        2. 细节缺失 (detail_count < 3) → 策略提示 (情境重建)
        3. 来源模糊 → 来源监控
        4. 叙事碎片化 → 意义反思 (身份连接)
        5. 情感丰富 → 策略提示 (情感连接)
        6. 默认 → 意义反思 (个人意义)
        
        Args:
            user_state: 用户当前状态
            memory_segment: 当前记忆片段 (可选)
        
        Returns:
            最合适的引导问题
        """
        # 决策树 (基于 config 使用指南)
        if user_state.confidence < 5:
            # 信心不足：先评估信心
            prompt = self._get_prompt_by_id("CA-001")
            if prompt:
                return prompt
        
        if user_state.detail_count < 3:
            # 细节缺失：情境重建
            prompt = self._get_prompt_by_id("SC-001")
            if prompt:
                return prompt
        
        if user_state.source_unclear:
            # 来源模糊：来源监控
            prompt = self._get_prompt_by_id("SM-001")
            if prompt:
                return prompt
        
        if user_state.narrative_fragmented:
            # 叙事碎片化：意义反思 (身份连接)
            prompt = self._get_prompt_by_id("MR-003")
            if prompt:
                return prompt
        
        if user_state.emotional_rich:
            # 情感丰富：情感连接
            prompt = self._get_prompt_by_id("SC-003")
            if prompt:
                return prompt
        
        # 默认：个人意义
        prompt = self._get_prompt_by_id("MR-001")
        if prompt:
            return prompt
        
        # Fallback: 返回第一个可用的 prompt
        for prompts in self.category_prompts.values():
            if prompts:
                return prompts[0]
        
        raise RuntimeError("No prompts available")
    
    def _get_prompt_by_id(self, prompt_id: str) -> Optional[Prompt]:
        """根据 ID 获取 prompt"""
        return self.prompts.get(prompt_id)
    
    def get_prompts_by_category(self, category: MetamemoryCategory) -> List[Prompt]:
        """获取某类别的所有 prompts"""
        return self.category_prompts.get(category, [])
    
    def get_all_prompts(self) -> Dict[str, Prompt]:
        """获取所有 prompts"""
        return self.prompts
    
    def select_prompts_for_session(self, user_state: UserState, 
                                    num_prompts: int = 5) -> List[Prompt]:
        """
        为一次会话选择多个引导问题 (用于 A/B 测试或连续引导)
        
        Args:
            user_state: 用户状态
            num_prompts: 需要的 prompt 数量
        
        Returns:
            prompt 列表 (按推荐顺序)
        """
        selected = []
        
        # 第一阶段：信心评估 (始终开始)
        ca_prompt = self._get_prompt_by_id("CA-001")
        if ca_prompt:
            selected.append(ca_prompt)
        
        # 第二阶段：策略提示 (情境重建)
        sc_prompt = self._get_prompt_by_id("SC-001")
        if sc_prompt and len(selected) < num_prompts:
            selected.append(sc_prompt)
        
        # 第三阶段：来源监控
        if user_state.source_unclear:
            sm_prompt = self._get_prompt_by_id("SM-001")
            if sm_prompt and len(selected) < num_prompts:
                selected.append(sm_prompt)
        
        # 第四阶段：意义反思
        mr_prompt = self._get_prompt_by_id("MR-001")
        if mr_prompt and len(selected) < num_prompts:
            selected.append(mr_prompt)
        
        # 补充：根据需要添加更多
        while len(selected) < num_prompts:
            # 轮流从各类别添加
            for category in MetamemoryCategory:
                prompts = self.category_prompts[category]
                for prompt in prompts:
                    if prompt not in selected and len(selected) < num_prompts:
                        selected.append(prompt)
                        break
                if len(selected) >= num_prompts:
                    break
        
        return selected[:num_prompts]


def demo():
    """演示用法"""
    print("=" * 60)
    print("元记忆策略选择器 - 演示")
    print("=" * 60)
    
    selector = MetamemorySelector()
    
    # 测试场景 1: 信心不足的用户
    print("\n【场景 1】信心不足的用户")
    user_state_1 = UserState(confidence=3.0, detail_count=1)
    prompt_1 = selector.select_prompt(user_state_1)
    print(f"选择策略：{prompt_1.category}")
    print(f"问题：{prompt_1.question}")
    print(f"追问：{prompt_1.follow_up}")
    
    # 测试场景 2: 细节缺失
    print("\n【场景 2】细节缺失的用户")
    user_state_2 = UserState(confidence=7.0, detail_count=2)
    prompt_2 = selector.select_prompt(user_state_2)
    print(f"选择策略：{prompt_2.category}")
    print(f"问题：{prompt_2.question}")
    print(f"技巧：{prompt_2.technique or 'N/A'}")
    
    # 测试场景 3: 叙事碎片化
    print("\n【场景 3】叙事碎片化的用户")
    user_state_3 = UserState(confidence=6.0, detail_count=5, narrative_fragmented=True)
    prompt_3 = selector.select_prompt(user_state_3)
    print(f"选择策略：{prompt_3.category}")
    print(f"问题：{prompt_3.question}")
    print(f"预期结果：{prompt_3.expected_outcome}")
    
    # 测试场景 4: 会话级多问题选择
    print("\n【场景 4】会话级多问题选择 (A/B 测试)")
    user_state_4 = UserState(confidence=5.0, detail_count=3, source_unclear=True)
    prompts_4 = selector.select_prompts_for_session(user_state_4, num_prompts=4)
    print(f"选择了 {len(prompts_4)} 个问题:")
    for i, p in enumerate(prompts_4, 1):
        print(f"  {i}. [{p.id}] {p.question[:50]}...")
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    demo()
