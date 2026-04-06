#!/usr/bin/env python3
"""
验证强度控制器 v0.6

动态调整 L1 触发阈值，平衡性能与效度。

核心功能:
1. 监控 L1 触发率 (滑动窗口)
2. 动态调整置信度阈值
3. 性能 - 效度平衡监控

基于设计稿：`designs/multi-agent-scorer-v0.6.md` §5
"""

import time
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import json


@dataclass
class ValidationControllerConfig:
    """验证强度控制器配置"""
    # L1 触发阈值
    confidence_threshold: float = 0.6  # 置信度 < 此值 → 触发 L1
    boundary_score_range: Tuple[float, float] = (55.0, 75.0)  # 评分在此区间 → 触发 L1
    
    # 性能目标
    target_l1_trigger_rate: float = 0.2  # 目标 20% 样本进入 L1
    target_l0_latency_ms: float = 100.0  # L0 延迟 < 100ms
    target_l1_latency_ms: float = 3000.0  # L1 延迟 < 3s
    
    # 动态调整
    auto_adjust_threshold: bool = True  # 根据实际触发率动态调整阈值
    adjustment_window: int = 1000  # 每 1000 样本调整一次
    max_threshold_change: float = 0.1  # 单次调整最大幅度
    min_threshold: float = 0.4  # 阈值下限
    max_threshold: float = 0.8  # 阈值上限


@dataclass
class PerformanceMetrics:
    """性能指标"""
    l1_trigger_rate: float  # L1 触发率 (滑动窗口)
    l0_latency_p95_ms: float  # L0 p95 延迟
    l1_latency_p95_ms: float  # L1 p95 延迟
    sample_count: int  # 样本总数
    l1_count: int  # L1 触发次数
    window_size: int  # 滑动窗口大小


@dataclass
class ValidationResult:
    """验证结果"""
    should_trigger_l1: bool  # 是否触发 L1
    trigger_reason: str  # 触发原因
    current_threshold: float  # 当前阈值
    adjusted: bool  # 阈值是否已调整
    adjustment_reason: str  # 调整理由


