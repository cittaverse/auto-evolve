# EXP-001 数据分析代码框架

**版本**: v1.0  
**创建日期**: 2026-04-03 00:45 UTC  
**适用实验**: Multi-Agent Scorer v0.6 效度验证 (EXP-001)  
**语言**: Python 3.9+  
**依赖**: pandas, scipy, numpy, matplotlib, seaborn, pingouin

---

## 一、项目结构

```
exp-001-analysis/
├── data/
│   ├── samples/
│   │   └── exp-001-samples.csv          # 200 条样本
│   ├── annotations/
│   │   ├── exp-001-annotator1.csv       # 标注员 1 评分
│   │   ├── exp-001-annotator2.csv       # 标注员 2 评分
│   │   └── exp-001-gold-standard.csv    # 金标准 (仲裁后)
│   └── scores/
│       └── exp-001-auto-scores.csv      # 自动评分结果
├── src/
│   ├── __init__.py
│   ├── data_loader.py                   # 数据加载与预处理
│   ├── reliability.py                   # 信度分析 (ICC, Cohen's κ)
│   ├── validity.py                      # 效度分析 (Pearson r, Williams' t)
│   ├── anti_hacking.py                  # 抗堆砌效度分析
│   ├── performance.py                   # 性能基准分析
│   └── visualization.py                 # 可视化图表
├── notebooks/
│   ├── 01_data_exploration.ipynb        # 数据探索
│   ├── 02_reliability_analysis.ipynb    # 信度分析
│   ├── 03_validity_analysis.ipynb       # 效度分析
│   ├── 04_anti_hacking_analysis.ipynb   # 抗堆砌分析
│   └── 05_performance_analysis.ipynb    # 性能分析
├── output/
│   ├── figures/                         # 图表输出
│   └── tables/                          # 表格输出
├── requirements.txt
└── README.md
```

---

## 二、核心分析脚本

### 2.1 数据加载与预处理 (`src/data_loader.py`)

```python
"""
EXP-001 数据加载与预处理模块
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict

class EXP001DataLoader:
    """EXP-001 实验数据加载器"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        
    def load_samples(self) -> pd.DataFrame:
        """加载样本数据"""
        return pd.read_csv(self.data_dir / "samples/exp-001-samples.csv")
    
    def load_annotations(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """加载标注数据"""
        annotator1 = pd.read_csv(self.data_dir / "annotations/exp-001-annotator1.csv")
        annotator2 = pd.read_csv(self.data_dir / "annotations/exp-001-annotator2.csv")
        gold_standard = pd.read_csv(self.data_dir / "annotations/exp-001-gold-standard.csv")
        return annotator1, annotator2, gold_standard
    
    def load_auto_scores(self) -> pd.DataFrame:
        """加载自动评分结果"""
        return pd.read_csv(self.data_dir / "scores/exp-001-auto-scores.csv")
    
    def merge_all_data(self) -> pd.DataFrame:
        """合并所有数据为分析就绪格式"""
        samples = self.load_samples()
        _, _, gold = self.load_annotations()
        auto = self.load_auto_scores()
        
        # 合并
        df = samples.merge(gold, on="sample_id", how="left")
        df = df.merge(auto, on="sample_id", how="left")
        
        return df
    
    def get_dimension_scores(self, df: pd.DataFrame, prefix: str = "") -> np.ndarray:
        """提取六维评分"""
        dims = ["C1", "C2", "C3", "C4", "C5", "C6"]
        return df[[f"{prefix}{d}" for d in dims]].values
    
    def get_overall_score(self, df: pd.DataFrame, prefix: str = "") -> np.ndarray:
        """提取总体评分"""
        return df[f"{prefix}overall"].values


# 使用示例
if __name__ == "__main__":
    loader = EXP001DataLoader()
    df = loader.merge_all_data()
    print(f"总样本量：{len(df)}")
    print(f"样本类型分布：\n{df['layer'].value_counts()}")
```

---

### 2.2 信度分析 (`src/reliability.py`)

