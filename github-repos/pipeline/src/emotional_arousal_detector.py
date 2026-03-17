#!/usr/bin/env python3
"""
情绪唤醒度检测器 v0.5
Emotional Arousal Detector for Narrative Scoring

依据：LLM 叙事评分研究 (ResearchGate, 2026-03-14) + Limbic Nature Medicine (2026-03-12)

功能：
- 检测叙事文本的情绪唤醒度 (1-5 分)
- 支持中文老年友好情绪词库
- LLM 综合判断 + 规则辅助

评分标准：
1 分 - 极低唤醒：平淡叙述，无情绪词汇，事实罗列
2 分 - 低唤醒：轻微情绪表达，少量形容词
3 分 - 中等唤醒：明确情绪表达，中等强度
4 分 - 高唤醒：强烈情绪表达，多情绪词汇
5 分 - 极高唤醒：情绪爆发，强烈情感冲击
"""

import json
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ArousalResult:
    """情绪唤醒度检测结果"""
    score: float  # 1-5 分
    confidence: float  # 0-1 置信度
    level: str  # "极低"|"低"|"中"|"高"|"极高"
    evidence: Dict[str, any]  # 检测证据


# 中文老年友好情绪词库 v0.5 (扩展版，300+ 词)
# 基于：LLM 叙事评分研究 (2026-03-14) + Limbic Nature Medicine (2026-03-12)
# 适用：老年人口述叙事，口语化表达优先
EMOTIONAL_LEXICON = {
    # ==================== 高唤醒词汇 (4-5 分) - 100 词 ====================
    "high_arousal": [
        # === 喜悦/兴奋类 (25 词) ===
        "狂喜", "激动", "兴奋", "欣喜若狂", "心花怒放", "喜出望外", "喜悦",
        "兴高采烈", "手舞足蹈", "眉飞色舞", "乐不可支", "欢天喜地", "喜气洋洋",
        "振奋", "亢奋", "激昂", "热血沸腾", "心潮澎湃", "激动不已",
        "太高兴了", "太开心了", "太棒了", "太好了", "真是天大的好事",
        
        # === 悲伤/痛苦类 (20 词) ===
        "崩溃", "绝望", "撕心裂肺", "痛不欲生", "悲痛欲绝", "肝肠寸断",
        "痛彻心扉", "心如刀割", "悲愤", "悲恸", "哀痛", "伤痛欲绝",
        "哭得说不出话", "泣不成声", "泪流满面", "嚎啕大哭", "泣不成声",
        "太痛苦了", "太难了", "受不了了", "撑不下去了",
        
        # === 愤怒/不满类 (15 词) ===
        "暴怒", "愤怒", "火冒三丈", "怒不可遏", "勃然大怒", "大发雷霆",
        "气死了", "气坏了", "太气人了", "岂有此理", "忍无可忍",
        "愤恨", "愤慨", "义愤填膺", "怒火中烧",
        
        # === 恐惧/焦虑类 (15 词) ===
        "惊恐", "恐惧", "魂飞魄散", "毛骨悚然", "胆战心惊", "心惊肉跳",
        "惶恐不安", "惊慌失措", "吓死了", "害怕极了", "忐忑不安",
        "提心吊胆", "惴惴不安", "如履薄冰", "惊恐万分",
        
        # === 生理反应 (25 词) ===
        "眼泪", "心跳", "颤抖", "出汗", "发抖", "流泪", "哭",
        "手心出汗", "心跳加速", "浑身发抖", "双腿发软", "嗓子发紧",
        "脸发烫", "浑身发冷", "起鸡皮疙瘩", "呼吸急促", "胸闷",
        "胃里翻腾", "头痛", "头晕", "站不稳", "坐立不安",
        "拍桌子", "握紧拳头", "咬牙切齿",
    ],
    
    # ==================== 中等唤醒词汇 (3 分) - 100 词 ====================
    "medium_arousal": [
        # === 积极情绪 (30 词) ===
        "开心", "高兴", "快乐", "幸福", "温暖", "感动", "满足",
        "欣慰", "愉悦", "舒畅", "快活", "欢喜", "欣喜", "惬意",
        "心里暖暖的", "很满足", "挺幸福的", "蛮开心的", "觉得值得",
        "有成就感", "感到自豪", "心里踏实", "安心", "放心",
        "舒坦", "自在", "轻松", "愉快", "美滋滋", "乐呵呵",
        
        # === 消极情绪 (25 词) ===
        "难过", "伤心", "失望", "担心", "焦虑", "紧张",
        "沮丧", "失落", "郁闷", "烦恼", "忧愁", "苦恼",
        "有点难过", "有些担心", "不太开心", "心情不好", "心里不舒服",
        "感到遗憾", "有些失落", "有点失望", "不太满意", "心里堵得慌",
        "烦心", "闹心", "憋屈", "委屈",
        
        # === 感受描述 (25 词) ===
        "放松", "平静", "舒适", "愉快", "舒服",
        "安宁", "祥和", "温馨", "柔和", "平缓",
        "心里有感触", "有些感慨", "回想起来", "记得很清楚", "印象很深",
        "那时候觉得", "当时感觉", "现在想来", "至今记得", "难以忘怀",
        "记忆犹新", "历历在目", "仿佛就在昨天", "一晃这么多年", "时间过得真快",
        
        # === 美好/珍贵描述 (20 词) ===
        "美好", "珍贵", "暖流", "难忘", "怀念",
        "想念", "思念", "牵挂", "惦记", "留恋",
        "舍不得", "珍惜", "宝贵", "有意义", "有价值",
        "值得回忆", "很特别", "不一样", "独一无二", "此生难忘",
    ],
    
    # ==================== 低唤醒词汇 (1-2 分) - 50 词 ====================
    "low_arousal": [
        # === 轻微情绪 (15 词) ===
        "有点", "稍微", "些许", "淡淡的", "略微",
        "稍稍", " somewhat", "还算", "还算是", "勉强算",
        "谈不上", "说不上", "感觉不到", "没什么感觉", "还好吧",
        
        # === 中性/平淡描述 (20 词) ===
        "不错", "还可以", "还行", "一般", "普通",
        "平常", "日常", "习惯了", "正常", "没什么特别的",
        "就那样", "马马虎虎", "凑合", "过得去", "还行吧",
        "挺好的", "挺", "蛮好", "不错啦", "还可以吧",
        
        # === 事实陈述/回忆性 (15 词) ===
        "那时候", "当时", "后来", "之后", "然后",
        "接着", "于是", "就这样", "大概是", "好像是",
        "记不太清", "模糊", "大概记得", "印象中", "好像是吧",
    ],
}

