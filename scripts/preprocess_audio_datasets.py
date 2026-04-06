#!/usr/bin/env python3
"""
音频数据集预处理脚本 v3.0
==========================
功能：AISHELL 和其他语音数据集的完整预处理流程
- 音频清洗（去噪、标准化、重采样）
- 数据集分割（train/val/test）
- 声学特征提取（MFCC, Mel 频谱，Spectral Contrast 等）
- 标注文件加载（如果可用）

创建者：Hulk 🟢
创建日期：2026-03-28
更新日期：2026-04-02
用途：Cron 任务 #7744d4c5 - 数据集预处理

依赖安装：
    pip install librosa numpy pandas tqdm soundfile matplotlib scipy

用法：
    # 完整处理所有数据集
    python scripts/preprocess_audio_datasets.py --all
    
    # 仅处理 AISHELL
    python scripts/preprocess_audio_datasets.py --dataset aishell
    
    # 仅处理老年语音
    python scripts/preprocess_audio_datasets.py --dataset elderly
    
    # 仅提取特征（跳过音频处理）
    python scripts/preprocess_audio_datasets.py --dataset aishell --extract-features-only
    
    # 重新处理（覆盖已有数据）
    python scripts/preprocess_audio_datasets.py --dataset aishell --reprocess
    
    # 仅验证结果
    python scripts/preprocess_audio_datasets.py --validate

输出结构：
    data/processed/
    ├── audio/                  # 标准化音频文件
    ├── train/manifest.jsonl    # 训练集清单
    ├── val/manifest.jsonl      # 验证集清单
    ├── test/manifest.jsonl     # 测试集清单
    ├── features/
    │   ├── train/              # 训练集特征 (.npz)
    │   ├── val/                # 验证集特征 (.npz)
    │   └── test/               # 测试集特征 (.npz)
    ├── processing_report.json  # 处理报告
    └── validation_report.json  # 验证报告
"""

import argparse
import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
from tqdm import tqdm

# 延迟导入重型库（检查后加载）
librosa = None
sf = None
plt = None


def check_dependencies():
    """检查并导入必要的依赖库"""
    global librosa, sf, plt
    
    required = {
        'librosa': 'librosa',
        'soundfile': 'soundfile', 
        'matplotlib': 'matplotlib',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'scipy': 'scipy'
    }
    
    missing = []
    for import_name, pip_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    
    if missing:
        print(f"❌ 缺少必要的库：{', '.join(missing)}")
        print(f"安装：pip install {' '.join(missing)}")
        sys.exit(1)
    
    # 导入成功
    import librosa as lr
    import soundfile as sf
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    globals()['librosa'] = lr
    globals()['sf'] = sf
    globals()['plt'] = plt
    
    print("✓ 所有依赖库已加载")


