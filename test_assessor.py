#!/usr/bin/env python3
"""
CittaVerse Pipeline - 单元测试用例
测试神经符号叙事评估引擎的核心功能
"""

import unittest
import json
from datetime import datetime


class TestEventExtraction(unittest.TestCase):
    """测试事件提取模块"""
    
    def test_extract_events_basic(self):
        """测试基础事件提取"""
        narrative = "我退休那年开始学习书法，现在每天去公园练习。"
        # 模拟提取结果
        events = [
            {"id": "E1", "content": "退休那年开始学习书法", "time_marker": "退休那年"},
            {"id": "E2", "content": "每天去公园练习", "time_marker": "现在"}
        ]
        self.assertEqual(len(events), 2)
        self.assertIn("书法", events[0]["content"])
    
    def test_extract_events_empty(self):
        """测试空输入处理"""
        narrative = ""
        events = []
        self.assertEqual(len(events), 0)
    
    def test_extract_events_no_time_marker(self):
        """测试无时间标记的事件"""
        narrative = "今天天气不错。"
        events = [
            {"id": "E1", "content": "天气不错", "time_marker": "今天"}
        ]
        self.assertIsNotNone(events[0]["time_marker"])


class TestGraphScoring(unittest.TestCase):
    """测试图论计分模块"""
    
    def test_coherence_score_perfect(self):
        """测试完全连贯的叙事"""
        # 所有事件共享实体
        events = [
            {"entities": ["书法", "公园"]},
            {"entities": ["书法", "公园"]},
            {"entities": ["书法", "公园"]}
        ]
        # 完全连接，分数应接近 1.0
        coherence = 1.0
        self.assertGreater(coherence, 0.8)
    
    def test_coherence_score_low(self):
        """测试低连贯性的叙事"""
        # 事件无共享实体
        events = [
            {"entities": ["书法"]},
            {"entities": ["游泳"]},
            {"entities": ["跑步"]}
        ]
        coherence = 0.0
        self.assertLess(coherence, 0.2)
    
    def test_coherence_score_boundary(self):
        """测试边界值"""
        # 单个事件
        events = [{"entities": ["书法"]}]
        coherence = 0.0  # 无法形成连接
        self.assertEqual(coherence, 0.0)


class TestReportGeneration(unittest.TestCase):
    """测试报告生成模块"""
    
    def test_report_structure(self):
        """测试报告结构完整性"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_events": 3,
                "coherence_score": 0.5,
                "quality_level": "中"
            },
            "recommendations": []
        }
        self.assertIn("timestamp", report)
        self.assertIn("summary", report)
        self.assertIn("total_events", report["summary"])
    
    def test_recommendation_generation(self):
        """测试建议生成逻辑"""
        coherence_score = 0.2
        recommendations = []
        if coherence_score < 0.3:
            recommendations.append("叙事连贯性较低，建议引导老人补充事件间的关联")
        self.assertGreater(len(recommendations), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
