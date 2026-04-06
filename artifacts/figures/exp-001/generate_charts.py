#!/usr/bin/env python3
"""
EXP-001 Multi-Agent Scorer v0.6 效度验证 - 数据可视化图表生成

生成以下图表:
1. Figure 1: 性能对比 - L0 vs. L0+L1 vs. 人工标注 (散点图 + 回归线)
2. Figure 2: 消融实验 - 各组件对评分效度的贡献 (柱状图)
3. Figure 3: 误差分析 - 评分误差分布 (箱线图 + 直方图)
4. Figure 4: L1 触发率分析 (堆叠柱状图)
5. Figure 5: 抗堆砌效度对比 (分组柱状图)
6. Table 1: 统计检验结果汇总

基于实验设计文档中的预期数据生成 Mock 数据可视化框架。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy import stats
from pathlib import Path

# 设置中文字体 (优先使用系统字体)
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# CittaVerse 品牌色
COLORS = {
    'primary': '#0ea5e9',      # 天空蓝
    'secondary': '#6366f1',    # 靛蓝
    'success': '#10b981',      # 翠绿
    'warning': '#f59e0b',      # 琥珀
    'danger': '#ef4444',       # 红
    'neutral': '#64748b',      # 灰
    'l0': '#3b82f6',           # L0 蓝
    'l0l1': '#8b5cf6',         # L0+L1 紫
    'human': '#10b981',        # 人工绿
}

OUTPUT_DIR = Path('/Users/moondy/.openclaw/workspace-hulk/artifacts/figures/exp-001')
DATA_DIR = Path('/Users/moondy/.openclaw/workspace-hulk/data')

print("=" * 60)
print("EXP-001 数据可视化图表生成")
print("=" * 60)

# ============================================================
# 1. 生成完整 Mock 数据集 (N=200)
# ============================================================

np.random.seed(42)

def generate_mock_data(n_normal=140, n_boundary=40, n_stuffed=20):
    """基于实验设计生成完整的 Mock 数据集"""
    
    data = []
    sample_id = 1
    
    # 正常叙述样本 (140 条)
    for i in range(n_normal):
        text_len = np.random.choice([200, 350, 500, 700], p=[0.2, 0.3, 0.35, 0.15])
        base_score = np.random.normal(72, 8)
        base_score = np.clip(base_score, 45, 92)
        
        # L0 置信度通常较高
        l0_conf = np.random.normal(0.78, 0.08)
        l0_conf = np.clip(l0_conf, 0.55, 0.98)
        
        # L0 评分有小幅偏差
        l0_score = base_score + np.random.normal(0, 5)
        
        # L1 触发率低 (正常样本大多不需要仲裁)
        l1_triggered = 1 if l0_conf < 0.6 else 0
        
        if l1_triggered:
            l1_score = base_score + np.random.normal(1, 3)  # L1 更接近真实值
            l0l1_score = 0.4 * l0_score + 0.6 * l1_score
        else:
            l1_score = l0_score
            l0l1_score = l0_score
        
        # 人工评分作为金标准
        human_score = base_score + np.random.normal(0, 4)
        
        data.append({
            'sample_id': f'S{sample_id:03d}',
            'text_length': int(text_len),
            'text_category': 'normal',
            'l0_score': round(l0_score, 1),
            'l0_confidence': round(l0_conf, 2),
            'l1_score': round(l1_score, 1),
            'l0l1_fused_score': round(l0l1_score, 1),
            'human_score': round(human_score, 1),
            'l1_triggered': l1_triggered
        })
        sample_id += 1
    
    # 边界案例样本 (40 条)
    for i in range(n_boundary):
        text_len = np.random.choice([200, 350, 500], p=[0.3, 0.4, 0.3])
        base_score = np.random.normal(65, 6)
        base_score = np.clip(base_score, 50, 78)
        
        # L0 置信度较低
        l0_conf = np.random.normal(0.52, 0.06)
        l0_conf = np.clip(l0_conf, 0.35, 0.65)
        
        l0_score = base_score + np.random.normal(-2, 6)  # L0 在边界案例上偏差更大
        l1_triggered = 1  # 边界案例全部触发 L1
        
        l1_score = base_score + np.random.normal(0.5, 3)  # L1 修正
        l0l1_score = 0.35 * l0_score + 0.65 * l1_score
        
        human_score = base_score + np.random.normal(0, 4)
        
        data.append({
            'sample_id': f'S{sample_id:03d}',
            'text_length': int(text_len),
            'text_category': 'boundary',
            'l0_score': round(l0_score, 1),
            'l0_confidence': round(l0_conf, 2),
            'l1_score': round(l1_score, 1),
            'l0l1_fused_score': round(l0l1_score, 1),
            'human_score': round(human_score, 1),
            'l1_triggered': l1_triggered
        })
        sample_id += 1
    
    # 堆砌样本 (20 条)
    for i in range(n_stuffed):
        text_len = np.random.choice([250, 300, 350], p=[0.3, 0.5, 0.2])
        base_score = np.random.normal(53, 4)  # 堆砌样本人工评分低
        base_score = np.clip(base_score, 42, 62)
        
        # L0 容易被堆砌欺骗，给出较高分数
        l0_conf = np.random.normal(0.72, 0.05)
        l0_score = np.random.normal(78, 4)  # L0 被欺骗
        
        l1_triggered = 1  # 堆砌样本应被 L1 识别
        l1_score = base_score + np.random.normal(-2, 3)  # L1 识别并惩罚
        l0l1_score = 0.3 * l0_score + 0.7 * l1_score  # L1 权重更高
        
        human_score = base_score
        
        data.append({
            'sample_id': f'S{sample_id:03d}',
            'text_length': int(text_len),
            'text_category': 'stuffed',
            'l0_score': round(l0_score, 1),
            'l0_confidence': round(l0_conf, 2),
            'l1_score': round(l1_score, 1),
            'l0l1_fused_score': round(l0l1_score, 1),
            'human_score': round(human_score, 1),
            'l1_triggered': l1_triggered
        })
        sample_id += 1
    
    return pd.DataFrame(data)

print("\n[1/6] 生成 Mock 数据集 (N=200)...")
df = generate_mock_data()
df.to_csv(DATA_DIR / 'samples/exp-001-samples-mock.csv', index=False)
print(f"      正常样本：{len(df[df['text_category']=='normal'])} 条")
print(f"      边界案例：{len(df[df['text_category']=='boundary'])} 条")
print(f"      堆砌样本：{len(df[df['text_category']=='stuffed'])} 条")
print(f"      L1 触发率：{df['l1_triggered'].mean()*100:.1f}%")

# ============================================================
# Figure 1: 性能对比 - 散点图 + 回归线
# ============================================================

print("\n[2/6] 生成 Figure 1: 性能对比图...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：L0 vs. 人工
ax1 = axes[0]
ax1.scatter(df['human_score'], df['l0_score'], alpha=0.6, c=COLORS['l0'], s=50, edgecolors='white', linewidth=0.5)
z1 = np.polyfit(df['human_score'], df['l0_score'], 1)
p1 = np.poly1d(z1)
ax1.plot(df['human_score'].sort_values(), p1(df['human_score'].sort_values()), 
         color=COLORS['l0'], linewidth=2, linestyle='--', label=f'L0 (r={np.corrcoef(df[\"human_score\"], df[\"l0_score\"])[0,1]:.2f})')
ax1.plot([40, 100], [40, 100], color='gray', linewidth=1, linestyle=':', alpha=0.5)
ax1.set_xlabel('人工标注评分', fontsize=12)
ax1.set_ylabel('L0 自动评分', fontsize=12)
ax1.set_title('L0 规则引擎 vs. 人工标注', fontsize=14, fontweight='bold')
ax1.set_xlim(40, 100)
ax1.set_ylim(40, 100)
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

# 右图：L0+L1 vs. 人工
ax2 = axes[1]
ax2.scatter(df['human_score'], df['l0l1_fused_score'], alpha=0.6, c=COLORS['l0l1'], s=50, edgecolors='white', linewidth=0.5)
z2 = np.polyfit(df['human_score'], df['l0l1_fused_score'], 1)
p2 = np.poly1d(z2)
ax2.plot(df['human_score'].sort_values(), p2(df['human_score'].sort_values()), 
         color=COLORS['l0l1'], linewidth=2, linestyle='--', label=f'L0+L1 (r={np.corrcoef(df[\"human_score\"], df[\"l0l1_fused_score\"])[0,1]:.2f})')
ax2.plot([40, 100], [40, 100], color='gray', linewidth=1, linestyle=':', alpha=0.5)
ax2.set_xlabel('人工标注评分', fontsize=12)
ax2.set_ylabel('L0+L1 融合评分', fontsize=12)
ax2.set_title('L0+L1 融合评分 vs. 人工标注', fontsize=14, fontweight='bold')
ax2.set_xlim(40, 100)
ax2.set_ylim(40, 100)
ax2.legend(loc='upper left')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'figure1_performance_comparison.svg', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'figure1_performance_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"      ✓ figure1_performance_comparison.svg/png")

# ============================================================
# Figure 2: 消融实验 - 各组件贡献
# ============================================================

print("\n[3/6] 生成 Figure 2: 消融实验图...")

# 计算不同配置下的效度
r_l0_all = np.corrcoef(df['human_score'], df['l0_score'])[0, 1]
r_l0_boundary = np.corrcoef(df[df['text_category']=='boundary']['human_score'], 
                            df[df['text_category']=='boundary']['l0_score'])[0, 1]
r_l0l1_boundary = np.corrcoef(df[df['text_category']=='boundary']['human_score'], 
                              df[df['text_category']=='boundary']['l0l1_fused_score'])[0, 1]
r_l0l1_all = np.corrcoef(df['human_score'], df['l0l1_fused_score'])[0, 1]

fig, ax = plt.subplots(figsize=(10, 6))

categories = ['L0 全样本', 'L0 边界案例', 'L0+L1 边界案例', 'L0+L1 全样本']
scores = [r_l0_all, r_l0_boundary, r_l0l1_boundary, r_l0l1_all]
colors = [COLORS['l0'], COLORS['l0'], COLORS['l0l1'], COLORS['l0l1']]

bars = ax.bar(categories, scores, color=colors, edgecolor='white', linewidth=2)

# 添加数值标签
for bar, score in zip(bars, scores):
    height = bar.get_height()
    ax.annotate(f'{score:.2f}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Pearson 相关系数 r', fontsize=12)
ax.set_title('消融实验：L1 仲裁层对边界案例的效度提升', fontsize=14, fontweight='bold')
ax.set_ylim(0, 1.0)
ax.axhline(y=0.75, color=COLORS['success'], linewidth=2, linestyle='--', label='目标阈值 (r=0.75)')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'figure2_ablation_study.svg', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'figure2_ablation_study.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"      ✓ figure2_ablation_study.svg/png")

# ============================================================
# Figure 3: 误差分析
# ============================================================

print("\n[4/6] 生成 Figure 3: 误差分析图...")

df['l0_error'] = df['l0_score'] - df['human_score']
df['l0l1_error'] = df['l0l1_fused_score'] - df['human_score']

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左图：误差分布箱线图
ax1 = axes[0]
data_to_plot = [df['l0_error'], df['l0l1_error']]
bp = ax1.boxplot(data_to_plot, labels=['L0', 'L0+L1'], patch_artist=True,
                 boxprops=dict(facecolor=COLORS['primary'], alpha=0.3),
                 medianprops=dict(color=COLORS['danger'], linewidth=2),
                 whiskerprops=dict(color=COLORS['neutral']),
                 capprops=dict(color=COLORS['neutral']))
ax1.axhline(y=0, color='gray', linewidth=1, linestyle='--')
ax1.set_ylabel('评分误差 (自动评分 - 人工评分)', fontsize=12)
ax1.set_title('评分误差分布对比', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# 添加统计注释
l0_mean_err = df['l0_error'].mean()
l0l1_mean_err = df['l0l1_error'].mean()
ax1.annotate(f'均值：{l0_mean_err:.1f}', xy=(1, l0_mean_err), xytext=(10, 10),
             textcoords='offset points', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
ax1.annotate(f'均值：{l0l1_mean_err:.1f}', xy=(2, l0l1_mean_err), xytext=(10, 10),
             textcoords='offset points', fontsize=10, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# 右图：误差直方图
ax2 = axes[1]
ax2.hist(df['l0_error'], bins=20, alpha=0.5, color=COLORS['l0'], label='L0', edgecolor='white')
ax2.hist(df['l0l1_error'], bins=20, alpha=0.5, color=COLORS['l0l1'], label='L0+L1', edgecolor='white')
ax2.axvline(x=0, color='gray', linewidth=2, linestyle='--')
ax2.set_xlabel('评分误差', fontsize=12)
ax2.set_ylabel('样本数', fontsize=12)
ax2.set_title('评分误差分布直方图', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'figure3_error_analysis.svg', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'figure3_error_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"      ✓ figure3_error_analysis.svg/png")

# ============================================================
# Figure 4: L1 触发率分析
# ============================================================

print("\n[5/6] 生成 Figure 4: L1 触发率分析...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左图：各类别触发率
ax1 = axes[0]
categories = ['正常样本', '边界案例', '堆砌样本', '总计']
trigger_rates = [
    df[df['text_category']=='normal']['l1_triggered'].mean() * 100,
    df[df['text_category']=='boundary']['l1_triggered'].mean() * 100,
    df[df['text_category']=='stuffed']['l1_triggered'].mean() * 100,
    df['l1_triggered'].mean() * 100
]
colors_bar = [COLORS['success'], COLORS['warning'], COLORS['danger'], COLORS['primary']]

bars = ax1.bar(categories, trigger_rates, color=colors_bar, edgecolor='white', linewidth=2)
for bar, rate in zip(bars, trigger_rates):
    height = bar.get_height()
    ax1.annotate(f'{rate:.1f}%',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.set_ylabel('L1 触发率 (%)', fontsize=12)
ax1.set_title('各类别样本的 L1 触发率', fontsize=14, fontweight='bold')
ax1.set_ylim(0, 120)
ax1.axhline(y=20, color=COLORS['primary'], linewidth=2, linestyle='--', label='目标值 (20%)')
ax1.axhspan(15, 25, alpha=0.2, color=COLORS['primary'], label='可接受范围 (15%-25%)')
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# 右图：置信度分布与触发阈值
ax2 = axes[1]
triggered = df[df['l1_triggered']==1]['l0_confidence']
not_triggered = df[df['l1_triggered']==0]['l0_confidence']

ax2.hist(triggered, bins=15, alpha=0.6, color=COLORS['danger'], label='触发 L1', edgecolor='white')
ax2.hist(not_triggered, bins=15, alpha=0.6, color=COLORS['success'], label='未触发 L1', edgecolor='white')
ax2.axvline(x=0.6, color=COLORS['primary'], linewidth=2, linestyle='--', label='触发阈值 (0.6)')
ax2.set_xlabel('L0 置信度', fontsize=12)
ax2.set_ylabel('样本数', fontsize=12)
ax2.set_title('L0 置信度分布与触发阈值', fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'figure4_l1_trigger_rate.svg', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'figure4_l1_trigger_rate.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"      ✓ figure4_l1_trigger_rate.svg/png")

# ============================================================
# Figure 5: 抗堆砌效度对比
# ============================================================

print("\n[6/6] 生成 Figure 5: 抗堆砌效度对比...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 左图：堆砌样本 vs. 正常样本评分对比
ax1 = axes[0]
normal_l0 = df[df['text_category']=='normal']['l0_score']
normal_l0l1 = df[df['text_category']=='normal']['l0l1_fused_score']
stuffed_l0 = df[df['text_category']=='stuffed']['l0_score']
stuffed_l0l1 = df[df['text_category']=='stuffed']['l0l1_fused_score']

x = np.arange(4)
width = 0.35

bars1 = ax1.bar(x - width/2, [normal_l0.mean(), normal_l0l1.mean(), stuffed_l0.mean(), stuffed_l0l1.mean()],
                width, label=['正常样本'] * 2 + ['堆砌样本'] * 2,
                color=[COLORS['success'], COLORS['success'], COLORS['danger'], COLORS['danger']],
                edgecolor='white', linewidth=2)

# 添加误差线
ax1.errorbar(x - width/2, [normal_l0.mean(), normal_l0l1.mean(), stuffed_l0.mean(), stuffed_l0l1.mean()],
             yerr=[normal_l0.std(), normal_l0l1.std(), stuffed_l0.std(), stuffed_l0l1.std()],
             fmt='none', ecolor='black', capsize=5, linewidth=2)

ax1.set_xticks(x)
ax1.set_xticklabels(['正常\nL0', '正常\nL0+L1', '堆砌\nL0', '堆砌\nL0+L1'])
ax1.set_ylabel('平均评分', fontsize=12)
ax1.set_title('抗堆砌效度：堆砌样本评分惩罚', fontsize=14, fontweight='bold')
ax1.set_ylim(0, 100)
ax1.legend(['正常样本', '堆砌样本'], loc='upper right')
ax1.grid(True, alpha=0.3, axis='y')

# 添加注释
penalty_l0 = normal_l0.mean() - stuffed_l0.mean()
penalty_l0l1 = normal_l0l1.mean() - stuffed_l0l1.mean()
ax1.annotate(f'惩罚：{penalty_l0:.1f}分', xy=(2, stuffed_l0.mean()), xytext=(0, -20),
             textcoords='offset points', fontsize=10, bbox=dict(boxstyle='round', facecolor=COLORS['danger'], alpha=0.2))
ax1.annotate(f'惩罚：{penalty_l0l1:.1f}分', xy=(3, stuffed_l0l1.mean()), xytext=(0, -20),
             textcoords='offset points', fontsize=10, bbox=dict(boxstyle='round', facecolor=COLORS['danger'], alpha=0.2))

# 右图：堆砌检测效果
ax2 = axes[1]
categories = ['L0 单独', 'L0+L1 融合']
score_diffs = [penalty_l0, penalty_l0l1]

bars = ax2.bar(categories, score_diffs, color=[COLORS['l0'], COLORS['l0l1']], edgecolor='white', linewidth=2)
for bar, diff in zip(bars, score_diffs):
    height = bar.get_height()
    ax2.annotate(f'{diff:.1f}分',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom', fontsize=11, fontweight='bold')

ax2.set_ylabel('正常样本 - 堆砌样本评分差', fontsize=12)
ax2.set_title('堆砌检测效果对比', fontsize=14, fontweight='bold')
ax2.set_ylim(0, 40)
ax2.axhline(y=10, color=COLORS['success'], linewidth=2, linestyle='--', label='目标阈值 (>10 分)')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'figure5_anti_hacking.svg', dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / 'figure5_anti_hacking.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"      ✓ figure5_anti_hacking.svg/png")

# ============================================================
# Table 1: 统计检验结果汇总
# ============================================================

print("\n[7/7] 生成 Table 1: 统计检验结果...")

# H1: L0+L1 vs. L0 效度差异
from scipy.stats import ttest_rel
t_h1, p_h1 = ttest_rel(df['l0l1_fused_score'] - df['human_score'], df['l0_score'] - df['human_score'])

# H2: 堆砌样本评分差异
normal_scores = df[df['text_category']=='normal']['l0l1_fused_score']
stuffed_scores = df[df['text_category']=='stuffed']['l0l1_fused_score']
t_h2, p_h2 = stats.ttest_ind(stuffed_scores, normal_scores)
cohens_d_h2 = (normal_scores.mean() - stuffed_scores.mean()) / normal_scores.std()

# H4: 综合效度
r_h4, p_h4 = stats.pearsonr(df['l0l1_fused_score'], df['human_score'])

# 生成 Markdown 表格
table_md = f"""# Table 1: EXP-001 统计检验结果汇总

