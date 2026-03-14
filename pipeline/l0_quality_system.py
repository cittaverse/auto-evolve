#!/usr/bin/env python3
"""
L0 标注质检多 Agent 系统 — 主入口

整合 4 个评委 Agent + 仲裁 Agent + 投票系统，实现自动化叙事质量评估。

架构：
1. 4 个评委并行评分 (Sensory/Context/Emotion/Coherence)
2. 投票系统计算加权分数 + 检测分歧
3. 如分歧超过阈值，启动仲裁
4. 输出最终评分 + 理由

验收指标：
- 一致性 (Cohen's Kappa): ≥0.85
- 相关性 (Pearson): ≥0.88
- P95 延迟：<500ms
- 吞吐量：>10 条/秒
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# 导入子模块
from judge_agent import JudgeAgent, JudgeResult, NarrativeInput
from arbitrator_agent import ArbitratorAgent, ArbitrationInput, ArbitrationResult
from voting_system import VotingSystem, VoteInput, VoteResult


@dataclass
class QualityAssessmentResult:
    """质检结果"""
    speaker_id: str
    life_stage: str
    dimension_scores: Dict[str, float]  # 各维度最终分数
    overall_score: float  # 综合分数
    grade: str  # 等级 (S/A/B/C/D)
    arbitration_triggered: bool  # 是否触发仲裁
    arbitration_reason: str  # 仲裁原因（如有）
    detailed_results: Dict  # 各评委详细结果
    total_latency_ms: float  # 总耗时


class L0QualitySystem:
    """L0 标注质检多 Agent 系统"""
    
    def __init__(self, config_path: str = None):
        """初始化系统"""
        # 加载配置
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(__file__),
                '..', 'config', 'judge_config.json'
            )
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 初始化评委
        self.judges = {}
        for judge_config in self.config['judges']:
            if judge_config['enabled']:
                self.judges[judge_config['name']] = JudgeAgent(
                    dimension=judge_config['name'],
                    config=judge_config
                )
        
        # 初始化投票系统和仲裁 Agent
        self.voting_system = VotingSystem(self.config.get('voting', {}))
        self.arbitrator = ArbitratorAgent(self.config.get('arbitration', {}))
        
        # 阈值配置
        self.conflict_threshold = self.config['thresholds']['conflict_threshold']
        self.grades = self.config['thresholds']['grades']
    
    def _calculate_grade(self, score: float) -> str:
        """根据分数计算等级"""
        for grade, min_score in sorted(self.grades.items(), key=lambda x: x[1], reverse=True):
            if score >= min_score:
                return grade
        return 'D'
    
    def _check_conflict(self, scores: Dict[str, float]) -> Tuple[bool, str]:
        """检查是否需要仲裁"""
        score_values = list(scores.values())
        if len(score_values) < 2:
            return False, ""
        
        max_score = max(score_values)
        min_score = min(score_values)
        diff = max_score - min_score
        
        if diff > self.conflict_threshold:
            return True, f"分数差异过大：{diff:.1f}分 > 阈值{self.conflict_threshold}分"
        
        return False, ""
    
    def assess(self, text: str, speaker_id: str = "unknown", life_stage: str = "unknown") -> QualityAssessmentResult:
        """
        评估单条叙事
        
        Args:
            text: 叙事文本
            speaker_id: 讲述者 ID
            life_stage: 人生阶段
        
        Returns:
            QualityAssessmentResult: 质检结果
        """
        start_time = time.time()
        
        narrative = NarrativeInput(
            text=text,
            speaker_id=speaker_id,
            life_stage=life_stage
        )
        
        # 1. 并行执行 4 个评委评分
        judge_results = {}
        with ThreadPoolExecutor(max_workers=self.config['performance']['max_workers']) as executor:
            futures = {
                executor.submit(judge.assess, narrative): name
                for name, judge in self.judges.items()
            }
            
            for future in as_completed(futures):
                name = futures[future]
                try:
                    result = future.result(timeout=self.config['performance']['api_timeout'])
                    judge_results[name] = result
                except Exception as e:
                    print(f"Judge {name} failed: {e}", file=sys.stderr)
                    judge_results[name] = JudgeResult(
                        dimension=name,
                        score=50.0,
                        confidence=0.3,
                        reasoning=f"评分失败：{e}",
                        evidence=[]
                    )
        
        # 2. 投票系统计算加权分数
        dimension_scores = {}
        for name, result in judge_results.items():
            dimension_scores[name] = result.score
        
        # 3. 检查是否需要仲裁
        conflict_needed, conflict_reason = self._check_conflict(dimension_scores)
        
        if conflict_needed and self.config['arbitration']['enable_debate']:
            # 4. 启动仲裁
            arb_input = ArbitrationInput(
                narrative_text=text,
                dimension_results={
                    name: asdict(result) for name, result in judge_results.items()
                },
                conflict_reason=conflict_reason
            )
            arb_result = self.arbitrator.arbitrate(arb_input)
            dimension_scores = arb_result.final_scores
            arbitration_triggered = True
            arbitration_reason = conflict_reason
        else:
            arbitration_triggered = False
            arbitration_reason = ""
        
        # 5. 计算综合分数（简单平均）
        overall_score = sum(dimension_scores.values()) / len(dimension_scores)
        grade = self._calculate_grade(overall_score)
        
        # 6. 计算总耗时
        total_latency_ms = (time.time() - start_time) * 1000
        
        return QualityAssessmentResult(
            speaker_id=speaker_id,
            life_stage=life_stage,
            dimension_scores=dimension_scores,
            overall_score=overall_score,
            grade=grade,
            arbitration_triggered=arbitration_triggered,
            arbitration_reason=arbitration_reason,
            detailed_results={
                name: asdict(result) for name, result in judge_results.items()
            },
            total_latency_ms=total_latency_ms
        )
    
    def assess_batch(self, narratives: List[Dict], max_workers: int = 4) -> List[QualityAssessmentResult]:
        """
        批量评估叙事
        
        Args:
            narratives: 叙事列表，每项包含 {text, speaker_id, life_stage}
            max_workers: 并发数
        
        Returns:
            List[QualityAssessmentResult]: 质检结果列表
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.assess,
                    item['text'],
                    item.get('speaker_id', 'unknown'),
                    item.get('life_stage', 'unknown')
                ): i
                for i, item in enumerate(narratives)
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Assessment failed: {e}", file=sys.stderr)
        
        return results


