#!/usr/bin/env python3
"""
AISHELL 数据集轻量级预处理脚本
=================================
用途：快速处理前 N 个样本，用于验证和演示
全量处理请使用：process_all_datasets.py

创建者：Hulk 🟢
创建日期：2026-03-30
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
from tqdm import tqdm

# 检查必要的库
for lib in ['librosa', 'soundfile', 'numpy', 'pandas', 'tqdm']:
    try:
        __import__(lib)
    except ImportError:
        print(f"错误：缺少必要的库：{lib}")
        print(f"安装：pip install {lib}")
        exit(1)

import librosa
import soundfile as sf


class AISHELLLiteProcessor:
    """AISHELL 轻量级处理器"""
    
    def __init__(
        self,
        workspace_root: str = "/Users/moondy/.openclaw/workspace-hulk",
        sample_rate: int = 16000,
        max_samples: int = 1000
    ):
        self.workspace = Path(workspace_root)
        self.sr = sample_rate
        self.max_samples = max_samples
        
        # 数据目录
        self.data_dir = self.workspace / "data"
        self.processed_dir = self.data_dir / "processed"
        self.features_dir = self.processed_dir / "features"
        
        print(f"🟢 AISHELL 轻量级处理器")
        print(f"   工作目录：{workspace_root}")
        print(f"   采样率：{sample_rate}Hz")
        print(f"   最大样本数：{max_samples}")
    
    def process(self) -> Dict:
        """执行完整处理流程"""
        print("\n" + "="*60)
        print("📊 AISHELL 轻量级预处理")
        print("="*60)
        
        report = {
            'dataset': 'aishell_lite',
            'start_time': datetime.now().isoformat(),
            'max_samples': self.max_samples,
            'steps': {}
        }
        
        aishell_raw = self.workspace / "data_aishell"
        
        # 1. 查找音频文件
        print("\n📁 扫描音频文件...")
        wav_files = list(aishell_raw.glob("wav/**/*.wav"))
        print(f"   找到 {len(wav_files)} 个 WAV 文件")
        
        if len(wav_files) == 0:
            print("❌ 未找到音频文件")
            report['status'] = 'failed'
            report['error'] = 'No audio files found'
            return report
        
        # 限制样本数
        wav_files = wav_files[:self.max_samples]
        print(f"   将处理前 {len(wav_files)} 个样本")
        report['steps']['input_files'] = len(wav_files)
        
        # 2. 音频标准化
        print("\n🔊 音频标准化...")
        processed_audio = self.processed_dir / "audio_lite"
        processed_audio.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        for wav_file in tqdm(wav_files, desc="标准化"):
            try:
                y, sr = librosa.load(wav_file, sr=self.sr)
                y = librosa.util.normalize(y)
                
                output_path = processed_audio / f"{wav_file.stem}_lite.wav"
                sf.write(output_path, y, self.sr)
                success_count += 1
            except Exception as e:
                pass
        
        print(f"✓ 标准化完成：{success_count}/{len(wav_files)}")
        report['steps']['normalized'] = success_count
        
        # 3. 数据集分割
        print("\n✂️  数据集分割...")
        processed_files = list(processed_audio.glob("*.wav"))
        
        np.random.seed(42)
        np.random.shuffle(processed_files)
        
        n_total = len(processed_files)
        n_train = int(n_total * 0.8)
        n_val = int(n_total * 0.1)
        
        train_files = processed_files[:n_train]
        val_files = processed_files[n_train:n_train + n_val]
        test_files = processed_files[n_train + n_val:]
        
        def create_manifest(files: List[Path], split_name: str) -> List[Dict]:
            manifest = []
            for audio_path in tqdm(files, desc=f"{split_name} manifest"):
                try:
                    y, sr = librosa.load(audio_path, sr=self.sr)
                    duration = len(y) / sr
                    
                    manifest.append({
                        'audio_path': str(audio_path),
                        'audio_id': audio_path.stem,
                        'duration': float(duration),
                        'transcript': "",  # 标注文件缺失
                        'language': 'zh-CN',
                        'split': split_name
                    })
                except:
                    pass
            return manifest
        
        (self.processed_dir / "train_lite").mkdir(exist_ok=True)
        (self.processed_dir / "val_lite").mkdir(exist_ok=True)
        (self.processed_dir / "test_lite").mkdir(exist_ok=True)
        
        for split_name, files in [
            ('train', train_files),
            ('val', val_files),
            ('test', test_files)
        ]:
            manifest = create_manifest(files, split_name)
            manifest_path = self.processed_dir / f"{split_name}_lite" / "manifest.jsonl"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                for item in manifest:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        split_report = {
            'train': len(train_files),
            'val': len(val_files),
            'test': len(test_files)
        }
        print(f"✓ 分割完成：train={split_report['train']}, val={split_report['val']}, test={split_report['test']}")
        report['steps']['splits'] = split_report
        
        # 4. 特征提取（仅训练集前 100 个样本）
        print("\n🎯 特征提取（预览）...")
        feature_samples = min(100, len(train_files))
        
        train_features_dir = self.features_dir / "train_lite"
        train_features_dir.mkdir(parents=True, exist_ok=True)
        
        manifest_path = self.processed_dir / "train_lite" / "manifest.jsonl"
        with open(manifest_path, 'r', encoding='utf-8') as f:
            samples = [json.loads(line) for line in f][:feature_samples]
        
        success_feat = 0
        for sample in tqdm(samples, desc="特征提取"):
            try:
                audio_path = sample['audio_path']
                audio_id = sample['audio_id']
                
                y, sr = librosa.load(audio_path, sr=self.sr)
                
                features = {
                    'mfcc': librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13).T,
                    'mel_spec': librosa.feature.melspectrogram(y=y, sr=sr, n_mels=40).T,
                    'spectral_contrast': librosa.feature.spectral_contrast(y=y, sr=sr).T,
                    'zcr': librosa.feature.zero_crossing_rate(y).T,
                }
                
                output_path = train_features_dir / f"{audio_id}.npz"
                np.savez_compressed(output_path, **features)
                success_feat += 1
            except:
                pass
        
        print(f"✓ 特征提取完成：{success_feat}/{feature_samples}")
        report['steps']['features'] = {
            'attempted': feature_samples,
            'success': success_feat
        }
        
        # 5. 生成报告
        report['end_time'] = datetime.now().isoformat()
        report['status'] = 'completed'
        
        report_path = self.processed_dir / "processing_report_lite.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 报告已保存：{report_path}")
        
        # 生成摘要
        self._generate_summary(report)
        
        return report
    
    def _generate_summary(self, report: Dict):
        """生成处理摘要"""
        summary = f"""
