#!/usr/bin/env python3
"""
VSNC Paper Figure Generator
Generates publication-ready SVG figures for the VSNC narrative scoring paper.

Usage:
    python generate_paper_figures.py --output ./output/

Dependencies:
    pip install matplotlib seaborn pandas numpy
"""

import argparse
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set publication-ready style
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
    'font.size': 10,
    'axes.labelsize': 8,
    'axes.titlesize': 10,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'legend.fontsize': 7,
    'figure.figsize': (7, 5),
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.format': 'svg',
})

# CittaVerse brand colors
COLORS = {
    'primary': '#0ea5e9',      # Sky blue
    'secondary': '#6366f1',    # Indigo
    'success': '#22c55e',      # Green
    'warning': '#f59e0b',      # Amber
    'danger': '#ef4444',       # Red
    'gray': '#6b7280',         # Gray
}

# Colorblind-safe palette
CB_PALETTE = sns.color_palette('colorblind', 10)


# =============================================================================
# Data: 04-04 Night Long Run Experiment (28 samples, 5 repetitions)
# =============================================================================

CATEGORY_DATA = {
    'Category': [
        'adversarial_emotion', 'positive', 'boundary_long', 'traumatic',
        'noise_typo', 'negative', 'reflective', 'neutral', 'cross_lingual',
        'adversarial_nonsense', 'noise_asr', 'boundary_short'
    ],
    'N': [2, 5, 1, 2, 2, 3, 2, 2, 2, 2, 2, 3],
    'Mean': [47.25, 46.06, 49.80, 43.75, 43.50, 42.90, 42.25, 40.00, 39.45, 34.50, 31.50, 29.00],
    'Std': [2.47, 3.21, 0.00, 1.06, 0.71, 2.85, 1.77, 0.00, 0.64, 0.71, 0.71, 0.50],
    'Min': [45.50, 42.50, 49.80, 43.00, 43.00, 40.50, 41.00, 40.00, 39.00, 34.00, 31.00, 28.50],
    'Max': [49.00, 50.20, 49.80, 44.50, 44.00, 46.00, 43.50, 40.00, 39.90, 35.00, 32.00, 29.50],
    'Group': [
        'adversarial', 'normal', 'boundary', 'normal',
        'noise', 'normal', 'normal', 'normal', 'normal',
        'adversarial', 'noise', 'boundary'
    ]
}

DIMENSION_DATA = {
    'Dimension': [
        'temporal_coherence', 'information_density', 'event_richness',
        'causal_coherence', 'identity_integration', 'emotional_depth'
    ],
    'Mean': [100.00, 67.08, 26.79, 23.57, 20.90, 8.05],
    'Std': [0.00, 12.45, 8.92, 9.34, 8.15, 4.23],
    'Min': [100.00, 40.00, 10.00, 5.00, 5.00, 0.00],
    'Max': [100.00, 95.00, 45.00, 42.00, 38.00, 18.00],
    'Theoretical_Importance': ['High', 'High', 'Medium', 'Medium', 'Medium', 'Low']
}

ABLATION_COMPONENT_DATA = {
    'Condition': [
        'Full System', '-Memory Graph', '-Strategy', '-Feedback', '-Sensory', '-Social'
    ],
    'Score': [78.5, 68.2, 64.5, 61.3, 58.7, 55.1],
    'Drop': [0.0, 10.3, 14.0, 17.2, 19.8, 23.4]
}

ABLATION_PROMPT_DATA = {
    'Strategy': ['P1 Zero-shot', 'P2 Few-shot', 'P3 Chain-of-Thought', 'P4 Structured'],
    'ICC': [0.64, 0.72, 0.76, 0.78],
    'JSON_Success': [78, 86, 88, 94]
}

LLM_COMPARISON_DATA = {
    'Model': ['Qwen-Plus', 'GPT-4o-mini', 'Claude-3-Haiku', 'GLM-4-Flash'],
    'ICC': [0.78, 0.75, 0.76, 0.72],
    'Cost_Yuan': [0.004, 0.001, 0.002, 0.001],
    'Selected': [True, False, False, False]
}


# =============================================================================
# Figure Generation Functions
# =============================================================================

