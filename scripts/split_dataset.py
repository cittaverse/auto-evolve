#!/usr/bin/env python3
"""
数据集分割工具
支持：随机分割、分层分割、说话人独立分割

Usage:
    python split_dataset.py --metadata /path/to/metadata.json --output_dir /path/to/output --method stratified

作者：Hulk 🟢
日期：2026-04-02
"""

import os
import json
import argparse
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


def random_split(samples: List[Dict], 
                 train_ratio: float = 0.8,
                 dev_ratio: float = 0.1,
                 test_ratio: float = 0.1,
                 seed: int = 42) -> Dict[str, List[Dict]]:
    """
    随机分割数据集
    
    Args:
        samples: 样本列表
        train_ratio: 训练集比例
        dev_ratio: 验证集比例
        test_ratio: 测试集比例
        seed: 随机种子
    
    Returns:
        分割后的字典
    """
    np.random.seed(seed)
    indices = np.random.permutation(len(samples))
    
    n_train = int(len(samples) * train_ratio)
    n_dev = int(len(samples) * dev_ratio)
    
    train_indices = indices[:n_train]
    dev_indices = indices[n_train:n_train + n_dev]
    test_indices = indices[n_train + n_dev:]
    
    return {
        "train": [samples[i] for i in train_indices],
        "dev": [samples[i] for i in dev_indices],
        "test": [samples[i] for i in test_indices]
    }


def stratified_split(samples: List[Dict],
                     stratify_key: str = "speaker_id",
                     train_ratio: float = 0.8,
                     dev_ratio: float = 0.1,
                     test_ratio: float = 0.1,
                     seed: int = 42) -> Dict[str, List[Dict]]:
    """
    分层分割（按说话人）
    
    Args:
        samples: 样本列表
        stratify_key: 分层键
        train_ratio: 训练集比例
        dev_ratio: 验证集比例
        test_ratio: 测试集比例
        seed: 随机种子
    
    Returns:
        分割后的字典
    """
    np.random.seed(seed)
    
    # 按 stratify_key 分组
    groups = defaultdict(list)
    for sample in samples:
        key = sample.get(stratify_key, "unknown")
        groups[key].append(sample)
    
    train_samples = []
    dev_samples = []
    test_samples = []
    
    # 对每组进行分割
    for key, group_samples in groups.items():
        indices = np.random.permutation(len(group_samples))
        
        n_train = int(len(group_samples) * train_ratio)
        n_dev = int(len(group_samples) * dev_ratio)
        
        train_samples.extend([group_samples[i] for i in indices[:n_train]])
        dev_samples.extend([group_samples[i] for i in indices[n_train:n_train + n_dev]])
        test_samples.extend([group_samples[i] for i in indices[n_train + n_dev:]])
    
    # 打乱
    np.random.shuffle(train_samples)
    np.random.shuffle(dev_samples)
    np.random.shuffle(test_samples)
    
    return {
        "train": train_samples,
        "dev": dev_samples,
        "test": test_samples
    }


def speaker_independent_split(samples: List[Dict],
                               train_speakers: Optional[List[str]] = None,
                               dev_speakers: Optional[List[str]] = None,
                               test_speakers: Optional[List[str]] = None,
                               seed: int = 42) -> Dict[str, List[Dict]]:
    """
    说话人独立分割（训练/验证/测试说话人完全不重叠）
    
    Args:
        samples: 样本列表
        train_speakers: 训练集说话人列表
        dev_speakers: 验证集说话人列表
        test_speakers: 测试集说话人列表
        seed: 随机种子
    
    Returns:
        分割后的字典
    """
    np.random.seed(seed)
    
    # 收集所有说话人
    all_speakers = set(s.get("speaker_id", "unknown") for s in samples)
    
    if train_speakers is None:
        # 自动分配：70% 训练，15% 验证，15% 测试
        speakers_list = list(all_speakers)
        np.random.shuffle(speakers_list)
        
        n_train = int(len(speakers_list) * 0.7)
        n_dev = int(len(speakers_list) * 0.15)
        
        train_speakers = set(speakers_list[:n_train])
        dev_speakers = set(speakers_list[n_train:n_train + n_dev])
        test_speakers = set(speakers_list[n_train + n_dev:])
    else:
        train_speakers = set(train_speakers)
        dev_speakers = set(dev_speakers) if dev_speakers else set()
        test_speakers = set(test_speakers) if test_speakers else set()
    
    # 按说话人分割样本
    train_samples = [s for s in samples if s.get("speaker_id") in train_speakers]
    dev_samples = [s for s in samples if s.get("speaker_id") in dev_speakers]
    test_samples = [s for s in samples if s.get("speaker_id") in test_speakers]
    
    return {
        "train": train_samples,
        "dev": dev_samples,
        "test": test_samples,
        "speaker_split": {
            "train": list(train_speakers),
            "dev": list(dev_speakers),
            "test": list(test_speakers)
        }
    }


