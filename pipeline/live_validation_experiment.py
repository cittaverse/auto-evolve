#!/usr/bin/env python3
"""
v0.7 Live Validation Experiment
================================

Purpose: Validate mock-based experiments against real LLM calls
Comparison: Mock (qwen3.5-plus mocked) vs Live (qwen3.5-plus via DASHSCOPE)
Dataset: Same 50-sample test set from ablation study
Metrics: Score delta, latency, cost, failure rate

Author: Hulk 🟢
Date: 2026-03-28
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# Add pipeline to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check API key
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY")
if not DASHSCOPE_API_KEY:
    print("❌ DASHSCOPE_API_KEY not set")
    sys.exit(1)

print(f"✅ DASHSCOPE_API_KEY available: {DASHSCOPE_API_KEY[:20]}...")

# Import scorer
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "narrative_scorer",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "narrative_scorer_v0.4.py"),
)
_ns = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_ns)

Event = _ns.Event
NarrativeScore = _ns.NarrativeScore
score_narrative_v0_5 = _ns.score_narrative_v0_5

# ============================================================================
# Test Dataset (50 samples from ablation study)
# ============================================================================

TEST_SAMPLES = [
    # Category 1: Positive/Upward (10 samples)
    {"id": "P01", "category": "positive", "text": "那年夏天，我考上了理想的大学。收到录取通知书的那天，全家人都围坐在一起，妈妈眼含热泪，爸爸拍了拍我的肩膀说'好孩子'。那一刻，我知道所有的努力都值得。"},
    {"id": "P02", "category": "positive", "text": "第一次站在领奖台上，聚光灯照得我睁不开眼。台下是热烈的掌声，我看到父母在人群中向我挥手。十年的训练，无数次的跌倒，在这一刻都化作了甜蜜的泪水。"},
    {"id": "P03", "category": "positive", "text": "婚礼那天，阳光很好。他站在红毯尽头等我，我挽着父亲的手一步步走向他。父亲把我的手交给他时说'好好对她'，那一刻我觉得自己是世界上最幸福的人。"},
    {"id": "P04", "category": "positive", "text": "孩子出生的那一刻，护士把他放在我胸口。那么小，那么软，哭声响亮。我突然明白了什么是责任，什么是无条件的爱。那是 2015 年 3 月 12 日，我永远记得。"},
    {"id": "P05", "category": "positive", "text": "创业第三年，我们终于拿到了 A 轮融资。签字那天，我和合伙人在办公室抱头痛哭。想起无数个加班到凌晨的夜晚，想起被投资人拒绝的沮丧，这一刻的成就感难以言表。"},
    {"id": "P06", "category": "positive", "text": "退休后和老伴去了西藏。站在布达拉宫前，海拔 3650 米，我们互相搀扶着拍照。她说'这辈子值了'，我说'是啊，下辈子还要一起'。"},
    {"id": "P07", "category": "positive", "text": "学会游泳那天我已经 60 岁了。教练说'您是我教过的最年长的学员'。从怕水到能游 500 米，用了整整一年。我明白了，人生没有太晚的开始。"},
    {"id": "P08", "category": "positive", "text": "女儿从国外留学回来，给我带了一台智能手机。她花了一下午教我微信、视频通话、看新闻。现在我每天都会给她发消息，距离不再是问题。"},
    {"id": "P09", "category": "positive", "text": "社区组织老年合唱团，我报名当了团长。每周三下午，我们聚在一起唱歌。《我和我的祖国》唱到最后，很多人眼里都有泪光。音乐让我们年轻。"},
    {"id": "P10", "category": "positive", "text": "去年体检，医生说我的指标比实际年龄年轻 10 岁。秘诀？每天晨练、读书、和朋友喝茶。退休不是终点，是另一种生活的开始。"},
    
    # Category 2: Negative/Downward (10 samples)
    {"id": "N01", "category": "negative", "text": "2008 年，工厂倒闭，我下岗了。45 岁，上有老下有小，不知道怎么办。在人才市场转了一个月，没人要。最后开了个小吃摊，起早贪黑，但至少能养活家人。"},
    {"id": "N02", "category": "negative", "text": "父亲走得很突然。前一天还在下棋，第二天就心梗去世了。我赶回来时他已经不在了。没能见最后一面，这是我这辈子最大的遗憾。"},
    {"id": "N03", "category": "negative", "text": "婚姻走到尽头时，我们已经无话可说。签字那天很平静，但心里空了一块。十年青春，最后只剩一本离婚证。"},
    {"id": "N04", "category": "negative", "text": "儿子高考失利，只考了个专科。他把自己关在房间里三天不出来。我安慰他说'没关系'，但心里比他还难受。怪我没能力给他更好的教育资源。"},
    {"id": "N05", "category": "negative", "text": "投资失败，积蓄全没了。朋友推荐的理财产品，说是保本高收益。现在人去楼空，报警也没用。不敢告诉家人，每天失眠。"},
    {"id": "N06", "category": "negative", "text": "查出糖尿病那天，我觉得天塌了。要终身打胰岛素，不能吃喜欢的甜食，还要担心并发症。医生说要控制饮食多运动，但 20 年的习惯哪是说改就改的。"},
    {"id": "N07", "category": "negative", "text": "老伴走后，房子突然变得好大。一个人吃饭，一个人看电视，一个人睡觉。孩子们都在外地，说接我去他们那边，但我不想离开这个生活了一辈子的地方。"},
    {"id": "N08", "category": "negative", "text": "退休工资不高，看病又要花钱。能省则省吧，小病扛着，大病...不敢想。不想给孩子添负担，他们也不容易。"},
    {"id": "N09", "category": "negative", "text": "年轻时和兄弟合伙做生意，被他骗了。几十万的货款，人去楼空。这么多年过去了，心里还是过不去这个坎。"},
    {"id": "N10", "category": "negative", "text": "女儿远嫁国外，一年回来一次。视频里看到她过得很好，但挂掉电话后还是忍不住哭。养大孩子，就是为了放手让她飞。"},
    
    # Category 3: Neutral (10 samples)
    {"id": "M01", "category": "neutral", "text": "每天早上 6 点起床，去公园打太极拳。7 点回家吃早饭，然后去菜市场买菜。下午和邻居下棋，晚上看新闻。日子平淡但安稳。"},
    {"id": "M02", "category": "neutral", "text": "在工厂干了 30 年，从学徒到师傅。现在退休了，偶尔回去看看。机器换了一批又一批，人也换了一批。时代变了。"},
    {"id": "M03", "category": "neutral", "text": "搬过五次家。第一次是结婚，第二次是孩子出生，第三次是换学区房，第四次是退休回老城，第五次...不知道会在哪里。"},
    {"id": "M04", "category": "neutral", "text": "做过很多工作：工人、销售、小老板、保安。每份工作都教会我一些东西。现在想想，人生没有白走的路。"},
    {"id": "M05", "category": "neutral", "text": "家里有三个兄弟姐妹，我排老二。小时候让着哥哥，照顾着弟弟。现在大家都老了，逢年过节聚一聚，聊聊往事。"},
    {"id": "M06", "category": "neutral", "text": "学了书法五年，现在能写一手像样的字。社区活动经常请我去写春联。修身养性，挺好的。"},
    {"id": "M07", "category": "neutral", "text": "每年体检，指标有高有低。医生说这个年纪正常。该吃吃该喝喝，开心最重要。"},
    {"id": "M08", "category": "neutral", "text": "孙子孙女四个，大的上大学，小的上幼儿园。周末都回来，家里热闹。平时就我和老伴，清清静静。"},
    {"id": "M09", "category": "neutral", "text": "年轻时喜欢旅游，去过十几个省。现在走不动了，看看电视里的旅游节目，也算云游四方。"},
    {"id": "M10", "category": "neutral", "text": "养了一只猫，15 岁了，比很多老人都长寿。它陪我度过了很多孤独的时光。动物比人懂你。"},
    
    # Category 4: Reflective (10 samples)
    {"id": "R01", "category": "reflective", "text": "回头看这一生，有得有失。年轻时追求名利，现在觉得健康和平静更重要。如果能重来，我会多陪陪家人，少加些班。但人生没有如果。"},
    {"id": "R02", "category": "reflective", "text": "60 岁学哲学，听起来可笑吧？但真的想明白了很多事。生死、得失、荣辱，都是相对的。内心平静了，看什么都顺了。"},
    {"id": "R03", "category": "reflective", "text": "年轻时总觉得父母不理解自己。现在自己当了父母，才明白他们的苦心。可惜他们不在了，子欲养而亲不待。"},
    {"id": "R04", "category": "reflective", "text": "创业失败过三次，每次都以为熬不过去，但都熬过来了。现在想想，失败不是终点，是成长的必经之路。"},
    {"id": "R05", "category": "reflective", "text": "婚姻 30 年，吵过闹过，也想过放弃。但现在明白了，长久的关系不是没有矛盾，而是愿意一起解决问题。"},
    {"id": "R06", "category": "reflective", "text": "退休前怕闲下来会不适应。现在发现，有时间读书、锻炼、陪家人，比工作时快乐多了。人生每个阶段都有它的美好。"},
    {"id": "R07", "category": "reflective", "text": "年轻时追求'有用'，现在喜欢'无用'的事：看云、听雨、发呆。庄子说'无用之用，方为大用'，现在懂了。"},
    {"id": "R08", "category": "reflective", "text": "孩子小时候盼他们长大，长大后盼他们常回家。现在明白了，父母子女一场，就是不断目送他们远行。"},
    {"id": "R09", "category": "reflective", "text": "经历过文革、改革开放、互联网时代。时代变迁太快，但人性没变。真诚、善良、勤奋，这些品质永远不会过时。"},
    {"id": "R10", "category": "reflective", "text": "医生说我的病治不好，只能控制。一开始接受不了，现在想通了。生老病死是自然规律，重要的是怎么活好每一天。"},
    
    # Category 5: Traumatic (10 samples)
    {"id": "T01", "category": "traumatic", "text": "地震那年，我失去了整个家。房子塌了，父母和妹妹都在里面。我被压在废墟下 36 小时，获救后才知道他们都走了。这么多年，我带着愧疚活着。"},
    {"id": "T02", "category": "traumatic", "text": "车祸夺走了我的一条腿。肇事者逃逸，至今没找到。康复训练很痛苦，但更痛的是心理创伤。现在看到车就害怕。"},
    {"id": "T03", "category": "traumatic", "text": "儿子 18 岁那年自杀了。没有预兆，没有遗书。我和他妈妈到现在都想不明白为什么。我们做错了什么？"},
    {"id": "T04", "category": "traumatic", "text": "被诊断癌症晚期时，我觉得天塌了。化疗、放疗、手术，三年过去了，我还活着。但每一天都在恐惧中度过，怕复发，怕转移。"},
    {"id": "T05", "category": "traumatic", "text": "火灾中我失去了妻子和孩子。我因为出差躲过一劫，但每次想到如果他们等我回来...这种假设折磨了我十年。"},
    {"id": "T06", "category": "traumatic", "text": "被最好的朋友背叛，骗走了所有积蓄。不仅是钱的问题，是信任的崩塌。现在我不敢相信任何人。"},
    {"id": "T07", "category": "traumatic", "text": "战争年代，我亲眼看着战友在眼前牺牲。子弹从耳边飞过，炮弹在身边爆炸。活下来是幸运，也是负担。"},
    {"id": "T08", "category": "traumatic", "text": "女儿被校园霸凌，患上抑郁症，休学在家。作为父母，看着孩子痛苦却无能为力，是最残忍的事。"},
    {"id": "T09", "category": "traumatic", "text": "下岗后去讨薪，被老板找人打了一顿。肋骨断了两根，医药费自己掏。那个年代，工人没地方说理。"},
    {"id": "T10", "category": "traumatic", "text": "洪水冲走了整个村子。我们一家侥幸逃生，但很多邻居没能跑出来。重建家园用了五年，但心理创伤一辈子都好不了。"},
]

print(f"✅ Loaded {len(TEST_SAMPLES)} test samples")

# ============================================================================
# Mock Scoring Function (replicate v0.4 mock behavior)
# ============================================================================

def mock_llm_score(text: str) -> Dict[str, Any]:
    """Mock LLM scoring — deterministic based on text length and keywords"""
    import hashlib
    
    # Deterministic "randomness" based on text
    h = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    
    base_score = 60 + (h % 35)  # 60-95 range
    
    # Keyword bonuses
    if any(w in text for w in ['爱', '幸福', '快乐', '成功', '值得']):
        base_score += 5
    if any(w in text for w in ['遗憾', '痛苦', '失去', '难过', '害怕']):
        base_score -= 3
    
    return {
        "event_extraction": {
            "events": [{"time": "过去", "description": "主要事件"}],
            "count": 1 + (h % 5)
        },
        "dimension_scores": {
            "event_richness": min(100, base_score + (h % 10)),
            "temporal_coherence": min(100, base_score + (h % 15) - 5),
            "causal_coherence": min(100, base_score + (h % 12) - 3),
            "emotional_depth": min(100, base_score + (h % 18) - 8),
            "identity_integration": min(100, base_score + (h % 14) - 5),
            "information_density": min(100, base_score + (h % 10) - 10)
        },
        "confidence": 0.75 + (h % 20) / 100,
        "reasoning": "Mock evaluation based on text patterns"
    }

def score_narrative_mock(text: str) -> NarrativeScore:
    """Mock version of score_narrative_v0_5"""
    mock_result = mock_llm_score(text)
    
    events = [Event(**e) for e in mock_result["event_extraction"]["events"]]
    
    return NarrativeScore(
        text_length=len(text),
        events=events,
        event_count=mock_result["event_extraction"]["count"],
        dimension_scores=mock_result["dimension_scores"],
        total_score=calculate_total_score(mock_result["dimension_scores"]),
        grade=assign_grade(calculate_total_score(mock_result["dimension_scores"])),
        confidence=mock_result["confidence"],
        reasoning=mock_result["reasoning"],
        is_mock=True
    )

# ============================================================================
# Live Scoring Function (real DASHSCOPE API)
# ============================================================================

def score_narrative_live(text: str, max_retries: int = 3) -> Tuple[Optional[NarrativeScore], Optional[str], float]:
    """Live scoring with DASHSCOPE API"""
    import dashscope
    from dashscope import Generation
    
    dashscope.api_key = DASHSCOPE_API_KEY
    
    prompt = f"""请分析以下中文叙事文本的质量，从六个维度评分（0-100 分）：

