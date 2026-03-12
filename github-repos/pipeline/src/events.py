"""
Event Detection Module - 事件检测模块

识别叙事中的事件边界和结构
"""

from typing import Dict, List, Optional
import re


class EventDetector:
    """
    事件检测器
    
    使用混合方法：
    1. 规则-based: 时间标记、连接词
    2. LLM-based: 语义边界检测
    """
    
    def __init__(self, model: str = "qwen-plus", language: str = "zh-CN"):
        self.model = model
        self.language = language
        
        # 中文时间标记词
        self.temporal_markers = [
            "那时候", "当时", "后来", "然后", "接着",
            "有一天", "记得", "想起", "那年",
            "以前", "后来", "之后", "之前"
        ]
        
        # 中文连接词
        self.connectives = [
            "因为", "所以", "但是", "可是", "不过",
            "而且", "并且", "于是", "因此"
        ]
    
    def detect_events(self, text: str) -> List[Dict]:
        """
        检测文本中的事件
        
        Args:
            text: 叙事文本
            
        Returns:
            事件列表，每个事件包含：
            - summary: 事件摘要
            - start: 起始位置
            - end: 结束位置
            - temporal_marker: 时间标记 (如有)
        """
        # 1. 基于规则的初步分割
        segments = self._rule_based_segmentation(text)
        
        # 2. 基于 LLM 的语义优化 (TODO)
        # events = self._llm_refine_segments(segments, text)
        events = segments  # 临时使用规则结果
        
        # 3. 提取事件摘要
        for event in events:
            event["summary"] = self._extract_summary(text, event)
        
        return events
    
    def _rule_based_segmentation(self, text: str) -> List[Dict]:
        """
        基于规则的文本分割
        
        使用时间标记词和连接词作为分割点
        """
        segments = []
        
        # 查找所有时间标记词位置
        markers = []
        for marker in self.temporal_markers:
            for match in re.finditer(marker, text):
                markers.append((match.start(), match.group(), "temporal"))
        
        # 查找所有连接词位置
        for conn in self.connectives:
            for match in re.finditer(conn, text):
                markers.append((match.start(), match.group(), "connective"))
        
        # 按位置排序
        markers.sort(key=lambda x: x[0])
        
        # 去重 (保留最早出现的标记)
        seen_positions = set()
        unique_markers = []
        for pos, marker, mtype in markers:
            if pos not in seen_positions:
                seen_positions.add(pos)
                unique_markers.append((pos, marker, mtype))
        
        # 分割文本
        if not unique_markers:
            # 无标记词，整段作为一个事件
            segments.append({
                "start": 0,
                "end": len(text),
                "temporal_marker": None
            })
        else:
            # 第一段 (标记词之前)
            if unique_markers[0][0] > 0:
                segments.append({
                    "start": 0,
                    "end": unique_markers[0][0],
                    "temporal_marker": None
                })
            
            # 标记词之间的段落
            for i in range(len(unique_markers) - 1):
                pos1, marker1, _ = unique_markers[i]
                pos2, _, _ = unique_markers[i + 1]
                
                if pos2 - pos1 > 20:  # 最小段落长度
                    segments.append({
                        "start": pos1,
                        "end": pos2,
                        "temporal_marker": marker1
                    })
            
            # 最后一段
            last_pos, last_marker, _ = unique_markers[-1]
            segments.append({
                "start": last_pos,
                "end": len(text),
                "temporal_marker": last_marker
            })
        
        return segments
    
    def _extract_summary(self, text: str, event: Dict) -> str:
        """提取事件摘要"""
        segment = text[event["start"]:event["end"]]
        
        # 截取前 50 字作为摘要
        if len(segment) > 50:
            return segment[:50] + "..."
        return segment.strip()