def duration_balanced_split(samples: List[Dict],
                            train_ratio: float = 0.8,
                            dev_ratio: float = 0.1,
                            test_ratio: float = 0.1,
                            seed: int = 42) -> Dict[str, List[Dict]]:
    """
    按时长平衡分割（确保各集合总时长相近）
    
    Args:
        samples: 样本列表
        train_ratio: 训练集比例
        dev_ratio: 验证集比例
        test_ratio: 测试集比例
        seed: 随机种子
    
    Returns:
        分割后的字典
    """
    np.random.seed(seed)
    
    # 按时长排序
    sorted_samples = sorted(samples, key=lambda x: x.get("duration", 0), reverse=True)
    
    train_samples = []
    dev_samples = []
    test_samples = []
    
    train_duration = 0
    dev_duration = 0
    test_duration = 0
    
    total_duration = sum(s.get("duration", 0) for s in samples)
    target_train = total_duration * train_ratio
    target_dev = total_duration * dev_ratio
    target_test = total_duration * test_ratio
    
    # 贪心分配
    for sample in sorted_samples:
        duration = sample.get("duration", 0)
        
        # 分配到当前总时长与目标差距最大的集合
        train_gap = target_train - train_duration
        dev_gap = target_dev - dev_duration
        test_gap = target_test - test_duration
        
        if train_gap >= dev_gap and train_gap >= test_gap:
            train_samples.append(sample)
            train_duration += duration
        elif dev_gap >= test_gap:
            dev_samples.append(sample)
            dev_duration += duration
        else:
            test_samples.append(sample)
            test_duration += duration
    
    return {
        "train": train_samples,
        "dev": dev_samples,
        "test": test_samples,
        "duration_stats": {
            "train_hours": round(train_duration / 3600, 2),
            "dev_hours": round(dev_duration / 3600, 2),
            "test_hours": round(test_duration / 3600, 2)
        }
    }


def save_splits(splits: Dict[str, List[Dict]], output_dir: Path):
    """保存分割结果"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for split_name, samples in splits.items():
        if split_name == "speaker_split" or split_name == "duration_stats":
            continue
        
        # JSON 格式
        json_path = output_dir / f"{split_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        
        # CSV 格式
        csv_path = output_dir / f"{split_name}.csv"
        if samples:
            with open(csv_path, 'w', encoding='utf-8') as f:
                headers = list(samples[0].keys())
                f.write(','.join(headers) + '\n')
                for s in samples:
                    values = []
                    for h in headers:
                        v = str(s.get(h, '')).replace('"', '""')
                        values.append(f'"{v}"')
                    f.write(','.join(values) + '\n')
        
        print(f"  ✓ {split_name}: {len(samples)} 个样本")
    
    # 保存分割统计
    stats_path = output_dir / "split_statistics.json"
    stats = {
        "train_samples": len(splits.get("train", [])),
        "dev_samples": len(splits.get("dev", [])),
        "test_samples": len(splits.get("test", [])),
        "total_samples": len(splits.get("train", [])) + 
                        len(splits.get("dev", [])) + 
                        len(splits.get("test", []))
    }
    
    if "speaker_split" in splits:
        stats["speaker_split"] = splits["speaker_split"]
    if "duration_stats" in splits:
        stats["duration_stats"] = splits["duration_stats"]
    
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="数据集分割工具")
    parser.add_argument("--metadata", type=str, required=True,
                       help="元数据文件路径 (JSON 或 CSV)")
    parser.add_argument("--output_dir", type=str, required=True,
                       help="输出目录")
    parser.add_argument("--method", type=str, default="random",
                       choices=["random", "stratified", "speaker_independent", "duration_balanced"],
                       help="分割方法")
    parser.add_argument("--train_ratio", type=float, default=0.8,
                       help="训练集比例")
    parser.add_argument("--dev_ratio", type=float, default=0.1,
                       help="验证集比例")
    parser.add_argument("--test_ratio", type=float, default=0.1,
                       help="测试集比例")
    parser.add_argument("--stratify_key", type=str, default="speaker_id",
                       help="分层键 (用于 stratified 方法)")
    parser.add_argument("--seed", type=int, default=42,
                       help="随机种子")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("数据集分割")
    print("=" * 60)
    print(f"元数据：{args.metadata}")
    print(f"输出目录：{args.output_dir}")
    print(f"分割方法：{args.method}")
    print(f"比例：train={args.train_ratio}, dev={args.dev_ratio}, test={args.test_ratio}")
    print("=" * 60)
    
    # 加载元数据
    metadata_path = Path(args.metadata)
    if metadata_path.suffix == '.json':
        with open(metadata_path, 'r', encoding='utf-8') as f:
            samples = json.load(f)
    elif metadata_path.suffix == '.csv':
        import csv
        samples = []
        with open(metadata_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 转换数值类型
                if 'duration' in row:
                    row['duration'] = float(row['duration'])
                samples.append(row)
    else:
        print(f"不支持的文件格式：{metadata_path.suffix}")
        return
    
    print(f"\n加载 {len(samples)} 个样本")
    
    # 执行分割
    if args.method == "random":
        splits = random_split(
            samples,
            train_ratio=args.train_ratio,
            dev_ratio=args.dev_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed
        )
    elif args.method == "stratified":
        splits = stratified_split(
            samples,
            stratify_key=args.stratify_key,
            train_ratio=args.train_ratio,
            dev_ratio=args.dev_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed
        )
    elif args.method == "speaker_independent":
        splits = speaker_independent_split(samples)
    elif args.method == "duration_balanced":
        splits = duration_balanced_split(
            samples,
            train_ratio=args.train_ratio,
            dev_ratio=args.dev_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed
        )
    
    # 保存结果
    output_dir = Path(args.output_dir)
    print(f"\n保存分割结果到：{output_dir}")
    save_splits(splits, output_dir)
    
    print("\n" + "=" * 60)
    print("数据集分割完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
