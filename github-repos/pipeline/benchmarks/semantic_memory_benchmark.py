#!/usr/bin/env python3
"""
Semantic Memory Performance Benchmark

Benchmarks SemanticMemory at different scales:
- 1K users (small-scale, early stage)
- 10K users (medium-scale, production)
- 50K users (large-scale, stress test)

Metrics:
- store_score() latency: target <10ms
- get_user_stats() latency: target <5ms
- get_user_trend(30 days) latency: target <20ms
- get_percentile_rank() latency: target <10ms
- apply_calibration() latency: target <1ms

Author: Hulk 🟢 (GEO #105)
Created: 2026-04-04
Part of: RB-016 Phase 3 - Semantic Memory Performance Validation
"""

import os
import sys
import json
import time
import random
import statistics
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.semantic_memory import SemanticMemory


def generate_random_scores() -> dict:
    """Generate a random score record for testing."""
    return {
        "final_score": round(random.uniform(0, 1), 3),
        "coherence": round(random.uniform(0, 1), 3),
        "emotional_richness": round(random.uniform(0, 1), 3),
        "narrative_depth": round(random.uniform(0, 1), 3),
        "linguistic_complexity": round(random.uniform(0, 1), 3),
        "authenticity": round(random.uniform(0, 1), 3),
        "temporal_structure": round(random.uniform(0, 1), 3),
        "confidence": round(random.uniform(0.5, 1.0), 2),
    }


def generate_random_metadata() -> dict:
    """Generate random metadata for testing."""
    return {
        "narrative_id": f"narr_{random.randint(1, 10000)}",
        "session_id": f"sess_{random.randint(1, 1000)}",
        "duration_seconds": random.randint(60, 1800),
        "word_count": random.randint(50, 2000),
    }


def benchmark_store_score(sm: SemanticMemory, num_scores: int) -> dict:
    """Benchmark store_score() latency."""
    latencies = []
    
    for i in range(num_scores):
        user_id = f"user_{random.randint(1, 100)}"
        session_id = f"sess_bench_{i:06d}"
        scores = generate_random_scores()
        metadata = generate_random_metadata()
        
        start = time.perf_counter()
        sm.store_score(
            user_id=user_id,
            session_id=session_id,
            scores=scores,
            metadata=metadata,
        )
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)  # Convert to ms
        
        # Progress indicator every 1000 scores
        if (i + 1) % 1000 == 0:
            print(f"    Progress: {i + 1:,}/{num_scores:,} scores ({(i + 1) / num_scores * 100:.0f}%)")
    
    return {
        "operation": "store_score",
        "num_scores": num_scores,
        "latencies_ms": latencies,
        "avg_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)],
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "target_ms": 10,
        "passes_target": statistics.mean(latencies) < 10,
    }


def benchmark_get_user_stats(sm: SemanticMemory, num_queries: int = 100) -> dict:
    """Benchmark get_user_stats() latency."""
    latencies = []
    found_count = 0
    
    for i in range(num_queries):
        user_id = f"user_{random.randint(1, 100)}"
        
        start = time.perf_counter()
        stats = sm.get_user_stats(user_id)
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)
        if stats:
            found_count += 1
    
    return {
        "operation": "get_user_stats",
        "num_queries": num_queries,
        "found_count": found_count,
        "hit_rate": found_count / num_queries,
        "latencies_ms": latencies,
        "avg_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)],
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "target_ms": 5,
        "passes_target": statistics.mean(latencies) < 5,
    }


def benchmark_get_user_trend(sm: SemanticMemory, num_queries: int = 50, days: int = 30) -> dict:
    """Benchmark get_user_trend() latency."""
    latencies = []
    
    for i in range(num_queries):
        user_id = f"user_{random.randint(1, 100)}"
        
        start = time.perf_counter()
        trend = sm.get_user_trend(user_id=user_id, days=days, granularity="day")
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)
    
    return {
        "operation": "get_user_trend",
        "num_queries": num_queries,
        "days": days,
        "granularity": "day",
        "latencies_ms": latencies,
        "avg_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)],
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "target_ms": 20,
        "passes_target": statistics.mean(latencies) < 20,
    }


def benchmark_get_percentile_rank(sm: SemanticMemory, num_queries: int = 100) -> dict:
    """Benchmark get_percentile_rank() latency."""
    latencies = []
    
    scores = [round(random.uniform(0, 1), 2) for _ in range(num_queries)]
    
    for score in scores:
        start = time.perf_counter()
        percentile = sm.get_percentile_rank(score=score, reference_group="general")
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)
    
    return {
        "operation": "get_percentile_rank",
        "num_queries": num_queries,
        "latencies_ms": latencies,
        "avg_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)],
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "target_ms": 10,
        "passes_target": statistics.mean(latencies) < 10,
    }