def generate_figure10_robustness(output_dir: Path):
    """Figure 10: Robustness by Category - Box plot with individual points"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Prepare data for boxplot
    df_cat = pd.DataFrame(CATEGORY_DATA)
    df_cat = df_cat.sort_values('Mean', ascending=True)
    
    # Create box plot
    group_colors = {
        'normal': COLORS['primary'],
        'noise': COLORS['warning'],
        'adversarial': COLORS['danger'],
        'boundary': COLORS['gray']
    }
    
    boxprops = dict(linewidth=1, color=COLORS['gray'])
    medianprops = dict(linewidth=2, color=COLORS['primary'])
    whiskerprops = dict(linewidth=1, color=COLORS['gray'])
    capprops = dict(linewidth=1, color=COLORS['gray'])
    
    # Simulate boxplot from summary stats (in real usage, would use raw data)
    positions = np.arange(len(df_cat))
    
    for i, (_, row) in enumerate(df_cat.iterrows()):
        color = group_colors.get(row['Group'], COLORS['gray'])
        # Draw simplified box representation
        ax.axvline(i, ymin=(row['Min'])/100, ymax=(row['Max'])/100, 
                   color=color, linewidth=2, alpha=0.6)
        ax.plot(i, row['Mean'], 'o', color=color, markersize=8)
    
    ax.set_xticks(positions)
    ax.set_xticklabels(df_cat['Category'], rotation=45, ha='right')
    ax.set_ylabel('Narrative Quality Score')
    ax.set_xlabel('Category')
    ax.set_title('Figure 10: Robustness by Category (N=28)', fontweight='bold')
    ax.set_ylim(20, 60)
    ax.grid(axis='y', alpha=0.3)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=COLORS['primary'], label='Normal (N=16)'),
        Patch(facecolor=COLORS['warning'], label='Noise (N=4)'),
        Patch(facecolor=COLORS['danger'], label='Adversarial (N=4)'),
        Patch(facecolor=COLORS['gray'], label='Boundary (N=4)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure10_robustness_by_category.svg')
    plt.close()
    print(f"✓ Generated: {output_dir / 'figure10_robustness_by_category.svg'}")


def generate_figure11_dimensions(output_dir: Path):
    """Figure 11: Dimension Distribution - Bar chart with error bars"""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    df_dim = pd.DataFrame(DIMENSION_DATA)
    
    positions = np.arange(len(df_dim))
    colors = [COLORS['primary']] * len(df_dim)
    colors[0] = COLORS['warning']  # Highlight temporal_coherence anomaly
    
    ax.bar(positions, df_dim['Mean'], yerr=df_dim['Std'],
           color=colors, capsize=5, edgecolor=COLORS['gray'], linewidth=1)
    
    ax.set_xticks(positions)
    ax.set_xticklabels(df_dim['Dimension'], rotation=45, ha='right')
    ax.set_ylabel('Score')
    ax.set_xlabel('Dimension')
    ax.set_title('Figure 11: Dimension Distribution (Mock Event Extraction)', fontweight='bold')
    ax.set_ylim(0, 110)
    ax.grid(axis='y', alpha=0.3)
    
    # Annotate temporal_coherence anomaly
    ax.annotate('⚠️ Mock artifact\n(constant 100)',
                xy=(0, 100), xytext=(0.5, 85),
                arrowprops=dict(arrowstyle='->', color=COLORS['danger']),
                color=COLORS['danger'], fontsize=7, ha='center')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure11_dimension_distribution.svg')
    plt.close()
    print(f"✓ Generated: {output_dir / 'figure11_dimension_distribution.svg'}")


def generate_figure7_ablation_components(output_dir: Path):
    """Figure 7: Component Ablation Study"""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    df = pd.DataFrame(ABLATION_COMPONENT_DATA)
    
    positions = np.arange(len(df))
    colors = [COLORS['primary']] * len(df)
    colors[0] = COLORS['success']  # Highlight full system
    
    bars = ax.bar(positions, df['Score'], color=colors, edgecolor=COLORS['gray'], linewidth=1)
    
    # Add drop annotations
    for i, (bar, drop) in enumerate(zip(bars, df['Drop'])):
        if drop > 0:
            ax.annotate(f'-{drop:.1f}',
                       xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                       xytext=(0, 5), textcoords='offset points',
                       ha='center', va='bottom', fontsize=7, color=COLORS['danger'])
    
    ax.set_xticks(positions)
    ax.set_xticklabels(df['Condition'], rotation=45, ha='right')
    ax.set_ylabel('Narrative Quality Score')
    ax.set_title('Figure 7: Component Ablation Study', fontweight='bold')
    ax.set_ylim(40, 85)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure7_ablation_components.svg')
    plt.close()
    print(f"✓ Generated: {output_dir / 'figure7_ablation_components.svg'}")


def generate_figure8_ablation_prompts(output_dir: Path):
    """Figure 8: Prompt Engineering Ablation"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    
    df = pd.DataFrame(ABLATION_PROMPT_DATA)
    positions = np.arange(len(df))
    
    # ICC plot
    bars1 = ax1.bar(positions, df['ICC'], color=COLORS['primary'],
                    edgecolor=COLORS['gray'], linewidth=1)
    ax1.set_xticks(positions)
    ax1.set_xticklabels(df['Strategy'], rotation=45, ha='right')
    ax1.set_ylabel('ICC vs Human')
    ax1.set_title('A: Rating Consistency', fontweight='bold')
    ax1.set_ylim(0.5, 0.85)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars1, df['ICC']):
        ax1.annotate(f'{val:.2f}',
                    xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 5), textcoords='offset points',
                    ha='center', va='bottom', fontsize=7)
    
    # JSON success plot
    bars2 = ax2.bar(positions, df['JSON_Success'], color=COLORS['secondary'],
                    edgecolor=COLORS['gray'], linewidth=1)
    ax2.set_xticks(positions)
    ax2.set_xticklabels(df['Strategy'], rotation=45, ha='right')
    ax2.set_ylabel('JSON Parsing Success Rate (%)')
    ax2.set_title('B: Output Reliability', fontweight='bold')
    ax2.set_ylim(60, 100)
    ax2.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars2, df['JSON_Success']):
        ax2.annotate(f'{val}%',
                    xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                    xytext=(0, 5), textcoords='offset points',
                    ha='center', va='bottom', fontsize=7)
    
    plt.suptitle('Figure 8: Prompt Engineering Ablation', fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'figure8_ablation_prompts.svg')
    plt.close()
    print(f"✓ Generated: {output_dir / 'figure8_ablation_prompts.svg'}")


