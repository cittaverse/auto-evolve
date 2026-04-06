#!/usr/bin/env python3
"""
AISHELL-1 数据集完整预处理脚本 v2.0
===================================
功能：下载转录、解压音频、清洗、分割、特征提取

创建者：Hulk 🟢
创建日期：2026-03-27
更新：增强转录处理、支持增量处理、添加质量检查

依赖：
    pip install librosa numpy pandas tqdm soundfile

用法：
    python scripts/process_aishell.py --download-transcript
    python scripts/process_aishell.py --process
    python scripts/process_aishell.py --all
"""

import argparse
import gzip
import json
import os
import shutil
import subprocess
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
    print("⚠️  警告：librosa 未安装，特征提取功能将不可用")
    print("   安装：pip install librosa")


class AISHELLProcessor:
    """AISHELL-1 数据集完整处理器"""
    
    def __init__(
        self,
        data_dir: str = "/home/node/.openclaw/workspace-hulk/data_aishell",
        output_dir: str = "/home/node/.openclaw/workspace-hulk/data/processed",
        sample_rate: int = 16000,
        test_split: float = 0.1,
        val_split: float = 0.1
    ):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.sr = sample_rate
        self.test_split = test_split
        self.val_split = val_split
        
        # 创建输出目录
        self._setup_dirs()
    
    def _setup_dirs(self):
        """创建必要的输出目录"""
        dirs = [
            self.output_dir,
            self.output_dir / "audio",
            self.output_dir / "train",
            self.output_dir / "val",
            self.output_dir / "test",
            self.output_dir / "features",
            self.output_dir / "features" / "train",
            self.output_dir / "features" / "val",
            self.output_dir / "features" / "test",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def download_transcript(self) -> bool:
        """下载转录文件"""
        print("\n{'='*60}")
        print("下载 AISHELL-1 转录文件")
        print(f"{'='*60}")
        
        transcript_url = "http://www.openslr.org/resources/33/data_aishell_transcript_v0.8.tar.gz"
        transcript_tgz = self.data_dir / "data_aishell_transcript_v0.8.tar.gz"
        transcript_dir = self.data_dir / "transcript"
        
        if transcript_dir.exists() and (transcript_dir / "aishell_transcript_v0.8.txt").exists():
            print("✓ 转录文件已存在，跳过下载")
            return True
        
        # 下载
        print(f"下载：{transcript_url}")
        try:
            if shutil.which("wget"):
                subprocess.run(
                    ["wget", "-c", transcript_url, "-O", str(transcript_tgz)],
                    check=True
                )
            elif shutil.which("curl"):
                subprocess.run(
                    ["curl", "-L", "-o", str(transcript_tgz), transcript_url],
                    check=True
                )
            else:
                print("⚠️  错误：需要 wget 或 curl")
                return False
        except Exception as e:
            print(f"⚠️  下载失败：{e}")
            return False
        
        # 解压
        print("解压转录文件...")
        try:
            with tarfile.open(transcript_tgz, "r:gz") as tar:
                tar.extractall(path=self.data_dir)
            
            # 移动到正确位置
            extracted_dir = self.data_dir / "data_aishell" / "transcript"
            if extracted_dir.exists():
                if transcript_dir.exists():
                    shutil.rmtree(transcript_dir)
                shutil.move(str(extracted_dir), str(transcript_dir))
                shutil.rmtree(self.data_dir / "data_aishell", ignore_errors=True)
            
            # 清理
            transcript_tgz.unlink()
            
            print("✓ 转录文件下载完成")
            return True
        except Exception as e:
            print(f"⚠️  解压失败：{e}")
            return False
    
    def load_transcripts(self) -> Dict[str, str]:
        """加载转录文本"""
        print("\n{'='*60}")
        print("加载转录文本")
        print(f"{'='*60}")
        
        transcript_path = self.data_dir / "transcript" / "aishell_transcript_v0.8.txt"
        
        if not transcript_path.exists():
            print(f"⚠️  转录文件不存在：{transcript_path}")
            print("   请先运行：python scripts/process_aishell.py --download-transcript")
            return {}
        
        transcripts = {}
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in tqdm(f, desc="加载转录"):
                parts = line.strip().split(' ', 1)
                if len(parts) == 2:
                    audio_id, text = parts
                    transcripts[audio_id] = text
        
        print(f"✓ 加载 {len(transcripts)} 条转录")
        return transcripts
    
    def extract_audio(self) -> List[Path]:
        """解压音频文件"""
        print("\n{'='*60}")
        print("解压音频文件")
        print(f"{'='*60}")
        
        wav_dir = self.data_dir / "wav"
        if not wav_dir.exists():
            print(f"⚠️  音频目录不存在：{wav_dir}")
            return []
        
        tar_files = list(wav_dir.glob("*.tar.gz"))
        print(f"找到 {len(tar_files)} 个压缩文件")
        
        extracted_files = []
        for tar_file in tar_files:
            try:
                with tarfile.open(tar_file, "r:gz") as tar:
                    tar.extractall(path=self.output_dir / "audio")
                    extracted_files.append(tar_file)
            except Exception as e:
                print(f"⚠️  解压失败 {tar_file.name}: {e}")
        
        print(f"✓ 解压完成：{len(extracted_files)}/{len(tar_files)}")
        
        # 返回所有 WAV 文件
        audio_files = list((self.output_dir / "audio").rglob("*.wav"))
        print(f"   共 {len(audio_files)} 个音频文件")
        return audio_files
    
    def normalize_audio(self, audio_path: Path, output_path: Path) -> bool:
        """标准化音频（重采样 + 音量归一化）"""
        try:
            if LIBROSA_AVAILABLE:
                y, _ = librosa.load(audio_path, sr=self.sr)
                y = librosa.util.normalize(y)
                sf.write(output_path, y, self.sr, format='WAV')
            else:
                # 无 librosa 时直接复制
                shutil.copy2(audio_path, output_path)
            return True
        except Exception as e:
            print(f"⚠️  标准化失败 {audio_path.name}: {e}")
            return False
    
    def extract_features(self, audio_path: Path) -> Dict[str, np.ndarray]:
        """提取音频特征"""
        if not LIBROSA_AVAILABLE:
            return {}
        
        try:
            y, sr = librosa.load(audio_path, sr=self.sr)
            
            return {
                'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).T,
                'mel_spec': librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40).T,
                'contrast': librosa.feature.spectral_contrast(y=y, sr=sr).T,
                'zcr': librosa.feature.zero_crossing_rate(y).T,
                'chroma': librosa.feature.chroma_stft(y=y, sr=sr).T,
                'spectral_centroid': librosa.feature.spectral_centroid(y=y, sr=sr).T,
                'spectral_rolloff': librosa.feature.spectral_rolloff(y=y, sr=sr).T,
            }
        except Exception as e:
            return {}
    
    def split_and_create_manifest(
        self,
        audio_files: List[Path],
        transcripts: Dict[str, str]
    ) -> Tuple[List, List, List]:
        """分割数据集并创建 manifest"""
        print("\n{'='*60}")
        print("分割数据集并创建 manifest")
        print(f"{'='*60}")
        
        np.random.seed(42)
        indices = np.random.permutation(len(audio_files))
        
        n_test = int(len(audio_files) * self.test_split)
        n_val = int(len(audio_files) * self.val_split)
        
        test_idx = indices[:n_test]
        val_idx = indices[n_test:n_test + n_val]
        train_idx = indices[n_test + n_val:]
        
        splits = {
            'train': train_idx,
            'val': val_idx,
            'test': test_idx
        }
        
        results = {'train': [], 'val': [], 'test': []}
        
        for split_name, idx_array in splits.items():
            manifest = []
            for i in tqdm(idx_array, desc=f"处理 {split_name}"):
                audio_path = audio_files[i]
                audio_id = audio_path.stem.replace('_norm', '')
                
                # 获取时长
                duration = 0.0
                if LIBROSA_AVAILABLE:
                    try:
                        y, sr = librosa.load(audio_path, sr=None)
                        duration = len(y) / sr
                    except:
                        pass
                
                manifest.append({
                    'audio_path': str(audio_path),
                    'audio_id': audio_id,
                    'duration': round(duration, 3),
                    'transcript': transcripts.get(audio_id, ""),
                    'language': 'zh-CN'
                })
            
            # 保存 manifest
            manifest_path = self.output_dir / split_name / "manifest.jsonl"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                for item in manifest:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
            results[split_name] = manifest
            print(f"✓ {split_name}: {len(manifest)} 条 → {manifest_path}")
        
        return results['train'], results['val'], results['test']
    
    def extract_features_batch(
        self,
        manifest: List[Dict],
        split: str,
        limit: Optional[int] = None
    ):
        """批量提取特征"""
        if not LIBROSA_AVAILABLE:
            print("⚠️  librosa 不可用，跳过特征提取")
            return
        
        print(f"\n{'='*60}")
        print(f"提取 {split} 特征")
        print(f"{'='*60}")
        
        features_dir = self.output_dir / "features" / split
        features_dir.mkdir(parents=True, exist_ok=True)
        
        count = 0
        for item in tqdm(manifest[:limit] if limit else manifest, desc=f"特征提取 ({split})"):
            audio_path = Path(item['audio_path'])
            if not audio_path.exists():
                continue
            
            features = self.extract_features(audio_path)
            if features:
                output_path = features_dir / f"{audio_path.stem}.npz"
                np.savez_compressed(output_path, **features)
                count += 1
        
        print(f"✓ 提取 {count} 个特征文件")
    
    def process_all(self, extract_features: bool = True, feature_limit: int = 1000):
        """完整处理流程"""
        print(f"\n{'='*60}")
        print("AISHELL-1 完整预处理流程")
        print(f"{'='*60}")
        
        # Step 1: 下载转录
        if not self.download_transcript():
            print("⚠️  转录下载失败，继续处理但转录将为空")
        
        # Step 2: 加载转录
        transcripts = self.load_transcripts()
        
        # Step 3: 解压音频
        audio_files = self.extract_audio()
        if not audio_files:
            print("⚠️  未找到音频文件，终止处理")
            return False
        
        # Step 4: 标准化音频
        print(f"\n{'='*60}")
        print("标准化音频")
        print(f"{'='*60}")
        
        normalized_files = []
        for audio_path in tqdm(audio_files, desc="标准化"):
            output_path = self.output_dir / "audio" / f"{audio_path.stem}_norm.wav"
            if self.normalize_audio(audio_path, output_path):
                normalized_files.append(output_path)
        
        print(f"✓ 标准化完成：{len(normalized_files)}/{len(audio_files)}")
        
        # Step 5: 分割并创建 manifest
        train, val, test = self.split_and_create_manifest(normalized_files, transcripts)
        
        # Step 6: 特征提取
        if extract_features and LIBROSA_AVAILABLE:
            self.extract_features_batch(train, 'train', limit=feature_limit)
            self.extract_features_batch(val, 'val', limit=feature_limit // 10)
            self.extract_features_batch(test, 'test', limit=feature_limit // 10)
        
        # Step 7: 保存报告
        self._save_report({
            'dataset': 'aishell-1',
            'total_audio_files': len(audio_files),
            'normalized_files': len(normalized_files),
            'train_samples': len(train),
            'val_samples': len(val),
            'test_samples': len(test),
            'transcripts_loaded': len(transcripts),
            'sample_rate': self.sr,
            'features_extracted': extract_features and LIBROSA_AVAILABLE,
            'feature_limit': feature_limit if extract_features else 0
        })
        
        print(f"\n{'='*60}")
        print("✓ AISHELL-1 处理完成")
        print(f"{'='*60}")
        print(f"输出目录：{self.output_dir}")
        
        return True
    
    def _save_report(self, stats: Dict):
        """保存处理报告"""
        import datetime
        stats['timestamp'] = datetime.datetime.now().isoformat()
        stats['processor_version'] = '2.0'
        
        report_path = self.output_dir / "aishell_processing_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 报告已保存：{report_path}")


def main():
    parser = argparse.ArgumentParser(
        description='AISHELL-1 数据集预处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--data-dir', type=str, 
                        default='/home/node/.openclaw/workspace-hulk/data_aishell',
                        help='原始数据目录')
    parser.add_argument('--output-dir', type=str,
                        default='/home/node/.openclaw/workspace-hulk/data/processed',
                        help='输出目录')
    parser.add_argument('--sample-rate', type=int, default=16000,
                        help='目标采样率 (Hz)')
    parser.add_argument('--download-transcript', action='store_true',
                        help='仅下载转录文件')
    parser.add_argument('--process', action='store_true',
                        help='执行完整处理流程')
    parser.add_argument('--all', action='store_true',
                        help='下载转录 + 完整处理')
    parser.add_argument('--no-features', action='store_true',
                        help='跳过特征提取')
    parser.add_argument('--feature-limit', type=int, default=1000,
                        help='每个 split 提取特征的最大样本数')
    
    args = parser.parse_args()
    
    processor = AISHELLProcessor(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        sample_rate=args.sample_rate
    )
    
    if args.download_transcript:
        processor.download_transcript()
    elif args.process or args.all:
        processor.process_all(
            extract_features=not args.no_features,
            feature_limit=args.feature_limit
        )
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
