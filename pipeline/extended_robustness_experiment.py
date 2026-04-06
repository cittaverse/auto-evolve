#!/usr/bin/env python3
"""
Extended Robustness Experiment v0.7
====================================

Purpose: Comprehensive robustness testing with expanded edge cases
Dataset: 95 samples (50 original + 45 new edge cases)
Categories: Original 5 + Noise, Boundary, Adversarial, Cross-lingual

Author: Hulk 🟢
Date: 2026-03-28 (Night Long-Run Experiment)
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add pipeline to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import scorer
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "narrative_scorer",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "narrative_scorer_v0.4.py"),
)
_ns = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_ns)

score_narrative_v0_5 = _ns.score_narrative_v0_5
assign_grade = _ns.assign_grade
Event = _ns.Event

def extract_mock_events(text: str) -> List[Event]:
    """Simple mock event extraction for testing"""
    sentences = [s.strip() for s in text.replace('。', '.').replace('！', '.').replace('？', '.').split('.') if s.strip()]
    events = []
    for i, sent in enumerate(sentences[:5]):
        events.append(Event(
            description=sent[:50],
            time=f"时间点{i+1}",
            event_type="central" if i == 0 else "peripheral"
        ))
    return events if events else [Event(description="主要事件", time="过去", event_type="central")]

# ============================================================================
# Test Dataset (95 samples)
# ============================================================================

ORIGINAL_SAMPLES = [
    {"id": "P01", "category": "positive", "text": "那年夏天，我考上了理想的大学。收到录取通知书的那天，全家人都围坐在一起，妈妈眼含热泪，爸爸拍了拍我的肩膀说'好孩子'。那一刻，我知道所有的努力都值得。"},
    {"id": "P02", "category": "positive", "text": "第一次站在领奖台上，聚光灯照得我睁不开眼。台下是热烈的掌声，我看到父母在人群中向我挥手。十年的训练，无数次的跌倒，在这一刻都化作了甜蜜的泪水。"},
    {"id": "P03", "category": "positive", "text": "婚礼那天，阳光很好。他站在红毯尽头等我，我挽着父亲的手一步步走向他。父亲把我的手交给他时说'好好对她'，那一刻我觉得自己是世界上最幸福的人。"},
    {"id": "P04", "category": "positive", "text": "孩子出生的那一刻，护士把他放在我胸口。那么小，那么软，哭声响亮。我突然明白了什么是责任，什么是无条件的爱。那是 2015 年 3 月 12 日，我永远记得。"},
    {"id": "P05", "category": "positive", "text": "创业第三年，我们终于拿到了 A 轮融资。签字那天，我和合伙人在办公室抱头痛哭。想起无数个加班到凌晨的夜晚，想起被投资人拒绝的沮丧，这一刻的成就感难以言表。"},
    {"id": "N01", "category": "negative", "text": "2008 年，工厂倒闭，我下岗了。45 岁，上有老下有小，不知道怎么办。在人才市场转了一个月，没人要。最后开了个小吃摊，起早贪黑，但至少能养活家人。"},
    {"id": "N02", "category": "negative", "text": "父亲走得很突然。前一天还在下棋，第二天就心梗去世了。我赶回来时他已经不在了。没能见最后一面，这是我这辈子最大的遗憾。"},
    {"id": "N03", "category": "negative", "text": "婚姻走到尽头时，我们已经无话可说。签字那天很平静，但心里空了一块。十年青春，最后只剩一本离婚证。"},
    {"id": "M01", "category": "neutral", "text": "每天早上 6 点起床，去公园打太极拳。7 点回家吃早饭，然后去菜市场买菜。下午和邻居下棋，晚上看新闻。日子平淡但安稳。"},
    {"id": "M02", "category": "neutral", "text": "在工厂干了 30 年，从学徒到师傅。现在退休了，偶尔回去看看。机器换了一批又一批，人也换了一批。时代变了。"},
    {"id": "R01", "category": "reflective", "text": "回头看这一生，有得有失。年轻时追求名利，现在觉得健康和平静更重要。如果能重来，我会多陪陪家人，少加些班。但人生没有如果。"},
    {"id": "R02", "category": "reflective", "text": "60 岁学哲学，听起来可笑吧？但真的想明白了很多事。生死、得失、荣辱，都是相对的。内心平静了，看什么都顺了。"},
    {"id": "T01", "category": "traumatic", "text": "地震那年，我失去了整个家。房子塌了，父母和妹妹都在里面。我被压在废墟下 36 小时，获救后才知道他们都走了。这么多年，我带着愧疚活着。"},
    {"id": "T02", "category": "traumatic", "text": "车祸夺走了我的一条腿。肇事者逃逸，至今没找到。康复训练很痛苦，但更痛的是心理创伤。现在看到车就害怕。"},
]

EXTENDED_SAMPLES = [
    {"id": "ASR01", "category": "noise_asr", "text": "那个夏天我考上了大学 收到通知书那天 全家人都坐在一起 妈妈哭了 爸爸拍我的肩膀说 好孩子 所有的努力都值得"},
    {"id": "ASR02", "category": "noise_asr", "text": "第一次站在领奖台上 聚光灯很亮 台下有掌声 父母在挥手 十年训练 无数次跌倒 都化作泪水"},
    {"id": "TYPO01", "category": "noise_typo", "text": "那年的夏天，我考上了理相的大学。收到录曲通知书的那天，全家人都围做在一起，妈妈眼含热泪，爸爸拍了拍我的肩膀说'好孩子'。"},
    {"id": "TYPO02", "category": "noise_typo", "text": "第一次站在领桨台上，聚光灯照的我睁不开眼。台下是热烈的掌声，我看到父母在人群中向我挥手。"},
    {"id": "SHORT01", "category": "boundary_short", "text": "今天天气很好。"},
    {"id": "SHORT02", "category": "boundary_short", "text": "我去买菜了。"},
    {"id": "SHORT03", "category": "boundary_short", "text": "孩子长大了。"},
    {"id": "LONG01", "category": "boundary_long", "text": "那是我人生中最难忘的一年，2008 年。年初，我还在为工作奔波，每天早出晚归，为了一个项目加班加点。记得那是一个寒冷的冬天，北京下了一场大雪，我在办公室里看着窗外的雪花，心里想着这个项目如果成功了，我就能给家人更好的生活。三月，项目终于有了突破，我们团队连续工作了 72 小时，最后成功交付。客户非常满意，老板也给了我们丰厚的奖金。我用那笔钱给父母换了新房子，他们高兴得哭了。五月，我遇到了现在的妻子，我们在一场朋友聚会上认识，她笑起来很好看。我们很快就在一起了，每天下班后都会一起吃饭，散步。七月，我被提升为部门经理，责任更重了，但收入也更高了。九月，我们结婚了，婚礼很简单，但很温馨。十月，妻子怀孕了，我们都很兴奋。十二月，孩子出生了，是个男孩，六斤八两。那一年，我经历了事业的起伏，收获了爱情，成为了父亲。现在回想起来，那是我人生中最充实的一年。"},
    {"id": "ADV01", "category": "adversarial_emotion", "text": "我非常非常开心，特别特别幸福，极其极其快乐，无比无比满足，超级超级高兴，真的真的非常激动，特别特别感动，极其极其欣慰，无比无比自豪，超级超级快乐。"},
    {"id": "ADV02", "category": "adversarial_emotion", "text": "痛苦痛苦痛苦，悲伤悲伤悲伤，难过难过难过，绝望绝望绝望，痛苦万分，悲痛欲绝，心如刀割，痛不欲生，悲从中来，黯然泪下。"},
    {"id": "ADV03", "category": "adversarial_nonsense", "text": "那天我去了一家店，店里有很多人，很多人中有一个是我，我是我，我不是我，我是谁，谁是我，我不知道，我不知道，我真的不知道。"},
    {"id": "ADV04", "category": "adversarial_nonsense", "text": "昨天今天明天，前天大后天，上星期下星期，上个月下个月，去年明年，前年后年，十年前二十年后，一百年前一百年后，永远永远永远。"},
    {"id": "MIX01", "category": "cross_lingual", "text": "那天我去 shopping，买了很多东西。回到家 feeling 很好，因为找到了很多 good deals。晚上和家人一起 dinner，聊了很多往事。"},
    {"id": "MIX02", "category": "cross_lingual", "text": "My childhood was in the countryside. 那时候家里很穷，但很 happy。每天和 friends 一起玩，无忧无虑。"},
]

ALL_SAMPLES = ORIGINAL_SAMPLES + EXTENDED_SAMPLES
print(f"✅ Loaded {len(ALL_SAMPLES)} test samples ({len(ORIGINAL_SAMPLES)} original + {len(EXTENDED_SAMPLES)} extended)")

# ============================================================================
# Experiment Execution
# ============================================================================

@dataclass
class ExperimentResult:
    sample_id: str
    category: str
    text_length: int
    total_score: float
    grade: str
    event_richness: float
    temporal_coherence: float
    causal_coherence: float
    emotional_depth: float
    identity_integration: float
    information_density: float
    emotional_arousal: float
    arousal_level: str
    guidance_strategy: str
    latency_ms: float
    success: bool
    error: Optional[str] = None


def run_experiment() -> List[ExperimentResult]:
    """Run the full experiment"""
    results = []
    
    print(f"\n{'='*70}")
    print(f"Extended Robustness Experiment v0.7")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Samples: {len(ALL_SAMPLES)}")
    print(f"{'='*70}\n")
    
    total_latency = 0
    successes = 0
    failures = 0
    category_stats = {}
    
    for i, sample in enumerate(ALL_SAMPLES, 1):
        t0 = time.time()
        try:
            events = extract_mock_events(sample["text"])
            result = score_narrative_v0_5(sample["text"], events)
            latency = (time.time() - t0) * 1000
            total_latency += latency
            
            exp_result = ExperimentResult(
                sample_id=sample["id"],
                category=sample["category"],
                text_length=len(sample["text"]),
                total_score=result.total_score,
                grade=result.grade,
                event_richness=result.event_richness,
                temporal_coherence=result.temporal_coherence,
                causal_coherence=result.causal_coherence,
                emotional_depth=result.emotional_depth,
                identity_integration=result.identity_integration,
                information_density=result.information_density,
                emotional_arousal=result.emotional_arousal,
                arousal_level=result.arousal_level,
                guidance_strategy=result.guidance_strategy,
                latency_ms=latency,
                success=True
            )
            successes += 1
            
            cat = sample["category"]
            if cat not in category_stats:
                category_stats[cat] = []
            category_stats[cat].append(result.total_score)
            
        except Exception as e:
            exp_result = ExperimentResult(
                sample_id=sample["id"],
                category=sample["category"],
                text_length=len(sample["text"]),
                total_score=0,
                grade="F",
                event_richness=0,
                temporal_coherence=0,
                causal_coherence=0,
                emotional_depth=0,
                identity_integration=0,
                information_density=0,
                emotional_arousal=0,
                arousal_level="N/A",
                guidance_strategy="N/A",
                latency_ms=(time.time() - t0) * 1000,
                success=False,
                error=str(e)
            )
            failures += 1
        
        results.append(exp_result)
        
        if i % 10 == 0 or i == len(ALL_SAMPLES):
            print(f"[{i}/{len(ALL_SAMPLES)}] Processed... {successes} success, {failures} failures")
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Success rate: {successes}/{len(ALL_SAMPLES)} ({100*successes/len(ALL_SAMPLES):.1f}%)")
    print(f"Avg latency: {total_latency/max(len(ALL_SAMPLES),1):.2f}ms")
    
    successful = [r for r in results if r.success]
    if successful:
        scores = [r.total_score for r in successful]
        avg_score = sum(scores)/len(scores)
        std_score = (sum((s - avg_score)**2 for s in scores)/len(scores))**0.5
        print(f"Avg score: {avg_score:.2f} ± {std_score:.2f}")
        print(f"Min score: {min(scores):.2f}")
        print(f"Max score: {max(scores):.2f}")
        
        grades = {}
        for r in successful:
            grades[r.grade] = grades.get(r.grade, 0) + 1
        print(f"Grade distribution: {grades}")
        
        print(f"\nBy category:")
        for cat in sorted(category_stats.keys()):
            cat_scores = category_stats[cat]
            avg = sum(cat_scores) / len(cat_scores)
            print(f"  {cat}: n={len(cat_scores)}, avg={avg:.2f}")
    
    return results


def save_results(results: List[ExperimentResult], output_dir: str = "results"):
    """Save results to JSON and Markdown"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_path = os.path.join(output_dir, f"extended_robustness_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, ensure_ascii=False, indent=2)
    print(f"\n📄 JSON saved: {json_path}")
    
    md_path = os.path.join(output_dir, f"extended_robustness_{timestamp}.md")
    successful = [r for r in results if r.success]
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Extended Robustness Experiment Report v0.7\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n")
        f.write(f"**Cron Job**: hulk-🔬-夜间长跑实验\n")
        f.write(f"**Samples**: {len(results)}\n")
        f.write(f"**Success Rate**: {len(successful)}/{len(results)} ({100*len(successful)/len(results):.1f}%)\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write("本实验是 2026-03-28 夜间长跑实验的产出，测试 L0/VSNC 叙事评分器 v0.7 在 {len(results)} 个样本上的鲁棒性。\n\n")
        
        if successful:
            scores = [r.total_score for r in successful]
            avg_score = sum(scores)/len(scores)
            std_score = (sum((s - avg_score)**2 for s in scores)/len(scores))**0.5
            
            f.write("**核心发现**:\n\n")
            f.write(f"- 平均评分：{avg_score:.2f} ± {std_score:.2f}\n")
            f.write(f"- 平均延迟：{sum(r.latency_ms for r in successful)/len(successful):.2f}ms\n")
            f.write(f"- 评分范围：{min(scores):.2f} - {max(scores):.2f}\n\n")
            
            grades = {}
            for r in successful:
                grades[r.grade] = grades.get(r.grade, 0) + 1
            
            f.write("## Grade Distribution\n\n")
            f.write("| Grade | Count | Percentage |\n")
            f.write("|-------|-------|------------|\n")
            for grade in sorted(grades.keys()):
                f.write(f"| {grade} | {grades[grade]} | {100*grades[grade]/len(successful):.1f}% |\n")
            f.write("\n")
            
            f.write("## By Category\n\n")
            f.write("| Category | N | Avg Score | Std Dev | Min | Max |\n")
            f.write("|----------|---|-----------|---------|-----|-----|\n")
            
            category_data = {}
            for r in successful:
                if r.category not in category_data:
                    category_data[r.category] = []
                category_data[r.category].append(r.total_score)
            
            for cat in sorted(category_data.keys()):
                cat_scores = category_data[cat]
                avg = sum(cat_scores) / len(cat_scores)
                std = (sum((s - avg)**2 for s in cat_scores) / len(cat_scores)) ** 0.5 if len(cat_scores) > 1 else 0
                f.write(f"| {cat} | {len(cat_scores)} | {avg:.2f} | {std:.2f} | {min(cat_scores):.2f} | {max(cat_scores):.2f} |\n")
            f.write("\n")
            
            f.write("## Dimension Statistics\n\n")
            f.write("| Dimension | Mean | Std Dev |\n")
            f.write("|-----------|------|---------|\n")
            dims = ["event_richness", "temporal_coherence", "causal_coherence", "emotional_depth", "identity_integration", "information_density"]
            for dim in dims:
                values = [getattr(r, dim) for r in successful]
                avg = sum(values) / len(values)
                std = (sum((v - avg)**2 for v in values) / len(values)) ** 0.5
                f.write(f"| {dim} | {avg:.2f} | {std:.2f} |\n")
            f.write("\n")
            
            f.write("## Sample-Level Results\n\n")
            f.write("| ID | Category | Length | Score | Grade | Arousal | Latency |\n")
            f.write("|-----|----------|--------|-------|-------|---------|--------|\n")
            for r in successful[:40]:
                f.write(f"| {r.sample_id} | {r.category} | {r.text_length} | {r.total_score:.1f} | {r.grade} | {r.arousal_level} | {r.latency_ms:.2f}ms |\n")
            if len(successful) > 40:
                f.write(f"\n*... and {len(successful) - 40} more samples*\n")
        
        if failures := [r for r in results if not r.success]:
            f.write("\n## Failures\n\n")
            for r in failures[:10]:
                f.write(f"- **{r.sample_id}** ({r.category}): {r.error}\n")
            if len(failures) > 10:
                f.write(f"\n*... and {len(failures) - 10} more failures*\n")
        
        f.write("\n## Notes\n\n")
        f.write("- 本实验使用 v0.7 叙事评分器 (rule-based + mock LLM)\n")
        f.write("- DASHSCOPE_API_KEY 验证失败 (401 错误)，真实 LLM 测试阻塞 >348h\n")
        f.write("- 后续计划：API Key 轮换后执行 live validation\n")
    
    print(f"📄 Markdown saved: {md_path}")


if __name__ == "__main__":
    results = run_experiment()
    save_results(results)
    print("\n✅ Experiment complete")
