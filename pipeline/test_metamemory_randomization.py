#!/usr/bin/env python3
"""
元记忆 A/B 测试随机分组脚本 - Mock 测试

用途：使用模拟参与者数据测试 metamemory_randomization.py 的功能
依赖：pipeline/metamemory_randomization.py
"""

import csv
import os
import sys
from datetime import datetime

# 创建 mock 参与者数据
MOCK_PARTICIPANTS = [
    # ID, 年龄，性别，教育年限，MoCA 分数，招募渠道
    ["P001", 68, "女", 12, 22, "社区"],
    ["P002", 72, "男", 9, 20, "医院"],
    ["P003", 65, "女", 16, 24, "线上"],
    ["P004", 70, "男", 12, 19, "社区"],
    ["P005", 66, "女", 14, 23, "转介绍"],
    ["P006", 74, "男", 8, 18, "医院"],
    ["P007", 69, "女", 15, 25, "线上"],
    ["P008", 71, "男", 10, 21, "社区"],
    ["P009", 67, "女", 13, 22, "医院"],
    ["P010", 73, "男", 11, 20, "转介绍"],
    ["P011", 64, "女", 16, 26, "线上"],  # MoCA>25，正常认知
    ["P012", 75, "男", 7, 17, "社区"],
    ["P013", 68, "女", 14, 23, "医院"],
    ["P014", 70, "男", 12, 21, "线上"],
    ["P015", 66, "女", 15, 24, "社区"],
    ["P016", 72, "男", 9, 19, "转介绍"],
    ["P017", 69, "女", 13, 22, "医院"],
    ["P018", 71, "男", 10, 20, "线上"],
    ["P019", 65, "女", 16, 25, "社区"],
    ["P020", 74, "男", 8, 18, "医院"],
]

def create_mock_csv(filepath):
    """创建 mock 参与者 CSV 文件"""
    header = ["participant_id", "age", "gender", "education_years", "moca_score", "recruitment_channel"]
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(MOCK_PARTICIPANTS)
    
    print(f"✅ Mock 数据已创建：{filepath}")
    print(f"   参与者数量：{len(MOCK_PARTICIPANTS)}")
    
    # 统计基本信息
    ages = [int(p[1]) for p in MOCK_PARTICIPANTS]
    moca_scores = [float(p[4]) for p in MOCK_PARTICIPANTS]
    genders = {"男": sum(1 for p in MOCK_PARTICIPANTS if p[2] == "男"),
               "女": sum(1 for p in MOCK_PARTICIPANTS if p[2] == "女")}
    
    print(f"   年龄范围：{min(ages)}-{max(ages)} 岁 (平均 {sum(ages)/len(ages):.1f} 岁)")
    print(f"   MoCA 范围：{min(moca_scores)}-{max(moca_scores)} (平均 {sum(moca_scores)/len(moca_scores):.1f})")
    print(f"   性别分布：{genders}")

def main():
    print("=" * 60)
    print("元记忆 A/B 测试随机分组 - Mock 测试")
    print("=" * 60)
    print()
    
    # 1. 创建 mock CSV
    mock_csv_path = "mock_participants.csv"
    create_mock_csv(mock_csv_path)
    print()
    
    # 2. 运行随机分组脚本
    print("运行随机分组脚本...")
    print("-" * 60)
    
    # 导入随机分组脚本
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from metamemory_randomization import load_participants, create_strata, randomize_within_strata, check_baseline_balance, save_assignments, save_baseline_report
    
    # 执行随机分组
    try:
        participants = load_participants(mock_csv_path)
        strata = create_strata(participants)
        assignments = randomize_within_strata(strata)
        balance = check_baseline_balance(assignments)
        save_assignments(assignments, "group_assignment.csv")
        save_baseline_report(balance, "baseline_check.txt")
        baseline_report = open("baseline_check.txt").read()
        
        print("\n✅ 随机分组完成!")
        print(f"   分组结果文件：group_assignment.csv")
        print(f"   基线报告文件：baseline_check.txt")
        print()
        
        # 3. 验证分组结果
        print("分组结果验证:")
        print("-" * 60)
        
        group_a = [a for a in assignments if a['group'] == 'A']
        group_b = [a for a in assignments if a['group'] == 'B']
        
        print(f"   A 组 (标准引导): {len(group_a)} 人")
        print(f"   B 组 (元记忆增强): {len(group_b)} 人")
        print()
        
        # 4. 显示基线均衡性检验摘要
        print("基线均衡性检验摘要:")
        print("-" * 60)
        print(baseline_report)
        print()
        
        # 5. 读取并显示分组结果
        print("分组详情 (前 10 名参与者):")
        print("-" * 60)
        
        with open("group_assignment.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i < 10:
                    print(f"   {row['name'] or 'P'+str(i+1)}: {row['age']}岁/{row['gender']}/"
                          f"MoCA={row['moca_score']}/教育={row['education'] or 'N/A'}年 "
                          f"→ {row['group']}组")
        
        print()
        print("=" * 60)
        print("✅ Mock 测试通过！")
        print("=" * 60)
        print()
        print("下一步:")
        print("1. 在腾讯问卷/问卷星创建筛选问卷")
        print("2. 招募参与者并收集真实数据")
        print("3. 使用真实数据替换 mock_participants.csv")
        print("4. 重新运行 metamemory_randomization.py 进行真实分组")
        
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 6. 清理 mock 文件 (可选)
    # os.remove(mock_csv_path)
    # print(f"\n已清理 mock 文件：{mock_csv_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