```python
"""
EXP-001 信度分析模块
- 标注者间信度 (Cohen's κ, ICC)
- 内部一致性 (Cronbach's α)
"""

import numpy as np
import pandas as pd
import pingouin as pg
from scipy import stats
from typing import Tuple

def cohens_kappa(rater1: np.ndarray, rater2: np.ndarray) -> Tuple[float, float]:
    """
    计算 Cohen's κ (分类变量)
    
    对于连续评分，先离散化为 5 档 (0-20, 21-40, 41-60, 61-80, 81-100)
    """
    # 离散化
    bins = [0, 20, 40, 60, 80, 100]
    r1_cat = np.digitize(rater1, bins)
    r2_cat = np.digitize(rater2, bins)
    
    # 计算 κ
    kappa_result = pg.inter_rater_agreement([r1_cat, r2_cat], retake=False)
    kappa = kappa_result.values[0, 1]  # κ 值
    
    # 近似标准误和置信区间
    se = np.sqrt((1 - kappa) / (len(rater1) * (1 - kappa)))
    ci_low = kappa - 1.96 * se
    ci_high = kappa + 1.96 * se
    
    return kappa, (ci_low, ci_high)


def icc_two_way_random(rater1: np.ndarray, rater2: np.ndarray, 
                       confidence=0.95) -> Dict:
    """
    计算 ICC (双因素随机效应模型，ICC(2,1))
    
    适用于：两名标注员从更大标注员群体中随机抽取
    """
    data = pd.DataFrame({
        'rater1': rater1,
        'rater2': rater2
    })
    
    # 使用 pingouin 计算 ICC
    icc_result = pg.intraclass_corr(data=data.reset_index(), 
                                     targets='index', 
                                     raters='variable', 
                                     ratings='value')
    
    # 提取 ICC(2,1)
    icc_row = icc_result[icc_result['Type'] == 'ICC2']
    icc = icc_row['ICC'].values[0]
    ci_low = icc_row[f'CI{int((1-confidence)*100)}%'].values[0]
    ci_high = icc_row[f'CI{int((1+confidence)*100)}%'].values[0]
    
    return {
        'ICC': icc,
        'CI': (ci_low, ci_high),
        'F': icc_row['F'].values[0],
        'p': icc_row['pval'].values[0]
    }


def cronbach_alpha(data: np.ndarray) -> float:
    """
    计算 Cronbach's α (内部一致性)
    
    data: n_samples × n_items 矩阵
    """
    items = data.shape[1]
    variances = np.var(data, axis=0, ddof=1)
    total_variance = np.var(np.sum(data, axis=1), ddof=1)
    
    alpha = (items / (items - 1)) * (1 - np.sum(variances) / total_variance)
    return alpha


def analyze_reliability(annotator1: pd.DataFrame, 
                        annotator2: pd.DataFrame) -> Dict:
    """
    完整信度分析
    
    返回:
    - 各维度 Cohen's κ
    - 各维度 ICC
    - 总体评分信度
    - Cronbach's α (六维度内部一致性)
    """
    dims = ["C1", "C2", "C3", "C4", "C5", "C6"]
    
    results = {
        'cohens_kappa': {},
        'icc': {},
        'overall_kappa': None,
        'overall_icc': None,
        'cronbach_alpha_annotator1': None,
        'cronbach_alpha_annotator2': None
    }
    
    # 各维度信度
    for dim in dims:
        r1 = annotator1[dim].values
        r2 = annotator2[dim].values
        
        # Cohen's κ
        kappa, ci = cohens_kappa(r1, r2)
        results['cohens_kappa'][dim] = {'kappa': kappa, 'CI': ci}
        
        # ICC
        icc_result = icc_two_way_random(r1, r2)
        results['icc'][dim] = icc_result
    
    # 总体评分信度
    r1_overall = annotator1['overall'].values
    r2_overall = annotator2['overall'].values
    
    results['overall_kappa'] = cohens_kappa(r1_overall, r2_overall)
    results['overall_icc'] = icc_two_way_random(r1_overall, r2_overall)
    
    # Cronbach's α
    dims1 = annotator1[dims].values
    dims2 = annotator2[dims].values
    results['cronbach_alpha_annotator1'] = cronbach_alpha(dims1)
    results['cronbach_alpha_annotator2'] = cronbach_alpha(dims2)
    
    return results


# 使用示例
if __name__ == "__main__":
    # 加载数据
    from data_loader import EXP001DataLoader
    loader = EXP001DataLoader()
    a1, a2, _ = loader.load_annotations()
    
    # 信度分析
    results = analyze_reliability(a1, a2)
    
    print("=== 标注者间信度分析 ===")
    print(f"\n总体评分 ICC: {results['overall_icc']['ICC']:.3f} "
          f"95% CI [{results['overall_icc']['CI'][0]:.3f}, "
          f"{results['overall_icc']['CI'][1]:.3f}]")
    
    print("\n各维度 ICC:")
    for dim, icc in results['icc'].items():
        print(f"  {dim}: {icc['ICC']:.3f} (p={icc['p']:.4f})")
    
    print("\n各维度 Cohen's κ:")
    for dim, kappa in results['cohens_kappa'].items():
        print(f"  {dim}: {kappa['kappa']:.3f} 95% CI [{kappa['CI'][0]:.3f}, {kappa['CI'][1]:.3f}]")
    
    print(f"\nCronbach's α (标注员 1): {results['cronbach_alpha_annotator1']:.3f}")
    print(f"Cronbach's α (标注员 2): {results['cronbach_alpha_annotator2']:.3f}")
```