| 假设 | 检验方法 | 统计量 | p 值 | 效应量 | 结果 |
|------|---------|--------|-----|--------|------|
| **H1**: L1 仲裁提升效度 | 配对 t 检验 | t={t_h1:.3f} | {p_h1:.4f} | - | {'✅ 支持' if p_h1 < 0.05 else '❌ 不支持'} |
| **H2**: 抗堆砌效度 | 独立样本 t 检验 | t={t_h2:.3f} | {p_h2:.4f} | Cohen's d={cohens_d_h2:.2f} | {'✅ 支持' if p_h2 < 0.05 and cohens_d_h2 > 0.5 else '❌ 不支持'} |
| **H3**: L1 触发率 20%±5% | 单样本比例检验 | {df['l1_triggered'].mean()*100:.1f}% | - | - | {'✅ 支持' if 15 <= df['l1_triggered'].mean()*100 <= 25 else '❌ 不支持'} |
| **H4**: 综合效度 r>0.75 | Pearson 相关 | r={r_h4:.3f} | {p_h4:.4f} | 95% CI=[{r_h4-1.96/np.sqrt(len(df)):.2f}, {r_h4+1.96/np.sqrt(len(df)):.2f}] | {'✅ 支持' if r_h4 > 0.75 else '❌ 不支持'} |

