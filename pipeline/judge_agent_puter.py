#!/usr/bin/env python3
"""
L0 标注质检多 Agent 系统 — 评委 Agent 实现 (Puter.js 版)

使用 Puter 免费 LLM API，无需 API Key。
支持模型：Qwen3-32b（中文支持好）

4 个评委 Agent 并行评分：
- Sensory (感官): 视觉/听觉/触觉/嗅觉/味觉细节
- Context (情境): 时间/地点/人物/事件完整性
- Emotion (情感): 情感表达深度与真实性
- Coherence (连贯性): 叙事逻辑与事件衔接
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# 使用 Puter LLM 客户端
from puter_llm_client import PuterLLMClient, ChatMessage


@dataclass
class JudgeResult:
    """单个评委的评分结果"""
    dimension: str  # 评分维度
    score: float  # 0-100 分
    confidence: float  # 0.0-1.0 置信度
    reasoning: str  # 自然语言理由
    evidence: List[str]  # 引用的原文片段


@dataclass
class NarrativeInput:
    """叙事输入"""
    text: str  # 原始叙事文本
    speaker_id: str  # 讲述者 ID
    life_stage: str  # 人生阶段 (Childhood/Youth/Adulthood/Late Adulthood)


class JudgeAgentPuter:
    """单个评委 Agent (Puter 版)"""
    
    def __init__(self, dimension: str, config: Optional[Dict] = None):
        """
        初始化评委 Agent
        
        Args:
            dimension: 评分维度 (Sensory/Context/Emotion/Coherence)
            config: 配置字典（可选）
        """
        self.dimension = dimension
        self.config = config or {}
        
        # 初始化 Puter 客户端（无需 API Key）
        self.client = PuterLLMClient(model="qwen3-32b")
    
    def _build_prompt(self, narrative: NarrativeInput) -> str:
        """构建评分 prompt"""
        dimension_prompts = {
            'Sensory': '''请评估以下叙事中的感官细节丰富度：
- 视觉细节（颜色、形状、光线、场景）
- 听觉细节（声音、对话、环境音）
- 触觉细节（温度、质地、身体感受）
- 嗅觉/味觉细节（气味、味道）

评分标准：
- 90-100: 感官细节极其丰富，读者能身临其境
- 70-89: 感官细节充足，有明确的场景感
- 50-69: 感官细节一般，部分场景有描述
- 30-49: 感官细节较少，mostly 抽象叙述
- 0-29: 几乎没有感官细节

叙事文本：
{narrative}

请严格按以下 JSON 格式输出（不要包含 Markdown 标记）：
{{
    "score": 0-100,
    "confidence": 0.0-1.0,
    "reasoning": "评分理由",
    "evidence": ["引用原文片段 1", "引用原文片段 2"]
}}''',
            
            'Context': '''请评估以下叙事的情境完整性：
- 时间信息（具体年份、季节、时段）
- 地点信息（具体位置、环境描述）
- 人物信息（涉及的人物及其关系）
- 事件信息（核心事件及其发展）

评分标准：
- 90-100: 四要素完整，细节清晰
- 70-89: 大部分要素完整，少量缺失
- 50-69: 部分要素缺失
- 30-49: 大部分要素缺失
- 0-29: 几乎没有情境信息

叙事文本：
{narrative}

请严格按以下 JSON 格式输出（不要包含 Markdown 标记）：
{{
    "score": 0-100,
    "confidence": 0.0-1.0,
    "reasoning": "评分理由",
    "evidence": ["引用原文片段 1", "引用原文片段 2"]
}}''',
            
            'Emotion': '''请评估以下叙事的情感表达深度：
- 情感词汇的使用
- 情感变化的层次
- 情感真实性
- 情感与事件的关联

评分标准：
- 90-100: 情感表达深刻、真实、多层次
- 70-89: 情感表达清晰，有一定深度
- 50-69: 情感表达一般，较为表面
- 30-49: 情感表达较少
- 0-29: 几乎没有情感表达

叙事文本：
{narrative}

请严格按以下 JSON 格式输出（不要包含 Markdown 标记）：
{{
    "score": 0-100,
    "confidence": 0.0-1.0,
    "reasoning": "评分理由",
    "evidence": ["引用原文片段 1", "引用原文片段 2"]
}}''',
            
            'Coherence': '''请评估以下叙事的连贯性：
- 时间顺序是否清晰
- 事件之间的因果/逻辑关系
- 叙述是否流畅
- 是否有跳跃或断裂

评分标准：
- 90-100: 逻辑清晰，衔接自然流畅
- 70-89: 整体连贯，少量跳跃
- 50-69: 部分连贯，有明显跳跃
- 30-49: 连贯性较差
- 0-29: 逻辑混乱，难以理解

叙事文本：
{narrative}

请严格按以下 JSON 格式输出（不要包含 Markdown 标记）：
{{
    "score": 0-100,
    "confidence": 0.0-1.0,
    "reasoning": "评分理由",
    "evidence": ["引用原文片段 1", "引用原文片段 2"]
}}'''
        }
        
        prompt_template = dimension_prompts.get(self.dimension, dimension_prompts['Coherence'])
        return prompt_template.format(narrative=narrative.text)
    
    def assess(self, narrative: NarrativeInput) -> JudgeResult:
        """
        评估叙事
        
        Args:
            narrative: 叙事输入
        
        Returns:
            JudgeResult: 评分结果
        """
        prompt = self._build_prompt(narrative)
        
        # 调用 Puter LLM
        response = self.client.chat([
            {"role": "system", "content": "你是一个专业的叙事分析专家，擅长评估口述历史的质量。请严格按 JSON 格式输出，不要包含 Markdown 标记。"},
            {"role": "user", "content": prompt}
        ])
        
        # 解析 JSON 响应
        try:
            # 清理响应（移除可能的 Markdown 标记）
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            
            return JudgeResult(
                dimension=self.dimension,
                score=float(data.get("score", 50)),
                confidence=float(data.get("confidence", 0.7)),
                reasoning=data.get("reasoning", "无说明"),
                evidence=data.get("evidence", [])
            )
            
        except json.JSONDecodeError as e:
            # JSON 解析失败，返回降级结果
            print(f"⚠️  JSON 解析失败 ({self.dimension}): {e}")
            print(f"   原始响应：{response.content[:200]}...")
            
            return JudgeResult(
                dimension=self.dimension,
                score=50.0,
                confidence=0.5,
                reasoning="JSON 解析失败，使用默认评分",
                evidence=[]
            )


class MultiJudgeSystem:
    """多评委系统"""
    
    def __init__(self):
        """初始化多评委系统"""
        self.dimensions = ['Sensory', 'Context', 'Emotion', 'Coherence']
        self.judges = {
            dim: JudgeAgentPuter(dimension=dim)
            for dim in self.dimensions
        }
    
    def assess_parallel(self, narrative: NarrativeInput) -> Dict[str, JudgeResult]:
        """
        并行执行所有评委评分
        
        Args:
            narrative: 叙事输入
        
        Returns:
            Dict[str, JudgeResult]: 各维度评分结果
        """
        results = {}
        
        print(f"\n开始多评委评分...")
        for dim in self.dimensions:
            print(f"  [{dim}] 评分中...")
            result = self.judges[dim].assess(narrative)
            results[dim] = result
            print(f"  [{dim}] 完成：{result.score:.1f}分 (置信度：{result.confidence:.2f})")
        
        return results
    
    def analyze_consensus(self, results: Dict[str, JudgeResult]) -> Dict:
        """
        分析评委一致性
        
        Args:
            results: 各维度评分结果
        
        Returns:
            Dict: 一致性分析报告
        """
        scores = [r.score for r in results.values()]
        confidences = [r.confidence for r in results.values()]
        
        max_score = max(scores)
        min_score = min(scores)
        max_diff = max_score - min_score
        avg_score = sum(scores) / len(scores)
        avg_confidence = sum(confidences) / len(confidences)
        
        # 判定一致性
        conflict_threshold = 15.0
        is_consistent = max_diff <= conflict_threshold
        
        return {
            "scores": scores,
            "max_score": max_score,
            "min_score": min_score,
            "max_diff": max_diff,
            "avg_score": avg_score,
            "avg_confidence": avg_confidence,
            "is_consistent": is_consistent,
            "conflict_threshold": conflict_threshold
        }


# 测试函数
def test_judge_system():
    """测试评委系统"""
    print("=" * 60)
    print("L0 质检多评委系统 (Puter 版) - 测试")
    print("=" * 60)
    
    # 测试样本
    test_narrative = NarrativeInput(
        text="""
        1978 年冬天，我 15 岁，在黑龙江下乡。清晨 5 点，天还没亮，
        茅草屋顶上结了一层白霜。我推开木门，"吱呀"一声，
        冷风灌进来，像刀子一样刮在脸上。院子里的井台结了冰，
        我提着水桶，手冻得通红，指尖几乎没有知觉。
        远处传来生产队的钟声，"当当当"，在寂静的清晨传得很远。
        """,
        speaker_id="test_001",
        life_stage="Youth"
    )
    
    # 创建系统
    system = MultiJudgeSystem()
    
    # 并行评分
    results = system.assess_parallel(test_narrative)
    
    # 分析一致性
    print("\n" + "=" * 60)
    print("一致性分析")
    print("=" * 60)
    
    consensus = system.analyze_consensus(results)
    
    print(f"最高分：{consensus['max_score']:.1f}")
    print(f"最低分：{consensus['min_score']:.1f}")
    print(f"差异：{consensus['max_diff']:.1f}分")
    print(f"平均分：{consensus['avg_score']:.1f}")
    print(f"平均置信度：{consensus['avg_confidence']:.2f}")
    print(f"一致性判定：{'✅ 一致' if consensus['is_consistent'] else '⚠️ 需要仲裁'}")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    test_judge_system()
