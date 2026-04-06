#!/usr/bin/env python3
"""
VSNC/L0 扩展鲁棒性测试套件 (2026-03-27)
========================================

在原有 131 用例基础上新增的测试：
  D. 新对抗模式 — 基于 v0.5 漏洞的深度攻击
  E. 跨模块一致性 — 多组件协同的边界情况
  F. 性能压力测试 — 高负载下的稳定性
  G. 语义完整性 — 输入输出语义合理性

被测模块：
  1. emotional_arousal_detector.py
  2. narrative_scorer_v0.4.py
  3. l0_quality_system.py
  4. arbitrator_agent.py

输出：JSON report + human-readable summary
"""

import json
import sys
import os
import time
import traceback
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from emotional_arousal_detector import EmotionalArousalDetector, get_ideal_central_ratio, get_guidance_strategy
import importlib.util as _ilu

_spec = _ilu.spec_from_file_location("narrative_scorer", os.path.join(os.path.dirname(os.path.abspath(__file__)), "narrative_scorer_v0.4.py"))
_ns = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_ns)

Event = _ns.Event
score_narrative_v0_5 = _ns.score_narrative_v0_5
assign_grade = _ns.assign_grade


@dataclass
class TestResult:
    id: str
    category: str
    subcategory: str
    description: str
    passed: bool
    details: str = ""
    exception: Optional[str] = None
    latency_ms: float = 0.0