---

### 2.3 效度分析 (`src/validity.py`)

```python
"""
EXP-001 效度分析模块
- Pearson 相关系数
- Williams' t-test (相关系数差异检验)
- Bland-Altman 一致性分析
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Dict
import pingouin as pg

def pearson_correlation(x: np.ndarray, y: np.ndarray) -> Dict:
    """
    计算 Pearson 相关系数及置信区间
    """
    r, p = stats.pearsonr(x, y)
    
    # Bootstrap 置信区间
    ci_result = stats.bootstrap((x, y), 
                                 statistic=lambda a, b: np.corrcoef(a, b)[0, 1],
                                 confidence_level=0.95,
                                 n_resamples=10000)
    
    return {
        'r': r,
        'p': p,
        'CI': (ci_result.confidence_interval.low, 
               ci_result.confidence_interval.high),
        'r_squared': r ** 2
    }


def williams_ttest(r1: float, r2: float, r12: float, n: int) -> Tuple[float, float]:
    """
    Williams' t-test: 检验两个相关系数差异是否显著
    
    参数:
    - r1: 第一个相关系数 (如 L0+L1 vs. 人工)
    - r2: 第二个相关系数 (如 L0 vs. 人工)
    - r12: 两个预测变量的相关系数 (L0 vs. L0+L1)
    - n: 样本量
    
    返回:
    - t: t 统计量
    - p: p 值
    """
    # Williams' t-test 公式
    numerator = (r1 - r2) * np.sqrt((n - 1) * (1 + r12))
    denominator = np.sqrt(2 * (n - 1) * (1 - r1**2 - r2**2 - r12**2) + 
                          2 * r1 * r2 * r12)
    
    t = numerator / denominator
    df = n - 3
    p = 2 * (1 - stats.t.cdf(abs(t), df))
    
    return t, p


def bland_altman_analysis(method1: np.ndarray, method2: np.ndarray) -> Dict:
    """
    Bland-Altman 一致性分析
    
    用于评估两种测量方法的一致性
    """
    # 计算差值和均值
    diff = method1 - method2
    mean = (method1 + method2) / 2
    
    # 均值差 (bias)
    bias = np.mean(diff)
    
    # 95% 一致性界限 (LoA)
    sd_diff = np.std(diff, ddof=1)
    loa_upper = bias + 1.96 * sd_diff
    loa_lower = bias - 1.96 * sd_diff
    
    # 95% CI for bias
    se_bias = sd_diff / np.sqrt(len(diff))
    bias_ci = (bias - 1.96 * se_bias, bias + 1.96 * se_bias)
    
    return {
        'bias': bias,
        'bias_CI': bias_ci,
        'LoA': (loa_lower, loa_upper),
        'sd_diff': sd_diff,
        'mean_diff': np.mean(diff),
        'limits_agreement_width': loa_upper - loa_lower
    }


def analyze_validity(gold_standard: pd.DataFrame, 
                     auto_scores: pd.DataFrame) -> Dict:
    """
    完整效度分析
    
    假设:
    - gold_standard 包含 'overall' 和 'C1'-'C6' 列
    - auto_scores 包含 'L0_overall', 'L0L1_overall', 'C1'-'C6' (L0), 'L1_C1'-'L1_C6' (L1 仲裁后)
    """
    # 合并数据
    df = gold_standard.merge(auto_scores, on="sample_id", how="inner")
    
    results = {
        'overall_correlation': {},
        'dimension_correlation': {},
        'williams_test': None,
        'bland_altman': {},
        'sample_size': len(df)
    }
    
    dims = ["C1", "C2", "C3", "C4", "C5", "C6"]
    
    # 1. 总体评分相关
    # L0 vs. 人工
    l0_corr = pearson_correlation(df['L0_overall'].values, 
                                   df['overall'].values)
    results['overall_correlation']['L0'] = l0_corr
    
    # L0+L1 vs. 人工
    l0l1_corr = pearson_correlation(df['L0L1_overall'].values, 
                                     df['overall'].values)
    results['overall_correlation']['L0L1'] = l0l1_corr
    
    # 2. Williams' t-test (H1 检验)
    # 需要 L0 和 L0+L1 的相关系数
    r_l0 = l0_corr['r']
    r_l0l1 = l0l1_corr['r']
    r_l0_l0l1 = np.corrcoef(df['L0_overall'].values, 
                            df['L0L1_overall'].values)[0, 1]
    
    t, p = williams_ttest(r_l0l1, r_l0, r_l0_l0l1, len(df))
    results['williams_test'] = {
        't': t,
        'p': p,
        'r_L0': r_l0,
        'r_L0L1': r_l0l1,
        'r_L0_vs_L0L1': r_l0_l0l1,
        'conclusion': 'L0+L1 显著优于 L0' if p < 0.05 else 'L0+L1 与 L0 无显著差异'
    }
    
    # 3. 各维度相关
    for dim in dims:
        l0_dim_corr = pearson_correlation(df[f'L0_{dim}'].values, 
                                           df[dim].values)
        l0l1_dim_corr = pearson_correlation(df[f'L0L1_{dim}'].values, 
                                             df[dim].values)
        
        results['dimension_correlation'][dim] = {
            'L0': l0_dim_corr,
            'L0L1': l0l1_dim_corr
        }
    
    # 4. Bland-Altman 一致性分析
    results['bland_altman']['L0'] = bland_altman_analysis(
        df['L0_overall'].values, df['overall'].values
    )
    results['bland_altman']['L0L1'] = bland_altman_analysis(
        df['L0L1_overall'].values, df['overall'].values
    )
    
    return results


def test_hypothesis_h4(r: float, ci: Tuple[float, float], 
                       threshold: float = 0.75) -> Dict:
    """
    H4 假设检验: r > 0.75
    
    H0: r ≤ 0.75
    H1: r > 0.75
    """
    supported = ci[0] > threshold  # 95% CI 下限 > 0.75
    
    return {
        'H0': f'r ≤ {threshold}',
        'H1': f'r > {threshold}',
        'observed_r': r,
        '95%_CI': ci,
        'supported': supported,
        'conclusion': 'H4 得到支持' if supported else 'H4 未得到支持'
    }


# 使用示例
if __name__ == "__main__":
    from data_loader import EXP001DataLoader
    loader = EXP001DataLoader()
    gold, auto = loader.load_annotations()[2], loader.load_auto_scores()
    
    results = analyze_validity(gold, auto)
    
    print("=== 效度分析结果 ===")
    print(f"\n样本量：N = {results['sample_size']}")
    
    print("\n总体评分相关性:")
    print(f"  L0 vs. 人工：r = {results['overall_correlation']['L0']['r']:.3f}, "
          f"p = {results['overall_correlation']['L0']['p']:.4f}, "
          f"95% CI [{results['overall_correlation']['L0']['CI'][0]:.3f}, "
          f"{results['overall_correlation']['L0']['CI'][1]:.3f}]")
    
    print(f"  L0+L1 vs. 人工：r = {results['overall_correlation']['L0L1']['r']:.3f}, "
          f"p = {results['overall_correlation']['L0L1']['p']:.4f}, "
          f"95% CI [{results['overall_correlation']['L0L1']['CI'][0]:.3f}, "
          f"{results['overall_correlation']['L0L1']['CI'][1]:.3f}]")
    
    print("\nWilliams' t-test (H1 检验):")
    wt = results['williams_test']
    print(f"  t({results['sample_size']-3}) = {wt['t']:.3f}, p = {wt['p']:.4f}")
    print(f"  结论：{wt['conclusion']}")
    
    print("\nBland-Altman 一致性:")
    ba_l0 = results['bland_altman']['L0']
    ba_l0l1 = results['bland_altman']['L0L1']
    print(f"  L0: bias = {ba_l0['bias']:.2f}, 95% LoA [{ba_l0['LoA'][0]:.2f}, {ba_l0['LoA'][1]:.2f}]")
    print(f"  L0+L1: bias = {ba_l0l1['bias']:.2f}, 95% LoA [{ba_l0l1['LoA'][0]:.2f}, {ba_l0l1['LoA'][1]:.2f}]")
    
    # H4 检验
    h4_result = test_hypothesis_h4(
        results['overall_correlation']['L0L1']['r'],
        results['overall_correlation']['L0L1']['CI']
    )
    print(f"\nH4 假设检验：{h4_result['conclusion']}")
```

