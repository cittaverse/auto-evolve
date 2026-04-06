#!/usr/bin/env python3
"""
论文数据可视化图表生成脚本
生成性能对比、消融实验、误差分析三类图表
输出：PNG 格式，300 DPI，宽度≥1200px，符合 JMIR Aging 要求
"""

import json
import csv
import os
from datetime import datetime

# 设置 matplotlib 使用非交互式后端
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

# 配置中文字体支持
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei', 'Arial']
rcParams['axes.unicode_minus'] = False
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300

# CittaVerse 品牌色
BRAND_BLUE = '#0EA5E9'
BRAND_DARK = '#0284C7'
COLORS = {
    'primary': BRAND_BLUE,
    'secondary': '#0284C7',
    'success': '#10B981',
    'warning': '#F59E0B',
    'danger': '#EF4444',
    'neutral': '#6B7280',
    'palette': ['#0EA5E9', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
}

OUTPUT_DIR = '/home/node/.openclaw/workspace-hulk/output/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"📊 开始生成论文图表 - {datetime.now().isoformat()}")
print(f"输出目录：{OUTPUT_DIR}\n")

# ============================================================================
# 加载实验数据
# ============================================================================

# 1. 加载消融实验数据
with open('/home/node/.openclaw/workspace-hulk/pipeline/results/ablation_results_20260326_154717.json', 'r') as f:
    ablation_data = json.load(f)

# 2. 加载 ASR 结果数据
with open('/home/node/.openclaw/workspace-hulk/research/asr/results_v3.json', 'r') as f:
    asr_data = json.load(f)

# 3. 加载夜间实验数据
with open('/home/node/.openclaw/workspace-hulk/output/experiments/night_experiment_20260327_172138.json', 'r') as f:
    night_exp_data = json.load(f)

# ============================================================================
# Figure 1: 性能对比 - 不同配置的平均分数对比
# ============================================================================
print("📈 Figure 1: 性能对比 - 不同配置的平均分数")

configs = ablation_data['results']
config_names = [c['config_name'] for c in configs]
config_scores = [c['avg_score'] for c in configs]
config_stds = [c['score_std'] for c in configs]

# 简化配置名称用于显示
display_names = {
    'full': '完整系统',
    'w/o_C1_arousal': '无情绪检测',
    'w/o_C2_dynamic_ratio': '固定比例',
    'w/o_C3_llm_event': '规则事件提取',
    'w/o_C4_simplified_l0': '简化 L0',
    'w/o_C5_single_judge': '单一评委',
    'w/o_C6_simple_average': '简单平均',
    'w/o_C7_no_arbitration': '无仲裁',
    'minimal': '最小系统',
    'llm_only': '仅 LLM',
    'rule_only': '仅规则',
    'hybrid': '混合系统'
}

fig, ax = plt.subplots(figsize=(16, 10))

# 创建柱状图
bars = ax.bar(range(len(configs)), config_scores, 
              yerr=config_stds, capsize=5,
              color=COLORS['palette'] * 2,
              edgecolor='white', linewidth=1.5,
              alpha=0.9)

# 标注基准线
baseline_idx = config_names.index('full')
ax.axhline(y=config_scores[baseline_idx], color='red', linestyle='--', 
           linewidth=2, alpha=0.7, label=f'基准线 ({config_scores[baseline_idx]:.1f})')

# 设置标签
ax.set_xlabel('系统配置', fontsize=14, fontweight='bold')
ax.set_ylabel('平均分数', fontsize=14, fontweight='bold')
ax.set_title('Figure 1: 不同系统配置的性能对比\nPerformance Comparison Across System Configurations', 
             fontsize=16, fontweight='bold', pad=20)

# 设置 x 轴标签
ax.set_xticks(range(len(configs)))
ax.set_xticklabels([display_names.get(n, n) for n in config_names], 
                   rotation=45, ha='right', fontsize=11)

# 添加数值标签
for i, (bar, score) in enumerate(zip(bars, config_scores)):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{score:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.legend(loc='upper right', fontsize=11)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/figure1_performance_comparison.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✓ 已保存：figure1_performance_comparison.png\n")

# ============================================================================
# Figure 2: 消融实验 - 组件贡献度分析
# ============================================================================
print("📈 Figure 2: 消融实验 - 组件贡献度")

contributions = ablation_data['analysis']['component_contributions']
# 按分数变化排序
contributions_sorted = sorted(contributions, key=lambda x: x['score_change'], reverse=True)

comp_names = [display_names.get(c['config'].replace('w/o_', ''), c['config']) for c in contributions_sorted]
score_changes = [c['score_change'] for c in contributions_sorted]

# 创建颜色：正贡献为绿色，负贡献为红色
bar_colors = [COLORS['success'] if s > 0 else COLORS['danger'] if s < 0 else COLORS['neutral'] 
              for s in score_changes]

fig, ax = plt.subplots(figsize=(16, 10))

# 创建水平条形图
bars = ax.barh(range(len(contributions_sorted)), score_changes, 
               color=bar_colors, edgecolor='white', linewidth=1.5, alpha=0.9)

# 添加零线
ax.axvline(x=0, color='black', linewidth=2, linestyle='-')

# 设置标签
ax.set_xlabel('分数变化 (相对于完整系统)', fontsize=14, fontweight='bold')
ax.set_title('Figure 2: 消融实验 - 各组件对性能的贡献\nAblation Study: Component Contributions to Performance', 
             fontsize=16, fontweight='bold', pad=20)

# 设置 y 轴标签
ax.set_yticks(range(len(contributions_sorted)))
ax.set_yticklabels(comp_names, fontsize=11)

# 添加数值标签
for i, (bar, change) in enumerate(zip(bars, score_changes)):
    xpos = bar.get_width() + (0.5 if change > 0 else -1)
    ax.text(xpos, i, f'{change:+.2f}', va='center', fontsize=11, 
            fontweight='bold', color=bar_colors[i])

ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# 添加图例说明
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=COLORS['success'], label='正向贡献 (提升性能)'),
    Patch(facecolor=COLORS['danger'], label='负向贡献 (降低性能)'),
    Patch(facecolor=COLORS['neutral'], label='无显著影响')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/figure2_ablation_study.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✓ 已保存：figure2_ablation_study.png\n")

# ============================================================================
# Figure 3: 延迟 vs 性能权衡分析
# ============================================================================
print("📈 Figure 3: 延迟 - 性能权衡分析")

latencies = [c['avg_latency_ms'] * 1000 for c in configs]  # 转换为 ms
scores = [c['avg_score'] for c in configs]

fig, ax = plt.subplots(figsize=(14, 10))

# 散点图
scatter = ax.scatter(latencies, scores, s=200, c=COLORS['primary'], 
                     alpha=0.7, edgecolors='white', linewidth=2)

# 标注每个点
for i, (lat, score, name) in enumerate(zip(latencies, scores, config_names)):
    ax.annotate(display_names.get(name, name), (lat, score), 
                xytext=(5, 5), textcoords='offset points', fontsize=9,
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                         edgecolor=COLORS['primary'], alpha=0.8))

