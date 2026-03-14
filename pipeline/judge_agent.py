#!/usr/bin/env python3
"""
L0 标注质检多 Agent 系统 — 评委 Agent 实现

4 个评委 Agent 并行评分：
- Sensory (感官): 视觉/听觉/触觉/嗅觉/味觉细节
- Context (情境): 时间/地点/人物/事件完整性
- Emotion (情感): 情感表达深度与真实性
- Coherence (连贯性): 叙事逻辑与事件衔接

架构参考：Claude Code Code Review (2026-03)
预期一致性：≥85% (vs 人工标注)
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dashscope import Generation


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


class JudgeAgent:
    """单个评委 Agent"""
    
    def __init__(self, dimension: str, config: Dict):
        self.dimension = dimension
        self.config = config
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY not set")
    
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
- 30-49: 感官细节较少， mostly 抽象叙述
- 0-29: 几乎没有感官细节

叙事文本：
{narrative}

请按以下 JSON 格式输出：
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
- 事件信息（发生了什么、如何发生）

评分标准：
- 90-100: 四要素完整且具体
- 70-89: 三要素完整，细节充足
- 50-69: 两要素完整，基本清晰
- 30-49: 仅一要素完整，模糊
- 0-29: 四要素均缺失或极模糊

叙事文本：
{narrative}

请按以下 JSON 格式输出：
{{
    "score": 0-100,
    "confidence": 0.0-1.0,
    "reasoning": "评分理由",
    "evidence": ["引用原文片段 1", "引用原文片段 2"]
}}''',
            
            'Emotion': '''请评估以下叙事的情感表达深度：
- 情感词汇的使用（直接表达情感）
- 情感变化的描述（情感如何随事件变化）
- 情感真实性（是否自然、不做作）
- 情感影响力（能否引起读者共鸣）

评分标准：
- 90-100: 情感深刻、真实、有感染力
- 70-89: 情感清晰表达，有一定深度
- 50-69: 有情感表达，但较表面
- 30-49: 情感表达较少，偏事实陈述
- 0-29: 几乎没有情感表达

叙事文本：
{narrative}

请按以下 JSON 格式输出：
{{
    "score": 0-100,
    "confidence": 0.0-1.0,
    "reasoning": "评分理由",
    "evidence": ["引用原文片段 1", "引用原文片段 2"]
}}''',
            
            'Coherence': '''请评估以下叙事的连贯性：
- 事件顺序是否清晰（时间线/因果链）
- 段落/事件之间的衔接是否自然
- 是否有逻辑跳跃或矛盾
- 整体叙事是否易于理解

评分标准：
- 90-100: 逻辑清晰，衔接自然，无跳跃
- 70-89: 整体连贯，偶有小跳跃
- 50-69: 基本可理解，有明显跳跃
- 30-49: 连贯性较差，需要猜测
- 0-29: 混乱，难以理解

叙事文本：
{narrative}

请按以下 JSON 格式输出：
{{
    "score": 0-100,
    "confidence": 0.0-1.0,
    "reasoning": "评分理由",
    "evidence": ["引用原文片段 1", "引用原文片段 2"]
}}'''
        }
        
        prompt_template = dimension_prompts.get(self.dimension, dimension_prompts['Coherence'])
        return prompt_template.format(narrative=narrative.text)
    
    def evaluate(self, narrative: NarrativeInput) -> JudgeResult:
        """执行评分"""
        prompt = self._build_prompt(narrative)
        
        try:
            response = Generation.call(
                model='qwen3.5-plus',
                messages=[{'role': 'user', 'content': prompt}],
                result_format='message'
            )
            
            # 解析 JSON 响应
            import json
            content = response.output.choices[0].message.content
            result_dict = json.loads(content)
            
            return JudgeResult(
                dimension=self.dimension,
                score=float(result_dict['score']),
                confidence=float(result_dict['confidence']),
                reasoning=result_dict['reasoning'],
                evidence=result_dict.get('evidence', [])
            )
            
        except Exception as e:
            # 降级处理：返回低置信度的中性评分
            return JudgeResult(
                dimension=self.dimension,
                score=50.0,
                confidence=0.3,
                reasoning=f"评分失败：{str(e)}",
                evidence=[]
            )


class MultiJudgeSystem:
    """多评委联合评分系统"""
    
    def __init__(self, config_path: str = None):
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # 默认配置
            self.config = {
                'judges': ['Sensory', 'Context', 'Emotion', 'Coherence'],
                'weights': {
                    'Sensory': 0.25,
                    'Context': 0.25,
                    'Emotion': 0.25,
                    'Coherence': 0.25
                },
                'conflict_threshold': 15.0,  # 分数差异>15 分触发仲裁
                'min_confidence': 0.6  # 最低置信度阈值
            }
        
        self.judges = {
            dim: JudgeAgent(dim, self.config)
            for dim in self.config['judges']
        }
    
    def evaluate_parallel(self, narrative: NarrativeInput) -> Dict[str, JudgeResult]:
        """并行执行所有评委评分"""
        import concurrent.futures
        
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_judge = {
                executor.submit(judge.evaluate, narrative): dim
                for dim, judge in self.judges.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_judge):
                dim = future_to_judge[future]
                try:
                    results[dim] = future.result()
                except Exception as e:
                    results[dim] = JudgeResult(
                        dimension=dim,
                        score=50.0,
                        confidence=0.0,
                        reasoning=f"执行错误：{str(e)}",
                        evidence=[]
                    )
        
        return results
    
    def weighted_average(self, results: Dict[str, JudgeResult]) -> Tuple[float, float]:
        """计算置信度加权平均分"""
        total_weight = 0.0
        weighted_sum = 0.0
        
        for dim, result in results.items():
            weight = self.config['weights'].get(dim, 0.25) * result.confidence
            weighted_sum += result.score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 50.0, 0.0
        
        return weighted_sum / total_weight, total_weight / len(results)
    
    def detect_conflict(self, results: Dict[str, JudgeResult]) -> bool:
        """检测是否存在评分分歧"""
        scores = [r.score for r in results.values()]
        if len(scores) < 2:
            return False
        
        max_score = max(scores)
        min_score = min(scores)
        
        return (max_score - min_score) > self.config['conflict_threshold']
    
    def evaluate(self, narrative: NarrativeInput) -> Dict:
        """完整评估流程"""
        # 1. 并行评分
        results = self.evaluate_parallel(narrative)
        
        # 2. 计算加权平均
        final_score, avg_confidence = self.weighted_average(results)
        
        # 3. 检测分歧
        needs_arbitration = self.detect_conflict(results)
        
        return {
            'narrative_id': narrative.speaker_id,
            'life_stage': narrative.life_stage,
            'dimension_scores': {
                dim: {
                    'score': r.score,
                    'confidence': r.confidence,
                    'reasoning': r.reasoning,
                    'evidence': r.evidence
                }
                for dim, r in results.items()
            },
            'final_score': final_score,
            'average_confidence': avg_confidence,
            'needs_arbitration': needs_arbitration,
            'arbitration_reason': f"分数差异过大 (max-min={max(r.score for r in results.values()) - min(r.score for r in results.values()):.1f}分)" if needs_arbitration else None
        }


if __name__ == '__main__':
    # 测试示例
    test_narrative = NarrativeInput(
        text="那是我 10 岁的夏天，在杭州西湖边。阳光透过柳树叶洒在湖面上，波光粼粼的。我和爷爷坐在长椅上，他给我讲他年轻时的故事。微风拂过，带来荷花的清香。爷爷的声音很温和，我记得他手上的皱纹和老茧。",
        speaker_id='test_001',
        life_stage='Childhood'
    )
    
    system = MultiJudgeSystem()
    result = system.evaluate(test_narrative)
    
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
