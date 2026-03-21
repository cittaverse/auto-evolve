#!/usr/bin/env python3
"""
ClawHub 50 标杆技能选择与优化脚本
从 600 个精选中选择 50 个标杆，进行深度优化
"""

import json
from pathlib import Path

# 配置
INPUT_FILE = Path("/home/node/.openclaw/workspace-hulk/data/clawhub-500/top-500.json")
OUTPUT_DIR = Path("/home/node/.openclaw/workspace-hulk/data/clawhub-500/benchmarks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 标杆选择标准
BENCHMARK_CRITERIA = {
    "高下载量": ["capability-evolver", "gog", "self-improving-agent", "agent-browser", "wacli"],
    "模式代表": {
        "Tool Wrapper": ["gog", "composio", "playwright-cli", "firecrawl", "exa"],
        "Generator": ["2slides-skills", "ai-ppt-generator", "report-generator"],
        "Reviewer": ["skill-vetter", "agent-audit", "ai-shield-audit", "security-scan"],
        "Inversion": ["adhd-founder-planner", "agent-estimation", "health-assistant"],
        "Pipeline": ["agent-mode-upgrades", "n8n-workflow-automation", "openclaw-weekly"],
    },
    "安全相关": ["skill-vetter", "agent-guardrails", "ai-sentinel", "secureclaw"],
    "创新设计": ["capability-evolver", "ontology", "agent-os", "memory-lancedb"],
}

def load_skills():
    """加载精选技能"""
    with open(INPUT_FILE, 'r') as f:
        return json.load(f)

def select_benchmarks(skills):
    """选择 50 个标杆技能"""
    benchmarks = []
    skill_map = {s["name"].lower().replace("-", "").replace("_", ""): s for s in skills}
    
    # 1. 高下载量优先（10 个）
    for name in BENCHMARK_CRITERIA["高下载量"]:
        for key, skill in skill_map.items():
            if name.lower().replace("-", "") in key:
                if skill not in benchmarks:
                    skill["benchmark_reason"] = "高下载量"
                    benchmarks.append(skill)
                break
        if len(benchmarks) >= 10:
            break
    
    # 2. 模式代表（25 个，每模式 5 个）
    for pattern, names in BENCHMARK_CRITERIA["模式代表"].items():
        count = 0
        for name in names:
            for key, skill in skill_map.items():
                if name.lower().replace("-", "") in key and skill.get("pattern") == pattern:
                    if skill not in benchmarks:
                        skill["benchmark_reason"] = f"模式代表 ({pattern})"
                        benchmarks.append(skill)
                        count += 1
                    break
            if count >= 5:
                break
    
    # 3. 安全相关（5 个）
    for name in BENCHMARK_CRITERIA["安全相关"]:
        for key, skill in skill_map.items():
            if name.lower().replace("-", "") in key:
                if skill not in benchmarks:
                    skill["benchmark_reason"] = "安全相关"
                    benchmarks.append(skill)
                break
    
    # 4. 创新设计（10 个）
    for name in BENCHMARK_CRITERIA["创新设计"]:
        for key, skill in skill_map.items():
            if name.lower().replace("-", "") in key:
                if skill not in benchmarks:
                    skill["benchmark_reason"] = "创新设计"
                    benchmarks.append(skill)
                break
    
    # 补齐到 50 个（按描述长度排序）
    remaining = [s for s in skills if s not in benchmarks]
    remaining.sort(key=lambda x: -len(x["description"]))
    for skill in remaining[:50 - len(benchmarks)]:
        skill["benchmark_reason"] = "精选补充"
        benchmarks.append(skill)
    
    return benchmarks[:50]

def optimize_benchmark(skill):
    """优化单个标杆技能"""
    optimization = {
        "name": skill["name"],
        "url": skill["url"],
        "pattern": skill.get("pattern", "Unclassified"),
        "benchmark_reason": skill.get("benchmark_reason", ""),
        "description": skill["description"],
        "optimization": {
            "design_pattern": {
                "status": "pending",
                "notes": "需要标注具体设计模式",
            },
            "checklist": {
                "status": "pending",
                "notes": "需要外置检查清单到 references/",
            },
            "template": {
                "status": "pending",
                "notes": "需要补充模板文件到 assets/",
            },
            "failure_handling": {
                "status": "pending",
                "notes": "需要定义失败处理流程",
            },
        }
    }
    return optimization

def main():
    print("=" * 60)
    print("ClawHub 50 标杆技能选择与优化")
    print("=" * 60)
    
    # 加载技能
    print("\n加载精选技能...")
    skills = load_skills()
    print(f"总计：{len(skills)} 个技能")
    
    # 选择标杆
    print("\n选择标杆技能...")
    benchmarks = select_benchmarks(skills)
    print(f"标杆数量：{len(benchmarks)} 个")
    
    # 按模式统计
    pattern_stats = {}
    for skill in benchmarks:
        pattern = skill.get("pattern", "Unclassified")
        pattern_stats[pattern] = pattern_stats.get(pattern, 0) + 1
    
    print("\n标杆模式分布:")
    for pattern, count in sorted(pattern_stats.items(), key=lambda x: -x[1]):
        print(f"  {pattern}: {count}")
    
    # 优化每个标杆
    print("\n优化标杆技能...")
    optimized = []
    for skill in benchmarks:
        opt = optimize_benchmark(skill)
        optimized.append(opt)
    
    # 保存结果
    benchmarks_output = OUTPUT_DIR / "benchmarks-50.json"
    with open(benchmarks_output, 'w') as f:
        json.dump(optimized, f, indent=2, ensure_ascii=False)
    print(f"\n已保存：{benchmarks_output}")
    
    # 生成优化任务列表
    tasks = []
    for opt in optimized:
        for task_type, task_info in opt["optimization"].items():
            tasks.append({
                "skill": opt["name"],
                "pattern": opt["pattern"],
                "task": task_type,
                "status": task_info["status"],
                "notes": task_info["notes"],
            })
    
    tasks_output = OUTPUT_DIR / "optimization-tasks.json"
    with open(tasks_output, 'w') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    print(f"已保存任务列表：{tasks_output} ({len(tasks)} 个任务)")
    
    # 生成统计报告
    stats = {
        "total_benchmarks": len(benchmarks),
        "pattern_distribution": pattern_stats,
        "total_tasks": len(tasks),
        "tasks_by_type": {
            task_type: sum(1 for t in tasks if t["task"] == task_type)
            for task_type in ["design_pattern", "checklist", "template", "failure_handling"]
        },
    }
    
    stats_output = OUTPUT_DIR / "stats.json"
    with open(stats_output, 'w') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"已保存统计：{stats_output}")
    
    print("\n" + "=" * 60)
    print("Phase 3 选择完成！")
    print("=" * 60)
    print(f"\n下一步：执行 {len(tasks)} 个优化任务")

if __name__ == "__main__":
    main()
