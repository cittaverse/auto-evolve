#!/usr/bin/env python3
"""
AISHELL 数据集预处理脚本 v2
功能：清洗、分割、特征提取、标注对齐

Usage:
    python preprocess_aishell_v2.py --data_dir /path/to/AISHELL-1 --output_dir /path/to/output

作者：Hulk 🟢
日期：2026-04-04
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
from datetime import datetime
import random


class AISHELLPreprocessor:
    """AISHELL 数据集预处理器 v2"""
    
    def __init__(self, data_dir: str, output_dir: str, sample_rate: int = 16000):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.sample_rate = sample_rate
        
        # 创建输出目录结构
        self._create_output_structure()
        
        # 统计信息
        self.stats = {
            "total_samples": 0,
            "valid_samples": 0,
            "invalid_samples": 0,
            "total_duration": 0.0,
            "speakers": set(),
            "duration_distribution": {"short": 0, "medium": 0, "long": 0}
        }
        
        # 特征配置
        self.feature_config = {
            "n_mfcc": 13,
            "n_mels": 40,
            "hop_length": 160,
            "win_length": 400,
            "n_fft": 512
        }
    
    def _create_output_structure(self):
        """创建输出目录结构"""
        dirs = [
            self.output_dir / "audio",
            self.output_dir / "features" / "train",
            self.output_dir / "features" / "val",
            self.output_dir / "features" / "test",
            self.output_dir / "train",
            self.output_dir / "val",
            self.output_dir / "test",
            self.output_dir / "metadata"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def load_transcript(self, transcript_path: Path) -> Dict[str, str]:
        """加载转录文本"""
        transcripts = {}
        
        if not transcript_path.exists():
            print(f"⚠️  标注文件不存在：{transcript_path}")
            return transcripts
        
        # 检查是否为 HTML
        with open(transcript_path, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            if '<!DOCTYPE html>' in first_line or '<html' in first_line:
                print(f"⚠️  标注文件为 HTML 格式，请运行 fix_aishell_transcript.py 修复")
                return transcripts
        
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # AISHELL 格式：UTTERANCE_ID TEXT
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    utterance_id, text = parts
                    transcripts[utterance_id] = text
        
        print(f"✓ 加载标注：{len(transcripts)} 条")
        return transcripts
    
    def find_audio_files(self) -> List[Path]:
        """查找所有音频文件"""
        wav_files = []
        wav_dir = self.data_dir / "wav"
        
        if not wav_dir.exists():
            print(f"⚠️  wav 目录不存在：{wav_dir}")
            return wav_files
        
        for root, dirs, files in os.walk(wav_dir):
            for file in files:
                if file.endswith('.wav'):
                    wav_files.append(Path(root) / file)
        
        print(f"✓ 找到音频文件：{len(wav_files)} 个")
        return wav_files
    
    def validate_audio(self, wav_path: Path) -> Tuple[bool, Optional[float], Optional[str]]:
        """
        验证音频文件
        返回：(是否有效，时长，错误信息)
        """
        try:
            # 使用 librosa 加载并验证
            y, sr = librosa.load(str(wav_path), sr=self.sample_rate)
            duration = len(y) / self.sample_rate
            
            # 检查时长 (0.3s - 20s)
            if duration < 0.3:
                return False, duration, "时长过短 (<0.3s)"
            if duration > 20.0:
                return False, duration, "时长过长 (>20s)"
            
            return True, duration, None
            
        except Exception as e:
            return False, None, str(e)
    
    def normalize_audio(self, wav_path: Path, output_path: Path) -> bool:
        """标准化音频"""
        try:
            import soundfile as sf
            
            y, sr = librosa.load(str(wav_path), sr=self.sample_rate)
            
            # 音量归一化
            y = librosa.util.normalize(y)
            
            # 保存 (使用 soundfile 替代已废弃的 librosa.output.write_wav)
            sf.write(str(output_path), y, sr)
            return True
        except Exception as e:
            print(f"  ⚠️  标准化失败 {wav_path.name}: {e}")
            return False
    
    def extract_features(self, wav_path: Path) -> Dict[str, np.ndarray]:
        """提取音频特征"""
        try:
            y, sr = librosa.load(str(wav_path), sr=self.sample_rate)
            
            features = {}
            
            # MFCC (13 维)
            mfcc = librosa.feature.mfcc(
                y=y, sr=sr, 
                n_mfcc=self.feature_config["n_mfcc"],
                hop_length=self.feature_config["hop_length"],
                win_length=self.feature_config["win_length"],
                n_fft=self.feature_config["n_fft"]
            )
            features["mfcc"] = mfcc
            features["mfcc_delta"] = librosa.feature.delta(mfcc)
            features["mfcc_delta2"] = librosa.feature.delta(mfcc, order=2)
            
            # Log Mel Spectrogram (40 维)
            features["log_mel"] = librosa.feature.melspectrogram(
                y=y, sr=sr,
                n_mels=self.feature_config["n_mels"],
                hop_length=self.feature_config["hop_length"],
                win_length=self.feature_config["win_length"],
                n_fft=self.feature_config["n_fft"]
            )
            
            # Chroma
            features["chroma"] = librosa.feature.chroma_stft(
                y=y, sr=sr,
                hop_length=self.feature_config["hop_length"],
                n_fft=self.feature_config["n_fft"]
            )
            
            # Spectral Contrast
            features["spectral_contrast"] = librosa.feature.spectral_contrast(
                y=y, sr=sr,
                hop_length=self.feature_config["hop_length"]
            )
            
            # Tonnetz
            features["tonnetz"] = librosa.feature.tonnetz(
                y=y, sr=sr,
                hop_length=self.feature_config["hop_length"]
            )
            
            # ZCR
            features["zcr"] = librosa.feature.zero_crossing_rate(
                y=y,
                hop_length=self.feature_config["hop_length"]
            )
            
            # RMS
            features["rms"] = librosa.feature.rms(
                y=y,
                hop_length=self.feature_config["hop_length"]
            )
            
            # Spectral Centroid
            features["spectral_centroid"] = librosa.feature.spectral_centroid(
                y=y, sr=sr,
                hop_length=self.feature_config["hop_length"]
            )
            
            # Spectral Rolloff
            features["spectral_rolloff"] = librosa.feature.spectral_rolloff(
                y=y, sr=sr,
                hop_length=self.feature_config["hop_length"]
            )
            
            # 全局统计量
            features["stats"] = {}
            for key, value in features.items():
                if isinstance(value, np.ndarray):
                    features["stats"][key] = {
                        "mean": float(np.mean(value)),
                        "std": float(np.std(value)),
                        "min": float(np.min(value)),
                        "max": float(np.max(value))
                    }
            
            return features
            
        except Exception as e:
            print(f"  ⚠️  特征提取失败 {wav_path.name}: {e}")
            return {}
    
    def save_features(self, features: Dict, output_path: Path):
        """保存特征到 NPZ 文件"""
        np.savez_compressed(str(output_path), **features)
    
    def split_dataset(self, audio_ids: List[str], 
                      ratios: Tuple[float, float, float] = (0.8, 0.1, 0.1)) -> Dict[str, List[str]]:
        """分割数据集"""
        random.shuffle(audio_ids)
        n = len(audio_ids)
        
        train_end = int(n * ratios[0])
        val_end = int(n * (ratios[0] + ratios[1]))
        
        return {
            "train": audio_ids[:train_end],
            "val": audio_ids[train_end:val_end],
            "test": audio_ids[val_end:]
        }
    
    def write_manifest(self, split: str, audio_data: List[Dict]):
        """写入 manifest 文件"""
        manifest_path = self.output_dir / split / "manifest.jsonl"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            for item in audio_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    def process(self, max_samples: Optional[int] = None):
        """执行完整预处理流程"""
        print(f"\n{'='*60}")
        print(f"AISHELL 数据集预处理 v2")
        print(f"{'='*60}")
        print(f"📁 数据目录：{self.data_dir}")
        print(f"📁 输出目录：{self.output_dir}")
        print(f"📊 采样率：{self.sample_rate} Hz")
        print()
        
        # 加载标注
        transcript_path = self.data_dir / "transcript" / "aishell_transcript_v0.8.txt"
        transcripts = self.load_transcript(transcript_path)
        
        # 查找音频文件
        audio_files = self.find_audio_files()
        if max_samples:
            audio_files = audio_files[:max_samples]
            print(f"📝 限制处理样本数：{max_samples}")
        
        self.stats["total_samples"] = len(audio_files)
        
        # 处理每个音频文件
        audio_data = []
        valid_audio_ids = []
        
        print(f"\n🔄 处理音频文件...")
        for wav_path in tqdm(audio_files, desc="处理中"):
            audio_id = wav_path.stem
            
            # 验证
            is_valid, duration, error = self.validate_audio(wav_path)
            
            if not is_valid:
                self.stats["invalid_samples"] += 1
                continue
            
            self.stats["valid_samples"] += 1
            self.stats["total_duration"] += duration
            
            # 时长分布
            if duration < 2:
                self.stats["duration_distribution"]["short"] += 1
            elif duration < 5:
                self.stats["duration_distribution"]["medium"] += 1
            else:
                self.stats["duration_distribution"]["long"] += 1
            
            # 提取说话人 ID
            speaker_id = wav_path.parent.name
            self.stats["speakers"].add(speaker_id)
            
            # 标准化音频
            output_audio_path = self.output_dir / "audio" / f"{audio_id}_norm.wav"
            if not self.normalize_audio(wav_path, output_audio_path):
                continue
            
            # 提取特征
            features = self.extract_features(wav_path)
            if features:
                feature_path = self.output_dir / "features" / "train" / f"{audio_id}.npz"
                self.save_features(features, feature_path)
            
            # 获取标注
            transcript = transcripts.get(audio_id, "")
            
            # 记录音频数据
            audio_data.append({
                "audio_id": audio_id,
                "audio_path": str(output_audio_path),
                "duration": round(duration, 3),
                "transcript": transcript,
                "speaker_id": speaker_id,
                "language": "zh-CN"
            })
            
            valid_audio_ids.append(audio_id)
        
        # 分割数据集
        print(f"\n📊 分割数据集...")
        splits = self.split_dataset(valid_audio_ids)
        
        # 写入 manifest
        for split_name, split_ids in splits.items():
            split_data = [item for item in audio_data if item["audio_id"] in split_ids]
            self.write_manifest(split_name, split_data)
            
            # 移动特征文件到对应目录
            if split_name != "train":
                src_dir = self.output_dir / "features" / "train"
                dst_dir = self.output_dir / "features" / split_name
                for audio_id in split_ids:
                    src = src_dir / f"{audio_id}.npz"
                    dst = dst_dir / f"{audio_id}.npz"
                    if src.exists():
                        src.rename(dst)
            
            print(f"  ✓ {split_name}: {len(split_data)} 样本")
        
        # 保存统计信息
        report = {
            "dataset": "aishell",
            "start_time": datetime.now().isoformat(),
            "stats": {
                "total_samples": self.stats["total_samples"],
                "valid_samples": self.stats["valid_samples"],
                "invalid_samples": self.stats["invalid_samples"],
                "total_duration_hours": round(self.stats["total_duration"] / 3600, 2),
                "num_speakers": len(self.stats["speakers"]),
                "duration_distribution": self.stats["duration_distribution"]
            },
            "splits": {
                split_name: len(split_ids) 
                for split_name, split_ids in splits.items()
            },
            "config": {
                "sample_rate": self.sample_rate,
                "feature_config": self.feature_config
            }
        }
        
        report_path = self.output_dir / "processing_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print(f"✅ 预处理完成")
        print(f"{'='*60}")
        print(f"📊 有效样本：{self.stats['valid_samples']} / {self.stats['total_samples']}")
        print(f"📊 总时长：{report['stats']['total_duration_hours']} 小时")
        print(f"📊 说话人数：{len(self.stats['speakers'])}")
        print(f"📊 报告：{report_path}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description='AISHELL 数据集预处理 v2')
    parser.add_argument('--data_dir', type=str, 
                        default='/Users/moondy/.openclaw/workspace-hulk/data_aishell',
                        help='AISHELL 数据目录')
    parser.add_argument('--output_dir', type=str,
                        default='/Users/moondy/.openclaw/workspace-hulk/data/processed_aishell_v2',
                        help='输出目录')
    parser.add_argument('--sample_rate', type=int, default=16000,
                        help='采样率')
    parser.add_argument('--max_samples', type=int, default=None,
                        help='最大处理样本数 (用于测试)')
    args = parser.parse_args()
    
    preprocessor = AISHELLPreprocessor(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        sample_rate=args.sample_rate
    )
    
    preprocessor.process(max_samples=args.max_samples)


if __name__ == '__main__':
    main()