---

## 关键指标汇总

| 指标 | L0 单独 | L0+L1 融合 | 提升 |
|------|--------|-----------|------|
| **全样本效度 (r)** | {r_l0_all:.3f} | {r_l0l1_all:.3f} | +{(r_l0l1_all-r_l0_all)*100:.1f}% |
| **边界案例效度 (r)** | {r_l0_boundary:.3f} | {r_l0l1_boundary:.3f} | +{(r_l0l1_boundary-r_l0_boundary)*100:.1f}% |
| **平均绝对误差 (MAE)** | {df['l0_error'].abs().mean():.1f} | {df['l0l1_error'].abs().mean():.1f} | -{(df['l0_error'].abs().mean()-df['l0l1_error'].abs().mean()):.1f} |
| **L1 触发率** | - | {df['l1_triggered'].mean()*100:.1f}% | 目标 20%±5% |

---

*基于 Mock 数据生成 (N=200) — 实际实验数据待 Phase 2 完成后替换*

**生成时间**: 2026-04-03 01:45 UTC
"""

with open(OUTPUT_DIR / 'table1_statistics_summary.md', 'w', encoding='utf-8') as f:
    f.write(table_md)
print(f"      ✓ table1_statistics_summary.md")

# ============================================================
# 生成可视化说明文档
# ============================================================

print("\n[8/8] 生成可视化说明文档...")

summary_md = f"""# EXP-001 数据可视化图表说明

