#!/usr/bin/env python3
"""
Procedural Memory Performance Benchmark (RB-016 Phase 4)

This benchmark measures the latency of ProceduralMemory operations:
- strategy_selection: Should be <5ms
- apply_calibration: Should be <1ms  
- get_strategy_config: Should be <0.1ms

Author: Hulk 🟢 (GEO #108)
Created: 2026-04-05

Usage:
    python3 -m benchmarks.procedural_memory_benchmark
"""

import time
import statistics
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.procedural_memory import (
    ProceduralMemory,
    UserContext,
    ScoringStrategy,
    DefaultStrategy,
    ElderlyFriendlyStrategy,
    TraumaSensitiveStrategy
)


def measure_latency(operation: callable, iterations: int = 1000) -> Dict[str, float]:
    """
    Measure latency of an operation over multiple iterations
    
    Returns:
        Dictionary with latency statistics (min, max, mean, median, p95, p99)
    """
    latencies = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        operation()
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to milliseconds
    
    return {
        'min': min(latencies),
        'max': max(latencies),
        'mean': statistics.mean(latencies),
        'median': statistics.median(latencies),
        'p95': sorted(latencies)[int(len(latencies) * 0.95)],
        'p99': sorted(latencies)[int(len(latencies) * 0.99)],
        'iterations': iterations,
    }


def benchmark_strategy_selection() -> Dict[str, float]:
    """
    Benchmark strategy selection latency
    
    Target: <5ms (should not significantly impact total scoring latency)
    """
    pm = ProceduralMemory()
    
    # Register strategies
    pm.register_strategy(DefaultStrategy())
    pm.register_strategy(ElderlyFriendlyStrategy())
    pm.register_strategy(TraumaSensitiveStrategy())
    
    # Create diverse user contexts
    contexts = [
        UserContext(user_id="user_1", age=25, text_length=100, session_count=1),
        UserContext(user_id="user_2", age=70, text_length=150, session_count=5),
        UserContext(user_id="user_3", age=45, narrative_topic="trauma", text_length=200),
        UserContext(user_id="user_4", age=30, cultural_background="East Asian", text_length=80),
    ]
    
    def selection_operation():
        import random
        context = random.choice(contexts)
        pm.select_strategy(context)
    
    return measure_latency(selection_operation, iterations=1000)


def benchmark_get_calibration_rules() -> Dict[str, float]:
    """
    Benchmark calibration rule retrieval latency
    
    Target: <1ms (rule lookup should be lightweight)
    """
    pm = ProceduralMemory()
    
    # Create calibration rules for test users
    # Rule 1: Elderly user dimension weight adjustment
    pm.create_calibration_rule(
        user_id="user_elderly",
        rule_type="dimension_weight",
        params={"emotional_depth": 1.1, "self_reflection": 1.1, "fluency": 0.9},
        priority=50
    )
    
    # Rule 2: Trauma sensitivity adjustment
    pm.create_calibration_rule(
        user_id="user_trauma",
        rule_type="sensitivity",
        params={"negative_event_penalty": 0.5, "growth_narrative_bonus": 1.2},
        priority=50
    )
    
    test_users = ["user_elderly", "user_trauma", "user_normal"]
    
    def get_rules_operation():
        import random
        user_id = random.choice(test_users)
        pm.get_calibration_rules(user_id)
    
    return measure_latency(get_rules_operation, iterations=1000)


def benchmark_get_strategy() -> Dict[str, float]:
    """
    Benchmark strategy retrieval latency
    
    Target: <0.1ms (simple lookup operation)
    """
    pm = ProceduralMemory()
    
    # Register strategies
    pm.register_strategy(DefaultStrategy())
    pm.register_strategy(ElderlyFriendlyStrategy())
    pm.register_strategy(TraumaSensitiveStrategy())
    
    def get_strategy_operation():
        import random
        strategy_name = random.choice(["default_v1", "elderly_friendly", "trauma_sensitive"])
        pm.get_strategy(strategy_name)
    
    return measure_latency(get_strategy_operation, iterations=1000)


