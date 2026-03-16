#!/usr/bin/env python3
"""
元记忆 A/B 测试随机分组脚本

功能：
- 读取筛选通过的参与者名单
- 按年龄+MoCA+ 性别 + 教育分层
- 每层内随机分配至 A/B 组
- 检查两组基线均衡性
- 输出分组结果

使用方式：
    python3 metamemory_randomization.py participants.csv

输入文件格式 (CSV):
    name,age,gender,education,moca_score,phone
    张三，65，男，高中，22,13800138000
    李四，72，女，初中，19,13900139000

输出文件：
    - group_assignment.csv: 分组结果 (含组别)
    - baseline_check.txt: 基线均衡性检验报告
"""

import csv
import random
from collections import defaultdict
from typing import List, Dict, Tuple
import sys

# 分层维度定义
AGE_BINS = [
    (60, 69, "60-69"),
    (70, 80, "70-80")
]

MOCA_BINS = [
    (18, 21, "18-21"),
    (22, 25, "22-25"),
    (None, None, "unknown")  # 未测 MoCA
]

GENDER_BINS = ["男", "女"]

EDU_BINS = [
    ("初中及以下", "low"),
    ("高中", "medium"),
    ("大专及以上", "high")
]


def categorize_age(age: int) -> str:
    """年龄分层"""
    for low, high, label in AGE_BINS:
        if low <= age <= high:
            return label
    return "unknown"


def categorize_moca(score: str) -> str:
    """MoCA 分层"""
    if not score or score.strip() == "":
        return "unknown"
    try:
        score = int(score)
        for low, high, label in MOCA_BINS:
            if low is None:  # unknown bin
                continue
            if low <= score <= high:
                return label
        return "unknown"
    except ValueError:
        return "unknown"


def categorize_education(edu: str) -> str:
    """教育程度分层"""
    edu = edu.strip()
    for pattern, label in EDU_BINS:
        if pattern in edu:
            return label
    return "medium"  # 默认


def load_participants(filepath: str) -> List[Dict]:
    """读取参与者名单"""
    participants = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            participants.append(row)
    return participants


def create_strata(participants: List[Dict]) -> Dict[str, List[Dict]]:
    """创建分层"""
    strata = defaultdict(list)
    
    for p in participants:
        age_cat = categorize_age(int(p['age']))
        moca_cat = categorize_moca(p.get('moca_score', ''))
        gender = p.get('gender', 'unknown')
        edu_cat = categorize_education(p.get('education', ''))
        
        # 分层键：年龄_MoCA_ 性别_教育
        stratum_key = f"{age_cat}_{moca_cat}_{gender}_{edu_cat}"
        strata[stratum_key].append(p)
    
    return strata


def randomize_within_strata(strata: Dict[str, List[Dict]]) -> List[Dict]:
    """层内随机化"""
    assignments = []
    
    for stratum_key, participants in strata.items():
        # 打乱顺序
        random.shuffle(participants)
        
        # 交替分配至 A/B 组
        for i, p in enumerate(participants):
            group = "A" if i % 2 == 0 else "B"
            p['group'] = group
            p['stratum'] = stratum_key
            assignments.append(p)
    
    return assignments


def check_baseline_balance(assignments: List[Dict]) -> Dict:
    """基线均衡性检查"""
    groups = {"A": [], "B": []}
    
    for p in assignments:
        groups[p['group']].append(p)
    
    # 计算各维度均值/比例
    def calc_stats(group_data):
        if not group_data:
            return {}
        
        n = len(group_data)
        ages = [int(p['age']) for p in group_data]
        moca_scores = []
        for p in group_data:
            score = p.get('moca_score', '')
            if score and score.strip():
                try:
                    moca_scores.append(int(score))
                except ValueError:
                    pass
        
        males = sum(1 for p in group_data if p.get('gender', '').upper() in ['M', '男', 'MALE'])
        
        return {
            'n': n,
            'age_mean': sum(ages) / n if n > 0 else 0,
            'age_std': (sum((x - sum(ages)/n)**2 for x in ages) / n) ** 0.5 if n > 1 else 0,
            'moca_mean': sum(moca_scores) / len(moca_scores) if moca_scores else 0,
            'male_ratio': males / n if n > 0 else 0
        }
    
    stats_a = calc_stats(groups['A'])
    stats_b = calc_stats(groups['B'])
    
    return {
        'A': stats_a,
        'B': stats_b,
        'diff_age': abs(stats_a.get('age_mean', 0) - stats_b.get('age_mean', 0)),
        'diff_moca': abs(stats_a.get('moca_mean', 0) - stats_b.get('moca_mean', 0)),
        'diff_male_ratio': abs(stats_a.get('male_ratio', 0) - stats_b.get('male_ratio', 0))
    }


