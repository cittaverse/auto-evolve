#!/usr/bin/env python3
"""
抗 Reward Hacking 模块 v0.6

检测并防御以下攻击向量:
1. 关键词堆砌 (Keyword Stuffing)
2. 情感词滥用 (Emotional Word Abuse)
3. 虚构细节 (Fabricated Details)
4. 模板化叙述 (Template Narratives)

基于设计稿：`designs/multi-agent-scorer-v0.6.md` §4
"""

import re
import statistics
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class RewardHackDetectionResult:
    """Reward Hacking 检测结果"""
    information_density: float  # 信息密度 (0-1)
    narrative_diversity: float  # 叙事多样性 (0-1)
    keyword_stuffing_detected: bool  # 是否检测到关键词堆砌
    stuffed_dimensions: List[str]  # 堆砌的维度
    overall_penalty: float  # 总体罚分 (0 到 -20)
    reasoning: str  # 检测理由


# 各维度关键词列表 (用于堆砌检测)
DIMENSION_KEYWORDS = {
    'C1_internal': ['记得', '清晰', '细节', '画面', '场景', '声音', '气味', '触感'],
    'C2_external': ['时间', '地点', '人物', '日期', '季节', '年份', '具体'],
    'C3_coherence': ['然后', '接着', '之后', '所以', '因为', '但是', '然而'],
    'C4_emotion': ['开心', '难过', '激动', '紧张', '温暖', '感动', '幸福', '悲伤'],
    'C5_density': ['信息', '内容', '丰富', '详细', '具体', '完整'],
    'C6_fluency': ['流畅', '自然', '通顺', '连贯', '清晰', '易懂'],
}


def calculate_information_density(text: str, external_details_count: int) -> float:
    """
    计算信息密度：单位字数的有效信息量
    
    参数:
        text: 叙事文本
        external_details_count: L0 检测到的外部细节数量 (时间/地点/人物等)
    
    返回:
        density: float (0-1)
    
    算法:
        - 期望：每 100 字包含 1-3 个外部细节
        - 密度过低 (<0.5 倍期望) → 信息稀疏
        - 密度过高 (>2.0 倍期望) → 可能堆砌
    """
    char_count = len(text)
    if char_count == 0:
        return 0.0
    
    # 计算实际密度：每 100 字的外部细节数
    actual_density = external_details_count / (char_count / 100.0)
    
    # 期望密度范围：1-3 个细节/100 字
    min_expected = 0.5
    max_expected = 3.0
    
    if actual_density < min_expected:
        # 密度过低，线性惩罚
        density = actual_density / min_expected
    elif actual_density > max_expected:
        # 密度过高，可能是堆砌，逐渐降低评分
        density = max(0.0, 1.0 - (actual_density - max_expected) / 3.0)
    else:
        # 正常范围
        density = 1.0
    
    return round(density, 3)


def calculate_narrative_diversity(text: str) -> float:
    """
    计算叙事多样性：句式/词汇/结构变化
    
    参数:
        text: 叙事文本
    
    返回:
        diversity: float (0-1)
    
    算法:
        1. 句式多样性：句子长度标准差
        2. 词汇多样性：独特词比例 (TTR)
        3. 综合：加权平均
    """
    # 按句号分割句子
    sentences = [s.strip() for s in text.split('。') if s.strip()]
    
    if len(sentences) < 2:
        return 0.5  # 样本太小，返回中性值
    
    # 1. 句式多样性：句子长度标准差 (归一化到 0-1)
    sentence_lengths = [len(s) for s in sentences]
    length_mean = statistics.mean(sentence_lengths)
    length_std = statistics.stdev(sentence_lengths) if len(sentence_lengths) > 1 else 0
    
    # 标准差/均值 = 变异系数，归一化
    cv = length_std / length_mean if length_mean > 0 else 0
    sentence_diversity = min(1.0, cv / 0.5)  # CV > 0.5 时达到上限
    
    # 2. 词汇多样性：TTR (Type-Token Ratio)
    # 中文分词简化：按字符分割 (粗略但无需额外依赖)
    words = list(text.replace(' ', '').replace('\n', ''))
    if len(words) == 0:
        return 0.0
    
    unique_words = set(words)
    ttr = len(unique_words) / len(words)
    
    # 综合多样性 (句式 40% + 词汇 60%)
    diversity = 0.4 * sentence_diversity + 0.6 * ttr
    
    return round(diversity, 3)


