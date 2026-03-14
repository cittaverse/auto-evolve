#!/usr/bin/env python3
"""
L0 标注质检多 Agent 系统 — 仲裁 Agent 实现

当 4 个评委的评分差异超过阈值时，启动仲裁流程：
1. 分析分歧原因
2. 组织辩论式仲裁（让评委"辩论"）
3. 做出最终裁决

架构参考：Claude Code Code Review (2026-03)
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from dashscope import Generation


@dataclass
class ArbitrationInput:
    """仲裁输入"""
    narrative_text: str
    dimension_results: Dict[str, Dict]  # 各评委的评分结果
    conflict_reason: str  # 分歧原因


@dataclass
class ArbitrationResult:
    """仲裁结果"""
    final_scores: Dict[str, float]  # 仲裁后的各维度分数
    adjustments: Dict[str, float]  # 各维度调整幅度
    reasoning: str  # 仲裁理由
    confidence: float  # 仲裁置信度


class ArbitratorAgent:
    """仲裁 Agent"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {
            'model': 'qwen3.5-plus',
            'debate_rounds': 2,
            'adjustment_limit': 15.0  # 单次调整不超过 15 分
        }
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
    
    def _build_debate_prompt(self, input_data: ArbitrationInput) -> str:
        """构建辩论式仲裁 prompt"""
        # 整理各评委的观点
        judge_opinions = []
        for dim, result in input_data.dimension_results.items():
            judge_opinions.append(
                f"**{dim} 评委**：{result['score']}分 (置信度：{result['confidence']:.2f})\n"
                f"理由：{result['reasoning']}\n"
                f"证据：{', '.join(result['evidence'][:2]) if result['evidence'] else '无'}"
            )
        
        opinions_text = '\n\n'.join(judge_opinions)
        
        prompt = f'''你是一位经验丰富的叙事质量评估仲裁员。现在有 4 位评委对同一篇叙事进行了评分，但他们的分数存在显著差异。

## 叙事原文
{input_data.narrative_text}

## 评委评分与理由

{opinions_text}

## 分歧情况
{input_data.conflict_reason}

## 你的任务

请进行辩论式仲裁：

1. **分析分歧根源**：为什么评委会给出差异这么大的分数？是标准理解不同，还是关注点不同？

2. **评估各评委理由的合理性**：哪位评委的理由更充分？证据更可靠？

3. **做出最终裁决**：对每个维度给出仲裁后的分数（可以调整，但调整幅度不应超过 15 分）

4. **说明仲裁理由**：清晰解释你为什么这样裁决

请按以下 JSON 格式输出：
{{
    "conflict_analysis": "分歧根源分析",
    "judge_evaluation": {{
        "Sensory": "对该评委的评价",
        "Context": "对该评委的评价",
        "Emotion": "对该评委的评价",
        "Coherence": "对该评委的评价"
    }},
    "final_scores": {{
        "Sensory": 0-100,
        "Context": 0-100,
        "Emotion": 0-100,
        "Coherence": 0-100
    }},
    "adjustments": {{
        "Sensory": 调整幅度（正数=上调，负数=下调）,
        "Context": 调整幅度,
        "Emotion": 调整幅度,
        "Coherence": 调整幅度
    }},
    "arbitration_reasoning": "仲裁理由",
    "confidence": 0.0-1.0
}}'''
        
        return prompt
    
    def arbitrate(self, input_data: ArbitrationInput) -> ArbitrationResult:
        """执行仲裁"""
        prompt = self._build_debate_prompt(input_data)
        
        try:
            response = Generation.call(
                model=self.config['model'],
                messages=[{'role': 'user', 'content': prompt}],
                result_format='message'
            )
            
            content = response.output.choices[0].message.content
            result_dict = json.loads(content)
            
            return ArbitrationResult(
                final_scores=result_dict['final_scores'],
                adjustments=result_dict['adjustments'],
                reasoning=result_dict['arbitration_reasoning'],
                confidence=result_dict['confidence']
            )
            
        except Exception as e:
            # 降级处理：不做调整，返回原始分数
            return ArbitrationResult(
                final_scores={
                    dim: result['score']
                    for dim, result in input_data.dimension_results.items()
                },
                adjustments={dim: 0.0 for dim in input_data.dimension_results.keys()},
                reasoning=f"仲裁失败：{str(e)}",
                confidence=0.0
            )


