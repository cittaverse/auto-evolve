#!/usr/bin/env python3
"""
特征提取工具
============
从音频文件中提取多种声学特征，支持批量处理和可视化

创建者：Hulk 🟢
创建日期：2026-03-25
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import numpy as np

try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("错误：需要安装 librosa 和 matplotlib")
    print("pip install librosa matplotlib")
    exit(1)


class FeatureExtractor:
    """音频特征提取器"""
    
    def __init__(self, sample_rate: int = 16000):
        self.sr = sample_rate
    
    def extract_all(
        self,
        audio_path: str,
        n_mfcc: int = 13,
        n_mels: int = 40
    ) -> Dict[str, np.ndarray]:
        """提取所有特征"""
        y, sr = librosa.load(audio_path, sr=self.sr)
        
        features = {
            'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc).T,
            'mel_spec': librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels).T,
            'contrast': librosa.feature.spectral_contrast(y=y, sr=sr).T,
            'zcr': librosa.feature.zero_crossing_rate(y).T,
            'chroma': librosa.feature.chroma_stft(y=y, sr=sr).T,
            'tonnetz': librosa.feature.tonnetz(y=y, sr=sr).T,
            'spectral_centroid': librosa.feature.spectral_centroid(y=y, sr=sr).T,
            'spectral_rolloff': librosa.feature.spectral_rolloff(y=y, sr=sr).T,
        }
        
        return features
    
    def plot_features(
        self,
        audio_path: str,
        output_dir: str,
        features: Optional[Dict] = None
    ):
        """绘制特征可视化"""
        if features is None:
            features = self.extract_all(audio_path)
        
        audio_name = Path(audio_path).stem
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 波形图
        plt.figure(figsize=(12, 4))
        y, sr = librosa.load(audio_path, sr=self.sr)
        librosa.display.waveshow(y, sr=sr)
        plt.title(f'Waveform - {audio_name}')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.tight_layout()
        plt.savefig(output_dir / f'{audio_name}_waveform.png', dpi=150)
        plt.close()
        
        # 2. MFCC
        plt.figure(figsize=(12, 4))
        librosa.display.specshow(
            features['mfcc'].T,
            sr=sr,
            x_axis='time'
        )
        plt.title(f'MFCC - {audio_name}')
        plt.colorbar(format='%+2.0f dB')
        plt.tight_layout()
        plt.savefig(output_dir / f'{audio_name}_mfcc.png', dpi=150)
        plt.close()
        
        # 3. Mel 频谱图
        plt.figure(figsize=(12, 4))
        librosa.display.specshow(
            features['mel_spec'].T,
            sr=sr,
            x_axis='time',
            y_axis='mel'
        )
        plt.title(f'Mel Spectrogram - {audio_name}')
        plt.colorbar(format='%+2.0f dB')
        plt.tight_layout()
        plt.savefig(output_dir / f'{audio_name}_mel.png', dpi=150)
        plt.close()
        
        # 4. 频谱对比度
        plt.figure(figsize=(12, 4))
        librosa.display.specshow(
            features['contrast'].T,
            sr=sr,
            x_axis='time'
        )
        plt.title(f'Spectral Contrast - {audio_name}')
        plt.colorbar()
        plt.tight_layout()
        plt.savefig(output_dir / f'{audio_name}_contrast.png', dpi=150)
        plt.close()
        
        print(f"可视化已保存至：{output_dir}")
    
    def save_features(
        self,
        features: Dict[str, np.ndarray],
        output_path: str,
        format: str = 'npz'
    ):
        """保存特征到文件"""
        output_path = Path(output_path)
        
        if format == 'npz':
            np.savez_compressed(output_path, **features)
        elif format == 'npy':
            # 保存为单个数组（拼接所有特征）
            combined = np.concatenate([
                features['mfcc'].flatten(),
                features['mel_spec'].flatten()
            ])
            np.save(output_path, combined)
        else:
            raise ValueError(f"不支持的格式：{format}")
        
        print(f"特征已保存：{output_path}")
    
    def batch_extract(
        self,
        audio_files: List[str],
        output_dir: str,
        plot: bool = False
    ) -> Dict[str, str]:
        """批量提取特征"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for audio_path in audio_files:
            try:
                audio_name = Path(audio_path).stem
                features = self.extract_all(audio_path)
                
                # 保存特征
                feature_path = output_dir / f'{audio_name}.npz'
                self.save_features(features, feature_path)
                
                # 可视化
                if plot:
                    self.plot_features(audio_path, output_dir, features)
                
                results[audio_name] = str(feature_path)
                print(f"✓ {audio_name}")
                
            except Exception as e:
                print(f"✗ {audio_path}: {e}")
                results[audio_name] = f"ERROR: {e}"
        
        return results


def main():
    parser = argparse.ArgumentParser(description='音频特征提取工具')
    
    parser.add_argument('audio', nargs='?', help='音频文件路径')
    parser.add_argument('--dir', help='音频目录（批量处理）')
    parser.add_argument('--output', default='./features', help='输出目录')
    parser.add_argument('--plot', action='store_true', help='生成可视化图')
    parser.add_argument('--sample-rate', type=int, default=16000, help='采样率')
    parser.add_argument('--list', action='store_true', help='列出支持的特征类型')
    
    args = parser.parse_args()
    
    if args.list:
        print("支持的特征类型:")
        print("  - mfcc (13 维)")
        print("  - mel_spec (40 维 Mel 频谱)")
        print("  - contrast (频谱对比度)")
        print("  - zcr (过零率)")
        print("  - chroma (色度特征)")
        print("  - tonnetz (调性网络)")
        print("  - spectral_centroid (频谱质心)")
        print("  - spectral_rolloff (频谱滚降)")
        return
    
    extractor = FeatureExtractor(sample_rate=args.sample_rate)
    
    if args.audio:
        # 单文件处理
        print(f"处理：{args.audio}")
        features = extractor.extract_all(args.audio)
        
        output_path = Path(args.output) / f"{Path(args.audio).stem}.npz"
        extractor.save_features(features, output_path)
        
        if args.plot:
            extractor.plot_features(args.audio, args.output, features)
        
        # 打印特征统计
        print("\n特征统计:")
        for name, feat in features.items():
            print(f"  {name}: shape={feat.shape}, mean={feat.mean():.3f}, std={feat.std():.3f}")
    
    elif args.dir:
        # 批量处理
        audio_dir = Path(args.dir)
        audio_files = list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.mp3"))
        
        print(f"批量处理 {len(audio_files)} 个文件...")
        results = extractor.batch_extract(
            [str(f) for f in audio_files],
            args.output,
            plot=args.plot
        )
        
        # 保存结果清单
        manifest_path = Path(args.output) / 'manifest.json'
        with open(manifest_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n清单已保存：{manifest_path}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
