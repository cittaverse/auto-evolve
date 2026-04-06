#!/usr/bin/env python3
"""
语音数据增强工具
支持：噪声注入、速度扰动、音高变换、混响、增益变化等

Usage:
    python data_augmentation.py --input_dir /path/to/wav --output_dir /path/to/augmented --methods noise,speed,pitch

作者：Hulk 🟢
日期：2026-04-02
"""

import os
import argparse
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import librosa
import soundfile as sf
from tqdm import tqdm
from dataclasses import dataclass
import random


@dataclass
class AugmentationConfig:
    """数据增强配置"""
    # 噪声注入
    add_noise: bool = True
    noise_snr_range: Tuple[float, float] = (10, 30)  # dB
    
    # 速度扰动
    speed_perturb: bool = True
    speed_factors: List[float] = None  # [0.9, 1.0, 1.1]
    
    # 音高变换
    pitch_shift: bool = True
    pitch_semitones_range: Tuple[int, int] = (-2, 2)
    
    # 混响
    add_reverb: bool = False
    reverb_level: float = 0.3
    
    # 增益变化
    gain_perturb: bool = True
    gain_range_db: Tuple[float, float] = (-5, 5)
    
    # 时间拉伸
    time_stretch: bool = False
    stretch_factors: List[float] = None  # [0.8, 1.0, 1.2]
    
    def __post_init__(self):
        if self.speed_factors is None:
            self.speed_factors = [0.9, 1.0, 1.1]
        if self.stretch_factors is None:
            self.stretch_factors = [0.8, 1.0, 1.2]