class ValidationIntensityController:
    """验证强度控制器"""
    
    def __init__(self, config: ValidationControllerConfig = None):
        """
        初始化控制器
        
        参数:
            config: 配置参数，使用默认配置如果为 None
        """
        self.config = config or ValidationControllerConfig()
        
        # 滑动窗口：记录每个样本的 L1 触发情况
        self.trigger_window: deque = deque(maxlen=self.config.adjustment_window)
        
        # 延迟记录
        self.l0_latencies: deque = deque(maxlen=self.config.adjustment_window)
        self.l1_latencies: deque = deque(maxlen=self.config.adjustment_window)
        
        # 计数器
        self.total_samples = 0
        self.total_l1_triggers = 0
        
        # 上次调整时间
        self.last_adjustment_time = time.time()
        self.last_adjustment_sample = 0
    
    def should_trigger_l1(
        self,
        confidence: float,
        final_score: float,
        l0_latency_ms: float = None
    ) -> ValidationResult:
        """
        判断是否触发 L1 仲裁
        
        参数:
            confidence: L0 置信度 (0-1)
            final_score: L0 最终评分 (0-100)
            l0_latency_ms: L0 延迟 (可选，用于性能监控)
        
        返回:
            ValidationResult: 验证结果
        """
        self.total_samples += 1
        trigger = False
        reasons = []
        
        # 记录 L0 延迟
        if l0_latency_ms is not None:
            self.l0_latencies.append(l0_latency_ms)
        
        # 触发条件 1: 低置信度
        if confidence < self.config.confidence_threshold:
            trigger = True
            reasons.append(f"置信度过低 ({confidence:.2f} < {self.config.confidence_threshold})")
        
        # 触发条件 2: 边界案例
        min_score, max_score = self.config.boundary_score_range
        if min_score <= final_score <= max_score:
            trigger = True
            reasons.append(f"边界案例 (评分 {final_score} 在 {min_score}-{max_score} 区间)")
        
        # 记录触发情况
        self.trigger_window.append(1 if trigger else 0)
        if trigger:
            self.total_l1_triggers += 1
        
        # 检查是否需要调整阈值
        adjusted = False
        adjustment_reason = ""
        
        if self.config.auto_adjust_threshold and self._should_adjust():
            new_threshold, reason = self._adjust_threshold()
            if abs(new_threshold - self.config.confidence_threshold) > 0.01:
                adjusted = True
                adjustment_reason = reason
                self.config.confidence_threshold = new_threshold
        
        return ValidationResult(
            should_trigger_l1=trigger,
            trigger_reason="; ".join(reasons) if reasons else "不触发 L1",
            current_threshold=self.config.confidence_threshold,
            adjusted=adjusted,
            adjustment_reason=adjustment_reason
        )
    
    def record_l1_latency(self, latency_ms: float):
        """
        记录 L1 延迟
        
        参数:
            latency_ms: L1 延迟 (ms)
        """
        self.l1_latencies.append(latency_ms)
    
    def _should_adjust(self) -> bool:
        """
        判断是否应该调整阈值
        
        返回:
            bool: 是否应该调整
        """
        # 检查样本数是否达到调整窗口
        if len(self.trigger_window) < self.config.adjustment_window:
            return False
        
        # 检查距离上次调整是否已过足够多样本
        samples_since_adjustment = self.total_samples - self.last_adjustment_sample
        if samples_since_adjustment < self.config.adjustment_window:
            return False
        
        return True
    
    def _adjust_threshold(self) -> Tuple[float, str]:
        """
        调整 L1 触发阈值
        
        返回:
            new_threshold: 新阈值
            reason: 调整理由
        """
        # 计算当前触发率
        current_rate = sum(self.trigger_window) / len(self.trigger_window)
        target_rate = self.config.target_l1_trigger_rate
        
        # 计算误差
        error = current_rate - target_rate
        
        # 调整方向:
        # - 触发率过高 → 提高阈值 (减少 L1 触发)
        # - 触发率过低 → 降低阈值 (增加 L1 触发)
        adjustment = -error * 0.1  # 学习率 0.1
        
        # 限制调整幅度
        adjustment = max(-self.config.max_threshold_change, 
                        min(self.config.max_threshold_change, adjustment))
        
        new_threshold = self.config.confidence_threshold + adjustment
        
        # 限制在 [min_threshold, max_threshold] 区间
        new_threshold = max(self.config.min_threshold, 
                           min(self.config.max_threshold, new_threshold))
        
        # 生成调整理由
        if error > 0.05:
            reason = f"L1 触发率过高 ({current_rate:.1%} > 目标{target_rate:.1%})，阈值从 {self.config.confidence_threshold:.2f} 调整为 {new_threshold:.2f}"
        elif error < -0.05:
            reason = f"L1 触发率过低 ({current_rate:.1%} < 目标{target_rate:.1%})，阈值从 {self.config.confidence_threshold:.2f} 调整为 {new_threshold:.2f}"
        else:
            reason = f"L1 触发率正常 ({current_rate:.1%} ≈ 目标{target_rate:.1%})，微调阈值"
        
        # 更新调整记录
        self.last_adjustment_time = time.time()
        self.last_adjustment_sample = self.total_samples
        
        return round(new_threshold, 3), reason
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """
        获取当前性能指标
        
        返回:
            PerformanceMetrics: 性能指标
        """
        # 计算 L1 触发率
        l1_trigger_rate = (
            sum(self.trigger_window) / len(self.trigger_window)
            if len(self.trigger_window) > 0 else 0.0
        )
        
        # 计算 p95 延迟
        l0_latency_p95 = self._calculate_p95(self.l0_latencies)
        l1_latency_p95 = self._calculate_p95(self.l1_latencies)
        
        return PerformanceMetrics(
            l1_trigger_rate=l1_trigger_rate,
            l0_latency_p95_ms=l0_latency_p95,
            l1_latency_p95_ms=l1_latency_p95,
            sample_count=self.total_samples,
            l1_count=self.total_l1_triggers,
            window_size=len(self.trigger_window)
        )
    
    def _calculate_p95(self, latencies: deque) -> float:
        """计算 p95 延迟"""
        if len(latencies) == 0:
            return 0.0
        
        sorted_latencies = sorted(latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(p95_index, len(sorted_latencies) - 1)]
    
    def get_status_report(self) -> Dict:
        """
        获取状态报告
        
        返回:
            dict: 状态报告
        """
        metrics = self.get_performance_metrics()
        
        return {
            'config': {
                'confidence_threshold': self.config.confidence_threshold,
                'target_l1_trigger_rate': self.config.target_l1_trigger_rate,
                'boundary_score_range': self.config.boundary_score_range,
            },
            'metrics': {
                'l1_trigger_rate': metrics.l1_trigger_rate,
                'l0_latency_p95_ms': metrics.l0_latency_p95_ms,
                'l1_latency_p95_ms': metrics.l1_latency_p95_ms,
                'sample_count': metrics.sample_count,
                'l1_count': metrics.l1_count,
                'window_size': metrics.window_size,
            },
            'status': {
                'trigger_rate_status': self._get_rate_status(metrics.l1_trigger_rate),
                'l0_latency_status': self._get_latency_status(metrics.l0_latency_p95_ms, self.config.target_l0_latency_ms),
                'l1_latency_status': self._get_latency_status(metrics.l1_latency_p95_ms, self.config.target_l1_latency_ms),
            }
        }
    
    def _get_rate_status(self, rate: float) -> str:
        """获取触发率状态"""
        target = self.config.target_l1_trigger_rate
        if abs(rate - target) < 0.05:
            return "✅ 正常"
        elif rate > target:
            return "⚠️ 过高"
        else:
            return "⚠️ 过低"
    
    def _get_latency_status(self, latency: float, target: float) -> str:
        """获取延迟状态"""
        if latency == 0:
            return "⏳ 无数据"
        elif latency <= target:
            return "✅ 达标"
        else:
            return "⚠️ 超标"
    
    def export_state(self) -> Dict:
        """
        导出状态 (用于持久化)
        
        返回:
            dict: 状态字典
        """
        return {
            'config': {
                'confidence_threshold': self.config.confidence_threshold,
                'target_l1_trigger_rate': self.config.target_l1_trigger_rate,
                'boundary_score_range': list(self.config.boundary_score_range),
                'adjustment_window': self.config.adjustment_window,
                'auto_adjust_threshold': self.config.auto_adjust_threshold,
            },
            'counters': {
                'total_samples': self.total_samples,
                'total_l1_triggers': self.total_l1_triggers,
            },
            'trigger_window': list(self.trigger_window),
        }
    
    def import_state(self, state: Dict):
        """
        导入状态 (用于恢复)
        
        参数:
            state: 状态字典
        """
        self.config.confidence_threshold = state['config']['confidence_threshold']
        self.config.target_l1_trigger_rate = state['config']['target_l1_trigger_rate']
        self.config.boundary_score_range = tuple(state['config']['boundary_score_range'])
        self.config.adjustment_window = state['config']['adjustment_window']
        self.config.auto_adjust_threshold = state['config']['auto_adjust_threshold']
        
        self.total_samples = state['counters']['total_samples']
        self.total_l1_triggers = state['counters']['total_l1_triggers']
        
        self.trigger_window = deque(state['trigger_window'], maxlen=self.config.adjustment_window)


