#!/usr/bin/env python3
"""
ASR Benchmark Evaluation Script (纯 Python 实现，无外部依赖)
计算 WER (Word Error Rate) 和 CER (Character Error Rate)

使用方法:
    python benchmark_eval.py --reference "参考文本" --hypothesis "ASR 输出"
    python benchmark_eval.py --batch samples.csv

作者: Hulk (OpenClaw)
日期: 2026-03-26
"""

import argparse
import csv
import json
import sys
from typing import Dict, List, Tuple


def levenshtein_distance(s1: List[str], s2: List[str]) -> Tuple[int, int, int]:
    """
    计算 Levenshtein 编辑距离，返回 (substitutions, deletions, insertions)
    
    使用动态规划算法
    """
    m, n = len(s1), len(s2)
    
    # 创建 DP 表
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # 初始化边界
    for i in range(m + 1):
        dp[i][0] = i  # 删除 i 个字符
    for j in range(n + 1):
        dp[0][j] = j  # 插入 j 个字符
    
    # 填充 DP 表
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # 字符相同，无需编辑
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j-1],  # 替换
                    dp[i-1][j],    # 删除
                    dp[i][j-1]     # 插入
                )
    
    # 回溯计算各类错误数量
    substitutions = 0
    deletions = 0
    insertions = 0
    
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i-1] == s2[j-1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i-1][j-1] + 1:
            substitutions += 1
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i-1][j] + 1:
            deletions += 1
            i -= 1
        else:
            insertions += 1
            j -= 1
    
    return substitutions, deletions, insertions


def calculate_wer_cer(reference: str, hypothesis: str) -> Dict[str, float]:
    """
    计算 WER 和 CER
    
    Args:
        reference: 真实转录文本 (Ground Truth)
        hypothesis: ASR 输出文本
    
    Returns:
        dict: {'wer': float, 'cer': float, 'wer_percent': str, 'cer_percent': str,
               'substitutions': int, 'deletions': int, 'insertions': int}
    """
    # 处理空值
    reference = reference or ""
    hypothesis = hypothesis or ""
    
    # 中文按字符分割
    ref_chars = list(reference.strip())
    hyp_chars = list(hypothesis.strip())
    
    # 中文按词分割 (简单分词：每个字作为一个词)
    # 对于更精确的 WER，可以使用 jieba 等分词工具
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()
    
    # 如果文本中没有空格，按字符处理
    if len(ref_words) == 1 and len(reference) > 1:
        ref_words = ref_chars
    if len(hyp_words) == 1 and len(hypothesis) > 1:
        hyp_words = hyp_chars
    
    # 计算 CER (Character Error Rate)
    s_cer, d_cer, i_cer = levenshtein_distance(ref_chars, hyp_chars)
    cer = (s_cer + d_cer + i_cer) / len(ref_chars) if ref_chars else 0
    
    # 计算 WER (Word Error Rate)
    s_wer, d_wer, i_wer = levenshtein_distance(ref_words, hyp_words)
    wer = (s_wer + d_wer + i_wer) / len(ref_words) if ref_words else 0
    
    return {
        'wer': wer,
        'cer': cer,
        'wer_percent': f"{wer:.2%}",
        'cer_percent': f"{cer:.2%}",
        'substitutions': s_cer,
        'deletions': d_cer,
        'insertions': i_cer,
        'reference_len': len(ref_chars),
        'hypothesis_len': len(hyp_chars),
    }


def calculate_batch_metrics(samples: List[Dict[str, str]]) -> Dict:
    """
    批量计算多个样本的指标
    
    Args:
        samples: [{'reference': str, 'hypothesis': str, 'id': str}, ...]
    
    Returns:
        dict: 包含每个样本的详细结果和汇总统计
    """
    results = []
    total_wer = 0
    total_cer = 0
    zero_error_count = 0
    
    for sample in samples:
        ref = sample.get('reference') or ''
        hyp = sample.get('hypothesis') or ''
        sample_id = sample.get('id', f'sample_{len(results)+1}')
        
        metrics = calculate_wer_cer(ref, hyp)
        metrics['id'] = sample_id
        metrics['reference'] = ref
        metrics['hypothesis'] = hyp
        metrics['audio_file'] = sample.get('audio_file', '')
        
        results.append(metrics)
        total_wer += metrics['wer']
        total_cer += metrics['cer']
        
        if metrics['wer'] == 0:
            zero_error_count += 1
    
    n = len(results)
    summary = {
        'count': n,
        'avg_wer': total_wer / n if n > 0 else 0,
        'avg_cer': total_cer / n if n > 0 else 0,
        'avg_wer_percent': f"{total_wer / n:.2%}" if n > 0 else "N/A",
        'avg_cer_percent': f"{total_cer / n:.2%}" if n > 0 else "N/A",
        'zero_error_samples': zero_error_count,
        'zero_error_ratio': f"{zero_error_count/n:.1%}" if n > 0 else "N/A",
        'best_sample': min(results, key=lambda x: x['wer'])['id'] if results else "N/A",
        'worst_sample': max(results, key=lambda x: x['wer'])['id'] if results else "N/A",
    }
    
    return {
        'summary': summary,
        'samples': results
    }


