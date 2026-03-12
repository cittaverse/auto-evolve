"""
Narrative Assessor - 叙事评估主入口

基于神经符号架构的叙事质量自动评估系统
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json

from .scoring import ScoreCalculator
from .events import EventDetector


@dataclass
class AssessmentResult:
    """评估结果数据结构"""
    internal_details_score: float  # 内部细节评分 (0-100)
    external_details_score: float  # 外部细节评分 (0-100)
    event_segmentation_score: float  # 事件分段评分 (0-100)
    coherence_score: float  # 连贯性评分 (0-100)
    overall_score: float  # 综合评分 (0-100)
    word_count: int  # 字数
    event_count: int  # 事件数量
    insights: List[str]  # 临床洞察建议
    evidence: Dict[str, List[str]]  # 评分依据


class NarrativeAssessor:
    """
    叙事评估器
    
    使用神经符号架构：
    1. 神经层 (LLM): 语义理解、事件提取、细节分类
    2. 符号层 (图论): 结构计分、连贯性分析
    
    Example:
        >>> assessor = NarrativeAssessor(model="qwen-plus", language="zh-CN")
        >>> result = assessor.assess_text("那是我年轻时候的事情了...")
        >>> print(f"Overall Score: {result.overall_score}")
    """
    
    def __init__(
        self,
        model: str = "qwen-plus",
        language: str = "zh-CN",
        api_key: Optional[str] = None
    ):
        """
        初始化评估器
        
        Args:
            model: LLM 模型名称 (qwen-plus / glm-4 / gpt-4)
            language: 语言代码 (zh-CN / en-US)
            api_key: API Key (可选，也可通过环境变量设置)
        """
        self.model = model
        self.language = language
        self.api_key = api_key
        
        # 初始化子模块
        self.event_detector = EventDetector(model=model, language=language)
        self.score_calculator = ScoreCalculator()
        
    def assess_text(self, text: str) -> AssessmentResult:
        """
        评估文本叙事质量
        
        Args:
            text: 叙事文本
            
        Returns:
            AssessmentResult: 评估结果
        """
        # 1. 事件边界检测 (神经层)
        events = self.event_detector.detect_events(text)
        
        # 2. 细节分类 (神经层)
        internal_details = self._extract_internal_details(text, events)
        external_details = self._extract_external_details(text, events)
        
        # 3. 图论计分 (符号层)
        scores = self.score_calculator.calculate(
            text=text,
            events=events,
            internal_details=internal_details,
            external_details=external_details
        )
        
        # 4. 生成洞察
        insights = self._generate_insights(scores, events)
        
        # 5. 收集证据
        evidence = self._collect_evidence(events, internal_details, external_details)
        
        return AssessmentResult(
            internal_details_score=scores["internal"],
            external_details_score=scores["external"],
            event_segmentation_score=scores["segmentation"],
            coherence_score=scores["coherence"],
            overall_score=scores["overall"],
            word_count=len(text),
            event_count=len(events),
            insights=insights,
            evidence=evidence
        )
    
    def _extract_internal_details(self, text: str, events: List[Dict]) -> List[str]:
        """提取内部细节 (感官记忆、情感体验)"""
        # TODO: 实现 LLM 调用
        # 提示词示例：
        # "请从以下文本中提取个人感官记忆和情感体验..."
        return []
    
    def _extract_external_details(self, text: str, events: List[Dict]) -> List[str]:
        """提取外部细节 (历史背景、社会环境)"""
        # TODO: 实现 LLM 调用
        return []
    
    def _generate_insights(self, scores: Dict, events: List[Dict]) -> List[str]:
        """生成临床洞察建议"""
        insights = []
        
        if scores["internal"] < 50:
            insights.append("建议鼓励更多感官细节描述（视觉、听觉、触觉等）")
        if scores["external"] < 40:
            insights.append("可引导讲述更多社会背景和历史环境信息")
        if scores["coherence"] < 60:
            insights.append("叙事连贯性有待提升，可使用时间线辅助回忆")
        if len(events) < 3:
            insights.append("事件数量较少，可深入挖掘特定时期经历")
            
        return insights
    
    def _collect_evidence(self, events: List[Dict], internal: List[str], external: List[str]) -> Dict:
        """收集评分依据"""
        return {
            "internal_details": internal[:5],  # 最多 5 条
            "external_details": external[:5],
            "events": [e.get("summary", "") for e in events[:5]]
        }
    
    def batch_assess(
        self,
        texts: List[str],
        output_file: Optional[str] = None
    ) -> List[AssessmentResult]:
        """
        批量评估
        
        Args:
            texts: 文本列表
            output_file: 输出文件路径 (可选)
            
        Returns:
            评估结果列表
        """
        results = [self.assess_text(text) for text in texts]
        
        if output_file:
            self._save_results(results, output_file)
            
        return results
    
    def _save_results(self, results: List[AssessmentResult], filepath: str):
        """保存结果到 JSON 文件"""
        data = [self._result_to_dict(r) for r in results]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _result_to_dict(self, result: AssessmentResult) -> Dict:
        """将 AssessmentResult 转换为字典"""
        return {
            "internal_details_score": result.internal_details_score,
            "external_details_score": result.external_details_score,
            "event_segmentation_score": result.event_segmentation_score,
            "coherence_score": result.coherence_score,
            "overall_score": result.overall_score,
            "word_count": result.word_count,
            "event_count": result.event_count,
            "insights": result.insights,
            "evidence": result.evidence
        }
