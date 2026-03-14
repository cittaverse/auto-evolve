#!/usr/bin/env python3
"""
L0 标注质检多 Agent 系统 — 基准测试

测试指标：
- P50/P95 延迟
- 吞吐量（条/秒）
- 仲裁率
- 成功率

用法：
    python3 benchmark.py --samples 100 --concurrency 4
"""

import os
import sys
import time
import argparse
import statistics
from typing import List, Dict
from dataclasses import dataclass

from l0_quality_system import L0QualitySystem, QualityAssessmentResult


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    total_samples: int
    successful: int
    failed: int
    success_rate: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    mean_latency_ms: float
    std_latency_ms: float
    throughput_samples_per_sec: float
    arbitration_rate: float
    avg_overall_score: float


# 测试用叙事样本（覆盖不同质量等级）
TEST_NARRATIVES = [
    # S 级样本（丰富细节）
    """
    1978 年冬天，我 15 岁，在黑龙江下乡。清晨 5 点，天还没亮，茅草屋顶上结了一层白霜。
    我推开木门，"吱呀"一声，冷风灌进来，像刀子一样刮在脸上。
    院子里的井台结了冰，我提着水桶，手冻得通红，指尖几乎没有知觉。
    远处传来生产队的钟声，"当当当"，在寂静的清晨传得很远。
    那时候觉得日子很长，不知道什么时候能回城。
    """,
    
    # A 级样本（良好细节）
    """
    我上大学那会儿，经常去图书馆。图书馆在五楼，有个很大的落地窗。
    下午阳光照进来，整个阅览室都是金色的。我喜欢坐在靠窗的位置，
    一边看书一边看外面的行人。那时候最喜欢读金庸的武侠小说，
    一坐就是一下午。
    """,
    
    # B 级样本（中等细节）
    """
    小时候家里条件不好，住在农村。夏天很热，晚上经常在院子里乘凉。
    奶奶会给我们讲故事，讲她年轻时候的事情。我印象最深的是她说
    以前走几十里山路去赶集，很不容易。
    """,
    
    # C 级样本（较少细节）
    """
    我年轻时在工厂工作，干了三十多年。那时候工作很辛苦，
    每天都要加班。但是收入还可以，能养活一家人。
    现在退休了，有时候会想起以前的日子。
    """,
    
    # D 级样本（几乎无细节）
    """
    我小时候过得还行，没什么特别的。后来上学，工作，结婚，
    就这样过来了。现在退休了，每天带带孙子，挺好的。
    """,
]


def generate_test_samples(n: int) -> List[Dict]:
    """生成测试样本"""
    samples = []
    for i in range(n):
        template = TEST_NARRATIVES[i % len(TEST_NARRATIVES)]
        samples.append({
            'text': template,
            'speaker_id': f'test_{i:04d}',
            'life_stage': ['Childhood', 'Youth', 'Adulthood', 'Late Adulthood'][i % 4]
        })
    return samples


def calculate_percentile(data: List[float], percentile: float) -> float:
    """计算百分位数"""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile / 100)
    return sorted_data[min(index, len(sorted_data) - 1)]


def run_benchmark(samples: int, concurrency: int) -> BenchmarkResult:
    """运行基准测试"""
    print(f"开始基准测试：{samples} 个样本，并发度={concurrency}")
    print("-" * 60)
    
    # 初始化系统
    system = L0QualitySystem()
    
    # 生成测试样本
    test_samples = generate_test_samples(samples)
    
    # 运行测试
    start_time = time.time()
    results: List[QualityAssessmentResult] = []
    failed = 0
    
    for i, sample in enumerate(test_samples):
        try:
            result = system.assess(
                text=sample['text'],
                speaker_id=sample['speaker_id'],
                life_stage=sample['life_stage']
            )
            results.append(result)
            
            # 进度报告
            if (i + 1) % 10 == 0 or i == len(test_samples) - 1:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                print(f"进度：{i + 1}/{samples} ({rate:.1f} 样本/秒)")
        
        except Exception as e:
            print(f"样本 {i} 失败：{e}", file=sys.stderr)
            failed += 1
    
    total_time = time.time() - start_time
    
    # 计算统计指标
    latencies = [r.total_latency_ms for r in results]
    scores = [r.overall_score for r in results]
    arbitration_count = sum(1 for r in results if r.arbitration_triggered)
    
    if not latencies:
        return BenchmarkResult(
            total_samples=samples,
            successful=0,
            failed=failed,
            success_rate=0.0,
            p50_latency_ms=0,
            p95_latency_ms=0,
            p99_latency_ms=0,
            mean_latency_ms=0,
            std_latency_ms=0,
            throughput_samples_per_sec=0,
            arbitration_rate=0,
            avg_overall_score=0
        )
    
    return BenchmarkResult(
        total_samples=samples,
        successful=len(results),
        failed=failed,
        success_rate=len(results) / samples * 100,
        p50_latency_ms=calculate_percentile(latencies, 50),
        p95_latency_ms=calculate_percentile(latencies, 95),
        p99_latency_ms=calculate_percentile(latencies, 99),
        mean_latency_ms=statistics.mean(latencies),
        std_latency_ms=statistics.stdev(latencies) if len(latencies) > 1 else 0,
        throughput_samples_per_sec=samples / total_time,
        arbitration_rate=arbitration_count / len(results) * 100,
        avg_overall_score=statistics.mean(scores)
    )


def print_results(result: BenchmarkResult):
    """打印测试结果"""
    print()
    print("=" * 60)
    print("基准测试结果")
    print("=" * 60)
    print()
    print("样本统计:")
    print(f"  总样本数：{result.total_samples}")
    print(f"  成功：{result.successful}")
    print(f"  失败：{result.failed}")
    print(f"  成功率：{result.success_rate:.1f}%")
    print()
    print("延迟指标:")
    print(f"  P50: {result.p50_latency_ms:.1f}ms")
    print(f"  P95: {result.p95_latency_ms:.1f}ms {'✅' if result.p95_latency_ms < 500 else '❌ (目标<500ms)'}")
    print(f"  P99: {result.p99_latency_ms:.1f}ms")
    print(f"  平均：{result.mean_latency_ms:.1f}ms ± {result.std_latency_ms:.1f}ms")
    print()
    print("吞吐量:")
    print(f"  {result.throughput_samples_per_sec:.1f} 样本/秒 {'✅' if result.throughput_samples_per_sec > 10 else '❌ (目标>10)'}")
    print()
    print("其他指标:")
    print(f"  仲裁率：{result.arbitration_rate:.1f}%")
    print(f"  平均分数：{result.avg_overall_score:.1f}")
    print()
    
    # 验收判定
    print("验收判定:")
    p95_pass = result.p95_latency_ms < 500
    throughput_pass = result.throughput_samples_per_sec > 10
    print(f"  P95 延迟 <500ms: {'✅ 通过' if p95_pass else '❌ 未通过'}")
    print(f"  吞吐量 >10 条/秒：{'✅ 通过' if throughput_pass else '❌ 未通过'}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='L0 质检系统基准测试')
    parser.add_argument('--samples', type=int, default=20, help='测试样本数')
    parser.add_argument('--concurrency', type=int, default=1, help='并发度')
    args = parser.parse_args()
    
    result = run_benchmark(args.samples, args.concurrency)
    print_results(result)


if __name__ == "__main__":
    main()
