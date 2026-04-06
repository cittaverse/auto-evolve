#!/usr/bin/env python3
"""
REMem Event Segmentation Module

Implements event boundary detection for narrative segmentation based on REMem (ICLR 2026).

Features:
- LLM-based event boundary detection
- Temporal anchor extraction
- Emotional valence scoring per segment
- Output: List of event objects with metadata

Status: Phase 1 Implementation (Can run without LLM API using rule-based fallback)

References:
- REMem: Reasoning with Episodic Memory in Language Agent (ICLR 2026)
- Towards LLMs with Human-like Episodic Memory (Cell Press TiCS, 2025)
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class EventSegment:
    """Represents a segmented event from narrative."""
    
    event_id: str
    text: str
    start_pos: int
    end_pos: int
    
    # Temporal anchors
    temporal_anchor: Optional[str] = None  # e.g., "2010 年", "退休后", "大学期间"
    time_expression: Optional[str] = None  # Raw time expression found
    
    # Emotional valence (0-100)
    emotional_valence: Optional[float] = None
    valence_label: Optional[str] = None  # "positive", "neutral", "negative"
    
    # Event metadata
    people_mentioned: List[str] = None
    places_mentioned: List[str] = None
    themes: List[str] = None
    
    # Boundary confidence (0-1)
    boundary_confidence: float = 0.0
    
    def __post_init__(self):
        if self.people_mentioned is None:
            self.people_mentioned = []
        if self.places_mentioned is None:
            self.places_mentioned = []
        if self.themes is None:
            self.themes = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EventSegmenter:
    """
    Segment narrative into episodic events using REMem-inspired approach.
    
    Two modes:
    1. LLM mode (requires DASHSCOPE_API_KEY): High accuracy, context-aware
    2. Rule-based mode (no API needed): Heuristic boundaries based on linguistic cues
    """
    
    def __init__(self, use_llm: bool = False, api_key: Optional[str] = None):
        self.use_llm = use_llm
        self.api_key = api_key
        self.llm_available = False
        
        # Check if LLM can be used
        if self.use_llm and self.api_key:
            self.llm_available = self._check_llm_availability()
        
        # Temporal expression patterns (Chinese)
        self.temporal_patterns = [
            r'(\d{4}年)',  # 2010 年
            r'(\d{4}年\d{1,2}月)',  # 2010 年 5 月
            r'(\d{4}年\d{1,2}月\d{1,2}日)',  # 2010 年 5 月 20 日
            r'(去年 | 今年 | 明年)',
            r'(上个月 | 这个月 | 下个月)',
            r'(昨天 | 今天 | 明天)',
            r'(小时候 | 年轻时 | 退休后)',
            r'(大学期间 | 工作后 | 结婚前)',
            r'(那段时间 | 那时候 | 当时)',
            r'(在.*期间)',  # 在北京期间
            r'(从.*到.*)',  # 从 2010 年到 2015 年
        ]
        
        # Event boundary cues (linguistic markers)
        self.boundary_cues = [
            '后来', '然后', '接着', '随后', '之后', '以后',
            '之前', '以前', '起初', '最后', '最终',
            '突然', '忽然', '没想到', '意外的是',
            '记得', '回想起', '回忆起', '印象最深的是',
            '有一天', '有一次', '那天', '那时候',
            '\n', '\n\n',  # Paragraph breaks
        ]
        
        # Emotional valence keywords
        self.positive_keywords = [
            '开心', '快乐', '高兴', '幸福', '满足', '自豪', '骄傲',
            '温暖', '感动', '感激', '美好', '愉快', '兴奋',
            '爱', '喜欢', '享受', '值得', '难忘', '珍贵'
        ]
        
        self.negative_keywords = [
            '难过', '伤心', '痛苦', '悲伤', '沮丧', '失望',
            '愤怒', '生气', '害怕', '恐惧', '焦虑', '担心',
            '遗憾', '后悔', '愧疚', '孤独', '无助', '绝望'
        ]
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM API is accessible."""
        try:
            # Try to import and make a minimal test call
            from dashscope import Generation
            # Don't actually call API here (to avoid charges/errors)
            # Just check if the library is available
            return True
        except ImportError:
            logger.warning("dashscope library not available, using rule-based mode")
            return False
    
    def segment(self, narrative: str) -> List[EventSegment]:
        """
        Segment narrative into episodic events.
        
        Args:
            narrative: The full narrative text
        
        Returns:
            List of EventSegment objects
        """
        if self.llm_available and self.use_llm:
            return self._segment_with_llm(narrative)
        else:
            return self._segment_rule_based(narrative)
    
    def _segment_with_llm(self, narrative: str) -> List[EventSegment]:
        """
        Segment narrative using LLM (high accuracy).
        
        This method uses Qwen model to detect event boundaries,
        extract temporal anchors, and score emotional valence.
        """
        # TODO: Implement LLM-based segmentation
        # For now, fall back to rule-based
        logger.info("LLM mode requested but not yet implemented, falling back to rule-based")
        return self._segment_rule_based(narrative)
    
    def _segment_rule_based(self, narrative: str) -> List[EventSegment]:
        """
        Segment narrative using rule-based heuristics.
        
        Strategy:
        1. Find all boundary cues
        2. Score boundary strength at each position
        3. Split at high-confidence boundaries
        4. Extract metadata for each segment
        """
        segments = []
        
        # Find all boundary cue positions
        boundary_positions = []
        for cue in self.boundary_cues:
            for match in re.finditer(re.escape(cue), narrative):
                boundary_positions.append({
                    'pos': match.start(),
                    'cue': cue,
                    'strength': self._cue_strength(cue)
                })
        
        # Sort by position
        boundary_positions.sort(key=lambda x: x['pos'])
        
        # Remove duplicates (same position)
        seen_positions = set()
        unique_boundaries = []
        for bp in boundary_positions:
            if bp['pos'] not in seen_positions:
                seen_positions.add(bp['pos'])
                unique_boundaries.append(bp)
        
        # Filter high-confidence boundaries
        high_confidence_boundaries = [
            bp for bp in unique_boundaries
            if bp['strength'] >= 0.5
        ]
        
        # If no high-confidence boundaries, treat whole text as one event
        if not high_confidence_boundaries:
            segment = self._create_event_segment(
                text=narrative,
                start_pos=0,
                end_pos=len(narrative),
                boundary_confidence=0.3
            )
            return [segment]
        
        # Create segments between boundaries
        start = 0
        for i, boundary in enumerate(high_confidence_boundaries):
            end = boundary['pos']
            
            # Skip very short segments (< 20 chars)
            if end - start < 20:
                continue
            
            segment_text = narrative[start:end].strip()
            if len(segment_text) < 20:
                continue
            
            segment = self._create_event_segment(
                text=segment_text,
                start_pos=start,
                end_pos=end,
                boundary_confidence=boundary['strength']
            )
            segments.append(segment)
            
            start = end
        
        # Add final segment
        if start < len(narrative) - 20:
            segment_text = narrative[start:].strip()
            segment = self._create_event_segment(
                text=segment_text,
                start_pos=start,
                end_pos=len(narrative),
                boundary_confidence=0.5
            )
            segments.append(segment)
        
        return segments
    
    def _cue_strength(self, cue: str) -> float:
        """Assign strength to boundary cue (0-1)."""
        strong_cues = ['后来', '然后', '突然', '记得', '回想起', '\n\n']
        medium_cues = ['接着', '随后', '之后', '有一天', '有一次']
        weak_cues = ['之前', '以前', '那时候']
        
        if any(c in cue for c in strong_cues):
            return 0.8
        elif any(c in cue for c in medium_cues):
            return 0.6
        elif any(c in cue for c in weak_cues):
            return 0.4
        else:
            return 0.3
    
    def _create_event_segment(
        self,
        text: str,
        start_pos: int,
        end_pos: int,
        boundary_confidence: float
    ) -> EventSegment:
        """Create an EventSegment with extracted metadata."""
        
        # Extract temporal anchors
        temporal_anchor, time_expression = self._extract_temporal_anchor(text)
        
        # Score emotional valence
        emotional_valence, valence_label = self._score_emotional_valence(text)
        
        # Extract people and places (simple regex, can be enhanced with NER)
        people_mentioned = self._extract_people(text)
        places_mentioned = self._extract_places(text)
        
        # Extract themes (simple keyword matching)
        themes = self._extract_themes(text)
        
        return EventSegment(
            event_id=f"evt_{start_pos}_{end_pos}",
            text=text,
            start_pos=start_pos,
            end_pos=end_pos,
            temporal_anchor=temporal_anchor,
            time_expression=time_expression,
            emotional_valence=emotional_valence,
            valence_label=valence_label,
            people_mentioned=people_mentioned,
            places_mentioned=places_mentioned,
            themes=themes,
            boundary_confidence=boundary_confidence
        )
    
    def _extract_temporal_anchor(self, text: str) -> tuple:
        """Extract temporal anchor from text."""
        # Flatten text for easier matching
        flat_text = text.replace('\n', ' ').replace('  ', ' ')
        
        for pattern in self.temporal_patterns:
            match = re.search(pattern, flat_text)
            if match:
                time_expr = match.group(0)
                # Normalize to anchor
                if re.match(r'\d{4}年', time_expr):
                    return time_expr, time_expr
                elif '退休' in time_expr or '结婚' in time_expr or '大学' in time_expr:
                    return f"人生阶段：{time_expr}", time_expr
                else:
                    return f"相对时间：{time_expr}", time_expr
        return None, None
    
    def _score_emotional_valence(self, text: str) -> tuple:
        """Score emotional valence (0-100)."""
        positive_count = sum(1 for kw in self.positive_keywords if kw in text)
        negative_count = sum(1 for kw in self.negative_keywords if kw in text)
        
        total = positive_count + negative_count
        if total == 0:
            return 50.0, "neutral"
        
        # Score: 0 (very negative) to 100 (very positive)
        score = 50.0 + (positive_count - negative_count) / total * 50.0
        
        if score > 60:
            label = "positive"
        elif score < 40:
            label = "negative"
        else:
            label = "neutral"
        
        return score, label
    
    def _extract_people(self, text: str) -> List[str]:
        """Extract people mentioned (simple: family terms, names)."""
        people = []
        family_terms = ['爸爸', '妈妈', '父亲', '母亲', '爷爷', '奶奶',
                       '外公', '外婆', '哥哥', '姐姐', '弟弟', '妹妹',
                       '儿子', '女儿', '丈夫', '妻子', '老公', '老婆',
                       '朋友', '同事', '同学', '老师']
        
        for term in family_terms:
            if term in text:
                people.append(term)
        
        # TODO: Add NER for actual names
        return list(set(people))
    
    def _extract_places(self, text: str) -> List[str]:
        """Extract places mentioned (simple: location markers)."""
        places = []
        place_markers = ['在', '到', '从', '去', '回']
        
        # Simple pattern: 在 XXX
        for marker in place_markers:
            pattern = rf'{marker}([^，,。.！？]+)'
            matches = re.findall(pattern, text)
            places.extend(matches)
        
        return list(set(places))[:5]  # Limit to 5
    
    def _extract_themes(self, text: str) -> List[str]:
        """Extract themes (simple keyword matching)."""
        theme_keywords = {
            '家庭': ['家', '家人', '家庭', '孩子', '父母', '结婚', '生子'],
            '工作': ['工作', '上班', '公司', '单位', '职业', '事业'],
            '学习': ['学习', '读书', '学校', '考试', '大学', '知识'],
            '健康': ['健康', '身体', '生病', '医院', '医生', '运动'],
            '旅行': ['旅行', '旅游', '玩', '景点', '风景', '出国'],
            '友谊': ['朋友', '友情', '聚会', '聊天', '陪伴'],
            '成就': ['成就', '成功', '完成', '实现', '梦想', '目标'],
            '挑战': ['困难', '挑战', '挫折', '失败', '压力'],
        }
        
        themes = []
        for theme, keywords in theme_keywords.items():
            if any(kw in text for kw in keywords):
                themes.append(theme)
        
        return themes