# 测试示例
if __name__ == '__main__':
    import random
    
    print("=" * 60)
    print("验证强度控制器测试")
    print("=" * 60)
    
    controller = ValidationIntensityController()
    
    # 模拟 1500 个样本
    for i in range(1500):
        # 随机生成置信度和评分
        confidence = random.uniform(0.3, 0.95)
        final_score = random.uniform(40, 90)
        l0_latency = random.uniform(50, 150)
        
        result = controller.should_trigger_l1(confidence, final_score, l0_latency)
        
        # 模拟 L1 延迟 (如果触发)
        if result.should_trigger_l1:
            l1_latency = random.uniform(1000, 4000)
            controller.record_l1_latency(l1_latency)
        
        # 每 500 样本打印状态
        if (i + 1) % 500 == 0:
            status = controller.get_status_report()
            print(f"\n--- 样本 {i + 1} ---")
            print(f"当前阈值：{status['config']['confidence_threshold']:.3f}")
            print(f"L1 触发率：{status['metrics']['l1_trigger_rate']:.1%} ({status['status']['trigger_rate_status']})")
            print(f"L0 p95 延迟：{status['metrics']['l0_latency_p95_ms']:.1f}ms ({status['status']['l0_latency_status']})")
            print(f"L1 p95 延迟：{status['metrics']['l1_latency_p95_ms']:.1f}ms ({status['status']['l1_latency_status']})")
            if status['metrics']['l1_count'] > 0:
                print(f"累计 L1 触发：{status['metrics']['l1_count']}次")
    
    # 导出状态
    print("\n" + "=" * 60)
    print("最终状态导出")
    print("=" * 60)
    state = controller.export_state()
    print(json.dumps(state, indent=2))
