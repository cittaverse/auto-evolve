"""
Scoring Module - 评分模块

基于图论的叙事结构计分
"""

from typing import Dict, List
import networkx as nx


class ScoreCalculator:
    """
    叙事质量计分器
    
    使用图论算法计算：
    1. 内部细节评分
    2. 外部细节评分
    3. 事件分段评分
    4. 连贯性评分
    """
    
    def __init__(self):
        # 权重配置
        self.weights = {
            "internal": 0.35,
            "external": 0.25,
            "segmentation": 0.20,
            "coherence": 0.20
        }
    
    def calculate(
        self,
        text: str,
        events: List[Dict],
        internal_details: List[str],
        external_details: List[str]
    ) -> Dict[str, float]:
        """
        计算各项评分
        
        Returns:
            包含各维度评分的字典
        """
        # 1. 内部细节评分 (基于细节数量和多样性)
        internal_score = self._score_internal_details(internal_details, text)
        
        # 2. 外部细节评分 (基于背景信息丰富度)
        external_score = self._score_external_details(external_details, text)
        
        # 3. 事件分段评分 (基于事件边界清晰度)
        segmentation_score = self._score_event_segmentation(events)
        
        # 4. 连贯性评分 (基于事件图结构)
        coherence_score = self._score_coherence(events)
        
        # 5. 综合评分 (加权平均)
        overall_score = (
            internal_score * self.weights["internal"] +
            external_score * self.weights["external"] +
            segmentation_score * self.weights["segmentation"] +
            coherence_score * self.weights["coherence"]
        )
        
        return {
            "internal": round(internal_score, 2),
            "external": round(external_score, 2),
            "segmentation": round(segmentation_score, 2),
            "coherence": round(coherence_score, 2),
            "overall": round(overall_score, 2)
        }
    
    def _score_internal_details(self, details: List[str], text: str) -> float:
        """
        内部细节评分
        
        评分标准：
        - 细节数量 (40%)
        - 感官多样性 (30%)
        - 情感深度 (30%)
        """
        if not details:
            return 0.0
        
        # 基础分：细节数量
        count_score = min(len(details) / 10.0, 1.0) * 40
        
        # TODO: 实现感官多样性分析
        diversity_score = 20.0  # 占位
        
        # TODO: 实现情感深度分析
        emotion_score = 20.0  # 占位
        
        return min(count_score + diversity_score + emotion_score, 100.0)
    
    def _score_external_details(self, details: List[str], text: str) -> float:
        """
        外部细节评分
        
        评分标准：
        - 历史背景提及 (40%)
        - 社会环境描述 (30%)
        - 他人互动 (30%)
        """
        if not details:
            return 0.0
        
        # 基础分：细节数量
        count_score = min(len(details) / 8.0, 1.0) * 40
        
        # TODO: 实现历史背景识别
        history_score = 20.0  # 占位
        
        # TODO: 实现社会环境分析
        social_score = 20.0  # 占位
        
        return min(count_score + history_score + social_score, 100.0)
    
    def _score_event_segmentation(self, events: List[Dict]) -> float:
        """
        事件分段评分
        
        评分标准：
        - 事件数量 (30%)
        - 边界清晰度 (40%)
        - 时间线完整性 (30%)
        """
        if not events:
            return 0.0
        
        # 事件数量分
        count_score = min(len(events) / 5.0, 1.0) * 30
        
        # TODO: 边界清晰度分析
        boundary_score = 30.0  # 占位
        
        # TODO: 时间线完整性分析
        timeline_score = 30.0  # 占位
        
        return min(count_score + boundary_score + timeline_score, 100.0)
    
    def _score_coherence(self, events: List[Dict]) -> float:
        """
        连贯性评分
        
        使用图论算法：
        1. 构建事件图 (节点=事件，边=因果关系/时间顺序)
        2. 计算图的连通性
        3. 计算最长路径 (叙事主线)
        """
        if len(events) < 2:
            return 50.0  # 单个事件无法评估连贯性
        
        # 构建事件图
        graph = self._build_event_graph(events)
        
        # 计算连通性
        connectivity = nx.number_connected_components(graph)
        connectivity_score = max(0, 40 - (connectivity - 1) * 10)
        
        # 计算最长路径 (叙事主线)
        try:
            longest_path = nx.dag_longest_path(graph)
            path_score = min(len(longest_path) / len(events), 1.0) * 60
        except nx.NetworkXError:
            path_score = 30.0  # 非 DAG 图
        
        return connectivity_score + path_score
    
    def _build_event_graph(self, events: List[Dict]) -> nx.DiGraph:
        """
        构建事件图
        
        节点：事件
        边：因果关系、时间顺序
        """
        graph = nx.DiGraph()
        
        # 添加节点
        for i, event in enumerate(events):
            graph.add_node(i, **event)
        
        # 添加边 (基于时间顺序和因果关系)
        for i in range(len(events) - 1):
            # 默认添加时间顺序边
            graph.add_edge(i, i + 1, type="temporal")
            
            # TODO: 基于 LLM 识别因果关系
            # if has_causal_relation(events[i], events[i+1]):
            #     graph.add_edge(i, i + 1, type="causal")
        
        return graph