class ExtendedRobustnessTestSuite:
    def __init__(self):
        self.results: List[TestResult] = []
        self.detector = EmotionalArousalDetector()

    def _record(self, result: TestResult):
        self.results.append(result)

    def _safe_run(self, fn, *args, **kwargs):
        t0 = time.time()
        try:
            val = fn(*args, **kwargs)
            return val, None, (time.time() - t0) * 1000
        except Exception as e:
            return None, traceback.format_exc(), (time.time() - t0) * 1000

    # ====================================================================
    # D. 新对抗模式 (New Adversarial Patterns)
    # ====================================================================

    def test_adversarial_emotion_gaming_v2(self):
        """D-01: 情感词堆砌 v2 — 测试多样性惩罚是否生效"""
        # 同一情感词重复 10 次
        text_repeat = "开心 " * 10 + "那是我十岁那年的夏天。"
        # 不同情感词各 1 次
        text_diverse = "开心 快乐 喜悦 兴奋 激动 幸福 满足 欣慰 愉悦 欢快 那是我十岁那年的夏天。"

        result1, exc1, lat1 = self._safe_run(self.detector.detect, text_repeat)
        result2, exc2, lat2 = self._safe_run(self.detector.detect, text_diverse)

        # 期望：重复文本的唤醒度应显著低于多样化文本
        passed = (exc1 is None and exc2 is None and
                  result1 is not None and result2 is not None and
                  result1.score <= result2.score)

        self._record(TestResult(
            id="D-01-1", category="adversarial_new", subcategory="emotion_gaming",
            description="情感词重复 vs 多样化",
            passed=passed,
            details=f"repeat={result1.score:.2f}, diverse={result2.score:.2f}",
            exception=exc1 or exc2,
            latency_ms=lat1 + lat2,
        ))

    def test_adversarial_identity_stuffing(self):
        """D-02: 身份词堆砌攻击"""
        # 堆砌所有身份词
        text = "我 自己 本人 我个人 作为我 我的经历 我的人生 我的记忆 我的故事 我的心里 " * 5
        events = [Event(description="event", event_type="central") for _ in range(10)]

        result, exc, lat = self._safe_run(score_narrative_v0_5, text, events)

        # 期望：身份词堆砌不应获得过高的身份整合分
        passed = (exc is None and result is not None and
                  result.identity_integration <= 80)

        self._record(TestResult(
            id="D-02-1", category="adversarial_new", subcategory="identity_stuffing",
            description="身份词堆砌攻击",
            passed=passed,
            details=f"identity_score={result.identity_integration if result else 'ERR'}",
            exception=exc,
            latency_ms=lat,
        ))

    def test_adversarial_event_inflation(self):
        """D-03: 事件数量膨胀攻击"""
        # 用极短文本构造大量事件
        text = "事。" * 200
        events = [Event(description="e", event_type="central") for _ in range(200)]

        result, exc, lat = self._safe_run(score_narrative_v0_5, text, events)

        # 期望：事件数量多但质量低不应获得高分
        passed = (exc is None and result is not None and
                  result.total_score <= 70)  # 不应超过 B 级

        self._record(TestResult(
            id="D-03-1", category="adversarial_new", subcategory="event_inflation",
            description="事件数量膨胀攻击",
            passed=passed,
            details=f"total={result.total_score if result else 'ERR'}, events={len(events)}",
            exception=exc,
            latency_ms=lat,
        ))

    def test_adversarial_mixed_attack(self):
        """D-04: 混合攻击 — 情感词 + 身份词 + 事件堆砌"""
        text = ("我 开心 我 快乐 我 兴奋 " * 10 +
                "那是我十岁那年的夏天。" * 5)
        events = [Event(description="event", event_type="central") for _ in range(50)]

        result, exc, lat = self._safe_run(score_narrative_v0_5, text, events)

        # 期望：混合攻击不应获得 S 级
        passed = (exc is None and result is not None and
                  result.grade != "S")

        self._record(TestResult(
            id="D-04-1", category="adversarial_new", subcategory="mixed_attack",
            description="混合关键词堆砌攻击",
            passed=passed,
            details=f"total={result.total_score if result else 'ERR'}, grade={result.grade if result else 'ERR'}",
            exception=exc,
            latency_ms=lat,
        ))

    # ====================================================================
    # E. 跨模块一致性 (Cross-Module Consistency)
    # ====================================================================

    def test_consistency_arousal_grade(self):
        """E-01: 唤醒度与等级的语义一致性"""
        # 高唤醒应对应情感深度分较高
        high_arousal_text = "我无比激动！眼泪止不住地流！心跳加速！这是我人生中最喜悦的时刻！"
        low_arousal_text = "那是一个普通的下午。我坐在院子里。阳光很好。"

        result1, exc1, lat1 = self._safe_run(self.detector.detect, high_arousal_text)
        result2, exc2, lat2 = self._safe_run(self.detector.detect, low_arousal_text)

        events1 = [Event(description="high arousal event", event_type="central")]
        events2 = [Event(description="low arousal event", event_type="central")]

        score1, exc3, lat3 = self._safe_run(score_narrative_v0_5, high_arousal_text, events1)
        score2, exc4, lat4 = self._safe_run(score_narrative_v0_5, low_arousal_text, events2)

        # 期望：高唤醒文本的情感深度分应高于低唤醒文本
        passed = (exc1 is None and exc2 is None and exc3 is None and exc4 is None and
                  result1 is not None and result2 is not None and
                  score1 is not None and score2 is not None and
                  score1.emotional_depth > score2.emotional_depth)

        self._record(TestResult(
            id="E-01-1", category="consistency", subcategory="arousal_emotion",
            description="唤醒度与情感深度分一致性",
            passed=passed,
            details=f"high_arousal={result1.score:.2f}(emotion={score1.emotional_depth}), "
                    f"low_arousal={result2.score:.2f}(emotion={score2.emotional_depth})",
            exception=exc1 or exc2 or exc3 or exc4,
            latency_ms=lat1 + lat2 + lat3 + lat4,
        ))

    def test_consistency_empty_input(self):
        """E-02: 空输入在各模块的一致性降级"""
        empty_text = ""
        events = []

        arousal, exc1, lat1 = self._safe_run(self.detector.detect, empty_text)
        score, exc2, lat2 = self._safe_run(score_narrative_v0_5, empty_text, events)
        grade, exc3, lat3 = self._safe_run(assign_grade, score.total_score if score else 0)

        # 期望：空输入在所有模块都应返回最低档
        passed = (exc1 is None and exc2 is None and exc3 is None and
                  arousal is not None and arousal.score <= 1.5 and
                  score is not None and score.total_score <= 10 and
                  grade == "D")

        self._record(TestResult(
            id="E-02-1", category="consistency", subcategory="empty_degradation",
            description="空输入一致性降级",
            passed=passed,
            details=f"arousal={arousal.score if arousal else 'ERR'}, "
                    f"total={score.total_score if score else 'ERR'}, grade={grade}",
            exception=exc1 or exc2 or exc3,
            latency_ms=lat1 + lat2 + lat3,
        ))

    def test_consistency_boundary_grades(self):
        """E-03: 等级边界一致性 (59/60/69/70/79/80/89/90)"""
        boundary_scores = [59, 60, 69, 70, 79, 80, 89, 90]
        expected_grades = ["D", "C", "C", "B", "B", "A", "A", "S"]

        all_passed = True
        details = []
        for score_val, expected_grade in zip(boundary_scores, expected_grades):
            grade, exc, lat = self._safe_run(assign_grade, score_val)
            if grade != expected_grade:
                all_passed = False
                details.append(f"{score_val}→{grade}(expected {expected_grade})")
            else:
                details.append(f"{score_val}→{grade}✓")

        self._record(TestResult(
            id="E-03-1", category="consistency", subcategory="grade_boundaries",
            description="等级边界一致性 (59/60/69/70/79/80/89/90)",
            passed=all_passed,
            details="; ".join(details),
            exception=None,
            latency_ms=0,
        ))

    # ====================================================================
    # F. 性能压力测试 (Performance Stress)
    # ====================================================================

    def test_performance_batch_processing(self):
        """F-01: 批量处理性能"""
        texts = [
            "那是我十岁那年的夏天，在老家院子里。阳光透过葡萄架洒下来。" * (i + 1)
            for i in range(50)
        ]
        events = [Event(description="event", event_type="central") for _ in range(10)]

        t0 = time.time()
        results = []
        for text in texts:
            result, exc, _ = self._safe_run(score_narrative_v0_5, text, events)
            if exc:
                results.append(None)
            else:
                results.append(result)
        total_time = (time.time() - t0) * 1000

        # 期望：50 条处理应在 5 秒内完成
        passed = (all(r is not None for r in results) and total_time < 5000)

        self._record(TestResult(
            id="F-01-1", category="performance", subcategory="batch",
            description="批量处理 50 条",
            passed=passed,
            details=f"total={total_time:.0f}ms, avg={total_time/50:.0f}ms/item",
            latency_ms=total_time,
        ))

    def test_performance_long_text(self):
        """F-02: 超长文本处理性能"""
        text = "那是我十岁那年的夏天。" * 500  # ~10000 字
        events = [Event(description="event", event_type="central") for _ in range(50)]

        t0 = time.time()
        result, exc, lat = self._safe_run(score_narrative_v0_5, text, events)
        total_time = (time.time() - t0) * 1000

        # 期望：10000 字应在 500ms 内完成
        passed = (exc is None and result is not None and total_time < 500)

        self._record(TestResult(
            id="F-02-1", category="performance", subcategory="long_text",
            description="超长文本处理 (10000 字)",
            passed=passed,
            details=f"time={total_time:.0f}ms, len={len(text)}",
            exception=exc,
            latency_ms=lat,
        ))

    # ====================================================================
    # G. 语义完整性 (Semantic Integrity)
    # ====================================================================

    def test_semantic_arousal_levels(self):
        """G-01: 唤醒度等级语义合理性"""
        cases = [
            ("今天天气不错。", "极低", 1.0, 2.0),
            ("我感到有些开心。", "低", 2.0, 3.0),
            ("我非常高兴！真的很棒！", "中", 3.0, 4.0),
            ("我激动得跳起来了！太震撼了！！！", "高", 4.0, 5.0),
        ]

        all_passed = True
        details = []
        for text, expected_level, min_score, max_score in cases:
            result, exc, _ = self._safe_run(self.detector.detect, text)
            if exc or result is None:
                all_passed = False
                details.append(f"{expected_level}: ERR")
            elif not (min_score <= result.score <= max_score):
                all_passed = False
                details.append(f"{expected_level}: {result.score:.2f}(expected {min_score}-{max_score})")
            else:
                details.append(f"{expected_level}: {result.score:.2f}✓")

        self._record(TestResult(
            id="G-01-1", category="semantic", subcategory="arousal_levels",
            description="唤醒度等级语义合理性",
            passed=all_passed,
            details="; ".join(details),
            latency_ms=0,
        ))

    def test_semantic_grade_distribution(self):
        """G-02: 等级分布合理性"""
        # 构造不同质量的文本
        cases = [
            ("。", "D", 0, 60),  # 极低质量
            ("我记得一件事。", "D", 0, 60),  # 低质量
            ("那是我十岁那年的夏天，在老家院子里。阳光透过葡萄架洒下来，在地上形成斑驳的光影。奶奶坐在旁边择菜，嘴里哼着不知名的小曲。", "B", 60, 80),  # 中等质量
        ]

        all_passed = True
        details = []
        for text, expected_grade, min_score, max_score in cases:
            events = [Event(description="event", event_type="central")]
            result, exc, _ = self._safe_run(score_narrative_v0_5, text, events)
            if exc or result is None:
                all_passed = False
                details.append(f"{expected_grade}: ERR")
            elif not (min_score <= result.total_score <= max_score):
                all_passed = False
                details.append(f"{expected_grade}: {result.total_score}(expected {min_score}-{max_score})")
            else:
                details.append(f"{expected_grade}: {result.total_score}✓")

        self._record(TestResult(
            id="G-02-1", category="semantic", subcategory="grade_distribution",
            description="等级分布合理性",
            passed=all_passed,
            details="; ".join(details),
            latency_ms=0,
        ))

    # ====================================================================
    # 运行所有测试
    # ====================================================================

    def run_all(self):
        """执行所有扩展测试"""
        print("=" * 70)
        print("   VSNC/L0 扩展鲁棒性测试报告 (2026-03-27)")
        print("=" * 70)
        print()

        # D. 新对抗模式
        self.test_adversarial_emotion_gaming_v2()
        self.test_adversarial_identity_stuffing()
        self.test_adversarial_event_inflation()
        self.test_adversarial_mixed_attack()

        # E. 跨模块一致性
        self.test_consistency_arousal_grade()
        self.test_consistency_empty_input()
        self.test_consistency_boundary_grades()

        # F. 性能压力测试
        self.test_performance_batch_processing()
        self.test_performance_long_text()

        # G. 语义完整性
        self.test_semantic_arousal_levels()
        self.test_semantic_grade_distribution()

        # 汇总
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        print(f"总计：{total} 测试 | ✅ {passed} 通过 | ❌ {failed} 失败 | 通过率 {passed/total*100:.1f}%")
        print()

        # 按类别汇总
        categories = {}
        for r in self.results:
            if r.category not in categories:
                categories[r.category] = {"passed": 0, "total": 0}
            categories[r.category]["total"] += 1
            if r.passed:
                categories[r.category]["passed"] += 1

        for cat, stats in sorted(categories.items()):
            print(f"  {'✅' if stats['passed'] == stats['total'] else '⚠️'}  {cat:20s}: {stats['passed']}/{stats['total']} ({stats['passed']/stats['total']*100:.0f}%)")

        print()

        # 失败详情
        failed_results = [r for r in self.results if not r.passed]
        if failed_results:
            print("❌ 失败用例详情:")
            for r in failed_results:
                print(f"  - {r.id}: {r.description}")
                print(f"    详情：{r.details}")
            print()

        # 保存报告
        report = {
            "date": "2026-03-27",
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total * 100,
            "by_category": categories,
            "results": [
                {
                    "id": r.id,
                    "category": r.category,
                    "subcategory": r.subcategory,
                    "description": r.description,
                    "passed": r.passed,
                    "details": r.details,
                    "latency_ms": r.latency_ms,
                }
                for r in self.results
            ],
        }

        report_path = "/home/node/.openclaw/workspace-hulk/pipeline/robustness_report_extended.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📄 完整报告已保存：{report_path}")
        print("=" * 70)

        return report


if __name__ == "__main__":
    suite = ExtendedRobustnessTestSuite()
    suite.run_all()