class DebateEngine:
    """辩论引擎 — 模拟多轮辩论"""
    
    def __init__(self, arbitrator: ArbitratorAgent):
        self.arbitrator = arbitrator
    
    def _build_round_prompt(self, narrative: str, current_scores: Dict[str, float], 
                           round_num: int, previous_debate: str = None) -> str:
        """构建单轮辩论 prompt"""
        prompt = f'''## 叙事质量评估辩论 — 第{round_num}轮

叙事原文：
{narrative}

当前各维度分数：
- Sensory: {current_scores.get('Sensory', 50)}
- Context: {current_scores.get('Context', 50)}
- Emotion: {current_scores.get('Emotion', 50)}
- Coherence: {current_scores.get('Coherence', 50)}
'''
        
        if previous_debate:
            prompt += f'''\n上一轮辩论要点：
{previous_debate}

请基于上一轮辩论，重新审视各维度分数是否需要调整。
'''
        
        prompt += '''
请 4 位评委（Sensory/Context/Emotion/Coherence）进行辩论：
1. 每位评委陈述自己的评分理由
2. 指出其他评委评分可能的问题
3. 提出自己分数是否应该调整

输出格式：
{
    "debate_summary": "辩论要点总结",
    "score_adjustments": {
        "Sensory": 调整建议（正/负/0）,
        "Context": 调整建议,
        "Emotion": 调整建议,
        "Coherence": 调整建议
    },
    "consensus_reached": true/false
}'''
        
        return prompt
    
    def run_debate(self, narrative: str, initial_scores: Dict[str, float], 
                   max_rounds: int = 2) -> Dict[str, float]:
        """运行多轮辩论"""
        current_scores = initial_scores.copy()
        debate_history = []
        
        for round_num in range(1, max_rounds + 1):
            previous_debate = '\n'.join(debate_history[-2:]) if debate_history else None
            
            prompt = self._build_round_prompt(narrative, current_scores, round_num, previous_debate)
            
            try:
                response = Generation.call(
                    model=self.arbitrator.config['model'],
                    messages=[{'role': 'user', 'content': prompt}],
                    result_format='message'
                )
                
                content = response.output.choices[0].message.content
                result = json.loads(content)
                
                debate_history.append(result['debate_summary'])
                
                # 应用调整
                for dim, adjustment in result['score_adjustments'].items():
                    if dim in current_scores:
                        # 限制调整幅度
                        adjustment = max(-15, min(15, adjustment))
                        current_scores[dim] += adjustment
                        # 确保分数在 0-100 范围内
                        current_scores[dim] = max(0, min(100, current_scores[dim]))
                
                # 如果达成共识，提前结束
                if result.get('consensus_reached', False):
                    break
                    
            except Exception as e:
                # 辩论失败，继续下一轮或结束
                continue
        
        return current_scores


def full_arbitration_flow(narrative_text: str, dimension_results: Dict[str, Dict], 
                          conflict_reason: str) -> Dict:
    """完整的仲裁流程"""
    # 1. 准备输入
    input_data = ArbitrationInput(
        narrative_text=narrative_text,
        dimension_results=dimension_results,
        conflict_reason=conflict_reason
    )
    
    # 2. 创建仲裁器
    arbitrator = ArbitratorAgent()
    
    # 3. 执行仲裁
    arbitration_result = arbitrator.arbitrate(input_data)
    
    # 4. （可选）运行辩论引擎进行多轮优化
    debate_engine = DebateEngine(arbitrator)
    initial_scores = {
        dim: result['score'] for dim, result in dimension_results.items()
    }
    
    debated_scores = debate_engine.run_debate(narrative_text, initial_scores, max_rounds=2)
    
    # 5. 合并结果（优先使用辩论后的分数）
    final_result = {
        'original_scores': initial_scores,
        'arbitrated_scores': arbitration_result.final_scores,
        'debated_scores': debated_scores,
        'final_used_scores': debated_scores,  # 使用辩论后的分数
        'adjustments': arbitration_result.adjustments,
        'arbitration_reasoning': arbitration_result.reasoning,
        'confidence': arbitration_result.confidence
    }
    
    return final_result


if __name__ == '__main__':
    # 测试示例
    test_dimension_results = {
        'Sensory': {'score': 85, 'confidence': 0.9, 'reasoning': '感官细节丰富', 'evidence': ['波光粼粼', '荷花的清香']},
        'Context': {'score': 90, 'confidence': 0.95, 'reasoning': '时间地点人物完整', 'evidence': ['10 岁的夏天', '杭州西湖边']},
        'Emotion': {'score': 60, 'confidence': 0.7, 'reasoning': '情感表达较少', 'evidence': []},
        'Coherence': {'score': 88, 'confidence': 0.85, 'reasoning': '叙事连贯', 'evidence': ['我和爷爷坐在长椅上']}
    }
    
    test_narrative = "那是我 10 岁的夏天，在杭州西湖边。阳光透过柳树叶洒在湖面上，波光粼粼的。我和爷爷坐在长椅上，他给我讲他年轻时的故事。微风拂过，带来荷花的清香。爷爷的声音很温和，我记得他手上的皱纹和老茧。"
    
    result = full_arbitration_flow(
        narrative_text=test_narrative,
        dimension_results=test_dimension_results,
        conflict_reason="Emotion 分数 (60) 显著低于其他维度 (85-90)，差异>15 分"
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