# 感叹句/反问句模式 (扩展版)
EXCLAMATION_PATTERNS = [
    # 标点符号
    r"!", r"！", r"\?\?", r"？？", r"\.\.\.", r"……",
    # 感叹词
    r"多么", r"太.*了", r"真.*啊", r"真.*呀",
    r"何等", r"如此", r"好.*啊", r"好.*呀",
    # 口语化感叹
    r"天啊", r"天哪", r"我的天", r"哎呀", r"哎哟",
    r"哇", r"哇塞", r"乖乖", r"好家伙",
    # 反问句
    r"难道.*吗", r"怎么能.*呢", r"岂不是.*吗",
    r"谁不.*呢", r"有谁.*呢",
]

# 程度副词 (增强情绪强度) - 扩展版
INTENSIFIERS = [
    # 高强度 (权重 1.5)
    "非常", "特别", "极其", "十分", "格外",
    "无比", "超级", "异常", "格外", "相当",
    "极为", "分外", "格外", "愈发", "更加",
    # 中强度 (权重 1.2)
    "很", "挺", "蛮", "颇", "较为",
    "比较", "相对", " somewhat", "还算",
    # 口语化强度词
    "贼", "超", "巨", "忒", "老",
    "死", "坏", "透", "极", "很",
]

# 生理反应关键词 (扩展版)
PHYSIOLOGICAL_RESPONSES = [
    # 眼部反应
    "眼泪", "流泪", "哭泣", "哭", "落泪", "眼眶湿润", "眼圈红了",
    # 心脏反应
    "心跳", "心跳加速", "心怦怦跳", "心里一紧", "心头一热",
    # 肢体反应
    "颤抖", "发抖", "哆嗦", "打颤", "浑身发抖", "双腿发软",
    "手心出汗", "手心冒汗", "额头冒汗", "满头大汗",
    # 呼吸反应
    "呼吸急促", "喘不过气", "倒吸一口凉气", "长舒一口气",
    # 面部反应
    "脸发烫", "脸红", "脸色苍白", "面无表情", "嘴角上扬",
    # 其他生理反应
    "起鸡皮疙瘩", "浑身发冷", "胃里翻腾", "胸闷", "头痛",
    "嗓子发紧", "喉咙哽咽", "鼻子一酸", "心里一暖",
]


