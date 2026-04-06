#!/usr/bin/env python3
"""
AISHELL 数据集预处理脚本
功能：清洗、分割、特征提取

Usage:
    python preprocess_aishell.py --data_dir /path/to/AISHELL-1 --output_dir /path/to/output

作者：Hulk 🟢
日期：2026-04-02
"""

import os
import sys
import argparse
import json
import wave
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import librosa
import librosa.feature
from tqdm import tqdm


class AISHELLPreprocessor:
    """AISHELL 数据集预处理器"""
    
    def __init__(self, data_dir: str, output_dir: str, sample_rate: int = 16000):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.sample_rate = sample_rate
        
        # 创建输出目录结构
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "wav").mkdir(exist_ok=True)
        (self.output_dir / "features").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)
        
        # 统计信息
        self.stats = {
            "total_samples": 0,
            "valid_samples": 0,
            "invalid_samples": 0,
            "total_duration": 0.0,
            "speakers": set()
        }
    
    def load_transcript(self, transcript_path: Path) -> Dict[str, str]:
        """加载转录文本"""
        transcripts = {}
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    utterance_id, text = parts
                    transcripts[utterance_id] = text
        return transcripts
    
    def validate_audio(self, wav_path: Path) -> Tuple[bool, Optional[float]]:
        """
        验证音频文件
        返回：(是否有效，时长)
        """
        try:
            with wave.open(str(wav_path), 'rb') as wf:
                n_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                
                # 检查音频参数
                if n_channels != 1:
                    return False, None
                if sample_width != 2:  # 16-bit
                    return False, None
                if framerate != 16000:
                    return False, None
                
                duration = n_frames / framerate
                
                # 检查时长 (0.5s - 20s)
                if duration < 0.5 or duration > 20.0:
                    return False, None
                
                return True, duration
        except Exception as e:
            return False, None
    
    def extract_features(self, wav_path: Path) -> Dict[str, np.ndarray]:
        """提取音频特征"""
        y, sr = librosa.load(str(wav_path), sr=self.sample_rate)
        
        features = {
            # MFCC (13 维)
            "mfcc": librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13),
            
            # Log Mel Spectrogram (40 维)
            "log_mel": librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40),
            
            # Chroma (12 维)
            "chroma": librosa.feature.chroma_stft(y=y, sr=sr),
            
            # Spectral Contrast (7 维)
            "spectral_contrast": librosa.feature.spectral_contrast(y=y, sr=sr),
            
            # Tonnetz (6 维)
            "tonnetz": librosa.feature.tonnetz(y=y, sr=sr)
        }
        
        # 计算统计特征 (mean, std)
        features_stats = {}
        for name, feat in features.items():
            features_stats[f"{name}_mean"] = np.mean(feat, axis=1)
            features_stats[f"{name}_std"] = np.std(feat, axis=1)
        
        return features_stats
    
    def process_dataset(self, split: str = "train") -> List[Dict]:
        """
        处理数据集
        
        Args:
            split: 数据集划分 (train/dev/test)
        
        Returns:
            样本元数据列表
        """
        # AISHELL-1 目录结构
        wav_dir = self.data_dir / "wav" / split
        transcript_file = self.data_dir / "transcript" / f"aishell_transcript_{split}.txt"
        
        if not wav_dir.exists():
            print(f"警告：{wav_dir} 不存在")
            return []
        
        if not transcript_file.exists():
            print(f"警告：{transcript_file} 不存在")
            return []
        
        # 加载转录
        transcripts = self.load_transcript(transcript_file)
        
        # 遍历音频文件
        samples = []
        wav_files = list(wav_dir.rglob("*.wav"))
        
        print(f"\n处理 {split} 集，共 {len(wav_files)} 个音频文件...")
        
        for wav_path in tqdm(wav_files, desc=f"Processing {split}"):
            utterance_id = wav_path.stem
            speaker_id = wav_path.parent.name
            
            self.stats["total_samples"] += 1
            
            # 验证音频
            is_valid, duration = self.validate_audio(wav_path)
            
            if not is_valid:
                self.stats["invalid_samples"] += 1
                continue
            
            # 检查是否有对应转录
            if utterance_id not in transcripts:
                self.stats["invalid_samples"] += 1
                continue
            
            self.stats["valid_samples"] += 1
            self.stats["total_duration"] += duration
            self.stats["speakers"].add(speaker_id)
            
            # 复制/处理音频文件
            output_wav_path = self.output_dir / "wav" / f"{utterance_id}.wav"
            # 这里可以选择复制文件或重新采样保存
            # shutil.copy2(wav_path, output_wav_path)
            
            # 提取特征
            features = self.extract_features(wav_path)
            
            # 保存特征
            output_feat_path = self.output_dir / "features" / f"{utterance_id}.npz"
            np.savez_compressed(output_feat_path, **features)
            
            # 构建样本元数据
            sample = {
                "utterance_id": utterance_id,
                "speaker_id": speaker_id,
                "split": split,
                "duration": round(duration, 3),
                "transcript": transcripts[utterance_id],
                "wav_path": str(output_wav_path),
                "feature_path": str(output_feat_path)
            }
            
            samples.append(sample)
        
        return samples
    
    def create_data_splits(self, samples: List[Dict], 
                          train_ratio: float = 0.8,
                          dev_ratio: float = 0.1,
                          test_ratio: float = 0.1) -> Dict[str, List[Dict]]:
        """
        创建数据集划分（如果原始数据没有划分）
        """
        np.random.seed(42)
        indices = np.random.permutation(len(samples))
        
        n_train = int(len(samples) * train_ratio)
        n_dev = int(len(samples) * dev_ratio)
        
        train_indices = indices[:n_train]
        dev_indices = indices[n_train:n_train + n_dev]
        test_indices = indices[n_train + n_dev:]
        
        splits = {
            "train": [samples[i] for i in train_indices],
            "dev": [samples[i] for i in dev_indices],
            "test": [samples[i] for i in test_indices]
        }
        
        return splits
    
    def save_metadata(self, samples: List[Dict], split: str):
        """保存元数据"""
        metadata_path = self.output_dir / "metadata" / f"{split}.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        
        # 同时保存为 CSV 格式
        csv_path = self.output_dir / "metadata" / f"{split}.csv"
        with open(csv_path, 'w', encoding='utf-8') as f:
            # 写入表头
            f.write("utterance_id,speaker_id,split,duration,transcript,wav_path,feature_path\n")
            for s in samples:
                # 转义文本中的逗号和引号
                transcript = s["transcript"].replace('"', '""')
                f.write(f'{s["utterance_id"]},{s["speaker_id"]},{s["split"]},'
                       f'{s["duration"]},"{transcript}",{s["wav_path"]},{s["feature_path"]}\n')
    
    def save_statistics(self):
        """保存统计信息"""
        stats = {
            "total_samples": self.stats["total_samples"],
            "valid_samples": self.stats["valid_samples"],
            "invalid_samples": self.stats["invalid_samples"],
            "total_duration_hours": round(self.stats["total_duration"] / 3600, 2),
            "num_speakers": len(self.stats["speakers"]),
            "avg_duration_seconds": round(
                self.stats["total_duration"] / max(self.stats["valid_samples"], 1), 3
            )
        }
        
        stats_path = self.output_dir / "metadata" / "statistics.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        return stats