def benchmark_strategy_registry_operations() -> Dict[str, float]:
    """
    Benchmark strategy registration and listing operations
    """
    pm = ProceduralMemory()
    
    def register_operation():
        pm.register_strategy(DefaultStrategy())
    
    def list_operation():
        pm.list_strategies()
    
    return {
        'register': measure_latency(register_operation, iterations=100),
        'list': measure_latency(list_operation, iterations=1000),
    }


def run_all_benchmarks() -> Dict[str, Any]:
    """Run all procedural memory benchmarks"""
    print("=" * 70)
    print("Procedural Memory Performance Benchmark (RB-016 Phase 4)")
    print("=" * 70)
    print()
    
    results = {}
    
    # Benchmark 1: Strategy Selection
    print("1. Strategy Selection (target: <5ms)")
    print("-" * 50)
    results['strategy_selection'] = benchmark_strategy_selection()
    print(f"   Mean: {results['strategy_selection']['mean']:.3f} ms")
    print(f"   Median: {results['strategy_selection']['median']:.3f} ms")
    print(f"   P95: {results['strategy_selection']['p95']:.3f} ms")
    print(f"   P99: {results['strategy_selection']['p99']:.3f} ms")
    passed = results['strategy_selection']['p99'] < 5.0
    print(f"   Status: {'✅ PASS' if passed else '❌ FAIL'} (P99 < 5ms)")
    print()
    
    # Benchmark 2: Get Calibration Rules
    print("2. Get Calibration Rules (target: <1ms)")
    print("-" * 50)
    results['get_calibration_rules'] = benchmark_get_calibration_rules()
    print(f"   Mean: {results['get_calibration_rules']['mean']:.3f} ms")
    print(f"   Median: {results['get_calibration_rules']['median']:.3f} ms")
    print(f"   P95: {results['get_calibration_rules']['p95']:.3f} ms")
    print(f"   P99: {results['get_calibration_rules']['p99']:.3f} ms")
    passed = results['get_calibration_rules']['p99'] < 1.0
    print(f"   Status: {'✅ PASS' if passed else '❌ FAIL'} (P99 < 1ms)")
    print()
    
    # Benchmark 3: Get Strategy
    print("3. Get Strategy (target: <0.1ms)")
    print("-" * 50)
    results['get_strategy'] = benchmark_get_strategy()
    print(f"   Mean: {results['get_strategy']['mean']:.4f} ms")
    print(f"   Median: {results['get_strategy']['median']:.4f} ms")
    print(f"   P95: {results['get_strategy']['p95']:.4f} ms")
    print(f"   P99: {results['get_strategy']['p99']:.4f} ms")
    passed = results['get_strategy']['p99'] < 0.1
    print(f"   Status: {'✅ PASS' if passed else '❌ FAIL'} (P99 < 0.1ms)")
    print()
    
    # Benchmark 4: Registry Operations
    print("4. Registry Operations")
    print("-" * 50)
    results['registry'] = benchmark_strategy_registry_operations()
    print(f"   Register (mean): {results['registry']['register']['mean']:.3f} ms")
    print(f"   List (mean): {results['registry']['list']['mean']:.4f} ms")
    print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    all_passed = (
        results['strategy_selection']['p99'] < 5.0 and
        results['get_calibration_rules']['p99'] < 1.0 and
        results['get_strategy']['p99'] < 0.1
    )
    print(f"Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print()
    
    return results


def save_results(results: Dict[str, Any], output_path: str = None):
    """Save benchmark results to JSON file"""
    import json
    
    if output_path is None:
        output_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'procedural_memory_benchmark_results.json'
        )
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_path}")


if __name__ == '__main__':
    results = run_all_benchmarks()
    save_results(results)