def save_assignments(assignments: List[Dict], filepath: str):
    """保存分组结果"""
    fieldnames = ['name', 'age', 'gender', 'education', 'moca_score', 'phone', 'group', 'stratum']
    
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for p in assignments:
            writer.writerow(p)


def save_baseline_report(balance: Dict, filepath: str):
    """保存基线均衡性报告"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("元记忆 A/B 测试 - 基线均衡性检验报告\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("A 组统计:\n")
        f.write(f"  人数：{balance['A'].get('n', 0)}\n")
        f.write(f"  年龄均值：{balance['A'].get('age_mean', 0):.1f} ± {balance['A'].get('age_std', 0):.1f} 岁\n")
        f.write(f"  MoCA 均值：{balance['A'].get('moca_mean', 0):.1f} 分\n")
        f.write(f"  男性比例：{balance['A'].get('male_ratio', 0):.1%}\n\n")
        
        f.write("B 组统计:\n")
        f.write(f"  人数：{balance['B'].get('n', 0)}\n")
        f.write(f"  年龄均值：{balance['B'].get('age_mean', 0):.1f} ± {balance['B'].get('age_std', 0):.1f} 岁\n")
        f.write(f"  MoCA 均值：{balance['B'].get('moca_mean', 0):.1f} 分\n")
        f.write(f"  男性比例：{balance['B'].get('male_ratio', 0):.1%}\n\n")
        
        f.write("-" * 60 + "\n")
        f.write("组间差异:\n")
        f.write(f"  年龄差异：{balance['diff_age']:.1f} 岁\n")
        f.write(f"  MoCA 差异：{balance['diff_moca']:.1f} 分\n")
        f.write(f"  男性比例差异：{balance['diff_male_ratio']:.1%}\n\n")
        
        # 判断是否均衡
        balanced = (
            balance['diff_age'] < 3.0 and
            balance['diff_moca'] < 2.0 and
            balance['diff_male_ratio'] < 0.15
        )
        
        if balanced:
            f.write("✅ 基线均衡：两组在年龄、MoCA、性别分布上无显著差异\n")
        else:
            f.write("⚠️ 基线不均衡：建议重新随机化或在统计分析中控制协变量\n")
        
        f.write("\n" + "=" * 60 + "\n")


def main():
    if len(sys.argv) < 2:
        print("用法：python3 metamemory_randomization.py participants.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 读取参与者名单
    print(f"读取参与者名单：{input_file}")
    participants = load_participants(input_file)
    print(f"共 {len(participants)} 人")
    
    # 创建分层
    print("创建分层...")
    strata = create_strata(participants)
    print(f"共 {len(strata)} 层")
    
    # 层内随机化
    print("层内随机化...")
    random.seed(42)  # 固定随机种子，确保可重复
    assignments = randomize_within_strata(strata)
    
    # 基线均衡性检查
    print("检查基线均衡性...")
    balance = check_baseline_balance(assignments)
    
    # 保存结果
    save_assignments(assignments, 'group_assignment.csv')
    print("分组结果已保存：group_assignment.csv")
    
    save_baseline_report(balance, 'baseline_check.txt')
    print("基线报告已保存：baseline_check.txt")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("分组摘要:")
    group_counts = defaultdict(int)
    for p in assignments:
        group_counts[p['group']] += 1
    print(f"  A 组：{group_counts['A']} 人")
    print(f"  B 组：{group_counts['B']} 人")
    print(f"  总计：{len(assignments)} 人")
    print("=" * 60)


if __name__ == '__main__':
    main()
