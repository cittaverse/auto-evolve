#!/usr/bin/env python3
"""
通用语音数据集预处理工具
支持：LibriSpeech, Common Voice, THCHS-30, ST-CMDS 等

Usage:
    python preprocess_common.py --dataset librispeech --data_dir /path/to/data --output_dir /path/to/output

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
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing


class GenericPreprocessor:
    """通用语音数据集预处理器"""
    
    def __init__(self, dataset_name: str, data_dir: str, output_dir: str, 
                 sample_rate: int = 16000, n_jobs: int = 4):
        self.dataset_name = dataset_name.lower()
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.sample_rate = sample_rate
        self.n_jobs = n_jobs
        
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
    
    def validate_audio(self, wav_path: Path) -> Tuple[bool, Optional[float]]:
        """验证音频文件"""
        try:
            y, sr = librosa.load(str(wav_path), sr=None)
            duration = len(y) / sr
            
            # 检查时长 (0.3s - 30s)
            if duration < 0.3 or duration > 30.0:
                return False, None
            
            return True, duration
        except Exception as e:
            return False, None
    
    def extract_features(self, wav_path: Path) -> Dict[str, np.ndarray]:
        """
        提取音频特征
        
        特征包括:
        - MFCC (13 维 + delta + delta-delta = 39 维)
        - Log Mel Spectrogram (40 维)
        - Chroma (12 维)
        - Spectral Contrast (7 维)
        - Zero Crossing Rate
        - RMS Energy
        """
        y, sr = librosa.load(str(wav_path), sr=self.sample_rate)
        
        # MFCC + 一阶 + 二阶差分
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_delta = librosa.feature.delta(mfcc)
        mfcc_delta2 = librosa.feature.delta(mfcc, order=2)
        
        features = {
            "mfcc": mfcc,
            "mfcc_delta": mfcc_delta,
            "mfcc_delta2": mfcc_delta2,
            "log_mel": librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40),
            "chroma": librosa.feature.chroma_stft(y=y, sr=sr),
            "spectral_contrast": librosa.feature.spectral_contrast(y=y, sr=sr),
            "tonnetz": librosa.feature.tonnetz(y=y, sr=sr),
            "zcr": librosa.feature.zero_crossing_rate(y),
            "rms": librosa.feature.rms(y)
        }
        
        # 计算统计特征
        features_stats = {}
        for name, feat in features.items():
            features_stats[f"{name}_mean"] = np.mean(feat, axis=1)
            features_stats[f"{name}_std"] = np.std(feat, axis=1)
            features_stats[f"{name}_min"] = np.min(feat, axis=1)
            features_stats[f"{name}_max"] = np.max(feat, axis=1)
        
        return features_stats
    
    def process_librispeech(self, split: str = "train-clean-100") -> List[Dict]:
        """处理 LibriSpeech 数据集"""
        wav_dir = self.data_dir / split
        if not wav_dir.exists():
            print(f"警告：{wav_dir} 不存在")
            return []
        
        samples = []
        wav_files = list(wav_dir.rglob("*.flac")) + list(wav_dir.rglob("*.wav"))
        
        print(f"\n处理 LibriSpeech {split}，共 {len(wav_files)} 个文件...")
        
        # 加载转录文本
        transcripts = self._load_librispeech_transcripts(wav_dir)
        
        for wav_path in tqdm(wav_files, desc=f"Processing {split}"):
            self.stats["total_samples"] += 1
            
            utterance_id = wav_path.stem
            parts = wav_path.stem.split('-')
            if len(parts) >= 2:
                speaker_id = parts[0]
                chapter_id = parts[1]
            else:
                speaker_id = "unknown"
                chapter_id = "unknown"
            
            is_valid, duration = self.validate_audio(wav_path)
            
            if not is_valid:
                self.stats["invalid_samples"] += 1
                continue
            
            self.stats["valid_samples"] += 1
            self.stats["total_duration"] += duration
            self.stats["speakers"].add(speaker_id)
            
            # 提取特征
            features = self.extract_features(wav_path)
            output_feat_path = self.output_dir / "features" / f"{utterance_id}.npz"
            np.savez_compressed(output_feat_path, **features)
            
            transcript = transcripts.get(utterance_id, "")
            
            sample = {
                "utterance_id": utterance_id,
                "speaker_id": speaker_id,
                "chapter_id": chapter_id,
                "dataset": "librispeech",
                "split": split,
                "duration": round(duration, 3),
                "transcript": transcript,
                "wav_path": str(wav_path),
                "feature_path": str(output_feat_path)
            }
            
            samples.append(sample)
        
        return samples
    
    def _load_librispeech_transcripts(self, wav_dir: Path) -> Dict[str, str]:
        """加载 LibriSpeech 转录文本"""
        transcripts = {}
        for text_file in wav_dir.rglob("*.trans.txt"):
            with open(text_file, 'r') as f:
                for line in f:
                    parts = line.strip().split(' ', 1)
                    if len(parts) == 2:
                        utterance_id, text = parts
                        transcripts[utterance_id] = text.lower()
        return transcripts
    
    def process_common_voice(self, split: str = "train") -> List[Dict]:
        """处理 Mozilla Common Voice 数据集"""
        wav_dir = self.data_dir / "clips"
        tsv_file = self.data_dir / f"{split}.tsv"
        
        if not wav_dir.exists():
            print(f"警告：{wav_dir} 不存在")
            return []
        
        if not tsv_file.exists():
            print(f"警告：{tsv_file} 不存在")
            return []
        
        # 加载 TSV 元数据
        import csv
        metadata = {}
        with open(tsv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                metadata[row['path']] = row
        
        samples = []
        audio_files = list(wav_dir.glob("*.mp3")) + list(wav_dir.glob("*.wav"))
        
        print(f"\n处理 Common Voice {split}，共 {len(audio_files)} 个文件...")
        
        for audio_path in tqdm(audio_files, desc=f"Processing {split}"):
            self.stats["total_samples"] += 1
            
            relative_path = audio_path.name
            if relative_path not in metadata:
                self.stats["invalid_samples"] += 1
                continue
            
            meta = metadata[relative_path]
            utterance_id = audio_path.stem
            
            is_valid, duration = self.validate_audio(audio_path)
            
            if not is_valid:
                self.stats["invalid_samples"] += 1
                continue
            
            self.stats["valid_samples"] += 1
            self.stats["total_duration"] += duration
            self.stats["speakers"].add(meta.get('client_id', 'unknown'))
            
            # 提取特征
            features = self.extract_features(audio_path)
            output_feat_path = self.output_dir / "features" / f"{utterance_id}.npz"
            np.savez_compressed(output_feat_path, **features)
            
            sample = {
                "utterance_id": utterance_id,
                "speaker_id": meta.get('client_id', 'unknown'),
                "dataset": "common_voice",
                "split": split,
                "duration": round(duration, 3),
                "transcript": meta.get('sentence', ''),
                "language": meta.get('locale', 'unknown'),
                "wav_path": str(audio_path),
                "feature_path": str(output_feat_path)
            }
            
            samples.append(sample)
        
        return samples
    
    def process_thchs30(self) -> List[Dict]:
        """处理 THCHS-30 中文数据集"""
        wav_dir = self.data_dir / "data"
        if not wav_dir.exists():
            print(f"警告：{wav_dir} 不存在")
            return []
        
        samples = []
        wav_files = list(wav_dir.glob("*.wav"))
        
        print(f"\n处理 THCHS-30，共 {len(wav_files)} 个文件...")
        
        for wav_path in tqdm(wav_files, desc="Processing THCHS-30"):
            self.stats["total_samples"] += 1
            
            utterance_id = wav_path.stem
            
            # 查找对应的转录文件
            transcript_path = wav_path.with_suffix('.trn')
            transcript = ""
            if transcript_path.exists():
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) >= 2:
                        transcript = lines[1].strip()  # 第二行是中文文本
            
            is_valid, duration = self.validate_audio(wav_path)
            
            if not is_valid:
                self.stats["invalid_samples"] += 1
                continue
            
            self.stats["valid_samples"] += 1
            self.stats["total_duration"] += duration
            
            # 提取特征
            features = self.extract_features(wav_path)
            output_feat_path = self.output_dir / "features" / f"{utterance_id}.npz"
            np.savez_compressed(output_feat_path, **features)
            
            sample = {
                "utterance_id": utterance_id,
                "speaker_id": "unknown",
                "dataset": "thchs30",
                "split": "mixed",
                "duration": round(duration, 3),
                "transcript": transcript,
                "wav_path": str(wav_path),
                "feature_path": str(output_feat_path)
            }
            
            samples.append(sample)
        
        return samples
    
    def save_metadata(self, samples: List[Dict], split: str):
        """保存元数据"""
        metadata_path = self.output_dir / "metadata" / f"{split}.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        
        # CSV 格式
        csv_path = self.output_dir / "metadata" / f"{split}.csv"
        with open(csv_path, 'w', encoding='utf-8') as f:
            if samples:
                headers = list(samples[0].keys())
                f.write(','.join(headers) + '\n')
                for s in samples:
                    values = []
                    for h in headers:
                        v = str(s.get(h, '')).replace('"', '""')
                        values.append(f'"{v}"')
                    f.write(','.join(values) + '\n')
    
    def save_statistics(self):
        """保存统计信息"""
        stats = {
            "dataset": self.dataset_name,
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
    parser = argparse.ArgumentParser(description="通用语音数据集预处理")
    parser.add_argument("--dataset", type=str, required=True,
                       choices=["librispeech", "common_voice", "thchs30", "st_cmds"],
                       help="数据集名称")
    parser.add_argument("--data_dir", type=str, required=True,
                       help="原始数据目录")
    parser.add_argument("--output_dir", type=str, required=True,
                       help="输出目录")
    parser.add_argument("--sample_rate", type=int, default=16000,
                       help="目标采样率")
    parser.add_argument("--split", type=str, default="train",
                       help="数据集划分")
    parser.add_argument("--n_jobs", type=int, default=4,
                       help="并行处理线程数")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"语音数据集预处理 - {args.dataset}")
    print("=" * 60)
    
    preprocessor = GenericPreprocessor(
        dataset_name=args.dataset,
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        sample_rate=args.sample_rate,
        n_jobs=args.n_jobs
    )
    
    # 根据数据集类型调用不同的处理方法
    if args.dataset == "librispeech":
        samples = preprocessor.process_librispeech(split=args.split)
    elif args.dataset == "common_voice":
        samples = preprocessor.process_common_voice(split=args.split)
    elif args.dataset == "thchs30":
        samples = preprocessor.process_thchs30()
    else:
        print(f"不支持的数据集：{args.dataset}")
        return
    
    preprocessor.save_metadata(samples, args.split)
    stats = preprocessor.save_statistics()
    
    print("\n" + "=" * 60)
    print("处理统计")
    print("=" * 60)
    print(f"数据集：{stats['dataset']}")
    print(f"总样本数：{stats['total_samples']}")
    print(f"有效样本：{stats['valid_samples']}")
    print(f"无效样本：{stats['invalid_samples']}")
    print(f"总时长：{stats['total_duration_hours']} 小时")
    print(f"说话人数：{stats['num_speakers']}")
    print(f"平均时长：{stats['avg_duration_seconds']} 秒")
    print("=" * 60)
    print(f"\n✓ {args.dataset} 预处理完成!")


if __name__ == "__main__":
    main()