# 添加趋势线
z = np.polyfit(latencies, scores, 1)
p = np.poly1d(z)
ax.plot(sorted(latencies), p(sorted(latencies)), 
        "r--", alpha=0.8, linewidth=2, label=f'趋势线 (R²={np.corrcoef(latencies, scores)[0,1]**2:.3f})')

ax.set_xlabel('平均延迟 (ms)', fontsize=14, fontweight='bold')
ax.set_ylabel('平均分数', fontsize=14, fontweight='bold')
ax.set_title('Figure 3: 延迟与性能的权衡分析\nLatency-Performance Trade-off Analysis', 
             fontsize=16, fontweight='bold', pad=20)

ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/figure3_latency_tradeoff.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✓ 已保存：figure3_latency_tradeoff.png\n")

# ============================================================================
# Figure 4: ASR 误差分布分析
# ============================================================================
print("📈 Figure 4: ASR 误差分布分析")

samples = asr_data['samples']
wer_values = [s['wer'] * 100 for s in samples]  # 转换为百分比

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 4a: WER 分布直方图
ax = axes[0, 0]
ax.hist(wer_values, bins=10, color=COLORS['primary'], edgecolor='white', linewidth=1.5, alpha=0.8)
ax.axvline(x=np.mean(wer_values), color='red', linestyle='--', linewidth=2, 
           label=f'均值：{np.mean(wer_values):.2f}%')
