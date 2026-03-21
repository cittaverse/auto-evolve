#!/usr/bin/env python3
"""
ClawHub 500 精选计划 - 数据处理脚本
从 awesome-openclaw-skills 提取技能数据，按 5 Patterns 分类标注
"""

import re
import json
from pathlib import Path

# 配置
CATEGORIES_DIR = Path("/tmp/clawhub-categories")
OUTPUT_DIR = Path("/home/node/.openclaw/workspace-hulk/data/clawhub-500")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 扩大配额（从 500 调整到 600，确保覆盖）
QUOTAS = {
    "Tool Wrapper": 120,  # 从 150 降至 120（实际只有 104 个）
    "Generator": 120,
    "Reviewer": 120,
    "Inversion": 120,
    "Pipeline": 120,
}

# 5 Patterns 定义
PATTERNS = {
    "Tool Wrapper": ["API", "integration", "connect", "wrapper", "client", "SDK", "plugin"],
    "Generator": ["generate", "create", "template", "report", "document", "presentation", "write"],
    "Reviewer": ["review", "audit", "check", "scan", "test", "security", "lint"],
    "Inversion": ["interview", "ask", "consult", "guide", "planner", "coach", "advisor"],
    "Pipeline": ["workflow", "pipeline", "orchestrate", "automation", "multi-step", "chain"],
}

def parse_category_file(filepath):
    """解析分类文件，提取技能列表"""
    skills = []
    with open(filepath, 'r') as f:
        content = f.read()
    
    # 匹配技能行：- [skill-name](url) - description
    pattern = r'^- \[([^\]]+)\]\(([^)]+)\) - (.+)$'
    for line in content.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            name, url, description = match.groups()
            skills.append({
                "name": name,
                "url": url,
                "description": description,
                "source_file": filepath.name,
            })
    return skills

def classify_skill(description):
    """按 5 Patterns 分类技能"""
    desc_lower = description.lower()
    matches = {}
    for pattern, keywords in PATTERNS.items():
        score = sum(1 for kw in keywords if kw in desc_lower)
        if score > 0:
            matches[pattern] = score
    
    if matches:
        return max(matches, key=matches.get)
    return "Unclassified"

def main():
    print("=" * 60)
    print("ClawHub 500 精选计划 - 数据处理")
    print("=" * 60)
    
    # 收集所有技能
    all_skills = []
    for cat_file in CATEGORIES_DIR.glob("*.md"):
        print(f"\n处理分类：{cat_file.name}")
        skills = parse_category_file(cat_file)
        print(f"  提取技能：{len(skills)} 个")
        for skill in skills:
            skill["pattern"] = classify_skill(skill["description"])
        all_skills.extend(skills)
    
    print(f"\n总计：{len(all_skills)} 个技能")
    
    # 按模式统计
    pattern_stats = {}
    for skill in all_skills:
        pattern = skill["pattern"]
        pattern_stats[pattern] = pattern_stats.get(pattern, 0) + 1
    
    print("\n按模式分布:")
    for pattern, count in sorted(pattern_stats.items(), key=lambda x: -x[1]):
        print(f"  {pattern}: {count}")
    
    # 保存原始数据
    raw_output = OUTPUT_DIR / "raw-skills.json"
    with open(raw_output, 'w') as f:
        json.dump(all_skills, f, indent=2, ensure_ascii=False)
    print(f"\n已保存：{raw_output}")
    
    # 精选 600（按模式配额，从 Unclassified 补充）
    selected = []
    for pattern, quota in QUOTAS.items():
        pattern_skills = [s for s in all_skills if s["pattern"] == pattern]
        # 按描述长度排序（长的通常更详细）
        pattern_skills.sort(key=lambda x: -len(x["description"]))
        selected.extend(pattern_skills[:quota])
        print(f"\n{pattern}: 精选 {len(pattern_skills[:quota])}/{quota}")
    
    # 从 Unclassified 补充 Tool Wrapper 缺口
    unclassified = [s for s in all_skills if s["pattern"] == "Unclassified"]
    unclassified.sort(key=lambda x: -len(x["description"]))
    tool_wrapper_need = QUOTAS["Tool Wrapper"] - len([s for s in selected if s["pattern"] == "Tool Wrapper"])
    if tool_wrapper_need > 0:
        print(f"\n从 Unclassified 补充 Tool Wrapper: {tool_wrapper_need} 个")
        for skill in unclassified[:tool_wrapper_need]:
            skill["pattern"] = "Tool Wrapper (supplement)"
        selected.extend(unclassified[:tool_wrapper_need])
    
    # 保存精选结果
    selected_output = OUTPUT_DIR / "top-500.json"
    with open(selected_output, 'w') as f:
        json.dump(selected, f, indent=2, ensure_ascii=False)
    print(f"\n已保存精选：{selected_output} ({len(selected)} 个技能)")
    
    # 生成统计报告
    stats = {
        "total_skills": len(all_skills),
        "selected_skills": len(selected),
        "pattern_distribution": pattern_stats,
        "selected_distribution": {
            pattern: sum(1 for s in selected if s["pattern"] == pattern)
            for pattern in PATTERNS.keys()
        },
    }
    
    stats_output = OUTPUT_DIR / "stats.json"
    with open(stats_output, 'w') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"已保存统计：{stats_output}")
    
    print("\n" + "=" * 60)
    print("Phase 2 完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