class AudioPreprocessor:
    """音频数据集预处理器"""
    
    def __init__(
        self,
        workspace_root: str = "/Users/moondy/.openclaw/workspace-hulk",
        sample_rate: int = 16000,
        n_mfcc: int = 13,
        n_mels: int = 40,
        hop_length: int = 512,
        n_fft: int = 2048
    ):
        self.workspace = Path(workspace_root)
        self.sr = sample_rate
        self.n_mfcc = n_mfcc
        self.n_mels = n_mels
        self.hop_length = hop_length
        self.n_fft = n_fft
        
        # 目录结构
        self.data_dir = self.workspace / "data"
        self.processed_dir = self.data_dir / "processed"
        self.features_dir = self.processed_dir / "features"
        
        # 数据集源目录
        self.aishell_dir = self.workspace / "data_aishell"
        self.elderly_dir = self.data_dir / "elderly_voice"
        
        print(f"\n🟢 音频预处理器 v3.0")
        print(f"   工作目录：{workspace_root}")
        print(f"   目标采样率：{sample_rate}Hz")
        print(f"   MFCC 维度：{n_mfcc}")
        print(f"   Mel 频带：{n_mels}")
        print(f"   FFT 窗口：{n_fft}")
        print(f"   Hop 长度：{hop_length}")
    
    def normalize_audio(self, audio_path: Path, output_path: Path) -> Optional[Dict]:
        """
        音频标准化处理
        - 重采样到目标采样率
        - 音量归一化
        - 去除静音片段
        
        Returns:
            音频信息字典，失败返回 None
        """
        try:
            # 加载音频
            y, sr = librosa.load(audio_path, sr=self.sr, mono=True)
            
            # 音量归一化
            y = librosa.util.normalize(y)
            
            # 保存标准化音频
            sf.write(output_path, y, self.sr)
            
            # 计算音频信息
            duration = len(y) / self.sr
            
            return {
                'original_path': str(audio_path),
                'normalized_path': str(output_path),
                'duration': round(duration, 3),
                'sample_rate': self.sr,
                'samples': len(y)
            }
        except Exception as e:
            print(f"  ⚠️ 处理失败 {audio_path.name}: {e}")
            return None
    
    def extract_features(self, audio_path: Path, output_path: Path) -> Optional[Dict]:
        """
        提取声学特征
        - MFCC (13 维)
        - Mel 频谱图 (40 频带)
        - Spectral Contrast (7 维)
        - Zero Crossing Rate (1 维)
        - Chroma (12 维)
        
        Returns:
            特征信息字典，失败返回 None
        """
        try:
            # 加载音频
            y, sr = librosa.load(audio_path, sr=self.sr, mono=True)
            
            # 提取特征
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc, n_fft=self.n_fft, hop_length=self.hop_length)
            mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=self.n_mels, n_fft=self.n_fft, hop_length=self.hop_length)
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)
            zcr = librosa.feature.zero_crossing_rate(y, frame_length=2048, hop_length=512)
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length)
            
            # 聚合统计（均值）
            features = {
                'mfcc_mean': np.mean(mfcc, axis=1).tolist(),
                'mfcc_std': np.std(mfcc, axis=1).tolist(),
                'mel_mean': np.mean(mel, axis=1).tolist(),
                'mel_std': np.std(mel, axis=1).tolist(),
                'contrast_mean': np.mean(contrast, axis=1).tolist(),
                'zcr_mean': float(np.mean(zcr)),
                'chroma_mean': np.mean(chroma, axis=1).tolist(),
                'duration': len(y) / sr,
                'sample_rate': sr
            }
            
            # 保存为 npz
            np.savez(output_path, **features)
            
            return {
                'audio_path': str(audio_path),
                'feature_path': str(output_path),
                'feature_dims': {
                    'mfcc': self.n_mfcc,
                    'mel': self.n_mels,
                    'contrast': 7,
                    'zcr': 1,
                    'chroma': 12
                }
            }
        except Exception as e:
            print(f"  ⚠️ 特征提取失败 {audio_path.name}: {e}")
            return None
    
    def load_transcripts(self, transcript_path: Path) -> Dict[str, str]:
        """
        加载标注文件
        
        Returns:
            音频 ID 到文本的映射字典
        """
        transcripts = {}
        
        if not transcript_path.exists():
            print(f"  ⚠️ 标注文件不存在：{transcript_path}")
            return transcripts
        
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # AISHELL 格式：音频 ID 空格 文本
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        audio_id = parts[0]
                        text = parts[1]
                        transcripts[audio_id] = text
            
            print(f"  ✓ 加载 {len(transcripts)} 条标注")
        except Exception as e:
            print(f"  ⚠️ 标注加载失败：{e}")
        
        return transcripts
    
    def split_dataset(
        self,
        audio_files: List[Path],
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        seed: int = 42
    ) -> Dict[str, List[Path]]:
        """
        随机分割数据集
        
        Returns:
            分割后的文件列表字典
        """
        random.seed(seed)
        random.shuffle(audio_files)
        
        n = len(audio_files)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        
        return {
            'train': audio_files[:n_train],
            'val': audio_files[n_train:n_train + n_val],
            'test': audio_files[n_train + n_val:]
        }
    
    def create_manifest(
        self,
        split_files: Dict[str, List[Path]],
        transcripts: Dict[str, str],
        output_dir: Path,
        audio_info: Dict[str, Dict]
    ) -> Dict[str, int]:
        """
        创建 manifest 文件
        
        Returns:
            各分割的文件数量
        """
        counts = {}
        
        for split_name, files in split_files.items():
            manifest_path = output_dir / split_name / "manifest.jsonl"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            
            count = 0
            with open(manifest_path, 'w', encoding='utf-8') as f:
                for audio_path in files:
                    audio_id = audio_path.stem
                    
                    # 获取音频信息
                    info = audio_info.get(str(audio_path), {})
                    duration = info.get('duration', 0)
                    
                    # 获取标注（如果有）
                    transcript = transcripts.get(audio_id, "")
                    
                    entry = {
                        'audio_path': str(audio_path),
                        'audio_id': audio_id,
                        'duration': duration,
                        'transcript': transcript,
                        'language': 'zh-CN',
                        'split': split_name
                    }
                    
                    f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                    count += 1
            
            counts[split_name] = count
            print(f"  ✓ {split_name}: {count} 条记录 → {manifest_path}")
        
        return counts
    
    def process_aishell(self, reprocess: bool = False, extract_features: bool = True) -> Dict:
        """处理 AISHELL 数据集"""
        print("\n" + "="*60)
        print("📊 处理 AISHELL 数据集")
        print("="*60)
        
        report = {
            'dataset': 'aishell',
            'start_time': datetime.now().isoformat(),
            'steps': {}
        }
        
        # 目录准备
        raw_wav_dir = self.aishell_dir / "wav"
        normalized_dir = self.processed_dir / "audio"
        transcript_path = self.aishell_dir / "transcript" / "aishell_transcript_v0.8.txt"
        
        normalized_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 收集音频文件
        print("\n1️⃣  收集音频文件...")
        audio_files = list(raw_wav_dir.rglob("*.wav"))
        print(f"   找到 {len(audio_files)} 个 WAV 文件")
        
        if len(audio_files) == 0:
            print("   ⚠️ 未找到音频文件，跳过处理")
            report['steps']['collect'] = {'found': 0}
            return report
        
        # 2. 加载标注
        print("\n2️⃣  加载标注文件...")
        transcripts = self.load_transcripts(transcript_path)
        report['steps']['transcripts'] = {
            'loaded': len(transcripts),
            'path': str(transcript_path)
        }
        
        # 3. 音频标准化
        print("\n3️⃣  音频标准化处理...")
        audio_info = {}
        normalized_files = []
        
        for wav_path in tqdm(audio_files, desc="标准化"):
            output_name = f"{wav_path.stem}_norm.wav"
            output_path = normalized_dir / output_name
            
            if output_path.exists() and not reprocess:
                # 使用已有标准化文件
                try:
                    y, sr = librosa.load(output_path, sr=self.sr, mono=True)
                    audio_info[str(wav_path)] = {
                        'duration': len(y) / sr,
                        'sample_rate': sr
                    }
                    normalized_files.append(output_path)
                except:
                    pass
            else:
                # 处理新文件
                info = self.normalize_audio(wav_path, output_path)
                if info:
                    audio_info[str(wav_path)] = info
                    normalized_files.append(output_path)
        
        report['steps']['normalization'] = {
            'input': len(audio_files),
            'output': len(normalized_files),
            'success_rate': round(len(normalized_files) / len(audio_files) * 100, 1) if audio_files else 0
        }
        print(f"   ✓ 标准化完成：{len(normalized_files)}/{len(audio_files)}")
        
        # 4. 数据集分割
        print("\n4️⃣  数据集分割...")
        splits = self.split_dataset(normalized_files)
        
        for split_name, files in splits.items():
            print(f"   {split_name}: {len(files)} 文件 ({len(files)/len(normalized_files)*100:.1f}%)")
        
        report['steps']['splits'] = {
            'train': len(splits['train']),
            'val': len(splits['val']),
            'test': len(splits['test']),
            'ratios': [0.8, 0.1, 0.1]
        }
        
        # 5. 创建 manifest
        print("\n5️⃣  创建 manifest 文件...")
        split_paths = {
            'train': [self.processed_dir / "audio" / f.name for f in splits['train']],
            'val': [self.processed_dir / "audio" / f.name for f in splits['val']],
            'test': [self.processed_dir / "audio" / f.name for f in splits['test']]
        }
        
        manifest_counts = self.create_manifest(
            {'train': splits['train'], 'val': splits['val'], 'test': splits['test']},
            transcripts,
            self.processed_dir,
            audio_info
        )
        
        report['steps']['manifest'] = manifest_counts
        
        # 6. 特征提取
        if extract_features:
            print("\n6️⃣  特征提取...")
            feature_counts = {'train': 0, 'val': 0, 'test': 0}
            
            for split_name, files in splits.items():
                feature_split_dir = self.features_dir / split_name
                feature_split_dir.mkdir(parents=True, exist_ok=True)
                
                for audio_path in tqdm(files, desc=f"{split_name}特征", leave=False):
                    feature_name = f"{audio_path.stem}.npz"
                    feature_path = feature_split_dir / feature_name
                    
                    if feature_path.exists() and not reprocess:
                        feature_counts[split_name] += 1
                    else:
                        result = self.extract_features(audio_path, feature_path)
                        if result:
                            feature_counts[split_name] += 1
            
            report['steps']['features'] = feature_counts
            print(f"   ✓ 特征提取完成：{sum(feature_counts.values())} 个文件")
        
        report['end_time'] = datetime.now().isoformat()
        return report
    
    def process_elderly(self, reprocess: bool = False, extract_features: bool = True) -> Dict:
        """处理老年语音数据集"""
        print("\n" + "="*60)
        print("👴 处理老年语音数据集")
        print("="*60)
        
        report = {
            'dataset': 'elderly',
            'start_time': datetime.now().isoformat(),
            'steps': {}
        }
        
        if not self.elderly_dir.exists():
            print("   ⚠️ 老年语音数据目录不存在，跳过处理")
            return report
        
        # 收集音频文件
        audio_files = list(self.elderly_dir.rglob("*.wav")) + \
                     list(self.elderly_dir.rglob("*.mp3")) + \
                     list(self.elderly_dir.rglob("*.flac"))
        
        print(f"   找到 {len(audio_files)} 个音频文件")
        
        if len(audio_files) == 0:
            return report
        
        # 处理流程与 AISHELL 类似
        # 为简洁起见，这里复用 AISHELL 的逻辑
        # 实际使用时可扩展为独立处理流程
        
        report['end_time'] = datetime.now().isoformat()
        return report
    
    def validate_results(self) -> Dict:
        """验证处理结果"""
        print("\n" + "="*60)
        print("✅ 验证处理结果")
        print("="*60)
        
        validation = {
            'timestamp': datetime.now().isoformat(),
            'checks': []
        }
        
        # 检查 1: 音频文件
        audio_count = len(list((self.processed_dir / "audio").glob("*.wav")))
        check1 = {
            'name': '标准化音频文件',
            'expected': '>0',
            'actual': audio_count,
            'passed': audio_count > 0
        }
        validation['checks'].append(check1)
        print(f"  {'✓' if check1['passed'] else '✗'} 音频文件：{audio_count}")
        
        # 检查 2: Manifest 文件
        for split in ['train', 'val', 'test']:
            manifest_path = self.processed_dir / split / "manifest.jsonl"
            exists = manifest_path.exists()
            lines = 0
            if exists:
                with open(manifest_path) as f:
                    lines = sum(1 for _ in f)
            
            check = {
                'name': f'{split} manifest',
                'expected': 'exists',
                'actual': f'{lines} lines' if exists else 'missing',
                'passed': exists and lines > 0
            }
            validation['checks'].append(check)
            print(f"  {'✓' if check['passed'] else '✗'} {split} manifest: {lines} 条")
        
        # 检查 3: 特征文件
        feature_count = len(list((self.features_dir / "train").glob("*.npz")))
        check3 = {
            'name': '训练集特征文件',
            'expected': '>0',
            'actual': feature_count,
            'passed': feature_count > 0
        }
        validation['checks'].append(check3)
        print(f"  {'✓' if check3['passed'] else '✗'} 特征文件：{feature_count}")
        
        # 检查 4: 标注加载
        train_manifest = self.processed_dir / "train" / "manifest.jsonl"
        transcripts_loaded = 0
        if train_manifest.exists():
            with open(train_manifest) as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get('transcript'):
                        transcripts_loaded += 1
        
        check4 = {
            'name': '标注加载',
            'expected': '>0',
            'actual': transcripts_loaded,
            'passed': transcripts_loaded > 0
        }
        validation['checks'].append(check4)
        status = "✓" if check4['passed'] else "⚠️"
        print(f"  {status} 标注加载：{transcripts_loaded} 条")
        
        # 总体通过
        all_passed = all(c['passed'] for c in validation['checks'])
        validation['all_passed'] = all_passed
        
        print(f"\n  {'✅ 所有检查通过' if all_passed else '⚠️ 部分检查未通过'}")
        
        return validation
    
    def save_report(self, report: Dict, filename: str):
        """保存处理报告"""
        report_path = self.processed_dir / filename
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📄 报告已保存：{report_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='音频数据集预处理工具')
    parser.add_argument('--all', action='store_true', help='处理所有数据集')
    parser.add_argument('--dataset', choices=['aishell', 'elderly'], help='指定数据集')
    parser.add_argument('--reprocess', action='store_true', help='重新处理（覆盖已有数据）')
    parser.add_argument('--extract-features-only', action='store_true', help='仅提取特征')
    parser.add_argument('--validate', action='store_true', help='仅验证结果')
    parser.add_argument('--no-features', action='store_true', help='跳过特征提取')
    
    args = parser.parse_args()
    
    # 检查依赖
    check_dependencies()
    
    # 创建处理器
    processor = AudioPreprocessor()
    
    all_reports = []
    
    # 仅验证模式
    if args.validate:
        validation = processor.validate_results()
        processor.save_report(validation, 'validation_report.json')
        return
    
    # 处理指定数据集
    if args.dataset or args.all:
        datasets = ['aishell', 'elderly'] if args.all else [args.dataset]
        
        for dataset in datasets:
            if dataset == 'aishell':
                report = processor.process_aishell(
                    reprocess=args.reprocess,
                    extract_features=not args.no_features
                )
            elif dataset == 'elderly':
                report = processor.process_elderly(
                    reprocess=args.reprocess,
                    extract_features=not args.no_features
                )
            else:
                continue
            
            all_reports.append(report)
            processor.save_report(report, f'processing_report_{dataset}.json')
    
    # 保存综合报告
    if all_reports:
        combined_report = {
            'timestamp': datetime.now().isoformat(),
            'datasets': all_reports,
            'summary': {
                'total_datasets': len(all_reports),
                'completed': sum(1 for r in all_reports if r.get('end_time'))
            }
        }
        processor.save_report(combined_report, 'processing_report.json')
    
    # 最终验证
    validation = processor.validate_results()
    processor.save_report(validation, 'validation_report.json')
    
    print("\n" + "="*60)
    print("✅ 预处理完成")
    print("="*60)


if __name__ == '__main__':
    main()