def segment_narrative(narrative: str, use_llm: bool = False) -> List[Dict[str, Any]]:
    """
    Convenience function to segment a narrative.
    
    Args:
        narrative: The narrative text
        use_llm: Whether to use LLM (default: False, rule-based)
    
    Returns:
        List of event segment dictionaries
    """
    segmenter = EventSegmenter(use_llm=use_llm)
    segments = segmenter.segment(narrative)
    return [seg.to_dict() for seg in segments]


if __name__ == "__main__":
    # Test with sample narrative
    sample_narrative = """
    记得那是 2010 年的夏天，我和家人一起去了北京旅行。那时候儿子刚上小学，
    他对一切都充满好奇。我们去了故宫、长城，他特别兴奋。
    
    后来，2015 年我退休后，生活节奏慢了下来。每天早晨去公园打太极，
    下午和朋友们下棋聊天。虽然没有了工作的压力，但有时候也会感到有些孤独。
    
    最难忘的是去年孙子出生，那一刻我感到无比幸福。现在每周都会去儿子家看孙子，
    看着他一天天长大，是我最大的快乐。
    """
    
    print("Testing REMem Event Segmentation (Rule-based Mode)")
    print("=" * 60)
    
    segments = segment_narrative(sample_narrative, use_llm=False)
    
    for i, seg in enumerate(segments, 1):
        print(f"\n【Event {i}】")
        print(f"文本：{seg['text'][:100]}...")
        print(f"时间锚点：{seg['temporal_anchor']}")
        print(f"情感效价：{seg['emotional_valence']:.1f} ({seg['valence_label']})")
        print(f"提到的人：{seg['people_mentioned']}")
        print(f"提到的地点：{seg['places_mentioned']}")
        print(f"主题：{seg['themes']}")
        print(f"边界置信度：{seg['boundary_confidence']:.2f}")