def load_samples_from_csv(csv_path: str) -> List[Dict[str, str]]:
    """
    从 CSV 文件加载测试样本
    
    CSV 格式:
        id,reference,hypothesis,audio_file
        001，今天天气真好，今天天气真好，file1.wav
    
    Args:
        csv_path: CSV 文件路径
    
    Returns:
        list: 样本列表
    """
    samples = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            samples.append({
                'id': row.get('id', ''),
                'reference': row.get('reference', ''),
                'hypothesis': row.get('hypothesis', ''),
                'audio_file': row.get('audio_file', '')
            })
    return samples


def main():
    parser = argparse.ArgumentParser(description='ASR 基准测试评估工具 (纯 Python 实现)')
    parser.add_argument('--reference', '-r', type=str, help='参考文本 (Ground Truth)')
    parser.add_argument('--hypothesis', '-p', type=str, help='ASR 输出文本 (prediction)')
    parser.add_argument('--batch', '-b', type=str, help='批量测试 CSV 文件路径')
    parser.add_argument('--output', '-o', type=str, help='输出文件路径 (JSON)')
    parser.add_argument('--detail', '-d', action='store_true', help='显示详细错误分析')
    
    args = parser.parse_args()
    
    # 单样本模式
    if args.reference and args.hypothesis:
        metrics = calculate_wer_cer(args.reference, args.hypothesis)
        print(f"\n{'='*60}")
        print(f"ASR 评估结果")
        print(f"{'='*60}")
        print(f"参考文本：{args.reference}")
        print(f"ASR 输出：{args.hypothesis}")
        print(f"{'='*60}")
        print(f"WER (词错误率): {metrics['wer_percent']}")
        print(f"CER (字错误率): {metrics['cer_percent']}")
        
        if args.detail:
            print(f"\n错误分析:")
            print(f"  替换 (S): {metrics['substitutions']}")
            print(f"  删除 (D): {metrics['deletions']}")
            print(f"  插入 (I): {metrics['insertions']}")
            print(f"  参考长度：{metrics['reference_len']} 字")
            print(f"  输出长度：{metrics['hypothesis_len']} 字")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到：{args.output}")
    
    # 批量模式
    elif args.batch:
        print(f"加载测试样本：{args.batch}")
        samples = load_samples_from_csv(args.batch)
        print(f"找到 {len(samples)} 个样本\n")
        
        results = calculate_batch_metrics(samples)
        
        print(f"{'='*60}")
        print(f"批量测试结果汇总")
        print(f"{'='*60}")
        print(f"样本数量：{results['summary']['count']}")
        print(f"平均 WER: {results['summary']['avg_wer_percent']}")
        print(f"平均 CER: {results['summary']['avg_cer_percent']}")
        print(f"零错误样本：{results['summary']['zero_error_samples']} ({results['summary']['zero_error_ratio']})")
        print(f"最佳样本：{results['summary']['best_sample']}")
        print(f"最差样本：{results['summary']['worst_sample']}")
        print(f"{'='*60}")
        
        # 显示每个样本的详情
        print(f"\n样本详情:")
        for sample in results['samples']:
            status = "✓" if sample['wer'] == 0 else "✗"
            print(f"  {status} [{sample['id']}] WER: {sample['wer_percent']}, CER: {sample['cer_percent']}")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n完整结果已保存到：{args.output}")
    
    else:
        parser.print_help()
        print("\n示例:")
        print("  # 单样本测试")
        print("  python benchmark_eval.py -r '今天天气真好' -h '今天天气真好'")
        print("\n  # 批量测试")
        print("  python benchmark_eval.py -b samples.csv -o results.json -d")


if __name__ == '__main__':
    main()