def detect_keyword_stuffing(text: str, dimension_keywords: Dict[str, List[str]] = None) -> Tuple[bool, List[str]]:
    """
    检测关键词堆砌
    
    参数:
        text: 叙事文本
        dimension_keywords: dict {dimension: [keywords]}，默认使用 DIMENSION_KEYWORDS
    
    返回:
        stuffing_detected: bool (是否检测到堆砌)
        stuffed_dimensions: list[str] (堆砌的维度列表)
    
    算法:
        - 期望：每 500 字某维度关键词出现 1 次
        - 实际出现 > 期望 3 倍 → 标记为堆砌
    """
    if dimension_keywords is None:
        dimension_keywords = DIMENSION_KEYWORDS
    
    stuffed_dimensions = []
    char_count = len(text)
    
    # 期望频率：每 500 字出现 1 次
    expected_count = char_count / 500.0
    
    for dim, keywords in dimension_keywords.items():
        # 计算该维度关键词实际出现次数
        keyword_count = sum(text.count(kw) for kw in keywords)
        
        # 如果实际出现 > 期望 3 倍，标记为堆砌
        if keyword_count > expected_count * 3:
            stuffed_dimensions.append(dim)
    
    return len(stuffed_dimensions) > 0, stuffed_dimensions


def detect_emotional_abuse(text: str, l0_emotion_score: float) -> Tuple[bool, str]:
    """
    检测情感词滥用：情感词是否与事件效价匹配
    
    参数:
        text: 叙事文本
        l0_emotion_score: L0 C4 情感效价评分
    
    返回:
        abuse_detected: bool
        reason: str (检测理由)
    
    简单规则:
        - 高情感词密度 + 低情感评分 → 可能滥用
        - 情感词数量 / 总字数 > 5% 且 L0 评分 < 50 → 滥用嫌疑
    """
    # 情感词列表 (简化版)
    emotion_words = [
        '开心', '难过', '激动', '紧张', '温暖', '感动', '幸福', '悲伤',
        '快乐', '痛苦', '兴奋', '害怕', '安心', '焦虑', '满足', '失望',
    ]
    
    # 计算情感词密度
    emotion_count = sum(text.count(ew) for ew in emotion_words)
    emotion_density = emotion_count / len(text) if len(text) > 0 else 0
    
    # 检测规则
    if emotion_density > 0.05 and l0_emotion_score < 50:
        return True, f"情感词密度过高 ({emotion_density:.1%}) 但情感评分偏低 ({l0_emotion_score})"
    
    return False, ""


def detect_template_narrative(text: str) -> Tuple[bool, str]:
    """
    检测模板化叙述：过度使用常见叙事模板
    
    参数:
        text: 叙事文本
    
    返回:
        template_detected: bool
        reason: str
    
    简单规则:
        - 开头/结尾模式化 (如"那是一个...的夏天", "至今记忆犹新")
        - 过渡词过度使用 (连续使用"然后...然后...然后")
    """
    # 常见模板开头
    template_openings = [
        '那是一个', '记得那是', '在我', '小时候', '至今记忆犹新', '印象深刻',
    ]
    
    # 检查开头是否模板化
    is_template_opening = any(text.startswith(tpl) for tpl in template_openings)
    
    # 检查"然后"连续使用
    ranhou_count = text.count('然后')
    if ranhou_count >= 5:
        return True, f"过渡词'然后'过度使用 ({ranhou_count}次)"
    
    if is_template_opening:
        return True, "叙事开头模式化"
    
    return False, ""


def calculate_overall_penalty(
    information_density: float,
    narrative_diversity: float,
    keyword_stuffing: bool,
    emotional_abuse: bool,
    template_narrative: bool
) -> Tuple[float, str]:
    """
    计算总体罚分
    
    参数:
        information_density: 信息密度 (0-1)
        narrative_diversity: 叙事多样性 (0-1)
        keyword_stuffing: 是否关键词堆砌
        emotional_abuse: 是否情感词滥用
        template_narrative: 是否模板化叙述
    
    返回:
        penalty: float (0 到 -20，负数表示罚分)
        reasoning: str
    """
    penalty = 0.0
    reasons = []
    
    # 信息密度过低罚分
    if information_density < 0.5:
        penalty += (0.5 - information_density) * 10  # 最多 -5 分
        reasons.append(f"信息密度过低 ({information_density:.2f})")
    
    # 叙事多样性过低罚分
    if narrative_diversity < 0.4:
        penalty += (0.4 - narrative_diversity) * 8  # 最多 -3.2 分
        reasons.append(f"叙事多样性不足 ({narrative_diversity:.2f})")
    
    # 关键词堆砌罚分
    if keyword_stuffing:
        penalty += 5.0
        reasons.append("检测到关键词堆砌")
    
    # 情感词滥用罚分
    if emotional_abuse:
        penalty += 4.0
        reasons.append("检测到情感词滥用")
    
    # 模板化叙述罚分
    if template_narrative:
        penalty += 3.0
        reasons.append("检测到模板化叙述")
    
    # 限制最大罚分 -20
    penalty = max(-20.0, -penalty)
    
    reasoning = "; ".join(reasons) if reasons else "未检测到 Reward Hacking 行为"
    
    return round(penalty, 2), reasoning