def main():
    """测试入口"""
    # 示例叙事
    test_narrative = """
    那是我 10 岁那年的夏天，在老家院子里。阳光透过葡萄架洒下来，在地上形成斑驳的光影。
    我坐在小板凳上，手里拿着奶奶刚洗好的葡萄，凉凉的，紫得发亮。
    奶奶在旁边择菜，嘴里哼着我不懂的小调。空气里有泥土的味道，还有葡萄的清香。
    那时候时间好像过得很慢，一个下午就像一辈子那么长。
    """
    
    # 初始化系统
    system = L0QualitySystem()
    
    # 评估
    result = system.assess(
        text=test_narrative,
        speaker_id="test_001",
        life_stage="Childhood"
    )
    
    # 输出结果
    print("=" * 60)
    print("L0 叙事质量评估结果")
    print("=" * 60)
    print(f"讲述者：{result.speaker_id}")
    print(f"人生阶段：{result.life_stage}")
    print(f"综合分数：{result.overall_score:.1f}")
    print(f"等级：{result.grade}")
    print(f"耗时：{result.total_latency_ms:.1f}ms")
    print(f"触发仲裁：{'是' if result.arbitration_triggered else '否'}")
    if result.arbitration_triggered:
        print(f"仲裁原因：{result.arbitration_reason}")
    print()
    print("各维度分数:")
    for dim, score in result.dimension_scores.items():
        print(f"  {dim}: {score:.1f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