---

### 2.4 抗堆砌效度分析 (`src/anti_hacking.py`)

```python
"""
EXP-001 抗 Reward Hacking 效度分析模块
- H2 检验: 堆砌样本评分下降 > 10 分
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple

def analyze_anti_hacking(df: pd.DataFrame) -> Dict:
    """
    抗堆砌效度分析
    
    H2: 堆砌样本评分显著低于正常样本 (下降 > 10 分)
    """
    # 分离堆砌样本和正常样本
    stuffed = df[df['layer'] == 'stuffed']
    normal = df[df['layer'] == 'normal']
    
    results = {}
    
    # 1. L0 评分对比
    l0_normal_mean = normal['L0_overall'].mean()
    l0_stuffed_mean = stuffed['L0_overall'].mean()
    l0_diff = l0_normal_mean - l0_stuffed_mean
    
    # t 检验
    l0_t, l0_p = stats.ttest_ind(normal['L0_overall'], stuffed['L0_overall'])
    l0_cohens_d = cohens_d(normal['L0_overall'], stuffed['L0_overall'])
    
    results['L0'] = {
        'normal_mean': l0_normal_mean,
        'stuffed_mean': l0_stuffed_mean,
        'difference': l0_diff,
        't': l0_t,
        'p': l0_p,
        'cohens_d': l0_cohens_d,
        'hacking_detected': l0_diff > 10 and l0_p < 0.05
    }
    
    # 2. L0+L1 评分对比
    l0l1_normal_mean = normal['L0L1_overall'].mean()
    l0l1_stuffed_mean = stuffed['L0L1_overall'].mean()
    l0l1_diff = l0l1_normal_mean - l0l1_stuffed_mean
    
    l0l1_t, l0l1_p = stats.ttest_ind(normal['L0L1_overall'], 
                                      stuffed['L0L1_overall'])
    l0l1_cohens_d = cohens_d(normal['L0L1_overall'], stuffed['L0L1_overall'])
    
    results['L0L1'] = {
        'normal_mean': l0l1_normal_mean,
        'stuffed_mean': l0l1_stuffed_mean,
        'difference': l0l1_diff,
        't': l0l1_t,
        'p': l0l1_p,
        'cohens_d': l0l1_cohens_d,
        'hacking_detected': l0l1_diff > 10 and l0l1_p < 0.05
    }
    
    # 3. L1 改进 (L0+L1 vs. L0 在堆砌样本上的差异)
    l1_improvement = l0l1_stuffed_mean - l0_stuffed_mean
    
    results['L1_improvement'] = {
        'L0_stuffed': l0_stuffed_mean,
        'L0L1_stuffed': l0l1_stuffed_mean,
        'improvement': l1_improvement,
        'conclusion': 'L1 有效识别并惩罚堆砌' if l1_improvement < 0 else 'L1 未有效识别堆砌'
    }
    
    return results


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """
    计算 Cohen's d (效应量)
    """
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    
    # 合并标准差
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    
    # Cohen's d
    d = (np.mean(group1) - np.mean(group2)) / pooled_std
    
    return d


def test_hypothesis_h2(results: Dict, threshold: float = 10.0) -> Dict:
    """
    H2 假设检验: 堆砌样本评分下降 > 10 分
    
    H0: μ(正常) - μ(堆砌) ≤ 10
    H1: μ(正常) - μ(堆砌) > 10
    """
    l0l1_result = results['L0L1']
    
    diff = l0l1_result['difference']
    supported = diff > threshold and l0l1_result['p'] < 0.05
    
    return {
        'H0': f'μ(正常) - μ(堆砌) ≤ {threshold}',
        'H1': f'μ(正常) - μ(堆砌) > {threshold}',
        'observed_diff': diff,
        'p_value': l0l1_result['p'],
        'cohens_d': l0l1_result['cohens_d'],
        'supported': supported,
        'conclusion': 'H2 得到支持' if supported else 'H2 未得到支持'
    }


# 使用示例
if __name__ == "__main__":
    from data_loader import EXP001DataLoader
    loader = EXP001DataLoader()
    df = loader.merge_all_data()
    
    results = analyze_anti_hacking(df)
    
    print("=== 抗 Reward Hacking 效度分析 ===")
    print(f"\n正常样本量：N = {len(df[df['layer'] == 'normal'])}")
    print(f"堆砌样本量：N = {len(df[df['layer'] == 'stuffed'])}")
    
    print("\nL0 评分对比:")
    l0 = results['L0']
    print(f"  正常样本：{l0['normal_mean']:.2f} ± {np.std(df[df['layer'] == 'normal']['L0_overall']):.2f}")
    print(f"  堆砌样本：{l0['stuffed_mean']:.2f} ± {np.std(df[df['layer'] == 'stuffed']['L0_overall']):.2f}")
    print(f"  差异：{l0['difference']:.2f} 分")
    print(f"  t 检验：t = {l0['t']:.3f}, p = {l0['p']:.4f}")
    print(f"  效应量：Cohen's d = {l0['cohens_d']:.3f}")
    print(f"  Hacking 检测：{'是' if l0['hacking_detected'] else '否'}")
    
    print("\nL0+L1 评分对比:")
    l0l1 = results['L0L1']
    print(f"  正常样本：{l0l1['normal_mean']:.2f} ± {np.std(df[df['layer'] == 'normal']['L0L1_overall']):.2f}")
    print(f"  堆砌样本：{l0l1['stuffed_mean']:.2f} ± {np.std(df[df['layer'] == 'stuffed']['L0L1_overall']):.2f}")
    print(f"  差异：{l0l1['difference']:.2f} 分")
    print(f"  t 检验：t = {l0l1['t']:.3f}, p = {l0l1['p']:.4f}")
    print(f"  效应量：Cohen's d = {l0l1['cohens_d']:.3f}")
    print(f"  Hacking 检测：{'是' if l0l1['hacking_detected'] else '否'}")
    
    print("\nL1 改进:")
    imp = results['L1_improvement']
    print(f"  L0 堆砌评分：{imp['L0_stuffed']:.2f}")
    print(f"  L0+L1 堆砌评分：{imp['L0L1_stuffed']:.2f}")
    print(f"  改进：{imp['improvement']:.2f} 分")
    print(f"  结论：{imp['conclusion']}")
    
    # H2 检验
    h2_result = test_hypothesis_h2(results)
    print(f"\nH2 假设检验：{h2_result['conclusion']}")
```