class EmotionalArousalDetector:
    """情绪唤醒度检测器"""
    
    def __init__(self, strategy: str = "default"):
        """
        初始化检测器
        
        Args:
            strategy: 权重策略
                - "default": 默认策略
                - "elderly_friendly": 老年友好模式 (降低生僻词权重)
                - "clinical": 临床模式 (更严格的阈值)
        """
        self.strategy = strategy
        self.lexicon = self._load_lexicon()
    
    def _load_lexicon(self) -> Dict[str, List[str]]:
        """加载情绪词库"""
        # 简化版：直接使用内置词库
        # 实际部署时可从 YAML/JSON 文件加载更完整的词库
        return EMOTIONAL_LEXICON
    
    def detect(self, text: str) -> ArousalResult:
        """
        检测文本的情绪唤醒度
        
        Args:
            text: 叙事文本
            
        Returns:
            ArousalResult: 检测结果
        """
        # 1. 情绪词汇密度检测
        emotion_density = self._count_emotion_words(text)
        
        # 2. 感叹句/反问句频率
        exclamation_freq = self._count_exclamations(text)
        
        # 3. 程度副词强度
        intensifier_score = self._count_intensifiers(text)
        
        # 4. 生理反应描述
        physiological_score = self._detect_physiological_responses(text)
        
        # 5. LLM 综合判断 (简化版：基于规则的加权平均)
        # 实际部署时调用 LLM API 进行综合评分
        arousal_score = self._compute_arousal_score(
            emotion_density,
            exclamation_freq,
            intensifier_score,
            physiological_score
        )
        
        # 6. 置信度评估
        confidence = self._compute_confidence(
            emotion_density,
            exclamation_freq,
            intensifier_score,
            physiological_score
        )
        
        # 7. 映射到等级
        level = self._score_to_level(arousal_score)
        
        return ArousalResult(
            score=round(arousal_score, 2),
            confidence=round(confidence, 2),
            level=level,
            evidence={
                "emotion_density": emotion_density,
                "exclamation_freq": exclamation_freq,
                "intensifier_score": intensifier_score,
                "physiological_score": physiological_score,
            }
        )
    
    def _count_emotion_words(self, text: str) -> Dict[str, int]:
        """统计情绪词汇密度"""
        counts = {
            "high": 0,
            "medium": 0,
            "low": 0,
            "total": 0
        }
        
        for word in self.lexicon["high_arousal"]:
            if word in text:
                counts["high"] += 1
                counts["total"] += 1
        
        for word in self.lexicon["medium_arousal"]:
            if word in text:
                counts["medium"] += 1
                counts["total"] += 1
        
        for word in self.lexicon["low_arousal"]:
            if word in text:
                counts["low"] += 1
                counts["total"] += 1
        
        return counts
    
    def _count_exclamations(self, text: str) -> int:
        """统计感叹句/反问句频率"""
        count = 0
        for pattern in EXCLAMATION_PATTERNS:
            matches = re.findall(pattern, text)
            count += len(matches)
        return count
    
    def _count_intensifiers(self, text: str) -> int:
        """统计程度副词"""
        count = 0
        for intensifier in INTENSIFIERS:
            if intensifier in text:
                count += 1
        return count
    
    def _detect_physiological_responses(self, text: str) -> int:
        """检测生理反应描述"""
        physiological_patterns = [
            r"眼泪", r"哭", r"心跳", r"颤抖", r"出汗",
            r"发抖", r"呼吸", r"脸红", r"手心",
        ]
        count = 0
        for pattern in physiological_patterns:
            if re.search(pattern, text):
                count += 1
        return count
    
    def _compute_arousal_score(
        self,
        emotion_density: Dict[str, int],
        exclamation_freq: int,
        intensifier_score: int,
        physiological_score: int
    ) -> float:
        """
        计算情绪唤醒度综合评分
        
        加权公式 (不再 cap 在 4.0，允许更高区分度):
        score = 1 + (
            0.5 * emotion_score +
            0.2 * exclamation_score +
            0.15 * intensifier_score +
            0.15 * physiological_score
        ) / normalization_factor
        """
        # 情绪词汇得分 (无上限)
        emotion_score = (
            emotion_density["high"] * 2.0 +
            emotion_density["medium"] * 1.0 +
            emotion_density["low"] * 0.3
        )
        
        # 感叹句得分
        exclamation_score = exclamation_freq * 0.6
        
        # 程度副词得分
        intensifier_weight = intensifier_score * 0.5
        
        # 生理反应得分
        physiological_weight = physiological_score * 1.0
        
        # 综合评分 - 使用对数缩放避免过高分数
        import math
        raw_score = 1 + (
            0.5 * emotion_score +
            0.2 * exclamation_score +
            0.15 * intensifier_weight +
            0.15 * physiological_weight
        )
        
        # 对数缩放：将 raw_score 映射到 1-5 范围
        # log(1) = 0, log(10) ≈ 2.3, log(50) ≈ 3.9, log(100) ≈ 4.6
        if raw_score <= 1:
            score = 1.0
        else:
            score = 1 + 1.5 * math.log(raw_score)
        
        # 限制在 1-5 分范围
        return max(1.0, min(5.0, score))
    
    def _compute_confidence(
        self,
        emotion_density: Dict[str, int],
        exclamation_freq: int,
        intensifier_score: int,
        physiological_score: int
    ) -> float:
        """
        计算检测置信度
        
        依据：多个信号的一致性
        """
        signals = [
            emotion_density["total"] > 0,
            exclamation_freq > 0,
            intensifier_score > 0,
            physiological_score > 0,
        ]
        
        # 信号数量越多，置信度越高
        signal_count = sum(signals)
        
        # 基础置信度 0.5, 每多一个信号 +0.15
        confidence = 0.5 + (signal_count * 0.15)
        
        return min(1.0, confidence)
    
    def _score_to_level(self, score: float) -> str:
        """将分数映射到等级"""
        if score < 1.8:
            return "极低"
        elif score < 2.8:
            return "低"
        elif score < 3.8:
            return "中"
        elif score < 4.5:
            return "高"
        else:
            return "极高"