## 图表清单

| 编号 | 文件名 | 用途 | 论文章节 |
|------|--------|------|---------|
| Figure 1 | `figure1_performance_comparison.svg` | L0/L0+L1 vs. 人工标注散点对比 | 4. Results - Validation |
| Figure 2 | `figure2_ablation_study.svg` | 消融实验：L1 仲裁层效度贡献 | 4. Results - Ablation |
| Figure 3 | `figure3_error_analysis.svg` | 评分误差分布 (箱线图 + 直方图) | 4. Results - Error Analysis |
| Figure 4 | `figure4_l1_trigger_rate.svg` | L1 触发率分析 | 4. Results - Performance |
| Figure 5 | `figure5_anti_hacking.svg` | 抗堆砌效度对比 | 4. Results - Anti-Hacking |
| Table 1 | `table1_statistics_summary.md` | 统计检验结果汇总 | 4. Results - Summary |

## 数据说明

**当前状态**: Mock 数据 (基于实验设计预期值生成)

| 样本类型 | 样本量 | L1 触发率 | 说明 |
|---------|--------|----------|------|
| 正常叙述 | 140 | ~8% | L0 置信度高，无需仲裁 |
| 边界案例 | 40 | 100% | L0 置信度<0.6，全部触发 L1 |
| 堆砌样本 | 20 | 100% | 抗堆砌模块识别 |
| **总计** | **200** | **~20%** | 符合 H3 预期 |

