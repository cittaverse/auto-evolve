#!/usr/bin/env python3
"""
高级音频特征提取工具
支持多种特征类型和配置选项

Usage:
    python feature_extractor.py --input_dir /path/to/wav --output_dir /path/to/features --config config.json

作者：Hulk 🟢
日期：2026-04-02
"""

import os
import json
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any
import librosa
import librosa.feature
from tqdm import tqdm
from dataclasses import dataclass, asdict
import soundfile as sf


@dataclass
class FeatureConfig:
    """特征提取配置"""
    # 基础参数
    sample_rate: int = 16000
    hop_length: int = 160
    win_length: int = 400
    n_fft: int = 512
    
    # MFCC 参数
    n_mfcc: int = 13
    n_mels: int = 40
    
    # 是否提取 delta 特征
    extract_delta: bool = True
    
    # 是否提取统计特征
    extract_stats: bool = True
    
    # 特征类型
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = [
                "mfcc", "log_mel", "chroma", 
                "spectral_contrast", "tonnetz", "zcr", "rms"
            ]


class AdvancedFeatureExtractor:
    """高级音频特征提取器"""
    
    def __init__(self, config: FeatureConfig):
        self.config = config
        
    def extract(self, audio_path: Path) -> Dict[str, np.ndarray]:
        """
        提取音频特征
        
        Args:
            audio_path: 音频文件路径
        
        Returns:
            特征字典
        """
        # 加载音频
        y, sr = librosa.load(str(audio_path), sr=self.config.sample_rate)
        
        features = {}
        
        # MFCC
        if "mfcc" in self.config.features:
            mfcc = librosa.feature.mfcc(
                y=y, sr=sr, 
                n_mfcc=self.config.n_mfcc,
                hop_length=self.config.hop_length,
                win_length=self.config.win_length,
                n_fft=self.config.n_fft
            )
            features["mfcc"] = mfcc
            
            if self.config.extract_delta:
                features["mfcc_delta"] = librosa.feature.delta(mfcc)
                features["mfcc_delta2"] = librosa.feature.delta(mfcc, order=2)
        
        # Log Mel Spectrogram
        if "log_mel" in self.config.features:
            features["log_mel"] = librosa.feature.melspectrogram(
                y=y, sr=sr,
                n_mels=self.config.n_mels,
                hop_length=self.config.hop_length,
                win_length=self.config.win_length,
                n_fft=self.config.n_fft
            )
        
        # Chroma
        if "chroma" in self.config.features:
            features["chroma"] = librosa.feature.chroma_stft(
                y=y, sr=sr,
                hop_length=self.config.hop_length
            )
        
        # Spectral Contrast
        if "spectral_contrast" in self.config.features:
            features["spectral_contrast"] = librosa.feature.spectral_contrast(
                y=y, sr=sr,
                hop_length=self.config.hop_length
            )
        
        # Tonnetz
        if "tonnetz" in self.config.features:
            features["tonnetz"] = librosa.feature.tonnetz(
                y=y, sr=sr
            )
        
        # Zero Crossing Rate
        if "zcr" in self.config.features:
            features["zcr"] = librosa.feature.zero_crossing_rate(
                y, hop_length=self.config.hop_length
            )
        
        # RMS Energy
        if "rms" in self.config.features:
            features["rms"] = librosa.feature.rms(
                y, hop_length=self.config.hop_length
            )
        
        # Spectral Centroid
        if "spectral_centroid" in self.config.features:
            features["spectral_centroid"] = librosa.feature.spectral_centroid(
                y=y, sr=sr, hop_length=self.config.hop_length
            )
        
        # Spectral Rolloff
        if "spectral_rolloff" in self.config.features:
            features["spectral_rolloff"] = librosa.feature.spectral_rolloff(
                y=y, sr=sr, hop_length=self.config.hop_length
            )
        
        # 添加统计特征
        if self.config.extract_stats:
            stats_features = {}
            for name, feat in features.items():
                stats_features[f"{name}_mean"] = np.mean(feat, axis=1, keepdims=True)
                stats_features[f"{name}_std"] = np.std(feat, axis=1, keepdims=True)
                stats_features[f"{name}_min"] = np.min(feat, axis=1, keepdims=True)
                stats_features[f"{name}_max"] = np.max(feat, axis=1, keepdims=True)
            
            features.update(stats_features)
        
        return features
    
    def extract_batch(self, audio_paths: List[Path], 
                     output_dir: Path,
                     verbose: bool = True) -> Dict[str, str]:
        """
        批量提取特征
        
        Args:
            audio_paths: 音频文件路径列表
            output_dir: 输出目录
            verbose: 是否显示进度条
        
        Returns:
            文件路径映射字典 {utterance_id: feature_path}
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        path_map = {}
        
        iterator = tqdm(audio_paths, desc="Extracting features") if verbose else audio_paths
        
        for audio_path in iterator:
            utterance_id = audio_path.stem
            
            try:
                features = self.extract(audio_path)
                output_path = output_dir / f"{utterance_id}.npz"
                np.savez_compressed(output_path, **features)
                path_map[utterance_id] = str(output_path)
            except Exception as e:
                print(f"错误：处理 {audio_path} 时失败 - {e}")
        
        return path_map


def compute_global_statistics(feature_dir: Path) -> Dict[str, Dict[str, np.ndarray]]:
    """
    计算全局特征统计量（用于标准化）
    
    Args:
        feature_dir: 特征文件目录
    
    Returns:
        全局均值和方差字典
    """
    feature_files = list(feature_dir.glob("*.npz"))
    
    if not feature_files:
        return {}
    
    # 累积统计
    sum_dict = {}
    sum_sq_dict = {}
    count_dict = {}
    n_files = 0
    
    for feat_file in tqdm(feature_files, desc="Computing global stats"):
        data = np.load(feat_file)
        n_files += 1
        
        for key, value in data.items():
            if value.ndim == 1:
                value = value.reshape(-1, 1)
            
            if key not in sum_dict:
                sum_dict[key] = np.zeros((value.shape[0], 1))
                sum_sq_dict[key] = np.zeros((value.shape[0], 1))
                count_dict[key] = 0
            
            # 按帧累积
            sum_dict[key] += np.sum(value, axis=1, keepdims=True)
            sum_sq_dict[key] += np.sum(value ** 2, axis=1, keepdims=True)
            count_dict[key] += value.shape[1]
    
    # 计算均值和方差
    global_stats = {}
    for key in sum_dict:
        mean = sum_dict[key] / count_dict[key]
        var = (sum_sq_dict[key] / count_dict[key]) - (mean ** 2)
        std = np.sqrt(np.maximum(var, 1e-8))  # 避免除零
        
        global_stats[key] = {
            "mean": mean.flatten(),
            "std": std.flatten()
        }
    
    return global_stats


def normalize_features(feature_path: Path, 
                      global_stats: Dict,
                      output_path: Optional[Path] = None) -> np.ndarray:
    """
    使用全局统计量标准化特征
    
    Args:
        feature_path: 特征文件路径
        global_stats: 全局统计量
        output_path: 输出路径（可选）
    
    Returns:
        标准化后的特征
    """
    data = np.load(feature_path)
    normalized = {}
    
    for key, value in data.items():
        if key in global_stats:
            mean = global_stats[key]["mean"]
            std = global_stats[key]["std"]
            
            # 确保维度匹配
            if value.ndim == 1:
                value = value.reshape(-1, 1)
            if len(mean) == value.shape[0]:
                normalized[key] = (value - mean.reshape(-1, 1)) / std.reshape(-1, 1)
            else:
                normalized[key] = value
        else:
            normalized[key] = value
    
    if output_path:
        np.savez_compressed(output_path, **normalized)
    
    return normalized


def main():
    parser = argparse.ArgumentParser(description="高级音频特征提取")
    parser.add_argument("--input_dir", type=str, required=True,
                       help="输入音频目录")
    parser.add_argument("--output_dir", type=str, required=True,
                       help="输出特征目录")
    parser.add_argument("--config", type=str, default=None,
                       help="配置文件路径 (JSON)")
    parser.add_argument("--sample_rate", type=int, default=16000,
                       help="采样率")
    parser.add_argument("--compute_global_stats", action="store_true",
                       help="计算全局统计量")
    parser.add_argument("--normalize", action="store_true",
                       help="标准化特征")
    
    args = parser.parse_args()
    
    # 加载配置
    if args.config:
        with open(args.config, 'r') as f:
            config_dict = json.load(f)
        config = FeatureConfig(**config_dict)
    else:
        config = FeatureConfig(sample_rate=args.sample_rate)
    
    print("=" * 60)
    print("高级音频特征提取")
    print("=" * 60)
    print(f"输入目录：{args.input_dir}")
    print(f"输出目录：{args.output_dir}")
    print(f"配置：{json.dumps(asdict(config), indent=2)}")
    print("=" * 60)
    
    # 创建提取器
    extractor = AdvancedFeatureExtractor(config)
    
    # 收集音频文件
    input_dir = Path(args.input_dir)
    audio_files = list(input_dir.glob("*.wav")) + \
                  list(input_dir.glob("*.flac")) + \
                  list(input_dir.glob("*.mp3"))
    
    print(f"\n发现 {len(audio_files)} 个音频文件")
    
    # 批量提取
    output_dir = Path(args.output_dir)
    path_map = extractor.extract_batch(audio_files, output_dir / "features")
    
    print(f"\n✓ 特征提取完成：{len(path_map)} 个文件")
    
    # 计算全局统计量
    if args.compute_global_stats:
        print("\n计算全局统计量...")
        global_stats = compute_global_statistics(output_dir / "features")
        
        # 保存统计量
        stats_path = output_dir / "global_stats.npz"
        np.savez(stats_path, **{
            k: np.vstack([v["mean"], v["std"]]) 
            for k, v in global_stats.items()
        })
        print(f"✓ 全局统计量已保存：{stats_path}")
    
    print("\n" + "=" * 60)
    print("特征提取完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