def detect_reward_hacking(
    text: str,
    external_details_count: int,
    l0_emotion_score: float
) -> RewardHackDetectionResult:
    """
    完整的 Reward Hacking 检测流程
    
    参数:
        text: 叙事文本
        external_details_count: L0 检测到的外部细节数量
        l0_emotion_score: L0 C4 情感效价评分
    
    返回:
        RewardHackDetectionResult: 检测结果
    """
    # 1. 信息密度检测
    information_density = calculate_information_density(text, external_details_count)
    
    # 2. 叙事多样性检测
    narrative_diversity = calculate_narrative_diversity(text)
    
    # 3. 关键词堆砌检测
    keyword_stuffing, stuffed_dims = detect_keyword_stuffing(text)
    
    # 4. 情感词滥用检测
    emotional_abuse, emotion_reason = detect_emotional_abuse(text, l0_emotion_score)
    
    # 5. 模板化叙述检测
    template_narrative, template_reason = detect_template_narrative(text)
    
    # 6. 计算总体罚分
    overall_penalty, reasoning = calculate_overall_penalty(
        information_density,
        narrative_diversity,
        keyword_stuffing,
        emotional_abuse,
        template_narrative
    )
    
    return RewardHackDetectionResult(
        information_density=information_density,
        narrative_diversity=narrative_diversity,
        keyword_stuffing_detected=keyword_stuffing,
        stuffed_dimensions=stuffed_dims,
        overall_penalty=overall_penalty,
        reasoning=reasoning
    )


# 测试示例
if __name__ == '__main__':
    # 正常叙事
    normal_text = """
    那是我 10 岁的夏天，在杭州西湖边。阳光透过柳树叶洒在湖面上，波光粼粼的。
    我和爷爷坐在长椅上，他给我讲他年轻时的故事。微风拂过，带来荷花的清香。
    爷爷的声音很温和，我记得他手上的皱纹和老茧。那时候时间好像过得很慢，
    一个下午就像一辈子那么长。
    """
    
    # 堆砌叙事 (关键词过多)
    stuffed_text = """
    记得那是一个清晰的具体细节丰富的场景，我记得清晰的细节，清晰的画面，
    清晰的场景，清晰的声音，清晰的气味，清晰的触感。时间地点人物都非常具体，
    具体到每一个细节，具体的日期，具体的季节，具体的年份。
    """
    
    print("=" * 60)
    print("正常叙事检测")
    print("=" * 60)
    result_normal = detect_reward_hacking(normal_text, external_details_count=5, l0_emotion_score=70)
    print(f"信息密度：{result_normal.information_density}")
    print(f"叙事多样性：{result_normal.narrative_diversity}")
    print(f"关键词堆砌：{result_normal.keyword_stuffing_detected}")
    print(f"堆砌维度：{result_normal.stuffed_dimensions}")
    print(f"总体罚分：{result_normal.overall_penalty}")
    print(f"检测理由：{result_normal.reasoning}")
    
    print()
    print("=" * 60)
    print("堆砌叙事检测")
    print("=" * 60)
    result_stuffed = detect_reward_hacking(stuffed_text, external_details_count=2, l0_emotion_score=40)
    print(f"信息密度：{result_stuffed.information_density}")
    print(f"叙事多样性：{result_stuffed.narrative_diversity}")
    print(f"关键词堆砌：{result_stuffed.keyword_stuffing_detected}")
    print(f"堆砌维度：{result_stuffed.stuffed_dimensions}")
    print(f"总体罚分：{result_stuffed.overall_penalty}")
    print(f"检测理由：{result_stuffed.reasoning}")