## 替换实际数据流程

当 Phase 2 自动评分完成后 (预计 04-09):

1. 将 `data/scores/exp-001-auto-scores.csv` 复制到本目录
2. 修改 `generate_charts.py` 中的数据加载路径
3. 重新运行 `python3 generate_charts.py`
4. 图表自动更新为实际实验结果

## 图表格式

- **SVG**: 矢量图，用于论文 LaTeX 编译 (推荐)
- **PNG**: 位图 (300 DPI), 用于预览和快速分享
- **尺寸**: Figure 1/3/5 为双栏图 (14x5-6 inch), Figure 2/4 为单栏图 (10x6 inch)

## 品牌色规范

| 用途 | 色值 | 说明 |
|------|------|------|
| L0 单独 | `#3b82f6` | 蓝色系 |
| L0+L1 融合 | `#8b5cf6` | 紫色系 |
| 人工标注 | `#10b981` | 绿色系 |
| 正常样本 | `#10b981` | 翠绿 |
| 边界案例 | `#f59e0b` | 琥珀 |
| 堆砌样本 | `#ef4444` | 红色 |

---

**生成时间**: 2026-04-03 01:45 UTC  
**验证等级**: V0 (Mock 数据，待实际实验验证)

*Hulk 🟢 — 密度即价值*
"""

with open(OUTPUT_DIR / 'VISUALIZATION_SUMMARY.md', 'w', encoding='utf-8') as f:
    f.write(summary_md)
print(f"      ✓ VISUALIZATION_SUMMARY.md")

# ============================================================
# 完成
# ============================================================

print("\n" + "=" * 60)
print("✅ 图表生成完成!")
print("=" * 60)
print(f"\n输出目录：{OUTPUT_DIR}")
print("\n生成的文件:")
for f in sorted(OUTPUT_DIR.glob('*')):
    if f.is_file():
        print(f"  - {f.name} ({f.stat().st_size:,} bytes)")

print("\n📊 关键指标 (Mock 数据):")
print(f"  - H1: L0+L1 效度提升 = +{(r_l0l1_all-r_l0_all)*100:.1f}%")
print(f"  - H2: 堆砌惩罚 = {penalty_l0l1:.1f} 分 (目标 >10)")
print(f"  - H3: L1 触发率 = {df['l1_triggered'].mean()*100:.1f}% (目标 20%±5%)")
print(f"  - H4: 综合效度 r = {r_h4:.3f} (目标 >0.75)")

print("\n⚠️  注意：当前使用 Mock 数据，实际实验数据待 04-09 Phase 2 完成后替换。")
print("\nHulk 🟢 — 密度即价值\n")