# AISHELL 轻量级预处理摘要

**执行时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**执行者**: Hulk 🟢  
**Cron 任务**: #7744d4c5 - 数据集预处理

## 处理结果

- **输入文件**: {report['steps'].get('input_files', 0)} 个 WAV 文件
- **标准化**: {report['steps'].get('normalized', 0)} 个文件
- **数据集分割**:
  - 训练集：{report['steps']['splits'].get('train', 0)} 个样本
  - 验证集：{report['steps']['splits'].get('val', 0)} 个样本
  - 测试集：{report['steps']['splits'].get('test', 0)} 个样本
- **特征提取**: {report['steps']['features'].get('success', 0)}/{report['steps']['features'].get('attempted', 0)} 个样本

## 输出目录

```
data/processed/
├── audio_lite/              # 标准化音频（lite 版）
├── train_lite/
│   └── manifest.jsonl      # 训练集标注
├── val_lite/
│   └── manifest.jsonl      # 验证集标注
├── test_lite/
│   └── manifest.jsonl      # 测试集标注
├── features/
│   └── train_lite/         # 训练集特征 (.npz)
└── processing_report_lite.json
```

## 标注状态

⚠️ **标注文件缺失** - transcript 字段为空

需要下载 AISHELL 标注文件：
1. 访问：https://www.openslr.org/33/
2. 下载 data_aishell.tgz
3. 提取 transcript/aishell_transcript_v0.8.txt
4. 放置到：data_aishell/transcript/

## 全量处理

要处理全部 ~178 小时音频（约 17,000+ 文件），请运行：

```bash
bash scripts/dataset_preprocess.sh --dataset aishell
```

或使用 Python 脚本：

```bash
python3 scripts/process_all_datasets.py --dataset aishell
```

**状态**: ✅ 轻量级处理完成
"""
        
        summary_path = self.workspace / "scripts" / "AISHELL_LITE_SUMMARY.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"📄 摘要已保存：{summary_path}")


def main():
    processor = AISHELLLiteProcessor(max_samples=100)
    report = processor.process()
    
    print("\n" + "="*60)
    print("✅ AISHELL 轻量级预处理完成")
    print("="*60)


if __name__ == '__main__':
    main()