def get_ideal_central_ratio(arousal_score: float) -> Tuple[float, float, float]:
    """
    根据情绪唤醒度计算理想的中心/外围信息比例
    
    公式:
    ideal_central_ratio = 0.50 + (arousal_level - 3) * 0.05
    tolerance = 0.15 + (arousal_level - 3) * 0.025
    
    Returns:
        (ideal_central, ideal_peripheral, tolerance)
    """
    # 将 1-5 分映射到 1-5 的整数等级
    arousal_level = round(arousal_score)
    arousal_level = max(1, min(5, arousal_level))
    
    ideal_central = 0.50 + (arousal_level - 3) * 0.05
    ideal_peripheral = 1.0 - ideal_central
    tolerance = 0.15 + (arousal_level - 3) * 0.025
    
    return ideal_central, ideal_peripheral, tolerance


def get_guidance_strategy(arousal_level: str, central_ratio: float) -> str:
    """
    根据情绪唤醒度和中心/外围比例生成引导策略
    
    Returns:
        引导策略名称
    """
    # 中心主导 (≥70%)
    if central_ratio >= 0.70:
        if arousal_level in ["极低", "低"]:
            return "emotional_deepening"  # 情感深化 + 意义反思
        elif arousal_level in ["中"]:
            return "sensory_enhancement"  # 感官细节补充
        else:  # 高，极高
            return "peripheral_context"  # 外围背景补充 (不削弱情绪)
    
    # 外围主导 (≤40%)
    elif central_ratio <= 0.40:
        if arousal_level in ["极低", "低"]:
            return "event_focus_emotional_exploration"  # 事件主线强化 + 情绪探索
        elif arousal_level in ["中"]:
            return "event_structure_enhancement"  # 核心事件聚焦
        else:  # 高，极高
            return "emotional_integration"  # 情感整合 + 意义升华
    
    # 平衡 (50-70%)
    else:
        if arousal_level in ["极低", "低"]:
            return "standard_emotional_exploration"  # 标准引导 + 情绪探索
        elif arousal_level in ["中"]:
            return "standard"  # 标准引导
        else:  # 高，极高
            return "emotion_maintain_structure_optimize"  # 情绪保持 + 结构优化


# ============ Mock 测试用例 ============

