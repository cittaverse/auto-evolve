#!/usr/bin/env python3
"""
论文数据可视化生成脚本 - 消融实验补充
生成：组件消融、Prompt 消融、模型对比三类图表
数据源：methods-evaluation.md 中的实验设计 (预期值)
输出：SVG 矢量图 (出版级)
"""

import os
import matplotlib.pyplot as plt
import numpy as np

# 出版级配置
FIG_WIDTH_MM = 180  # 双栏宽度
FIG_HEIGHT_MM = 120
DPI = 300

# 品牌色
CITTAVERSE_BLUE = '#0ea5e9'
COLORBLIND_SAFE = ['#0072B2', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#D55E00', '#CC79A7']

# 中文字体配置
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def generate_component_ablation(output_path):
    """Figure 7: 组件消融实验 (基于实验设计预期值)"""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_MM/25.4, FIG_HEIGHT_MM/25.4))
    
    # 数据来自 methods-evaluation.md §3.3.6
    # 预期影响基于设计目标 (非实测)
    components = ['Full System', 'E1: -Memory Graph', 'E2: -Strategy', 
                  'E3: -Feedback', 'E4: -Sensory', 'E5: -Social']
    scores = [78.5, 68.2, 64.5, 61.3, 58.7, 55.1]  # 预期叙事质量分
    drops = [0, -10.3, -14.0, -17.2, -19.8, -23.4]  # 下降幅度
    
    # 柱状图
    colors = [CITTAVERSE_BLUE] + ['#ef4444'] * 5  # 完整系统蓝色，消融红色
    bars = ax.bar(components, scores, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
    
    # 标注下降幅度
    for i, (score, drop) in enumerate(zip(scores, drops)):
        if drop < 0:
            ax.text(i, score + 2, f'{drop:.1f}', ha='center', fontsize=8, 
                   fontweight='bold', color='#ef4444')
    
    ax.set_ylabel('Narrative Quality Score', fontsize=9)
    ax.set_title('Component Ablation Study (Expected Impact)', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 90)
    
    # 旋转 x 轴标签
    plt.xticks(rotation=25, ha='right', fontsize=7)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")


def generate_prompt_ablation(output_path):
    """Figure 8: Prompt 工程消融实验"""
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH_MM/25.4, FIG_HEIGHT_MM/25.4))
    
    # 数据来自 methods-evaluation.md §3.3.7
    strategies = ['P1: Zero-shot', 'P2: Few-shot', 'P3: CoT', 'P4: Structured']
    icc_scores = [0.64, 0.72, 0.76, 0.78]  # 与人类评分 ICC
    parse_rates = [78, 86, 88, 94]  # JSON 解析成功率 %
    
    # 左图：ICC 对比
    ax1 = axes[0]
    bars1 = ax1.bar(strategies, icc_scores, color=CITTAVERSE_BLUE, alpha=0.7, edgecolor='black')
    ax1.set_ylabel('ICC vs Human Rater', fontsize=9)
    ax1.set_title('Inter-Rater Reliability', fontsize=10, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, 1.0)
    
    # 标注数值
    for i, icc in enumerate(icc_scores):
        ax1.text(i, icc + 0.02, f'{icc:.2f}', ha='center', fontsize=8, fontweight='bold')
    
    # 右图：解析成功率
    ax2 = axes[1]
    bars2 = ax2.bar(strategies, parse_rates, color='#10b981', alpha=0.7, edgecolor='black')
    ax2.set_ylabel('JSON Parse Success Rate (%)', fontsize=9)
    ax2.set_title('Output Parsing Reliability', fontsize=10, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, 100)
    
    # 标注数值
    for i, rate in enumerate(parse_rates):
        ax2.text(i, rate + 2, f'{rate}%', ha='center', fontsize=8, fontweight='bold')
    
    plt.xticks(rotation=25, ha='right', fontsize=7)
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")


def generate_model_comparison(output_path):
    """Figure 9: LLM 后端模型对比"""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_MM/25.4, FIG_HEIGHT_MM/25.4))
    
    # 数据来自 methods-evaluation.md §3.3.8
    models = ['Qwen-Plus', 'GPT-4o-mini', 'Claude-3-Haiku', 'GLM-4-Flash']
    icc_scores = [0.78, 0.75, 0.76, 0.72]
    costs_cny = [0.004, 0.001, 0.002, 0.001]  # 转换为 CNY 近似值
    
    # 散点图 (ICC vs Cost)
    colors = ['#0ea5e9', '#94a3b8', '#94a3b8', '#94a3b8']  # 选中的蓝色，其他灰色
    sizes = [150, 100, 100, 100]
    
    scatter = ax.scatter(costs_cny, icc_scores, s=sizes, c=colors, alpha=0.7, 
                         edgecolors='black', linewidth=1)
    
    # 标注模型名称
    for i, model in enumerate(models):
        ax.annotate(model, (costs_cny[i], icc_scores[i]), 
                   xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # 标注选中的模型
    ax.annotate('✅ Selected', (costs_cny[0], icc_scores[0]), 
               xytext=(5, -15), textcoords='offset points', fontsize=8, 
               color='#0ea5e9', fontweight='bold')
    
    ax.set_xlabel('Cost per Evaluation (CNY ¥)', fontsize=9)
    ax.set_ylabel('Inter-Rater Reliability (ICC)', fontsize=9)
    ax.set_title('LLM Backend Comparison: Performance vs Cost', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 对数坐标 (成本跨度大)
    ax.set_xscale('log')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")


def main():
    output_dir = '/Users/moondy/.openclaw/workspace-hulk/artifacts/visualizations/2026-04-06'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🟢 Hulk Ablation Figure Generator")
    print(f"   Output: {output_dir}")
    print(f"   Data Source: methods-evaluation.md (Expected values, not实测)")
    print()
    
    # 生成消融实验图表
    generate_component_ablation(os.path.join(output_dir, 'fig7_component_ablation.svg'))
    generate_prompt_ablation(os.path.join(output_dir, 'fig8_prompt_ablation.svg'))
    generate_model_comparison(os.path.join(output_dir, 'fig9_model_comparison.svg'))
    
    print()
    print(f"✅ Ablation figures generated successfully!")
    print(f"   ⚠️  Note: These are EXPECTED values from experimental design,")
    print(f"            not empirical results. Replace after Pilot RCT.")


if __name__ == '__main__':
    main()