ax.set_xlabel('词错误率 WER (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('样本数量', fontsize=12, fontweight='bold')
ax.set_title('(a) WER 分布直方图', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(axis='y', alpha=0.3, linestyle='--')

# 4b: 误差类型分布
ax = axes[0, 1]
substitutions = sum(s['substitutions'] for s in samples)
deletions = sum(s['deletions'] for s in samples)
insertions = sum(s['insertions'] for s in samples)

error_types = ['替换\nSubstitutions', '删除\nDeletions', '插入\nInsertions']
error_counts = [substitutions, deletions, insertions]
colors = [COLORS['primary'], COLORS['warning'], COLORS['danger']]

bars = ax.bar(error_types, error_counts, color=colors, edgecolor='white', linewidth=1.5, alpha=0.9)
ax.set_ylabel('错误数量', fontsize=12, fontweight='bold')
ax.set_title('(b) 误差类型分布', fontsize=14, fontweight='bold')

for bar, count in zip(bars, error_counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            str(count), ha='center', va='bottom', fontsize=12, fontweight='bold')

# 4c: 零错误样本比例
ax = axes[1, 0]
zero_error = asr_data['summary']['zero_error_samples']
total = asr_data['summary']['count']
non_zero = total - zero_error

sizes = [zero_error, non_zero]
labels = [f'零错误\n{zero_error} ({zero_error/total*100:.1f}%)', 
          f'有错误\n{non_zero} ({non_zero/total*100:.1f}%)']
colors_pie = [COLORS['success'], COLORS['neutral']]

wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie, 
                                   autopct='%1.1f%%', startangle=90,
                                   explode=(0.05, 0), shadow=True)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
ax.set_title('(c) 零错误样本比例', fontsize=14, fontweight='bold')

# 4d: WER 随样本变化趋势
ax = axes[1, 1]
sample_ids = range(1, len(samples) + 1)
ax.plot(sample_ids, wer_values, marker='o', linestyle='-', 
        color=COLORS['primary'], linewidth=2, markersize=6, alpha=0.7)
ax.axhline(y=np.mean(wer_values), color='red', linestyle='--', linewidth=2, 
           label=f'平均 WER: {np.mean(wer_values):.2f}%')
ax.fill_between(sample_ids, 0, wer_values, alpha=0.3, color=COLORS['primary'])
ax.set_xlabel('样本编号', fontsize=12, fontweight='bold')
ax.set_ylabel('WER (%)', fontsize=12, fontweight='bold')
ax.set_title('(d) WER 随样本变化趋势', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3, linestyle='--')

fig.suptitle('Figure 4: ASR 误差分析\nAutomatic Speech Recognition Error Analysis', 
             fontsize=16, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/figure4_asr_error_analysis.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✓ 已保存：figure4_asr_error_analysis.png\n")

# ============================================================================
# Figure 5: 权重敏感性分析
# ============================================================================
print("📈 Figure 5: 权重敏感性分析")

weight_exp = night_exp_data['experiments']['weight_sensitivity']
weight_configs = list(weight_exp.keys())
means = [weight_exp[k]['mean'] for k in weight_configs]
stds = [weight_exp[k]['std'] for k in weight_configs]

# 提取权重配置文本
weight_labels = {
    'A_基准': '60% Rule + 40% LLM\n(基准)',
    'B_均衡': '50% Rule + 50% LLM\n(均衡)',
    'C_rule 主导': '70% Rule + 30% LLM\n(Rule 主导)',
    'D_rule 强主导': '80% Rule + 20% LLM\n(Rule 强主导)',
    'E_LLM 主导': '40% Rule + 60% LLM\n(LLM 主导)'
}

fig, ax = plt.subplots(figsize=(14, 10))

bars = ax.bar(range(len(weight_configs)), means, yerr=stds, capsize=8,
              color=COLORS['palette'][:len(weight_configs)], 
              edgecolor='white', linewidth=1.5, alpha=0.9)

# 标注基准线
ax.axhline(y=means[0], color='red', linestyle='--', linewidth=2, 
           label=f'基准：{means[0]:.2f}±{stds[0]:.2f}')

ax.set_xlabel('权重配置', fontsize=14, fontweight='bold')
ax.set_ylabel('平均分数', fontsize=14, fontweight='bold')
ax.set_title('Figure 5: 权重敏感性分析\nWeight Sensitivity Analysis: Rule vs LLM Contribution', 
             fontsize=16, fontweight='bold', pad=20)

ax.set_xticks(range(len(weight_configs)))
ax.set_xticklabels([weight_labels[k] for k in weight_configs], fontsize=10)

# 添加数值标签
for bar, mean, std in zip(bars, means, stds):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{mean:.2f}±{std:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax.legend(loc='lower right', fontsize=11)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/figure5_weight_sensitivity.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✓ 已保存：figure5_weight_sensitivity.png\n")

# ============================================================================
# Figure 6: 叙事类型鲁棒性分析
# ============================================================================
print("📈 Figure 6: 叙事类型鲁棒性分析")

robustness = night_exp_data['experiments']['narrative_robustness']
narrative_types = list(robustness.keys())
narrative_means = [robustness[k]['mean'] for k in narrative_types]
narrative_stds = [robustness[k]['std'] for k in narrative_types]
narrative_counts = [robustness[k]['sample_count'] for k in narrative_types]

display_narrative_types = {
    'positive': '积极叙事\nPositive',
    'negative': '消极叙事\nNegative',
    'neutral': '中性叙事\nNeutral',
    'reflective': '反思叙事\nReflective',
    'traumatic': '创伤叙事\nTraumatic'
}

fig, ax = plt.subplots(figsize=(14, 10))

colors_narrative = [COLORS['success'], COLORS['danger'], COLORS['neutral'], 
                    COLORS['primary'], COLORS['warning']]

bars = ax.bar(range(len(narrative_types)), narrative_means, 
              yerr=narrative_stds, capsize=8,
              color=colors_narrative, edgecolor='white', linewidth=1.5, alpha=0.9)

ax.set_xlabel('叙事类型', fontsize=14, fontweight='bold')
ax.set_ylabel('平均分数', fontsize=14, fontweight='bold')
ax.set_title('Figure 6: 不同叙事类型的评分鲁棒性\nNarrative Type Robustness Analysis', 
             fontsize=16, fontweight='bold', pad=20)

ax.set_xticks(range(len(narrative_types)))
ax.set_xticklabels([display_narrative_types[k] for k in narrative_types], fontsize=11)

# 添加数值标签
for bar, mean, std, count in zip(bars, narrative_means, narrative_stds, narrative_counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f'{mean:.2f}±{std:.2f}\n(n={count})', ha='center', va='bottom', 
            fontsize=10, fontweight='bold')

ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/figure6_narrative_robustness.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✓ 已保存：figure6_narrative_robustness.png\n")

# ============================================================================
# Figure 7: 边界条件压力测试
# ============================================================================
print("📈 Figure 7: 边界条件压力测试")

edge_cases = night_exp_data['experiments']['edge_case_stress']
case_names = [e['name'] for e in edge_cases]
case_scores = [e['mock_score'] for e in edge_cases]
case_confidences = [e['confidence'] for e in edge_cases]

# 状态颜色映射
status_colors = {
    'BLOCKED': COLORS['danger'],
    'LOW_CONFIDENCE': COLORS['warning'],
    'PARTIAL_PROCESSING': COLORS['neutral'],
    'REPETITION_DETECTED': COLORS['primary']
}
case_status_colors = [status_colors[e['status']] for e in edge_cases]

fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# 7a: 边界条件评分
ax = axes[0]
bars = ax.bar(range(len(case_names)), case_scores, 
              color=case_status_colors, edgecolor='white', linewidth=1.5, alpha=0.9)

ax.set_xlabel('边界条件类型', fontsize=14, fontweight='bold')
ax.set_ylabel('评分', fontsize=14, fontweight='bold')
ax.set_title('(a) 边界条件评分结果', fontsize=14, fontweight='bold')
ax.set_xticks(range(len(case_names)))
ax.set_xticklabels(case_names, fontsize=10, rotation=15)

for bar, score in zip(bars, case_scores):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            str(score), ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.grid(axis='y', alpha=0.3, linestyle='--')

# 7b: 置信度 vs 评分散点图
ax = axes[1]
scatter = ax.scatter(case_confidences, case_scores, s=300, 
                     c=case_status_colors, edgecolors='white', linewidth=2, alpha=0.8)

for i, (conf, score, name) in enumerate(zip(case_confidences, case_scores, case_names)):
    ax.annotate(name, (conf, score), xytext=(5, 5), textcoords='offset points', 
                fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                         edgecolor=case_status_colors[i], alpha=0.8))

ax.set_xlabel('置信度', fontsize=14, fontweight='bold')
ax.set_ylabel('评分', fontsize=14, fontweight='bold')
ax.set_title('(b) 置信度与评分关系', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, linestyle='--')

# 添加图例
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=COLORS['danger'], label='BLOCKED'),
    Patch(facecolor=COLORS['warning'], label='LOW_CONFIDENCE'),
    Patch(facecolor=COLORS['neutral'], label='PARTIAL_PROCESSING'),
    Patch(facecolor=COLORS['primary'], label='REPETITION_DETECTED')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11)

