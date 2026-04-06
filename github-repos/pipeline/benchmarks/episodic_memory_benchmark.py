#!/usr/bin/env python3
"""
Episodic Memory Performance Benchmark

Benchmarks EpisodicMemory at different scales:
- 1K vectors (small-scale, early stage)
- 10K vectors (medium-scale, production)
- 50K vectors (large-scale, stress test)

Metrics:
- add_event() latency: target <10ms
- search_similar(top_k=10) latency: target <100ms
- get_event() latency: target <5ms

Author: Hulk 🟢 (GEO #103)
Created: 2026-04-04
Part of: RB-016 Phase 2 - Episodic Memory Performance Validation
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

from src.services.episodic_memory import EpisodicMemory


def generate_random_embedding(dim: int = 768) -> list[float]:
    """Generate a random normalized embedding vector."""
    import math
    vec = [random.gauss(0, 1) for _ in range(dim)]
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec]


def generate_random_metadata() -> dict:
    """Generate random metadata for testing."""
    emotions = ["happy", "sad", "neutral", "excited", "anxious", "calm", "angry", "surprised"]
    topics = ["work", "family", "health", "travel", "hobby", "learning", "relationship", "finance"]
    
    return {
        "emotion": random.choice(emotions),
        "topic": random.choice(topics),
        "user_id": f"user_{random.randint(1, 100)}",
        "quality_score": round(random.uniform(0, 1), 2),
    }


def benchmark_add_event(em: EpisodicMemory, num_events: int) -> dict:
    """Benchmark add_event() latency."""
    latencies = []
    
    for i in range(num_events):
        event_id = f"evt_bench_{i:06d}"
        narrative_text = f"Benchmark narrative event {i} with some descriptive text about daily activities and reflections."
        embedding = generate_random_embedding(768)
        metadata = generate_random_metadata()
        
        start = time.perf_counter()
        em.add_event(
            event_id=event_id,
            narrative_text=narrative_text,
            embedding=embedding,
            metadata=metadata,
        )
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)  # Convert to ms
        
        # Progress indicator every 1000 events
        if (i + 1) % 1000 == 0:
            print(f"    Progress: {i + 1:,}/{num_events:,} events ({(i + 1) / num_events * 100:.0f}%)")
    
    return {
        "operation": "add_event",
        "num_events": num_events,
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


def benchmark_search_similar(em: EpisodicMemory, num_queries: int = 50, top_k: int = 10) -> dict:
    """Benchmark search_similar() latency."""
    latencies = []
    results_counts = []
    
    # Generate query embeddings
    for i in range(num_queries):
        query_embedding = generate_random_embedding(768)
        
        start = time.perf_counter()
        results = em.search_similar(
            query_embedding=query_embedding,
            top_k=top_k,
        )
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)  # Convert to ms
        results_counts.append(len(results))
    
    return {
        "operation": "search_similar",
        "num_queries": num_queries,
        "top_k": top_k,
        "latencies_ms": latencies,
        "avg_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)],
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "avg_results": statistics.mean(results_counts),
        "target_ms": 100,
        "passes_target": statistics.mean(latencies) < 100,
    }


def benchmark_search_with_filters(em: EpisodicMemory, num_queries: int = 50, top_k: int = 10) -> dict:
    """Benchmark search_similar() with metadata filtering."""
    latencies = []
    
    emotions = ["happy", "sad", "neutral"]
    
    for i in range(num_queries):
        query_embedding = generate_random_embedding(768)
        filters = {"emotion": random.choice(emotions)}
        
        start = time.perf_counter()
        results = em.search_similar(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)
    
    return {
        "operation": "search_similar_with_filters",
        "num_queries": num_queries,
        "top_k": top_k,
        "filters": "emotion",
        "latencies_ms": latencies,
        "avg_ms": statistics.mean(latencies),
        "median_ms": statistics.median(latencies),
        "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)],
        "p99_ms": sorted(latencies)[int(len(latencies) * 0.99)],
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "target_ms": 100,
        "passes_target": statistics.mean(latencies) < 100,
    }


def benchmark_get_event(em: EpisodicMemory, num_queries: int = 50) -> dict:
    """Benchmark get_event() latency."""
    latencies = []
    found_count = 0
    
    # Get some existing event IDs
    stats = em.get_stats()
    if stats["event_count"] == 0:
        return {"error": "No events in database"}
    
    for i in range(num_queries):
        # Generate a random event ID that might exist
        event_id = f"evt_bench_{random.randint(0, stats['event_count'] - 1):06d}"
        
        start = time.perf_counter()
        event = em.get_event(event_id)
        end = time.perf_counter()
        
        latencies.append((end - start) * 1000)
        if event:
            found_count += 1
    
    return {
        "operation": "get_event",
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


def run_scale_benchmark(scale: str, num_events: int) -> dict:
    """Run full benchmark suite at a specific scale."""
    print(f"\n{'='*60}")
    print(f"Episodic Memory Benchmark — Scale: {scale} ({num_events:,} events)")
    print(f"{'='*60}")
    
    # Create temporary database
    db_path = f"/tmp/episodic_memory_bench_{scale}.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Initialize EpisodicMemory
    print(f"\nInitializing EpisodicMemory at {db_path}...")
    em = EpisodicMemory(db_path=db_path, embedding_dim=768)
    
    results = {
        "scale": scale,
        "num_events": num_events,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "benchmarks": {},
    }
    
    # Benchmark 1: add_event
    print(f"\n[Benchmark 1/4] add_event() — {num_events:,} events...")
    start = time.perf_counter()
    add_results = benchmark_add_event(em, num_events)
    end = time.perf_counter()
    results["benchmarks"]["add_event"] = add_results
    print(f"  ✓ Completed in {(end - start):.2f}s")
    print(f"    Avg: {add_results['avg_ms']:.3f}ms | Median: {add_results['median_ms']:.3f}ms | P95: {add_results['p95_ms']:.3f}ms")
    print(f"    Target: <{add_results['target_ms']}ms | Status: {'✅ PASS' if add_results['passes_target'] else '❌ FAIL'}")
    
    # Benchmark 2: search_similar
    print(f"\n[Benchmark 2/4] search_similar(top_k=10) — 100 queries...")
    search_results = benchmark_search_similar(em, num_queries=100, top_k=10)
    results["benchmarks"]["search_similar"] = search_results
    print(f"  ✓ Avg: {search_results['avg_ms']:.3f}ms | Median: {search_results['median_ms']:.3f}ms | P95: {search_results['p95_ms']:.3f}ms")
    print(f"    Target: <{search_results['target_ms']}ms | Status: {'✅ PASS' if search_results['passes_target'] else '❌ FAIL'}")
    
    # Benchmark 3: search_similar with filters
    print(f"\n[Benchmark 3/4] search_similar(top_k=10, filters) — 100 queries...")
    filtered_results = benchmark_search_with_filters(em, num_queries=100, top_k=10)
    results["benchmarks"]["search_similar_filtered"] = filtered_results
    print(f"  ✓ Avg: {filtered_results['avg_ms']:.3f}ms | Median: {filtered_results['median_ms']:.3f}ms | P95: {filtered_results['p95_ms']:.3f}ms")
    print(f"    Target: <{filtered_results['target_ms']}ms | Status: {'✅ PASS' if filtered_results['passes_target'] else '❌ FAIL'}")
    
    # Benchmark 4: get_event
    print(f"\n[Benchmark 4/4] get_event() — 100 queries...")
    get_results = benchmark_get_event(em, num_queries=100)
    results["benchmarks"]["get_event"] = get_results
    if "error" not in get_results:
        print(f"  ✓ Avg: {get_results['avg_ms']:.3f}ms | Median: {get_results['median_ms']:.3f}ms | P95: {get_results['p95_ms']:.3f}ms")
        print(f"    Target: <{get_results['target_ms']}ms | Status: {'✅ PASS' if get_results['passes_target'] else '❌ FAIL'}")
        print(f"    Hit rate: {get_results['hit_rate']*100:.1f}%")
    
    # Get final stats
    stats = em.get_stats()
    results["final_stats"] = stats
    print(f"\n[Final Stats] Event count: {stats['event_count']:,} | Storage: {stats['storage_mb']:.2f}MB")
    
    # Cleanup
    em.close()
    os.remove(db_path)
    print(f"\n[Cleanup] Temporary database removed")
    
    return results


def main():
    """Run benchmarks at all scales."""
    print("="*60)
    print("Episodic Memory Performance Benchmark Suite")
    print("RB-016 Phase 2 - GEO #103")
    print("="*60)
    
    # Define scales
    # Note: 50K is commented out by default - uncomment for stress testing
    scales = [
        ("1K", 1000),
        ("10K", 10000),
        # ("50K", 50000),  # Stress test - takes ~10-15 minutes
    ]
    
    all_results = []
    
    for scale_name, num_events in scales:
        results = run_scale_benchmark(scale_name, num_events)
        all_results.append(results)
    
    # Aggregate summary
    print("\n" + "="*60)
    print("AGGREGATE SUMMARY")
    print("="*60)
    
    summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "scales_tested": [s[0] for s in scales],
        "results": all_results,
        "overall_status": "PASS",
    }
    
    # Check if all targets are met
    for scale_result in all_results:
        for bench_name, bench_data in scale_result["benchmarks"].items():
            if not bench_data.get("passes_target", True):
                summary["overall_status"] = "FAIL"
                break
    
    print(f"\nOverall Status: {'✅ ALL TARGETS MET' if summary['overall_status'] == 'PASS' else '⚠️ SOME TARGETS MISSED'}")
    
    # Performance table
    print("\n" + "-"*60)
    print("Performance Summary (avg latency)")
    print("-"*60)
    print(f"{'Scale':<10} {'add_event':<15} {'search':<15} {'search+filter':<15} {'get_event':<15}")
    print("-"*60)
    
    for scale_result in all_results:
        scale = scale_result["scale"]
        add_ms = scale_result["benchmarks"]["add_event"]["avg_ms"]
        search_ms = scale_result["benchmarks"]["search_similar"]["avg_ms"]
        filter_ms = scale_result["benchmarks"]["search_similar_filtered"]["avg_ms"]
        get_ms = scale_result["benchmarks"]["get_event"].get("avg_ms", "N/A")
        
        if isinstance(get_ms, float):
            print(f"{scale:<10} {add_ms:>8.3f}ms    {search_ms:>8.3f}ms    {filter_ms:>8.3f}ms    {get_ms:>8.3f}ms")
        else:
            print(f"{scale:<10} {add_ms:>8.3f}ms    {search_ms:>8.3f}ms    {filter_ms:>8.3f}ms    {get_ms:>15}")
    
    print("-"*60)
    
    # Save results to JSON
    output_dir = Path(__file__).parent
    output_file = output_dir / "episodic_memory_benchmark_results.json"
    
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n[Output] Results saved to: {output_file}")
    print(f"\nBenchmark complete!")
    
    return summary


if __name__ == "__main__":
    main()
