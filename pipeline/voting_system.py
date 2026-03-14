#!/usr/bin/env python3
"""
L0 标注质检多 Agent 系统 — 置信度加权投票系统

投票策略：
1. 置信度加权平均（默认）
2. 中位数投票（抗异常值）
3. 一致性检测（Cohen's Kappa）

用于计算多评委评分的最终结果，并检测分歧。
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats


@dataclass
class VoteInput:
    """投票输入"""
    dimension: str
    scores: List[float]  # 各评委的分数
    confidences: List[float]  # 各评委的置信度
    reasonings: List[str]  # 各评委的理由


@dataclass
class VoteResult:
    """投票结果"""
    final_score: float
    method: str  # 使用的投票方法
    confidence: float
    agreement_level: str  # 一致性水平
    statistics: Dict  # 详细统计信息


class VotingSystem:
    """投票系统"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {
            'min_agreement_threshold': 0.6,  # 最低一致性阈值
            'outlier_std_threshold': 2.0,  # 异常值标准差阈值
        }
    
    def weighted_average(self, scores: List[float], confidences: List[float]) -> Tuple[float, float]:
        """置信度加权平均"""
        if len(scores) != len(confidences):
            raise ValueError("Scores and confidences must have same length")
        
        total_weight = sum(confidences)
        if total_weight == 0:
            return np.mean(scores), 0.0
        
        weighted_sum = sum(s * c for s, c in zip(scores, confidences))
        weighted_avg = weighted_sum / total_weight
        
        # 计算加权置信度
        avg_confidence = total_weight / len(confidences)
        
        return weighted_avg, avg_confidence
    
    def median_vote(self, scores: List[float]) -> float:
        """中位数投票（抗异常值）"""
        return np.median(scores)
    
    def detect_outliers(self, scores: List[float], threshold: float = 2.0) -> List[int]:
        """检测异常值（基于标准差）"""
        if len(scores) < 3:
            return []
        
        mean = np.mean(scores)
        std = np.std(scores)
        
        if std == 0:
            return []
        
        outliers = []
        for i, score in enumerate(scores):
            z_score = abs((score - mean) / std)
            if z_score > threshold:
                outliers.append(i)
        
        return outliers
    
    def calculate_agreement(self, scores: List[float]) -> Tuple[float, str]:
        """
        计算评分一致性
        
        返回：
        - 变异系数 (CV): 标准差/均值，越小一致性越高
        - 一致性等级描述
        """
        if len(scores) < 2:
            return 1.0, "N/A"
        
        mean = np.mean(scores)
        std = np.std(scores)
        
        # 变异系数 (Coefficient of Variation)
        cv = std / mean if mean > 0 else float('inf')
        
        # 转换为一致性分数 (0-1)
        # CV=0 → 1.0 (完全一致), CV=0.3 → 0.5 (中等), CV>0.5 → <0.3 (低)
        agreement = max(0, 1 - cv * 3)
        
        # 等级描述
        if agreement >= 0.8:
            level = "极强一致"
        elif agreement >= 0.6:
            level = "强一致"
        elif agreement >= 0.4:
            level = "中等一致"
        elif agreement >= 0.2:
            level = "弱一致"
        else:
            level = "严重分歧"
        
        return agreement, level
    
    def cohen_kappa(self, labels_1: List[int], labels_2: List[int]) -> float:
        """
        计算 Cohen's Kappa（分类一致性）
        
        用于对比系统评分与人工标注的一致性
        """
        if len(labels_1) != len(labels_2):
            raise ValueError("Labels must have same length")
        
        kappa, _ = stats.cohen_kappa_score(labels_1, labels_2)
        return kappa
    
    def pearson_correlation(self, scores_1: List[float], scores_2: List[float]) -> float:
        """
        计算 Pearson 相关系数（连续评分一致性）
        
        用于对比系统评分与人工标注的相关性
        """
        if len(scores_1) != len(scores_2):
            raise ValueError("Scores must have same length")
        
        corr, _ = stats.pearsonr(scores_1, scores_2)
        return corr
    
    def vote(self, input_data: VoteInput, method: str = 'weighted') -> VoteResult:
        """
        执行投票
        
        Args:
            input_data: 投票输入
            method: 'weighted' (置信度加权) | 'median' (中位数) | 'trimmed' (截尾平均)
        """
        scores = input_data.scores
        confidences = input_data.confidences
        
        # 检测异常值
        outliers = self.detect_outliers(scores)
        
        # 计算一致性
        agreement, level = self.calculate_agreement(scores)
        
        # 执行投票
        if method == 'weighted':
            final_score, avg_confidence = self.weighted_average(scores, confidences)
        elif method == 'median':
            final_score = self.median_vote(scores)
            avg_confidence = np.mean(confidences)
        elif method == 'trimmed':
            # 去掉最高和最低分后平均
            if len(scores) > 2:
                sorted_scores = sorted(scores)
                trimmed = sorted_scores[1:-1]
                final_score = np.mean(trimmed)
            else:
                final_score = np.mean(scores)
            avg_confidence = np.mean(confidences)
        else:
            raise ValueError(f"Unknown voting method: {method}")
        
        # 统计信息
        statistics = {
            'mean': np.mean(scores),
            'std': np.std(scores),
            'min': min(scores),
            'max': max(scores),
            'range': max(scores) - min(scores),
            'outliers': outliers,
            'agreement_score': agreement,
            'cv': np.std(scores) / np.mean(scores) if np.mean(scores) > 0 else float('inf')
        }
        
        return VoteResult(
            final_score=final_score,
            method=method,
            confidence=avg_confidence,
            agreement_level=level,
            statistics=statistics
        )