文本：{text}

请按以下 JSON 格式返回：
{{
  "events": [{{"time": "时间线索", "description": "事件描述"}}],
  "dimension_scores": {{
    "event_richness": 0-100,
    "temporal_coherence": 0-100,
    "causal_coherence": 0-100,
    "emotional_depth": 0-100,
    "identity_integration": 0-100,
    "information_density": 0-100
  }},
  "confidence": 0.0-1.0,
  "reasoning": "评分理由"
}}

只返回 JSON，不要其他内容。"""
    
    for attempt in range(max_retries):
        try:
            t0 = time.time()
            response = Generation.call(
                model="qwen3.5-plus",
                messages=[{"role": "user", "content": prompt}],
                result_format="message"
            )
            latency = (time.time() - t0) * 1000
            
            if response.status_code == 200:
                import json as json_mod
                result_text = response.output.choices[0].message.content
                result = json_mod.loads(result_text)
                
                events = [Event(**e) for e in result.get("events", [])]
                dim_scores = result.get("dimension_scores", {})
                
                total = calculate_total_score(dim_scores)
                
                return NarrativeScore(
                    text_length=len(text),
                    events=events,
                    event_count=len(events),
                    dimension_scores=dim_scores,
                    total_score=total,
                    grade=assign_grade(total),
                    confidence=result.get("confidence", 0.5),
                    reasoning=result.get("reasoning", ""),
                    is_mock=False
                ), None, latency
            else:
                error_msg = f"API error: {response.status_code} - {response.message}"
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return None, error_msg, latency
                
        except Exception as e:
            error_msg = f"Exception: {traceback.format_exc()}"
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None, error_msg, (time.time() - t0) * 1000 if 't0' in dir() else 0
    
    return None, "Max retries exceeded", 0

# ============================================================================
# Experiment Execution
# ============================================================================

@dataclass
class ExperimentResult:
    sample_id: str
    category: str
    mock_score: Optional[float]
    live_score: Optional[float]
    score_delta: Optional[float]
    mock_grade: Optional[str]
    live_grade: Optional[str]
    mock_latency_ms: float
    live_latency_ms: float
    mock_confidence: float
    live_confidence: float
    success: bool
    error: Optional[str] = None


def run_experiment() -> List[ExperimentResult]:
    """Run the full experiment"""
    results = []
    
    print(f"\n{'='*70}")
    print(f"v0.7 Live Validation Experiment")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Samples: {len(TEST_SAMPLES)}")
    print(f"{'='*70}\n")
    
    total_mock_latency = 0
    total_live_latency = 0
    successes = 0
    failures = 0
    
    for i, sample in enumerate(TEST_SAMPLES, 1):
        print(f"[{i}/{len(TEST_SAMPLES)}] {sample['id']} ({sample['category']})...", end=" ")
        
        # Mock scoring
        t0 = time.time()
        try:
            mock_result = score_narrative_mock(sample["text"])
            mock_latency = (time.time() - t0) * 1000
            mock_score = mock_result.total_score
            mock_grade = mock_result.grade
            mock_confidence = mock_result.confidence
        except Exception as e:
            mock_score = None
            mock_grade = None
            mock_confidence = 0
            mock_latency = 0
        
        # Live scoring
        live_result, error, live_latency = score_narrative_live(sample["text"])
        
        if live_result:
            live_score = live_result.total_score
            live_grade = live_result.grade
            live_confidence = live_result.confidence
            score_delta = live_score - mock_score if mock_score else None
            success = True
            successes += 1
        else:
            live_score = None
            live_grade = None
            live_confidence = 0
            score_delta = None
            success = False
            failures += 1
        
        total_mock_latency += mock_latency
        total_live_latency += live_latency
        
        result = ExperimentResult(
            sample_id=sample["id"],
            category=sample["category"],
            mock_score=mock_score,
            live_score=live_score,
            score_delta=score_delta,
            mock_grade=mock_grade,
            live_grade=live_grade,
            mock_latency_ms=mock_latency,
            live_latency_ms=live_latency,
            mock_confidence=mock_confidence,
            live_confidence=live_confidence,
            success=success,
            error=error
        )
        results.append(result)
        
        status = "✅" if success else "❌"
        delta_str = f"{score_delta:+.1f}" if score_delta else "N/A"
        mock_str = f"{mock_score:.1f}({mock_grade})" if mock_score else "N/A"
        live_str = f"{live_score:.1f}({live_grade})" if live_score else "N/A"
        print(f"{status} Mock={mock_str} Live={live_str} Δ={delta_str} ({live_latency:.0f}ms)")
    
    # Summary statistics
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    successful_results = [r for r in results if r.success]
    
    if successful_results:
        deltas = [r.score_delta for r in successful_results if r.score_delta is not None]
        avg_delta = sum(deltas) / len(deltas) if deltas else 0
        std_delta = (sum((d - avg_delta) ** 2 for d in deltas) / len(deltas)) ** 0.5 if len(deltas) > 1 else 0
        
        print(f"Success rate: {successes}/{len(TEST_SAMPLES)} ({100*successes/len(TEST_SAMPLES):.1f}%)")
        print(f"Avg score delta (live - mock): {avg_delta:+.2f} ± {std_delta:.2f}")
        print(f"Avg mock latency: {total_mock_latency/len(TEST_SAMPLES):.1f}ms")
        print(f"Avg live latency: {total_live_latency/len(TEST_SAMPLES):.1f}ms")
        print(f"Latency overhead: {total_live_latency/total_mock_latency:.1f}x" if total_mock_latency > 0 else "N/A")
        
        # By category
        print(f"\nBy category:")
        for cat in ["positive", "negative", "neutral", "reflective", "traumatic"]:
            cat_results = [r for r in successful_results if r.category == cat]
            if cat_results:
                cat_deltas = [r.score_delta for r in cat_results if r.score_delta is not None]
                avg_cat_delta = sum(cat_deltas) / len(cat_deltas) if cat_deltas else 0
                print(f"  {cat}: n={len(cat_results)}, avg Δ={avg_cat_delta:+.2f}")
    else:
        print("❌ No successful live evaluations")
    
    return results


def save_results(results: List[ExperimentResult], output_dir: str = "results"):
    """Save results to JSON and Markdown"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_path = os.path.join(output_dir, f"live_validation_{timestamp}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, ensure_ascii=False, indent=2)
    print(f"\n📄 JSON saved: {json_path}")
    
    # Markdown report
    md_path = os.path.join(output_dir, f"live_validation_{timestamp}.md")
    successful = [r for r in results if r.success]
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# v0.7 Live Validation Report\n\n")
        f.write(f"**Date**: {datetime.now().isoformat()}\n")
        f.write(f"**Samples**: {len(results)}\n")
        f.write(f"**Success Rate**: {len(successful)}/{len(results)} ({100*len(successful)/len(results):.1f}%)\n\n")
        
        if successful:
            deltas = [r.score_delta for r in successful if r.score_delta is not None]
            avg_delta = sum(deltas) / len(deltas) if deltas else 0
            
            f.write("## Key Metrics\n\n")
            f.write(f"| Metric | Value |\n")
            f.write(f"|--------|-------|\n")
            f.write(f"| Avg Score Delta (live - mock) | {avg_delta:+.2f} |\n")
            f.write(f"| Avg Live Latency | {sum(r.live_latency_ms for r in successful)/len(successful):.1f}ms |\n")
            f.write(f"| Avg Mock Latency | {sum(r.mock_latency_ms for r in successful)/len(successful):.1f}ms |\n\n")
            
            f.write("## By Category\n\n")
            f.write("| Category | N | Avg Δ | Success Rate |\n")
            f.write("|----------|---|-------|-------------|\n")
            for cat in ["positive", "negative", "neutral", "reflective", "traumatic"]:
                cat_results = [r for r in results if r.category == cat]
                cat_successful = [r for r in cat_results if r.success]
                cat_deltas = [r.score_delta for r in cat_successful if r.score_delta is not None]
                avg_cat = sum(cat_deltas) / len(cat_deltas) if cat_deltas else 0
                f.write(f"| {cat} | {len(cat_results)} | {avg_cat:+.2f} | {len(cat_successful)}/{len(cat_results)} |\n")
            
            f.write("\n## Sample-Level Results\n\n")
            f.write("| ID | Category | Mock | Live | Δ | Grade | Latency |\n")
            f.write("|-----|----------|------|------|---|-------|--------|\n")
            for r in successful[:20]:  # First 20 samples
                delta_str = f"{r.score_delta:+.1f}" if r.score_delta else "N/A"
                f.write(f"| {r.sample_id} | {r.category} | {r.mock_score:.1f} | {r.live_score:.1f} | {delta_str} | {r.live_grade} | {r.live_latency_ms:.0f}ms |\n")
            
            if len(successful) > 20:
                f.write(f"\n*... and {len(successful) - 20} more samples*\n")
        
        if failures := [r for r in results if not r.success]:
            f.write("\n## Failures\n\n")
            for r in failures[:10]:
                f.write(f"- **{r.sample_id}**: {r.error}\n")
            if len(failures) > 10:
                f.write(f"\n*... and {len(failures) - 10} more failures*\n")
    
    print(f"📄 Markdown saved: {md_path}")


if __name__ == "__main__":
    results = run_experiment()
    save_results(results)
    print("\n✅ Experiment complete")