def main():
    parser = argparse.ArgumentParser(description="AISHELL 数据集预处理")
    parser.add_argument("--data_dir", type=str, required=True, 
                       help="AISHELL-1 原始数据目录")
    parser.add_argument("--output_dir", type=str, required=True,
                       help="输出目录")
    parser.add_argument("--sample_rate", type=int, default=16000,
                       help="目标采样率")
    parser.add_argument("--splits", type=str, nargs="+", 
                       default=["train", "dev", "test"],
                       help="要处理的数据集划分")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("AISHELL 数据集预处理")
    print("=" * 60)
    print(f"输入目录：{args.data_dir}")
    print(f"输出目录：{args.output_dir}")
    print(f"采样率：{args.sample_rate} Hz")
    print(f"处理划分：{args.splits}")
    print("=" * 60)
    
    preprocessor = AISHELLPreprocessor(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        sample_rate=args.sample_rate
    )
    
    all_samples = []
    
    for split in args.splits:
        samples = preprocessor.process_dataset(split=split)
        preprocessor.save_metadata(samples, split)
        all_samples.extend(samples)
        print(f"\n✓ {split} 集处理完成：{len(samples)} 个有效样本")
    
    # 保存统计信息
    stats = preprocessor.save_statistics()
    
    print("\n" + "=" * 60)
    print("处理统计")
    print("=" * 60)
    print(f"总样本数：{stats['total_samples']}")
    print(f"有效样本：{stats['valid_samples']}")
    print(f"无效样本：{stats['invalid_samples']}")
    print(f"总时长：{stats['total_duration_hours']} 小时")
    print(f"说话人数：{stats['num_speakers']}")
    print(f"平均时长：{stats['avg_duration_seconds']} 秒")
    print("=" * 60)
    print("\n✓ AISHELL 预处理完成!")


if __name__ == "__main__":
    main()