def benchmark_apply_calibration(sm: SemanticMemory, num_queries: int = 100) -> dict:
    """Benchmark apply_calibration() latency."""
    latencies = []
    
    for i in range(num_queries):
        user_id = f"user_{random.randint(1, 100)}"
        raw_scores = {
            "event_richness": round(random.uniform(0, 1), 3),
            "temporal_causal_coherence": round(random.uniform(0, 1), 3),
            "emotional_depth": round(random.uniform(0, 1), 3),
            "identity_integration": round(random.uniform(0, 1), 3),
        }
        
        start = time.perf_counter()
        calibrated = sm.apply_calibration(user_id=user_id, raw_scores=raw_scores)
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)
    
    return {
        "operation": "apply_calibration",
        "num_queries": num_queries,
        "latencies_ms": latencies,
        "avg_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)],
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "target_ms": 1,
        "passes_target": statistics.mean(latencies) < 1,
    }


def benchmark_knowledge_operations(sm: SemanticMemory, num_ops: int = 50) -> dict:
    """Benchmark knowledge base operations."""
    store_latencies = []
    get_latencies = []
    
    for i in range(num_ops):
        category = f"category_{random.randint(1, 10)}"
        key = f"knowledge_key_{i:04d}"
        value = {"rule": f"Rule description {i}", "version": "1.0"}
        
        # Store
        start = time.perf_counter()
        sm.store_knowledge(category=category, key=key, value=value)
        end = time.perf_counter()
        store_latencies.append((end - start) * 1000)
        
        # Get
        start = time.perf_counter()
        retrieved = sm.get_knowledge(category=category, key=key)
        end = time.perf_counter()
        get_latencies.append((end - start) * 1000)
    
    return {
        "operation": "knowledge_operations",
        "num_ops": num_ops,
        "store_avg_ms": statistics.mean(store_latencies),
        "get_avg_ms": statistics.mean(get_latencies),
        "store_target_ms": 10,
        "get_target_ms": 5,
        "store_passes_target": statistics.mean(store_latencies) < 10,
        "get_passes_target": statistics.mean(get_latencies) < 5,
    }


def run_scale_benchmark(scale: str, num_users: int, scores_per_user: int = 10) -> dict:
    """Run full benchmark suite at a specific scale."""
    print(f"\n{'='*60}")
    print(f"Semantic Memory Benchmark — Scale: {scale} ({num_users:,} users, ~{num_users * scores_per_user:,} scores)")
    print(f"{'='*60}")
    
    # Create temporary database
    db_path = f"/tmp/semantic_memory_bench_{scale}.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Initialize SemanticMemory
    print(f"\nInitializing SemanticMemory at {db_path}...")
    sm = SemanticMemory(db_path=db_path)
    
    results = {
        "scale": scale,
        "num_users": num_users,
        "scores_per_user": scores_per_user,
        "total_scores": num_users * scores_per_user,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "benchmarks": {},
    }
    
    total_scores = num_users * scores_per_user
    
    # Benchmark 1: store_score
    print(f"\n[Benchmark 1/6] store_score() — {total_scores:,} scores...")
    start = time.perf_counter()
    store_results = benchmark_store_score(sm, total_scores)
    end = time.perf_counter()
    results["benchmarks"]["store_score"] = store_results
    print(f"  ✓ Completed in {(end - start):.2f}s")
    print(f"    Avg: {store_results['avg_ms']:.3f}ms | Median: {store_results['median_ms']:.3f}ms | P95: {store_results['p95_ms']:.3f}ms")
    print(f"    Target: <{store_results['target_ms']}ms | Status: {'✅ PASS' if store_results['passes_target'] else '❌ FAIL'}")
    
    # Benchmark 2: get_user_stats
    print(f"\n[Benchmark 2/6] get_user_stats() — 100 queries...")
    stats_results = benchmark_get_user_stats(sm, num_queries=100)
    results["benchmarks"]["get_user_stats"] = stats_results
    print(f"  ✓ Avg: {stats_results['avg_ms']:.3f}ms | Median: {stats_results['median_ms']:.3f}ms | P95: {stats_results['p95_ms']:.3f}ms")
    print(f"    Target: <{stats_results['target_ms']}ms | Status: {'✅ PASS' if stats_results['passes_target'] else '❌ FAIL'}")
    print(f"    Hit rate: {stats_results['hit_rate']*100:.1f}%")
    
    # Benchmark 3: get_user_trend
    print(f"\n[Benchmark 3/6] get_user_trend(30 days) — 50 queries...")
    trend_results = benchmark_get_user_trend(sm, num_queries=50, days=30)
    results["benchmarks"]["get_user_trend"] = trend_results
    print(f"  ✓ Avg: {trend_results['avg_ms']:.3f}ms | Median: {trend_results['median_ms']:.3f}ms | P95: {trend_results['p95_ms']:.3f}ms")
    print(f"    Target: <{trend_results['target_ms']}ms | Status: {'✅ PASS' if trend_results['passes_target'] else '❌ FAIL'}")
    
    # Benchmark 4: get_percentile_rank
    print(f"\n[Benchmark 4/6] get_percentile_rank() — 100 queries...")
    percentile_results = benchmark_get_percentile_rank(sm, num_queries=100)
    results["benchmarks"]["get_percentile_rank"] = percentile_results
    print(f"  ✓ Avg: {percentile_results['avg_ms']:.3f}ms | Median: {percentile_results['median_ms']:.3f}ms | P95: {percentile_results['p95_ms']:.3f}ms")
    print(f"    Target: <{percentile_results['target_ms']}ms | Status: {'✅ PASS' if percentile_results['passes_target'] else '❌ FAIL'}")
    
    # Benchmark 5: apply_calibration
    print(f"\n[Benchmark 5/6] apply_calibration() — 100 queries...")
    calib_results = benchmark_apply_calibration(sm, num_queries=100)
    results["benchmarks"]["apply_calibration"] = calib_results
    print(f"  ✓ Avg: {calib_results['avg_ms']:.3f}ms | Median: {calib_results['median_ms']:.3f}ms | P95: {calib_results['p95_ms']:.3f}ms")
    print(f"    Target: <{calib_results['target_ms']}ms | Status: {'✅ PASS' if calib_results['passes_target'] else '❌ FAIL'}")
    
    # Benchmark 6: knowledge operations
    print(f"\n[Benchmark 6/6] knowledge operations — 50 store + 50 get...")
    knowledge_results = benchmark_knowledge_operations(sm, num_ops=50)
    results["benchmarks"]["knowledge_operations"] = knowledge_results
    print(f"  ✓ Store Avg: {knowledge_results['store_avg_ms']:.3f}ms | Get Avg: {knowledge_results['get_avg_ms']:.3f}ms")
    print(f"    Target: store <{knowledge_results['store_target_ms']}ms, get <{knowledge_results['get_target_ms']}ms")
    print(f"    Status: {'✅ PASS' if knowledge_results['store_passes_target'] and knowledge_results['get_passes_target'] else '❌ FAIL'}")
    
    # Get final stats
    stats = sm.get_stats()
    results["final_stats"] = stats
    print(f"\n[Final Stats] Users: {stats.get('user_count', 'N/A')} | Scores: {stats.get('score_count', 'N/A')} | Storage: {stats.get('storage_mb', 0):.2f}MB")
    
    # Cleanup
    sm.close()
    os.remove(db_path)
    print(f"\n[Cleanup] Temporary database removed")
    
    return results


