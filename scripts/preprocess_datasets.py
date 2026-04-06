#!/usr/bin/env python3
"""
数据集预处理脚本 v1.0
=====================
功能：AISHELL 及其他语音数据集的清洗、分割、特征提取

创建者：Hulk 🟢
创建日期：2026-03-25
用途：为 CittaVerse 语音识别/叙事分析 pipeline 准备标准化数据

依赖：
    pip install librosa numpy pandas tqdm soundfile

用法：
    python scripts/preprocess_datasets.py --dataset aishell --output data/processed
    python scripts/preprocess_datasets.py --dataset all --workers 4
"""

import argparse
import json
import os
import tarfile
import wave
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import soundfile as sf
from tqdm import tqdm

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("警告：librosa 未安装，特征提取功能将不可用")
    print("安装：pip install librosa")


class DatasetPreprocessor:
    """语音数据集预处理主类"""
    
    def __init__(
        self,
        dataset_name: str,
        raw_dir: str,
        output_dir: str,
        sample_rate: int = 16000,
        test_split: float = 0.1,
        val_split: float = 0.1
    ):
        self.dataset_name = dataset_name
        self.raw_dir = Path(raw_dir)
        self.output_dir = Path(output_dir)
        self.sample_rate = sample_rate
        self.test_split = test_split
        self.val_split = val_split
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "audio").mkdir(exist_ok=True)
        (self.output_dir / "train").mkdir(exist_ok=True)
        (self.output_dir / "val").mkdir(exist_ok=True)
        (self.output_dir / "test").mkdir(exist_ok=True)
        
        print(f"初始化预处理器：{dataset_name}")
        print(f"  原始数据：{raw_dir}")
        print(f"  输出目录：{output_dir}")
        print(f"  目标采样率：{sample_rate}Hz")
        print(f"  分割比例：train={1-test_split-val_split:.1%}, val={val_split:.1%}, test={test_split:.1%}")
    
    def extract_aishell(self) -> bool:
        """解压 AISHELL 数据集"""
        print("\n=== 解压 AISHELL 数据集 ===")
        
        aishell_dir = self.raw_dir.parent / "data_aishell"
        if not aishell_dir.exists():
            print(f"错误：未找到 AISHELL 目录 {aishell_dir}")
            return False
        
        # 查找所有 tar.gz 文件
        tar_files = list(aishell_dir.glob("wav/*.tar.gz"))
        print(f"找到 {len(tar_files)} 个压缩文件")
        
        extracted_count = 0
        for tar_file in tqdm(tar_files, desc="解压"):
            try:
                with tarfile.open(tar_file, "r:gz") as tar:
                    tar.extractall(path=self.output_dir / "audio")
                    extracted_count += 1
            except Exception as e:
                print(f"警告：解压失败 {tar_file.name}: {e}")
        
        print(f"解压完成：{extracted_count}/{len(tar_files)}")
        return extracted_count > 0
    
    def load_aishell_transcript(self) -> Dict[str, str]:
        """加载 AISHELL 文本标注"""
        print("\n=== 加载 AISHELL 文本标注 ===")
        
        # AISHELL 的标注文件位置
        transcript_path = self.raw_dir.parent / "data_aishell" / "transcript" / "aishell_transcript_v0.8.txt"
        
        if not transcript_path.exists():
            print(f"警告：未找到标注文件 {transcript_path}")
            return {}
        
        transcripts = {}
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    audio_id, text = parts
                    transcripts[audio_id] = text
        
        print(f"加载标注：{len(transcripts)} 条")
        return transcripts
    
    def collect_audio_files(self) -> List[Path]:
        """收集所有音频文件"""
        print("\n=== 收集音频文件 ===")
        
        audio_dir = self.output_dir / "audio"
        if not audio_dir.exists():
            print(f"错误：音频目录不存在 {audio_dir}")
            return []
        
        # 查找所有 WAV 文件
        audio_files = list(audio_dir.rglob("*.wav"))
        print(f"找到 {len(audio_files)} 个音频文件")
        
        return audio_files
    
    def normalize_audio(self, audio_path: Path, output_path: Path) -> bool:
        """标准化音频文件（重采样、音量归一化）"""
        try:
            if not LIBROSA_AVAILABLE:
                # 如果没有 librosa，直接复制文件
                import shutil
                shutil.copy2(audio_path, output_path)
                return True
            
            # 加载音频
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # 音量归一化
            y = librosa.util.normalize(y)
            
            # 保存
            sf.write(output_path, y, self.sample_rate, format='WAV')
            return True
            
        except Exception as e:
            print(f"警告：处理失败 {audio_path.name}: {e}")
            return False
    
    def extract_features(
        self,
        audio_path: Path,
        n_mfcc: int = 13,
        n_mels: int = 40
    ) -> Dict[str, np.ndarray]:
        """提取音频特征"""
        if not LIBROSA_AVAILABLE:
            return {}
        
        try:
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            features = {}
            
            # MFCC
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
            features['mfcc'] = mfcc.T  # 转置为 (time, features)
            
            # Mel 频谱图
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels)
            features['mel_spec'] = mel_spec.T
            
            # 频谱对比度
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
            features['contrast'] = contrast.T
            
            # 过零率
            zcr = librosa.feature.zero_crossing_rate(y)
            features['zcr'] = zcr.T
            
            return features
            
        except Exception as e:
            print(f"特征提取失败 {audio_path.name}: {e}")
            return {}
    
    def split_dataset(
        self,
        files: List[Path],
        transcripts: Dict[str, str]
    ) -> Tuple[List, List, List]:
        """分割数据集为 train/val/test"""
        print("\n=== 分割数据集 ===")
        
        np.random.seed(42)  # 可复现
        indices = np.random.permutation(len(files))
        
        n_test = int(len(files) * self.test_split)
        n_val = int(len(files) * self.val_split)
        
        test_idx = indices[:n_test]
        val_idx = indices[n_test:n_test + n_val]
        train_idx = indices[n_test + n_val:]
        
        train_files = [files[i] for i in train_idx]
        val_files = [files[i] for i in val_idx]
        test_files = [files[i] for i in test_idx]
        
        print(f"训练集：{len(train_files)} 文件")
        print(f"验证集：{len(val_files)} 文件")
        print(f"测试集：{len(test_files)} 文件")
        
        return train_files, val_files, test_files
    
    def create_manifest(
        self,
        files: List[Path],
        transcripts: Dict[str, str],
        output_path: Path
    ):
        """创建数据清单（manifest）"""
        manifest = []
        
        for audio_path in tqdm(files, desc="创建清单"):
            audio_id = audio_path.stem
            duration = 0.0
            
            # 获取音频时长
            if LIBROSA_AVAILABLE:
                try:
                    y, sr = librosa.load(audio_path, sr=None)
                    duration = len(y) / sr
                except:
                    duration = 0.0
            
            transcript = transcripts.get(audio_id, "")
            
            manifest.append({
                'audio_path': str(audio_path),
                'audio_id': audio_id,
                'duration': duration,
                'transcript': transcript,
                'language': 'zh-CN'
            })
        
        # 保存为 JSONL
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in manifest:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"清单已保存：{output_path} ({len(manifest)} 条)")
        return manifest
    
    def process_aishell(self) -> bool:
        """处理 AISHELL 数据集的主流程"""
        print(f"\n{'='*60}")
        print(f"开始处理 AISHELL 数据集")
        print(f"{'='*60}")
        
        # Step 1: 解压
        if not self.extract_aishell():
            print("解压失败，终止处理")
            return False
        
        # Step 2: 加载标注
        transcripts = self.load_aishell_transcript()
        
        # Step 3: 收集音频文件
        audio_files = self.collect_audio_files()
        if not audio_files:
            print("未找到音频文件，终止处理")
            return False
        
        # Step 4: 标准化音频
        print("\n=== 标准化音频 ===")
        normalized_files = []
        for audio_path in tqdm(audio_files, desc="标准化"):
            output_path = self.output_dir / "audio" / f"{audio_path.stem}_norm.wav"
            if self.normalize_audio(audio_path, output_path):
                normalized_files.append(output_path)
        
        print(f"标准化完成：{len(normalized_files)}/{len(audio_files)}")
        
        # Step 5: 分割数据集
        train_files, val_files, test_files = self.split_dataset(
            normalized_files, transcripts
        )
        
        # Step 6: 创建清单
        print("\n=== 创建数据清单 ===")
        self.create_manifest(train_files, transcripts, self.output_dir / "train" / "manifest.jsonl")
        self.create_manifest(val_files, transcripts, self.output_dir / "val" / "manifest.jsonl")
        self.create_manifest(test_files, transcripts, self.output_dir / "test" / "manifest.jsonl")
        
        # Step 7: 特征提取（可选）
        if LIBROSA_AVAILABLE:
            print("\n=== 特征提取 ===")
            self.extract_features_batch(train_files[:100], "train")  # 示例：只处理前 100 个
        
        # Step 8: 保存处理报告
        self.save_processing_report({
            'dataset': self.dataset_name,
            'total_files': len(audio_files),
            'normalized_files': len(normalized_files),
            'train_files': len(train_files),
            'val_files': len(val_files),
            'test_files': len(test_files),
            'transcripts_loaded': len(transcripts),
            'sample_rate': self.sample_rate
        })
        
        print(f"\n{'='*60}")
        print(f"AISHELL 处理完成 ✓")
        print(f"输出目录：{self.output_dir}")
        print(f"{'='*60}")
        
        return True
    
    def extract_features_batch(self, files: List[Path], split: str):
        """批量提取特征并保存"""
        features_dir = self.output_dir / "features" / split
        features_dir.mkdir(parents=True, exist_ok=True)
        
        for audio_path in tqdm(files, desc=f"特征提取 ({split})"):
            features = self.extract_features(audio_path)
            if features:
                output_path = features_dir / f"{audio_path.stem}.npz"
                np.savez_compressed(output_path, **features)
    
    def save_processing_report(self, stats: Dict):
        """保存处理报告"""
        report_path = self.output_dir / "processing_report.json"
        
        import datetime
        stats['timestamp'] = datetime.datetime.now().isoformat()
        stats['processor_version'] = '1.0'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"处理报告已保存：{report_path}")