---

### 2.5 性能基准分析 (`src/performance.py`)

```python
"""
EXP-001 性能基准分析模块
- H3 检验: L1 触发率 20% ± 5%
- 延迟统计 (p50/p95/p99)
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict

def analyze_trigger_rate(df: pd.DataFrame) -> Dict:
    """
    L1 触发率分析 (H3 检验)
    
    H3: L1 触发率 = 20% ± 5%
    """
    total = len(df)
    triggered = df['L1_triggered'].sum()  # 假设 L1_triggered 是 0/1 标志
    trigger_rate = triggered / total
    
    # 二项式置信区间
    ci_low, ci_high = stats.binom.interval(0.95, total, trigger_rate)
    ci_low = ci_low / total
    ci_high = ci_high / total
    
    # 比例检验 (vs. 20%)
    p0 = 0.20
    z = (trigger_rate - p0) / np.sqrt(p0 * (1 - p0) / total)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))
    
    # 判断是否在目标范围内
    in_target = 0.15 <= trigger_rate <= 0.25
    
    return {
        'total_samples': total,
        'triggered_samples': triggered,
        'trigger_rate': trigger_rate,
        '95%_CI': (ci_low, ci_high),
        'target': 0.20,
        'target_range': (0.15, 0.25),
        'z': z,
        'p_value': p_value,
        'in_target': in_target,
        'conclusion': 'H3 得到支持' if in_target else 'H3 未得到支持'
    }


def analyze_latency(df: pd.DataFrame) -> Dict:
    """
    延迟统计分析
    """
    results = {}
    
    # L0 延迟
    if 'L0_latency_ms' in df.columns:
        l0 = df['L0_latency_ms']
        results['L0'] = {
            'p50': np.percentile(l0, 50),
            'p95': np.percentile(l0, 95),
            'p99': np.percentile(l0, 99),
            'mean': l0.mean(),
            'std': l0.std(),
            'min': l0.min(),
            'max': l0.max()
        }
    
    # L1 延迟 (仅触发样本)
    if 'L1_latency_ms' in df.columns:
        l1 = df[df['L1_triggered'] == 1]['L1_latency_ms']
        if len(l1) > 0:
            results['L1'] = {
                'p50': np.percentile(l1, 50),
                'p95': np.percentile(l1, 95),
                'p99': np.percentile(l1, 99),
                'mean': l1.mean(),
                'std': l1.std(),
                'min': l1.min(),
                'max': l1.max(),
                'sample_size': len(l1)
            }
    
    # 总延迟 (L0 + L1 加权)
    if 'L0_latency_ms' in df.columns and 'L1_latency_ms' in df.columns:
        # 加权平均：总延迟 = L0 + (触发率 × L1)
        trigger_rate = df['L1_triggered'].mean()
        l0_mean = df['L0_latency_ms'].mean()
        l1_mean = df[df['L1_triggered'] == 1]['L1_latency_ms'].mean() if 'L1_latency_ms' in df.columns else 0
        
        total_weighted = l0_mean + trigger_rate * l1_mean
        
        results['total_weighted'] = {
            'mean': total_weighted,
            'formula': f'L0_mean + trigger_rate × L1_mean = {l0_mean:.1f} + {trigger_rate:.2f} × {l1_mean:.1f}'
        }
    
    return results


def test_hypothesis_h3(trigger_rate_result: Dict) -> Dict:
    """
    H3 假设检验: L1 触发率 20% ± 5%
    
    H0: 触发率 ∉ [15%, 25%]
    H1: 15% ≤ 触发率 ≤ 25%
    """
    return {
        'H0': '触发率 ∉ [15%, 25%]',
        'H1': '15% ≤ 触发率 ≤ 25%',
        'observed_rate': trigger_rate_result['trigger_rate'],
        '95%_CI': trigger_rate_result['95%_CI'],
        'supported': trigger_rate_result['in_target'],
        'conclusion': 'H3 得到支持' if trigger_rate_result['in_target'] else 'H3 未得到支持'
    }


# 使用示例
if __name__ == "__main__":
    from data_loader import EXP001DataLoader
    loader = EXP001DataLoader()
    df = loader.merge_all_data()
    
    print("=== 性能基准分析 ===")
    
    # H3 检验
    trigger_result = analyze_trigger_rate(df)
    print(f"\nL1 触发率 (H3 检验):")
    print(f"  总样本量：N = {trigger_result['total_samples']}")
    print(f"  触发样本量：N = {trigger_result['triggered_samples']}")
    print(f"  触发率：{trigger_result['trigger_rate']:.2%}")
    print(f"  95% CI: [{trigger_result['95%_CI'][0]:.2%}, {trigger_result['95%_CI'][1]:.2%}]")
    print(f"  目标范围：[{trigger_result['target_range'][0]:.0%}, {trigger_result['target_range'][1]:.0%}]")
    print(f"  结论：{trigger_result['conclusion']}")
    
    # 延迟分析
    latency_result = analyze_latency(df)
    print(f"\n延迟统计:")
    if 'L0' in latency_result:
        l0 = latency_result['L0']
        print(f"  L0: p50={l0['p50']:.1f}ms, p95={l0['p95']:.1f}ms, p99={l0['p99']:.1f}ms")
    if 'L1' in latency_result:
        l1 = latency_result['L1']
        print(f"  L1: p50={l1['p50']:.1f}ms, p95={l1['p95']:.1f}ms, p99={l1['p99']:.1f}ms (N={l1['sample_size']})")
    if 'total_weighted' in latency_result:
        tw = latency_result['total_weighted']
        print(f"  总延迟 (加权): {tw['mean']:.1f}ms")
        print(f"  公式：{tw['formula']}")
```

