#!/usr/bin/env python3
"""
论文数据可视化生成脚本 v2
生成：性能对比、消融实验、误差分析三类图表
输出：SVG 矢量图 (出版级)
"""

import json
import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# 配置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 出版级配置
FIG_WIDTH_MM = 180  # 双栏宽度
FIG_HEIGHT_MM = 120
DPI = 300

# 品牌色
CITTAVERSE_BLUE = '#0ea5e9'
COLORBLIND_SAFE = ['#0072B2', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#D55E00', '#CC79A7']

def load_asr_results(path):
    """加载 ASR 性能数据"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_robustness_results(path):
    """加载鲁棒性测试数据"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_asr_performance_plot(asr_data, output_path):
    """Figure 1: ASR 性能分布图"""
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH_MM/25.4, FIG_HEIGHT_MM/25.4))
    
    samples = asr_data['samples']
    wers = [s['wer'] * 100 for s in samples]  # 转换为百分比
    
    # 左图：WER 分布直方图
    ax1 = axes[0]
    ax1.hist(wers, bins=10, color=CITTAVERSE_BLUE, edgecolor='white', alpha=0.8)
    ax1.axvline(np.mean(wers), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(wers):.2f}%')
    ax1.set_xlabel('Word Error Rate (%)', fontsize=9)
    ax1.set_ylabel('Frequency', fontsize=9)
    ax1.set_title('ASR WER Distribution (N=40)', fontsize=10, fontweight='bold')
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3)
    
    # 右图：零错误率饼图
    ax2 = axes[1]
    zero_error = asr_data['summary']['zero_error_samples']
    total = asr_data['summary']['count']
    ax2.pie([zero_error, total - zero_error], 
            labels=[f'Zero Error\n({zero_error})', f'With Error\n({total - zero_error})'],
            colors=[CITTAVERSE_BLUE, '#e5e7eb'],
            autopct='%1.1f%%', startangle=90)
    ax2.set_title('Zero Error Rate', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")

def generate_robustness_boxplot(robustness_data, output_path):
    """Figure 2: 不同噪声类别的鲁棒性对比 (箱线图)"""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_MM/25.4, FIG_HEIGHT_MM/25.4))
    
    # 准备数据
    categories = ['noise', 'edge_case', 'adversarial']
    category_labels = ['ASR 噪声 (N=8)', '边界情况 (N=12)', '对抗样本 (N=10)']
    
    all_scores = []
    for cat in categories:
        cat_data = robustness_data['by_category'].get(cat, [])
        scores = [item['scores']['L0 Score'] for item in cat_data if 'scores' in item]
        all_scores.append(scores)
    
    # 箱线图
    bp = ax.boxplot(all_scores, labels=category_labels, patch_artist=True,
                    boxprops=dict(facecolor=CITTAVERSE_BLUE, alpha=0.6),
                    medianprops=dict(color='red', linewidth=2),
                    whiskerprops=dict(linewidth=1.5),
                    capprops=dict(linewidth=1.5))
    
    ax.set_ylabel('L0 Score', fontsize=9)
    ax.set_title('Robustness by Noise Category', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 4)
    
    # 添加均值标注
    for i, (cat, scores) in enumerate(zip(categories, all_scores)):
        mean_val = np.mean(scores)
        ax.text(i + 1, mean_val + 0.1, f'μ={mean_val:.2f}', ha='center', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")

def generate_dimension_radar(robustness_data, output_path):
    """Figure 3: 六维度评分雷达图"""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_MM/25.4, FIG_HEIGHT_MM/25.4), subplot_kw=dict(polar=True))
    
    # 六维度名称
    dimensions = ['情感表达', '叙事连贯', '细节丰富', '自我反思', '社会连接', '认知活跃']
    angles = np.linspace(0, 2 * np.pi, len(dimensions), endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    # 计算各维度平均分
    all_results = robustness_data['all_results']
    dim_scores = {d: [] for d in dimensions}
    for item in all_results:
        for dim in dimensions:
            if dim in item['scores']:
                dim_scores[dim].append(item['scores'][dim])
    
    means = [np.mean(dim_scores[d]) for d in dimensions]
    means += means[:1]  # 闭合
    
    # 绘制雷达图
    ax.plot(angles, means, 'o-', linewidth=2, color=CITTAVERSE_BLUE, label='Mean Score')
    ax.fill(angles, means, alpha=0.25, color=CITTAVERSE_BLUE)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, fontsize=8)
    ax.set_ylim(0, 4)
    ax.set_title('Six-Dimension Score Profile', fontsize=10, fontweight='bold', pad=20)
    ax.grid(True)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")