class AudioAugmenter:
    """音频数据增强器"""
    
    def __init__(self, config: AugmentationConfig, 
                 noise_dir: Optional[str] = None):
        self.config = config
        self.noise_dir = Path(noise_dir) if noise_dir else None
        self.noise_cache = {}
    
    def load_noise(self, noise_path: Path) -> np.ndarray:
        """加载噪声文件并缓存"""
        if str(noise_path) not in self.noise_cache:
            noise, sr = librosa.load(str(noise_path), sr=None)
            self.noise_cache[str(noise_path)] = noise
        return self.noise_cache[str(noise_path)]
    
    def add_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """添加背景噪声"""
        if self.noise_dir is None:
            # 使用高斯噪声
            noise = np.random.randn(len(audio))
            noise = noise / np.max(np.abs(noise)) * np.max(np.abs(audio)) * 0.1
        else:
            # 从噪声库中随机选择
            noise_files = list(self.noise_dir.glob("*.wav")) + \
                         list(self.noise_dir.glob("*.mp3"))
            if not noise_files:
                return audio
            
            noise_path = random.choice(noise_files)
            noise = self.load_noise(noise_path)
            
            # 调整噪声长度
            if len(noise) < len(audio):
                noise = np.tile(noise, int(np.ceil(len(audio) / len(noise))))
            noise = noise[:len(audio)]
            
            # 按 SNR 调整噪声强度
            snr = random.uniform(*self.config.noise_snr_range)
            audio_power = np.sum(audio ** 2) / len(audio)
            noise_power = np.sum(noise ** 2) / len(noise)
            target_noise_power = audio_power / (10 ** (snr / 10))
            noise = noise * np.sqrt(target_noise_power / (noise_power + 1e-8))
        
        return audio + noise
    
    def speed_perturbation(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """速度扰动"""
        factor = random.choice(self.config.speed_factors)
        if factor == 1.0:
            return audio
        
        audio_stretched = librosa.effects.time_stretch(audio, rate=factor)
        
        # 调整长度回原始
        if len(audio_stretched) > len(audio):
            audio_stretched = audio_stretched[:len(audio)]
        else:
            audio_stretched = np.pad(audio_stretched, (0, len(audio) - len(audio_stretched)))
        
        return audio_stretched
    
    def pitch_shifting(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """音高变换"""
        semitones = random.uniform(*self.config.pitch_semitones_range)
        if semitones == 0:
            return audio
        
        return librosa.effects.pitch_shift(audio, sr=sr, n_steps=semitones)
    
    def add_reverb(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """添加混响效果（简化版）"""
        # 简单的混响模拟：添加衰减的回声
        delay_samples = int(0.05 * sr)  # 50ms 延迟
        decay = self.config.reverb_level
        
        reverb = np.zeros_like(audio)
        reverb[delay_samples:] = audio[:-delay_samples] * decay
        
        return audio + reverb
    
    def gain_perturbation(self, audio: np.ndarray) -> np.ndarray:
        """增益变化"""
        gain_db = random.uniform(*self.config.gain_range_db)
        gain_linear = 10 ** (gain_db / 20)
        return audio * gain_linear
    
    def time_stretching(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """时间拉伸"""
        factor = random.choice(self.config.stretch_factors)
        if factor == 1.0:
            return audio
        
        audio_stretched = librosa.effects.time_stretch(audio, rate=factor)
        
        # 调整长度
        if len(audio_stretched) > len(audio):
            audio_stretched = audio_stretched[:len(audio)]
        else:
            audio_stretched = np.pad(audio_stretched, (0, len(audio) - len(audio_stretched)))
        
        return audio_stretched
    
    def augment(self, audio: np.ndarray, sr: int, 
                methods: Optional[List[str]] = None) -> np.ndarray:
        """
        应用增强
        
        Args:
            audio: 原始音频
            sr: 采样率
            methods: 要应用的方法列表，None 则使用配置中的所有方法
        
        Returns:
            增强后的音频
        """
        if methods is None:
            methods = []
            if self.config.add_noise:
                methods.append("noise")
            if self.config.speed_perturb:
                methods.append("speed")
            if self.config.pitch_shift:
                methods.append("pitch")
            if self.config.add_reverb:
                methods.append("reverb")
            if self.config.gain_perturb:
                methods.append("gain")
            if self.config.time_stretch:
                methods.append("stretch")
        
        augmented = audio.copy()
        
        for method in methods:
            if method == "noise" and self.config.add_noise:
                augmented = self.add_noise(augmented, sr)
            elif method == "speed" and self.config.speed_perturb:
                augmented = self.speed_perturbation(augmented, sr)
            elif method == "pitch" and self.config.pitch_shift:
                augmented = self.pitch_shifting(augmented, sr)
            elif method == "reverb" and self.config.add_reverb:
                augmented = self.add_reverb(augmented, sr)
            elif method == "gain" and self.config.gain_perturb:
                augmented = self.gain_perturbation(augmented)
            elif method == "stretch" and self.config.time_stretch:
                augmented = self.time_stretching(augmented, sr)
        
        # 限制幅度防止削波
        augmented = np.clip(augmented, -1.0, 1.0)
        
        return augmented
    
    def augment_file(self, input_path: Path, output_path: Path,
                    methods: Optional[List[str]] = None,
                    n_copies: int = 1):
        """
        增强单个文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            methods: 增强方法
            n_copies: 生成副本数量
        """
        audio, sr = librosa.load(str(input_path), sr=None)
        
        for i in range(n_copies):
            augmented = self.augment(audio, sr, methods)
            
            if n_copies > 1:
                stem = output_path.stem
                suffix = output_path.suffix
                output_file = output_path.parent / f"{stem}_aug{i+1}{suffix}"
            else:
                output_file = output_path
            
            sf.write(str(output_file), augmented, sr)
        
        return n_copies


def main():
    parser = argparse.ArgumentParser(description="语音数据增强")
    parser.add_argument("--input_dir", type=str, required=True,
                       help="输入音频目录")
    parser.add_argument("--output_dir", type=str, required=True,
                       help="输出目录")
    parser.add_argument("--methods", type=str, default="noise,gain",
                       help="增强方法，逗号分隔 (noise,speed,pitch,reverb,gain,stretch)")
    parser.add_argument("--noise_dir", type=str, default=None,
                       help="噪声文件目录")
    parser.add_argument("--n_copies", type=int, default=1,
                       help="每个样本生成的增强副本数")
    parser.add_argument("--config", type=str, default=None,
                       help="配置文件路径 (JSON)")
    
    args = parser.parse_args()
    
    # 解析方法
    methods = [m.strip() for m in args.methods.split(",")] if args.methods else []
    
    # 加载配置
    if args.config:
        import json
        with open(args.config, 'r') as f:
            config_dict = json.load(f)
        config = AugmentationConfig(**config_dict)
    else:
        config = AugmentationConfig()
    
    print("=" * 60)
    print("语音数据增强")
    print("=" * 60)
    print(f"输入目录：{args.input_dir}")
    print(f"输出目录：{args.output_dir}")
    print(f"增强方法：{methods}")
    print(f"副本数量：{args.n_copies}")
    print("=" * 60)
    
    # 创建增强器
    augmenter = AudioAugmenter(config, noise_dir=args.noise_dir)
    
    # 收集音频文件
    input_dir = Path(args.input_dir)
    audio_files = list(input_dir.glob("*.wav")) + \
                  list(input_dir.glob("*.flac"))
    
    print(f"\n发现 {len(audio_files)} 个音频文件")
    
    # 创建输出目录
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 批量处理
    total_augmented = 0
    for audio_path in tqdm(audio_files, desc="Augmenting"):
        output_path = output_dir / audio_path.name
        n = augmenter.augment_file(
            audio_path, output_path, 
            methods=methods,
            n_copies=args.n_copies
        )
        total_augmented += n
    
    print("\n" + "=" * 60)
    print(f"数据增强完成!")
    print(f"原始文件：{len(audio_files)}")
    print(f"增强后文件：{total_augmented}")
    print("=" * 60)


if __name__ == "__main__":
    main()