---

## 三、主分析脚本 (`analyze_exp001.py`)

```python
#!/usr/bin/env python3
"""
EXP-001 完整分析流程

使用方法:
    python analyze_exp001.py

输出:
    - output/figures/ 图表
    - output/tables/ 表格
    - output/exp-001-analysis-report.md Markdown 报告
"""

import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_loader import EXP001DataLoader
from reliability import analyze_reliability
from validity import analyze_validity, test_hypothesis_h4
from anti_hacking import analyze_anti_hacking, test_hypothesis_h2
from performance import analyze_trigger_rate, analyze_latency, test_hypothesis_h3

def main():
    print("=" * 60)
    print("EXP-001 Multi-Agent Scorer v0.6 效度验证")
    print("=" * 60)
    
    # 1. 加载数据
    print("\n[1/5] 加载数据...")
    loader = EXP001DataLoader()
    df = loader.merge_all_data()
    a1, a2, gold = loader.load_annotations()
    print(f"  总样本量：N = {len(df)}")
    print(f"  样本类型分布：{df['layer'].value_counts().to_dict()}")
    
    # 2. 信度分析
    print("\n[2/5] 信度分析...")
    reliability_results = analyze_reliability(a1, a2)
    print(f"  总体评分 ICC: {reliability_results['overall_icc']['ICC']:.3f}")
    print(f"  标注者间信度：{'合格 (κ > 0.7)' if reliability_results['overall_kappa'][0] > 0.7 else '需改进 (κ < 0.7)'}")
    
    # 3. 效度分析 (H1, H4)
    print("\n[3/5] 效度分析...")
    validity_results = analyze_validity(gold, df)
    print(f"  L0 vs. 人工：r = {validity_results['overall_correlation']['L0']['r']:.3f}")
    print(f"  L0+L1 vs. 人工：r = {validity_results['overall_correlation']['L0L1']['r']:.3f}")
    print(f"  Williams' t-test: p = {validity_results['williams_test']['p']:.4f}")
    print(f"  H1 检验：{validity_results['williams_test']['conclusion']}")
    
    h4_result = test_hypothesis_h4(
        validity_results['overall_correlation']['L0L1']['r'],
        validity_results['overall_correlation']['L0L1']['CI']
    )
    print(f"  H4 检验：{h4_result['conclusion']}")
    
    # 4. 抗堆砌分析 (H2)
    print("\n[4/5] 抗堆砌效度分析...")
    hacking_results = analyze_anti_hacking(df)
    h2_result = test_hypothesis_h2(hacking_results)
    print(f"  正常样本 vs. 堆砌样本差异：{hacking_results['L0L1']['difference']:.2f} 分")
    print(f"  H2 检验：{h2_result['conclusion']}")
    
    # 5. 性能分析 (H3)
    print("\n[5/5] 性能基准分析...")
    trigger_result = analyze_trigger_rate(df)
    h3_result = test_hypothesis_h3(trigger_result)
    print(f"  L1 触发率：{trigger_result['trigger_rate']:.2%}")
    print(f"  H3 检验：{h3_result['conclusion']}")
    
    latency_result = analyze_latency(df)
    if 'L0' in latency_result:
        print(f"  L0 p95 延迟：{latency_result['L0']['p95']:.1f}ms")
    if 'L1' in latency_result:
        print(f"  L1 p95 延迟：{latency_result['L1']['p95']:.1f}ms")
    
    # 6. 汇总结果
    print("\n" + "=" * 60)
    print("假设检验汇总")
    print("=" * 60)
    print(f"H1 (L1 仲裁效度): {validity_results['williams_test']['conclusion']}")
    print(f"H2 (抗堆砌效度): {h2_result['conclusion']}")
    print(f"H3 (触发率控制): {h3_result['conclusion']}")
    print(f"H4 (综合效度): {h4_result['conclusion']}")
    
    print("\n分析完成！")
    print("详细报告：output/exp-001-analysis-report.md")
    print("图表：output/figures/")
    print("表格：output/tables/")


if __name__ == "__main__":
    main()
```

---

## 四、requirements.txt

```txt
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
seaborn>=0.12.0
pingouin>=0.5.0
jupyter>=1.0.0
```

---

## 五、使用指南

### 5.1 安装依赖

```bash
cd exp-001-analysis
pip install -r requirements.txt
```

### 5.2 准备数据

确保以下文件存在:
- `data/samples/exp-001-samples.csv`
- `data/annotations/exp-001-annotator1.csv`
- `data/annotations/exp-001-annotator2.csv`
- `data/annotations/exp-001-gold-standard.csv`
- `data/scores/exp-001-auto-scores.csv`

### 5.3 运行分析

```bash
python analyze_exp001.py
```

### 5.4 查看结果

- **Markdown 报告**: `output/exp-001-analysis-report.md`
- **图表**: `output/figures/`
- **表格**: `output/tables/`

---

*数据分析代码框架 v1.0 — 2026-04-03 00:45 UTC*

**下一步**: 等待人工标注和自动评分完成后，填充数据并运行分析

Hulk 🟢