def generate_figure9_llm_comparison(output_dir: Path):
    """Figure 9: LLM Backend Comparison"""
    fig, ax = plt.subplots(figsize=(7, 5))
    
    df = pd.DataFrame(LLM_COMPARISON_DATA)
    
    # Scatter plot
    for i, row in df.iterrows():
        color = COLORS['success'] if row['Selected'] else COLORS['gray']
        size = 100 if row['Selected'] else 50
        marker = 's' if row['Selected'] else 'o'
        
        ax.scatter(row['Cost_Yuan'], row['ICC'], s=size, c=color,
                  marker=marker, edgecolor=COLORS['gray'], linewidth=1,
                  label=row['Model'] if row['Selected'] else None)
        
        # Annotate model name
        ax.annotate(row['Model'],
                   xy=(row['Cost_Yuan'], row['ICC']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=7)
    
    ax.set_xlabel('Cost (¥/eval)')
    ax.set_ylabel('ICC vs Human')
    ax.set_title('Figure 9: LLM Backend Comparison', fontweight='bold')
    ax.grid(alpha=0.3)
    
    # Add legend
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'figure9_llm_comparison.svg')
    plt.close()
    print(f"✓ Generated: {output_dir / 'figure9_llm_comparison.svg'}")


def save_data_csv(output_dir: Path):
    """Save all figure data to CSV for reference"""
    all_data = {}
    all_data['category_robustness'] = pd.DataFrame(CATEGORY_DATA)
    all_data['dimension_distribution'] = pd.DataFrame(DIMENSION_DATA)
    all_data['ablation_components'] = pd.DataFrame(ABLATION_COMPONENT_DATA)
    all_data['ablation_prompts'] = pd.DataFrame(ABLATION_PROMPT_DATA)
    all_data['llm_comparison'] = pd.DataFrame(LLM_COMPARISON_DATA)
    
    with open(output_dir / 'figure_data.csv', 'w') as f:
        for name, df in all_data.items():
            f.write(f'# {name}\n')
            df.to_csv(f, index=False)
            f.write('\n')
    
    print(f"✓ Saved: {output_dir / 'figure_data.csv'}")


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate VSNC paper figures')
    parser.add_argument('--output', type=str, default='./output',
                       help='Output directory for SVG files')
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating figures to: {output_dir.absolute()}")
    print("=" * 60)
    
    # Generate all figures
    generate_figure7_ablation_components(output_dir)
    generate_figure8_ablation_prompts(output_dir)
    generate_figure9_llm_comparison(output_dir)
    generate_figure10_robustness(output_dir)
    generate_figure11_dimensions(output_dir)
    
    # Save data
    save_data_csv(output_dir)
    
    print("=" * 60)
    print("✓ All figures generated successfully!")
    print(f"Output directory: {output_dir.absolute()}")


if __name__ == '__main__':
    main()