class ConsensusEvaluator:
    """一致性评估器 — 用于系统验收"""
    
    def __init__(self):
        self.voting_system = VotingSystem()
    
    def evaluate_consistency(self, system_scores: List[float], human_scores: List[float]) -> Dict:
        """
        评估系统与人工标注的一致性
        
        Returns:
            包含 Kappa、相关性、准确率等指标的字典
        """
        # 1. Pearson 相关性（连续评分）
        pearson_corr, pearson_p = stats.pearsonr(system_scores, human_scores)
        
        # 2. Spearman 秩相关（排名一致性）
        spearman_corr, spearman_p = stats.spearmanr(system_scores, human_scores)
        
        # 3. 将连续分数转换为等级（用于 Kappa 计算）
        def score_to_grade(score):
            if score >= 85:
                return 4  # S
            elif score >= 70:
                return 3  # A
            elif score >= 55:
                return 2  # B
            elif score >= 40:
                return 1  # C
            else:
                return 0  # D
        
        system_grades = [score_to_grade(s) for s in system_scores]
        human_grades = [score_to_grade(h) for h in human_scores]
        
        # 4. Cohen's Kappa（分类一致性）
        kappa = self.voting_system.cohen_kappa(system_grades, human_grades)
        
        # 5. 准确率（等级完全匹配）
        exact_match = sum(1 for s, h in zip(system_grades, human_grades) if s == h) / len(system_grades)
        
        # 6. ±1 等级准确率（允许 1 级误差）
        within_one = sum(1 for s, h in zip(system_grades, human_grades) if abs(s - h) <= 1) / len(system_grades)
        
        # 7. 平均绝对误差
        mae = np.mean([abs(s - h) for s, h in zip(system_scores, human_scores)])
        
        # 8. 均方根误差
        rmse = np.sqrt(np.mean([(s - h) ** 2 for s, h in zip(system_scores, human_scores)]))
        
        return {
            'pearson_correlation': pearson_corr,
            'pearson_p_value': pearson_p,
            'spearman_correlation': spearman_corr,
            'spearman_p_value': spearman_p,
            'cohens_kappa': kappa,
            'exact_match_accuracy': exact_match,
            'within_one_accuracy': within_one,
            'mean_absolute_error': mae,
            'root_mean_square_error': rmse,
            'sample_size': len(system_scores),
            'interpretation': self._interpret_metrics(pearson_corr, kappa, exact_match)
        }
    
    def _interpret_metrics(self, pearson: float, kappa: float, accuracy: float) -> str:
        """解读指标"""
        interpretations = []
        
        # Pearson 解读
        if pearson >= 0.88:
            interpretations.append("相关性极强 (r≥0.88)")
        elif pearson >= 0.70:
            interpretations.append("相关性强 (r≥0.70)")
        elif pearson >= 0.50:
            interpretations.append("相关性中等 (r≥0.50)")
        else:
            interpretations.append("相关性弱 (r<0.50)")
        
        # Kappa 解读
        if kappa >= 0.85:
            interpretations.append("一致性极强 (κ≥0.85)")
        elif kappa >= 0.65:
            interpretations.append("一致性强 (κ≥0.65)")
        elif kappa >= 0.40:
            interpretations.append("一致性中等 (κ≥0.40)")
        else:
            interpretations.append("一致性弱 (κ<0.40)")
        
        # 准确率解读
        if accuracy >= 0.85:
            interpretations.append("准确率高 (≥85%)")
        elif accuracy >= 0.70:
            interpretations.append("准确率中等 (≥70%)")
        else:
            interpretations.append("准确率低 (<70%)")
        
        return " | ".join(interpretations)


if __name__ == '__main__':
    # 测试示例
    voting_system = VotingSystem()
    
    test_input = VoteInput(
        dimension='Sensory',
        scores=[85, 88, 82, 90],
        confidences=[0.9, 0.85, 0.8, 0.95],
        reasonings=['细节丰富', '场景感强', '部分细节', '身临其境']
    )
    
    result = voting_system.vote(test_input, method='weighted')
    
    print(f"最终分数：{result.final_score:.2f}")
    print(f"投票方法：{result.method}")
    print(f"置信度：{result.confidence:.2f}")
    print(f"一致性：{result.agreement_level}")
    print(f"统计信息：{result.statistics}")
    
    # 测试一致性评估器
    print("\n--- 一致性评估测试 ---")
    evaluator = ConsensusEvaluator()
    
    # 模拟 50 条样本
    np.random.seed(42)
    human_scores = np.random.normal(75, 10, 50).clip(0, 100)
    system_scores = human_scores + np.random.normal(0, 5, 50)  # 系统评分有少量误差
    
    consistency_result = evaluator.evaluate_consistency(system_scores.tolist(), human_scores.tolist())
    
    import json
    print(json.dumps(consistency_result, indent=2))
