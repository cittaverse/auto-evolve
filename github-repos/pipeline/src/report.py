"""
Report Generator - 报告生成模块

生成 JSON/PDF 格式的评估报告
"""

from typing import List, Dict, Optional
from dataclasses import asdict
import json

from .assessor import AssessmentResult


class ReportGenerator:
    """
    报告生成器
    
    支持格式：
    - JSON: 结构化数据
    - PDF: 可视化报告 (TODO)
    """
    
    def __init__(self, language: str = "zh-CN"):
        self.language = language
    
    def generate_json(
        self,
        result: AssessmentResult,
        output_file: Optional[str] = None
    ) -> str:
        """
        生成 JSON 格式报告
        
        Args:
            result: 评估结果
            output_file: 输出文件路径 (可选)
            
        Returns:
            JSON 字符串
        """
        data = {
            "version": "1.0",
            "language": self.language,
            "assessment": asdict(result),
            "interpretation": self._generate_interpretation(result)
        }
        
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(json_str)
        
        return json_str
    
    def generate_group_report(
        self,
        results: List[AssessmentResult],
        output_file: Optional[str] = None
    ) -> Dict:
        """
        生成群体分析报告
        
        Args:
            results: 多个评估结果
            output_file: 输出文件路径 (可选)
            
        Returns:
            群体分析数据
        """
        if not results:
            return {"error": "No results provided"}
        
        # 计算统计指标
        scores = [r.overall_score for r in results]
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)
        
        # 计算各维度平均分
        avg_internal = sum(r.internal_details_score for r in results) / len(results)
        avg_external = sum(r.external_details_score for r in results) / len(results)
        avg_coherence = sum(r.coherence_score for r in results) / len(results)
        
        # 收集常见洞察
        all_insights = []
        for r in results:
            all_insights.extend(r.insights)
        
        insight_counts = {}
        for insight in all_insights:
            insight_counts[insight] = insight_counts.get(insight, 0) + 1
        
        # 排序
        top_insights = sorted(insight_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        report = {
            "version": "1.0",
            "language": self.language,
            "summary": {
                "total_assessments": len(results),
                "average_score": round(avg_score, 2),
                "min_score": round(min_score, 2),
                "max_score": round(max_score, 2)
            },
            "dimension_averages": {
                "internal_details": round(avg_internal, 2),
                "external_details": round(avg_external, 2),
                "coherence": round(avg_coherence, 2)
            },
            "top_insights": [
                {"insight": insight, "count": count}
                for insight, count in top_insights
            ]
        }
        
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        
        return report
    
    def _generate_interpretation(self, result: AssessmentResult) -> Dict:
        """生成评分解读"""
        def interpret_score(score: float) -> str:
            if score >= 80:
                return "优秀"
            elif score >= 60:
                return "良好"
            elif score >= 40:
                return "中等"
            else:
                return "需提升"
        
        return {
            "internal_details": {
                "score": result.internal_details_score,
                "level": interpret_score(result.internal_details_score),
                "description": "个人感官记忆和情感体验的丰富程度"
            },
            "external_details": {
                "score": result.external_details_score,
                "level": interpret_score(result.external_details_score),
                "description": "历史背景和社会环境的描述程度"
            },
            "coherence": {
                "score": result.coherence_score,
                "level": interpret_score(result.coherence_score),
                "description": "叙事整体逻辑流畅度"
            },
            "overall": {
                "score": result.overall_score,
                "level": interpret_score(result.overall_score),
                "description": "综合叙事质量评分"
            }
        }