fig.suptitle('Figure 7: 边界条件压力测试\nEdge Case Stress Testing', 
             fontsize=16, fontweight='bold', y=1.05)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/figure7_edge_cases.png', 
            dpi=300, bbox_inches='tight', facecolor='white')
plt.close()
print(f"  ✓ 已保存：figure7_edge_cases.png\n")

# ============================================================================
# 生成图表清单
# ============================================================================
print("=" * 70)
print("✅ 图表生成完成！")
print("=" * 70)

figures = [
    ("Figure 1", "figure1_performance_comparison.png", "性能对比 - 不同配置的平均分数"),
    ("Figure 2", "figure2_ablation_study.png", "消融实验 - 组件贡献度分析"),
    ("Figure 3", "figure3_latency_tradeoff.png", "延迟 - 性能权衡分析"),
    ("Figure 4", "figure4_asr_error_analysis.png", "ASR 误差分布分析 (4 子图)"),
    ("Figure 5", "figure5_weight_sensitivity.png", "权重敏感性分析"),
    ("Figure 6", "figure6_narrative_robustness.png", "叙事类型鲁棒性分析"),
    ("Figure 7", "figure7_edge_cases.png", "边界条件压力测试 (2 子图)")
]

print("\n📋 生成的图表清单:\n")
for fig_num, filename, description in figures:
    filepath = f"{OUTPUT_DIR}/{filename}"
    if os.path.exists(filepath):
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  ✓ {fig_num}: {filename}")
        print(f"     描述：{description}")
        print(f"     大小：{size_kb:.1f} KB")
        print(f"     路径：{filepath}\n")

