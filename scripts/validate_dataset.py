#!/usr/bin/env python3
"""
数据集验证工具
==============
检查预处理后的数据质量，发现潜在问题

创建者：Hulk 🟢
创建日期：2026-03-25
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

try:
    import soundfile as sf
    import librosa
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    print("警告：部分依赖未安装，某些检查将跳过")


class DatasetValidator:
    """数据集验证器"""
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.issues = []
        self.stats = {}
    
    def check_manifest(self, manifest_path: str) -> Dict:
        """检查 manifest 文件"""
        manifest_path = Path(manifest_path)
        
        if not manifest_path.exists():
            self.issues.append(f"ERROR: Manifest 不存在：{manifest_path}")
            return {'valid': False}
        
        entries = []
        missing_files = []
        empty_transcripts = []
        duration_stats = []
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                    
                    # 检查音频文件是否存在
                    audio_path = Path(entry.get('audio_path', ''))
                    if not audio_path.exists():
                        missing_files.append({
                            'line': line_num,
                            'id': entry.get('audio_id', 'unknown'),
                            'path': str(audio_path)
                        })
                    
                    # 检查标注是否为空
                    transcript = entry.get('transcript', '').strip()
                    if not transcript:
                        empty_transcripts.append({
                            'line': line_num,
                            'id': entry.get('audio_id', 'unknown')
                        })
                    
                    # 收集时长统计
                    duration = entry.get('duration', 0)
                    if duration > 0:
                        duration_stats.append(duration)
                    
                except json.JSONDecodeError as e:
                    self.issues.append(f"ERROR: 第{line_num}行 JSON 解析失败：{e}")
        
        # 统计信息
        stats = {
            'total_entries': len(entries),
            'missing_files': len(missing_files),
            'empty_transcripts': len(empty_transcripts),
            'avg_duration': np.mean(duration_stats) if duration_stats else 0,
            'min_duration': min(duration_stats) if duration_stats else 0,
            'max_duration': max(duration_stats) if duration_stats else 0,
            'valid': len(missing_files) == 0 and len(empty_transcripts) == 0
        }
        
        if missing_files:
            self.issues.append(f"WARNING: {len(missing_files)} 个音频文件缺失")
            if len(missing_files) <= 5:
                for mf in missing_files:
                    self.issues.append(f"  - {mf['id']}: {mf['path']}")
        
        if empty_transcripts:
            self.issues.append(f"WARNING: {len(empty_transcripts)} 条空标注")
        
        return stats
    
    def check_audio_quality(self, audio_paths: List[str], max_duration: float = 30.0) -> Dict:
        """检查音频质量"""
        if not TOOLS_AVAILABLE:
            return {'skipped': True}
        
        quality_issues = []
        duration_distribution = []
        
        for audio_path in audio_paths[:100]:  # 抽样检查
            try:
                y, sr = librosa.load(audio_path, sr=None)
                duration = len(y) / sr
                duration_distribution.append(duration)
                
                # 检查时长
                if duration > max_duration:
                    quality_issues.append({
                        'path': audio_path,
                        'issue': 'too_long',
                        'value': f"{duration:.2f}s"
                    })
                elif duration < 0.1:
                    quality_issues.append({
                        'path': audio_path,
                        'issue': 'too_short',
                        'value': f"{duration:.2f}s"
                    })
                
                # 检查静音
                rms = np.sqrt(np.mean(y**2))
                if rms < 0.001:
                    quality_issues.append({
                        'path': audio_path,
                        'issue': 'too_quiet',
                        'value': f"RMS={rms:.6f}"
                    })
                
                # 检查削波
                if np.max(np.abs(y)) >= 0.99:
                    quality_issues.append({
                        'path': audio_path,
                        'issue': 'clipping',
                        'value': f"peak={np.max(np.abs(y)):.4f}"
                    })
                
            except Exception as e:
                quality_issues.append({
                    'path': audio_path,
                    'issue': 'load_error',
                    'value': str(e)
                })
        
        return {
            'checked': len(audio_paths[:100]),
            'issues': len(quality_issues),
            'avg_duration': np.mean(duration_distribution) if duration_distribution else 0,
            'quality_issues': quality_issues[:10]  # 只显示前 10 个问题
        }
    
    def check_split_balance(self) -> Dict:
        """检查数据集分割平衡"""
        splits = ['train', 'val', 'test']
        counts = {}
        
        for split in splits:
            manifest_path = self.data_dir / split / 'manifest.jsonl'
            if manifest_path.exists():
                with open(manifest_path, 'r') as f:
                    counts[split] = sum(1 for _ in f)
            else:
                counts[split] = 0
        
        total = sum(counts.values())
        ratios = {
            split: count / total if total > 0 else 0
            for split, count in counts.items()
        }
        
        # 检查比例是否合理
        expected_ratios = {'train': 0.8, 'val': 0.1, 'test': 0.1}
        balance_issues = []
        
        for split, expected in expected_ratios.items():
            actual = ratios.get(split, 0)
            if abs(actual - expected) > 0.05:  # 允许 5% 偏差
                balance_issues.append({
                    'split': split,
                    'expected': expected,
                    'actual': actual
                })
        
        return {
            'counts': counts,
            'ratios': ratios,
            'total': total,
            'balance_issues': balance_issues
        }
    
    def check_features(self, features_dir: str) -> Dict:
        """检查特征文件"""
        features_dir = Path(features_dir)
        
        if not features_dir.exists():
            return {'exists': False}
        
        feature_files = list(features_dir.glob('*.npz'))
        
        # 抽样检查特征文件
        valid_count = 0
        invalid_files = []
        
        for feat_file in feature_files[:50]:
            try:
                data = np.load(feat_file)
                if len(data.files) > 0:
                    valid_count += 1
                else:
                    invalid_files.append(str(feat_file))
            except:
                invalid_files.append(str(feat_file))
        
        return {
            'exists': True,
            'total_files': len(feature_files),
            'valid_count': valid_count,
            'invalid_files': invalid_files[:10]
        }
    
    def validate_all(self) -> Dict:
        """执行完整验证"""
        print("=" * 60)
        print("数据集验证报告")
        print("=" * 60)
        print()
        
        results = {}
        
        # 1. 检查各分割集
        for split in ['train', 'val', 'test']:
            manifest_path = self.data_dir / split / 'manifest.jsonl'
            print(f"\n[{split.upper()}] 检查 Manifest...")
            stats = self.check_manifest(manifest_path)
            results[split] = stats
            print(f"  总条目：{stats.get('total_entries', 0)}")
            print(f"  缺失文件：{stats.get('missing_files', 0)}")
            print(f"  空标注：{stats.get('empty_transcripts', 0)}")
            print(f"  平均时长：{stats.get('avg_duration', 0):.2f}s")
        
        # 2. 检查分割平衡
        print(f"\n[平衡性] 检查数据集分割...")
        balance = self.check_split_balance()
        results['balance'] = balance
        print(f"  训练集：{balance['counts'].get('train', 0)} ({balance['ratios'].get('train', 0):.1%})")
        print(f"  验证集：{balance['counts'].get('val', 0)} ({balance['ratios'].get('val', 0):.1%})")
        print(f"  测试集：{balance['counts'].get('test', 0)} ({balance['ratios'].get('test', 0):.1%})")
        
        if balance['balance_issues']:
            for issue in balance['balance_issues']:
                print(f"  ⚠ {issue['split']}: 期望{issue['expected']:.1%}, 实际{issue['actual']:.1%}")
        
        # 3. 检查特征文件
        features_dir = self.data_dir / 'features'
        print(f"\n[特征] 检查特征文件...")
        feat_check = self.check_features(features_dir / 'train')
        results['features'] = feat_check
        if feat_check.get('exists'):
            print(f"  特征目录：存在")
            print(f"  文件总数：{feat_check.get('total_files', 0)}")
            print(f"  有效文件：{feat_check.get('valid_count', 0)}")
        else:
            print(f"  特征目录：不存在")
        
        # 4. 汇总问题
        print(f"\n{'=' * 60}")
        print("发现的问题")
        print("=" * 60)
        
        if self.issues:
            for issue in self.issues:
                print(f"  {issue}")
        else:
            print("  ✓ 未发现严重问题")
        
        # 5. 总体评估
        print(f"\n{'=' * 60}")
        print("总体评估")
        print("=" * 60)
        
        all_valid = all(
            results.get(split, {}).get('valid', False)
            for split in ['train', 'val', 'test']
        )
        
        if all_valid and not self.issues:
            print("  ✓ 数据集验证通过")
        else:
            print("  ⚠ 数据集存在问题，建议修复后使用")
        
        # 保存报告
        report_path = self.data_dir / 'validation_report.json'
        with open(report_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n报告已保存：{report_path}")
        
        return results


def main():
    parser = argparse.ArgumentParser(description='数据集验证工具')
    parser.add_argument('data_dir', help='数据集目录')
    parser.add_argument('--audio-quality', action='store_true', help='检查音频质量（较慢）')
    parser.add_argument('--output', help='报告输出路径')
    
    args = parser.parse_args()
    
    validator = DatasetValidator(args.data_dir)
    results = validator.validate_all()
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n详细报告：{args.output}")


if __name__ == '__main__':
    main()