def main():
    parser = argparse.ArgumentParser(
        description='语音数据集预处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--dataset',
        type=str,
        default='aishell',
        choices=['aishell', 'common_voice', 'elderly_voice', 'all'],
        help='要处理的数据集'
    )
    
    parser.add_argument(
        '--raw-dir',
        type=str,
        default='/home/node/.openclaw/workspace-hulk/data',
        help='原始数据目录'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='/home/node/.openclaw/workspace-hulk/data/processed',
        help='输出目录'
    )
    
    parser.add_argument(
        '--sample-rate',
        type=int,
        default=16000,
        help='目标采样率 (Hz)'
    )
    
    parser.add_argument(
        '--test-split',
        type=float,
        default=0.1,
        help='测试集比例'
    )
    
    parser.add_argument(
        '--val-split',
        type=float,
        default=0.1,
        help='验证集比例'
    )
    
    parser.add_argument(
        '--skip-normalization',
        action='store_true',
        help='跳过音频标准化'
    )
    
    parser.add_argument(
        '--extract-features',
        action='store_true',
        help='提取 MFCC 等特征'
    )
    
    args = parser.parse_args()
    
    # 创建预处理器
    preprocessor = DatasetPreprocessor(
        dataset_name=args.dataset,
        raw_dir=args.raw_dir,
        output_dir=args.output_dir,
        sample_rate=args.sample_rate,
        test_split=args.test_split,
        val_split=args.val_split
    )
    
    # 处理指定数据集
    if args.dataset == 'aishell':
        success = preprocessor.process_aishell()
    else:
        print(f"暂不支持的数据集：{args.dataset}")
        print("当前仅支持：aishell")
        success = False
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