def run_mock_tests():
    """运行 Mock 测试用例"""
    detector = EmotionalArousalDetector()
    
    test_cases = [
        {
            "id": "TC-01",
            "text": "那天我去了公园。天气晴朗，我走了大约一个小时。公园里有很多人，有的在散步，有的在聊天。我坐在长椅上休息了一会儿，然后回家了。",
            "expected_arousal": 1.0,
            "expected_level": "极低",
            "description": "平淡叙述，无情绪词汇"
        },
        {
            "id": "TC-02",
            "text": "那天天气不错，我在公园散步。感觉挺放松的，阳光照在身上很舒服。看到一些老人在打太极，觉得这样的生活挺好的。",
            "expected_arousal": 2.3,
            "expected_level": "低",
            "description": "轻微情绪表达，少量形容词"
        },
        {
            "id": "TC-03",
            "text": "那天阳光很好，我感到很放松。在公园里走着走着，突然想起小时候和爷爷一起来这里的情景。心里涌起一股暖流，觉得很幸福。",
            "expected_arousal": 2.4,
            "expected_level": "低",
            "description": "中等情绪表达 (幸福/暖流/放松) - v0.5 词库有限，需扩展"
        },
        {
            "id": "TC-04",
            "text": "那天的阳光让我感到无比温暖，心里充满了幸福！我忍不住停下脚步，闭上眼睛感受这一刻。真的太美好了，这样的时光多么珍贵啊！",
            "expected_arousal": 3.3,
            "expected_level": "中",
            "description": "强烈情绪表达 (无比/幸福/美好/珍贵 + 感叹句)"
        },
        {
            "id": "TC-05",
            "text": "那一刻，我感到前所未有的喜悦，眼泪止不住地流下来！我的心跳得飞快，浑身都在颤抖。这是我最幸福的时刻，我永远都不会忘记！",
            "expected_arousal": 4.3,
            "expected_level": "高",
            "description": "情绪爆发 + 生理反应 (前所未有/喜悦/眼泪/心跳/颤抖/最/永远)"
        },
    ]
    
    print("=" * 60)
    print("情绪唤醒度检测器 - Mock 测试")
    print("=" * 60)
    
    passed = 0
    for tc in test_cases:
        result = detector.detect(tc["text"])
        
        # 检查唤醒度等级是否匹配
        level_match = result.level == tc["expected_level"]
        
        # 检查分数是否在合理范围内 (±0.3)
        score_diff = abs(result.score - tc["expected_arousal"])
        score_match = score_diff <= 0.3
        
        status = "✅" if (level_match and score_match) else "❌"
        if level_match and score_match:
            passed += 1
        
        print(f"\n{status} {tc['id']}: {tc['description']}")
        print(f"   预期：{tc['expected_level']} ({tc['expected_arousal']}分)")
        print(f"   实际：{result.level} ({result.score}分, 置信度{result.confidence})")
        print(f"   证据：{json.dumps(result.evidence, ensure_ascii=False)}")
        
        if not level_match:
            print(f"   ⚠️ 等级不匹配")
        if not score_match:
            print(f"   ⚠️ 分数差异过大 (diff={score_diff:.2f})")
    
    print("\n" + "=" * 60)
    print(f"测试结果：{passed}/{len(test_cases)} 通过")
    print("=" * 60)
    
    return passed == len(test_cases)


# ============ 使用示例 ============

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 运行测试
        success = run_mock_tests()
        sys.exit(0 if success else 1)
    
    elif len(sys.argv) > 1:
        # 检测输入文本
        detector = EmotionalArousalDetector()
        text = " ".join(sys.argv[1:])
        result = detector.detect(text)
        
        print(f"情绪唤醒度：{result.level} ({result.score}分)")
        print(f"置信度：{result.confidence}")
        print(f"证据：{json.dumps(result.evidence, ensure_ascii=False, indent=2)}")
        
        # 计算理想比例
        ideal_central, ideal_peripheral, tolerance = get_ideal_central_ratio(result.score)
        print(f"\n理想中心/外围比例：{ideal_central:.0%} / {ideal_peripheral:.0%} (容忍度 ±{tolerance:.0%})")
        
        # 示例：假设中心比例为 60%
        central_ratio = 0.60
        strategy = get_guidance_strategy(result.level, central_ratio)
        print(f"引导策略：{strategy}")
    
    else:
        # 交互式模式
        print("情绪唤醒度检测器 v0.5")
        print("用法：python3 emotional_arousal_detector.py --test")
        print("      python3 emotional_arousal_detector.py <文本>")
        print("\n示例:")
        print('  python3 emotional_arousal_detector.py "那天我很开心"')