def generate_error_type_analysis(asr_data, output_path):
    """Figure 4: ASR 错误类型分析"""
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH_MM/25.4, FIG_HEIGHT_MM/25.4))
    
    samples = asr_data['samples']
    error_samples = [s for s in samples if s['wer'] > 0]
    
    # 左图：错误样本的 WER 分布
    ax1 = axes[0]
    error_wers = [s['wer'] * 100 for s in error_samples]
    ax1.bar(range(len(error_samples)), error_wers, color='#ef4444', alpha=0.7)
    ax1.set_xlabel('Error Sample ID', fontsize=9)
    ax1.set_ylabel('WER (%)', fontsize=9)
    ax1.set_title(f'Error Samples WER (N={len(error_samples)})', fontsize=10, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 右图：错误类型统计 (substitutions/deletions/insertions)
    ax2 = axes[1]
    total_sub = sum(s['substitutions'] for s in error_samples)
    total_del = sum(s['deletions'] for s in error_samples)
    total_ins = sum(s['insertions'] for s in error_samples)
    
    error_types = ['Substitutions', 'Deletions', 'Insertions']
    error_counts = [total_sub, total_del, total_ins]
    colors = ['#ef4444', '#f59e0b', '#10b981']
    
    ax2.bar(error_types, error_counts, color=colors, alpha=0.7)
    ax2.set_ylabel('Count', fontsize=9)
    ax2.set_title('Error Type Distribution', fontsize=10, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 标注数值
    for i, count in enumerate(error_counts):
        ax2.text(i, count + 0.1, str(count), ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")

def generate_ablation_by_noise_type(robustness_data, output_path):
    """Figure 5: 消融实验 - 不同噪声类型对 L0 Score 的影响"""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_MM/25.4, FIG_HEIGHT_MM/25.4))
    
    all_results = robustness_data['all_results']
    
    # 按 noise_type 分组
    noise_types = {}
    for item in all_results:
        nt = item.get('noise_type', 'unknown')
        if nt not in noise_types:
            noise_types[nt] = []
        noise_types[nt].append(item['scores']['L0 Score'])
    
    # 计算均值和标准差
    means = {k: np.mean(v) for k, v in noise_types.items()}
    stds = {k: np.std(v) for k, v in noise_types.items()}
    
    # 排序
    sorted_types = sorted(means.keys(), key=lambda x: means[x], reverse=True)
    
    # 绘制柱状图
    x_pos = range(len(sorted_types))
    y_vals = [means[t] for t in sorted_types]
    y_errs = [stds[t] for t in sorted_types]
    
    bars = ax.bar(x_pos, y_vals, yerr=y_errs, capsize=5, 
                  color=CITTAVERSE_BLUE, alpha=0.7, ecolor='red')
    
    # 设置 x 轴标签 (旋转)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(sorted_types, rotation=45, ha='right', fontsize=7)
    ax.set_ylabel('L0 Score (Mean ± Std)', fontsize=9)
    ax.set_title('Ablation Study: Impact of Noise Types on L0 Score', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 4)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")

def generate_lref_stage_distribution(robustness_data, output_path):
    """Figure 6: LREF 阶段分布"""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_MM/25.4, FIG_HEIGHT_MM/25.4))
    
    all_results = robustness_data['all_results']
    
    # 统计各 LREF 阶段数量
    stage_counts = {}
    for item in all_results:
        stage = item.get('lref_stage', 'L0')
        stage_counts[stage] = stage_counts.get(stage, 0) + 1
    
    # 排序
    stages = sorted(stage_counts.keys())
    counts = [stage_counts[s] for s in stages]
    
    # 绘制柱状图
    colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'][:len(stages)]
    ax.bar(stages, counts, color=colors, alpha=0.7)
    
    ax.set_xlabel('LREF Stage', fontsize=9)
    ax.set_ylabel('Count', fontsize=9)
    ax.set_title('LREF Stage Distribution', fontsize=10, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 标注数值
    for i, count in enumerate(counts):
        ax.text(i, count + 0.1, str(count), ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight')
    plt.close()
    print(f"✓ Generated: {output_path}")

def main():
    # 路径配置
    base_dir = '/Users/moondy/.openclaw/workspace-hulk'
    asr_path = os.path.join(base_dir, 'research/asr/results_v11.json')
    robustness_path = os.path.join(base_dir, 'research/vsnc-l0-robustness-results.json')
    output_dir = os.path.join(base_dir, 'artifacts/visualizations/2026-04-06')
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🟢 Hulk Visualization Generator v2")
    print(f"   Output: {output_dir}")
    print()
    
    # 加载数据
    print("Loading data...")
    asr_data = load_asr_results(asr_path)
    robustness_data = load_robustness_results(robustness_path)
    print(f"   ASR samples: {asr_data['summary']['count']}")
    print(f"   Robustness tests: {robustness_data['summary']['total_tests']}")
    print()
    
    # 生成图表
    print("Generating figures...")
    
    # 性能对比
    generate_asr_performance_plot(asr_data, os.path.join(output_dir, 'fig1_asr_performance.svg'))
    generate_error_type_analysis(asr_data, os.path.join(output_dir, 'fig2_error_analysis.svg'))
    
    # 消融实验
    generate_ablation_by_noise_type(robustness_data, os.path.join(output_dir, 'fig3_ablation_noise.svg'))
    generate_lref_stage_distribution(robustness_data, os.path.join(output_dir, 'fig4_lref_stages.svg'))
    
    # 误差分析
    generate_robustness_boxplot(robustness_data, os.path.join(output_dir, 'fig5_robustness_boxplot.svg'))
    generate_dimension_radar(robustness_data, os.path.join(output_dir, 'fig6_dimension_radar.svg'))
    
    print()
    print(f"✅ All figures generated successfully!")
    print(f"   Output directory: {output_dir}")
    
    # 生成报告
    report_path = os.path.join(output_dir, 'generation_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# 论文数据可视化生成报告\n\n")
        f.write(f"**生成时间**: {datetime.now().isoformat()}\n")
        f.write(f"**数据源**:\n")
        f.write(f"- ASR 性能：{asr_data['summary']['count']} 样本\n")
        f.write(f"- 鲁棒性测试：{robustness_data['summary']['total_tests']} 测试\n\n")
        f.write(f"**生成图表**:\n")
        f.write(f"1. fig1_asr_performance.svg - ASR 性能分布\n")
        f.write(f"2. fig2_error_analysis.svg - 错误类型分析\n")
        f.write(f"3. fig3_ablation_noise.svg - 噪声类型消融\n")
        f.write(f"4. fig4_lref_stages.svg - LREF 阶段分布\n")
        f.write(f"5. fig5_robustness_boxplot.svg - 鲁棒性箱线图\n")
        f.write(f"6. fig6_dimension_radar.svg - 六维度雷达图\n")
    print(f"   Report: {report_path}")

if __name__ == '__main__':
    main()