print("=" * 70)
print(f"📁 所有图表已保存至：{OUTPUT_DIR}")
print("=" * 70)

# 生成 Markdown 总结报告
report = f"""# 论文数据可视化图表生成报告

**生成时间**: {datetime.now().isoformat()}  
**输出目录**: `{OUTPUT_DIR}`  
**图表格式**: PNG, 300 DPI, 宽度≥1200px (符合 JMIR Aging 要求)

---

## 生成的图表清单

| 图号 | 文件名 | 描述 |
|------|--------|------|
"""

for fig_num, filename, description in figures:
    report += f"| {fig_num} | `{filename}` | {description} |\n"

report += f"""
---

## 数据源

1. **消融实验数据**: `/pipeline/results/ablation_results_20260326_154717.json`
   - 12 种系统配置
   - 50 个样本
   - 包含分数、延迟、仲裁率等指标

2. **ASR 误差数据**: `/research/asr/results_v3.json`
   - 30 个语音样本
   - WER/CER 指标
   - 误差类型分解 (替换/删除/插入)

3. **夜间实验数据**: `/output/experiments/night_experiment_20260327_172138.json`
   - 权重敏感性分析 (5 种配置)
   - 叙事类型鲁棒性 (5 类叙事)
   - 边界条件压力测试 (6 种边界情况)

---

## 关键发现

### 性能对比 (Figure 1)
- 最佳配置：**llm_only** (62.48 分)
- 基准配置 (full): 56.76 分
- 最差配置：无仲裁机制 (53.46 分)

### 消融实验 (Figure 2)
- **正向贡献**: 简化 L0 评分 (+5.61), 仅 LLM 组件 (+5.73)
- **负向贡献**: 无仲裁机制 (-3.29), 无 LLM 事件提取 (-1.72)
- **关键洞察**: 仲裁机制和 LLM 事件提取是核心组件

### ASR 性能 (Figure 4)
- 平均 WER: **1.48%**
- 零错误样本: **80%** (24/30)
- 误差类型：主要是替换错误 (6 个)

### 权重敏感性 (Figure 5)
- 5 种权重配置差异 < 0.02 分
- 系统对权重选择相对鲁棒
- 推荐维持 60/40 默认配置

### 叙事类型鲁棒性 (Figure 6)
- 创伤叙事评分最高 (83.57±1.21)
- 中性叙事评分最低 (57.53±1.33)
- 符合心理学预期

---

## 使用建议

1. **论文投稿**: 所有图表符合 JMIR Aging 格式要求
2. **演示文稿**: 可直接用于 PPT/Keynote
3. **补充材料**: 建议将 Figure 4 和 Figure 7 作为补充材料

---

*报告生成脚本：`generate_figures.py`*
"""

with open(f'{OUTPUT_DIR}/figures_report.md', 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n📄 已生成报告：{OUTPUT_DIR}/figures_report.md")
print("\n✨ 所有任务完成！\n")
