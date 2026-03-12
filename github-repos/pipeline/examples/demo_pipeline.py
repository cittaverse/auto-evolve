#!/usr/bin/env python3
"""
CittaVerse Pipeline - 叙事评估 Demo
简易示例：演示神经符号架构的核心流程

用法：python demo_pipeline.py
"""

import json
from datetime import datetime

# ============================================================
# 神经层：LLM 事件提取（模拟）
# ============================================================

def extract_events(narrative_text):
    """
    使用 LLM 从叙事文本中提取事件单元
    
    Args:
        narrative_text: 老年人口述文本
        
    Returns:
        list[dict]: 事件列表，每个事件包含 {id, content, time_marker, entities}
    """
    # 模拟 LLM 提取结果（实际应调用 API）
    events = [
        {
            "id": "E1",
            "content": "退休后开始学习书法",
            "time_marker": "退休那年",
            "entities": ["书法", "退休"],
            "emotion": "positive"
        },
        {
            "id": "E2", 
            "content": "每天早晨去公园练习",
            "time_marker": "现在",
            "entities": ["公园", "早晨"],
            "emotion": "neutral"
        },
        {
            "id": "E3",
            "content": "认识了同样喜欢书法的老张",
            "time_marker": "三个月前",
            "entities": ["老张", "书法"],
            "emotion": "positive"
        }
    ]
    return events


# ============================================================
# 符号层：图论结构计分
# ============================================================

def build_event_graph(events):
    """
    构建事件连接图，计算叙事连贯性
    
    Args:
        events: 事件列表
        
    Returns:
        dict: 图结构 + 连贯性分数
    """
    # 构建邻接矩阵（基于实体重叠）
    n = len(events)
    adjacency = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(i + 1, n):
            # 计算实体重叠度
            shared = set(events[i]["entities"]) & set(events[j]["entities"])
            if shared:
                adjacency[i][j] = adjacency[j][i] = len(shared)
    
    # 计算连贯性分数
    total_connections = sum(sum(row) for row in adjacency)
    max_possible = n * (n - 1)  # 完全图的边数
    coherence_score = total_connections / max_possible if max_possible > 0 else 0
    
    return {
        "adjacency": adjacency,
        "coherence_score": round(coherence_score, 3),
        "event_count": n
    }


# ============================================================
# 评估报告生成
# ============================================================

def generate_report(events, graph):
    """生成评估报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_events": graph["event_count"],
            "coherence_score": graph["coherence_score"],
            "quality_level": "高" if graph["coherence_score"] > 0.5 else "中" if graph["coherence_score"] > 0.2 else "低"
        },
        "events": events,
        "recommendations": []
    }
    
    # 生成建议
    if graph["coherence_score"] < 0.3:
        report["recommendations"].append("叙事连贯性较低，建议引导老人补充事件间的关联")
    if graph["event_count"] < 3:
        report["recommendations"].append("事件数量较少，建议继续深入访谈")
    
    return report


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print("CittaVerse Pipeline - 叙事评估 Demo")
    print("=" * 60)
    print()
    
    # 模拟输入
    sample_narrative = """
    我退休那年开始学习书法，觉得这是个好机会。
    现在每天早晨都去公园练习，风雨无阻。
    三个月前认识了同样喜欢书法的老张，我们经常一起交流。
    """
    
    print("📖 输入叙事:")
    print(sample_narrative)
    print()
    
    # 神经层：事件提取
    print("🧠 神经层：事件提取中...")
    events = extract_events(sample_narrative)
    print(f"   提取到 {len(events)} 个事件")
    print()
    
    # 符号层：图论计分
    print("📊 符号层：构建事件图...")
    graph = build_event_graph(events)
    print(f"   连贯性分数：{graph['coherence_score']}")
    print()
    
    # 生成报告
    print("📝 生成评估报告...")
    report = generate_report(events, graph)
    print(f"   质量等级：{report['summary']['quality_level']}")
    if report["recommendations"]:
        print("   建议:")
        for rec in report["recommendations"]:
            print(f"   - {rec}")
    print()
    
    print("=" * 60)
    print("✅ Demo 完成")
    print("=" * 60)
    
    # 输出 JSON 报告
    print("\n📄 JSON 报告:")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