def main():
    """Run benchmarks at all scales."""
    print("="*60)
    print("Semantic Memory Performance Benchmark Suite")
    print("RB-016 Phase 3 - GEO #105")
    print("="*60)
    
    # Define scales
    # Note: 10K and 50K are commented out by default - uncomment for full benchmark
    scales = [
        ("1K", 1000, 10),      # 1K users × 10 scores = 10K scores
        # ("10K", 10000, 10),  # 10K users × 10 scores = 100K scores (~5-10 min)
        # ("50K", 50000, 10),  # Stress test - takes ~10-15 minutes
    ]
    
    all_results = []
    
    for scale_name, num_users, scores_per_user in scales:
        results = run_scale_benchmark(scale_name, num_users, scores_per_user)
        all_results.append(results)
    
    # Aggregate summary
    print("\n" + "="*60)
    print("AGGREGATE SUMMARY")
    print("="*60)
    
    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "scales_tested": [f"{s[0]} ({s[1]} users)" for s in scales],
        "results": all_results,
        "overall_status": "PASS",
    }
    
    # Check if all targets are met
    for scale_result in all_results:
        for bench_name, bench_data in scale_result["benchmarks"].items():
            if bench_name == "knowledge_operations":
                if not bench_data.get("store_passes_target", True) or not bench_data.get("get_passes_target", True):
                    summary["overall_status"] = "FAIL"
                    break
            else:
                if not bench_data.get("passes_target", True):
                    summary["overall_status"] = "FAIL"
                    break
    
    print(f"\nOverall Status: {'✅ ALL TARGETS MET' if summary['overall_status'] == 'PASS' else '⚠️ SOME TARGETS MISSED'}")
    
    # Performance table
    print("\n" + "-"*80)
    print("Performance Summary (avg latency)")
    print("-"*80)
    print(f"{'Scale':<10} {'store_score':<15} {'get_stats':<15} {'get_trend':<15} {'percentile':<15} {'calibrate':<15}")
    print("-"*80)
    
    for scale_result in all_results:
        scale = scale_result["scale"]
        store_ms = scale_result["benchmarks"]["store_score"]["avg_ms"]
        stats_ms = scale_result["benchmarks"]["get_user_stats"]["avg_ms"]
        trend_ms = scale_result["benchmarks"]["get_user_trend"]["avg_ms"]
        pct_ms = scale_result["benchmarks"]["get_percentile_rank"]["avg_ms"]
        calib_ms = scale_result["benchmarks"]["apply_calibration"]["avg_ms"]
        
        print(f"{scale:<10} {store_ms:>8.3f}ms    {stats_ms:>8.3f}ms    {trend_ms:>8.3f}ms    {pct_ms:>8.3f}ms    {calib_ms:>8.3f}ms")
    
    print("-"*80)
    
    # Save results to JSON
    output_dir = Path(__file__).parent
    output_file = output_dir / "semantic_memory_benchmark_results.json"
    
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n[Output] Results saved to: {output_file}")
    print(f"\nBenchmark complete!")
    
    return summary


if __name__ == "__main__":
    main()
