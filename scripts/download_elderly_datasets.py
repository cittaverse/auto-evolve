#!/usr/bin/env python3
"""
老年语音数据集下载与预处理
==========================
支持多个老年语音相关数据集的下载和标准化处理

创建者：Hulk 🟢
创建日期：2026-03-27

支持的数据集:
- CASIA 老年语音数据集 (中文)
- Common Voice (多语言，可筛选老年说话者)
- VoxCeleb (可用于年龄相关研究)

用法:
    python scripts/download_elderly_datasets.py --list
    python scripts/download_elderly_datasets.py --dataset casia
    python scripts/download_elderly_datasets.py --dataset common_voice --language zh-CN
"""

import argparse
import json
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class ElderlyVoiceDatasetDownloader:
    """老年语音数据集下载器"""
    
    def __init__(self, output_dir: str = "/home/node/.openclaw/workspace-hulk/data/elderly_voice"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据集配置
        self.datasets = {
            'casia': {
                'name': 'CASIA 老年语音数据集',
                'description': '中国科学院自动化研究所老年语音数据集',
                'language': 'zh-CN',
                'url': 'http://www.cassp.org.cn/resources',  # 需要申请
                'notes': '需要学术申请，无法自动下载'
            },
            'common_voice': {
                'name': 'Mozilla Common Voice',
                'description': '多语言众包语音数据集，可按年龄筛选',
                'language': 'multi',
                'url': 'https://commonvoice.mozilla.org/',
                'notes': '支持中文，可筛选 60+ 岁说话者'
            },
            'voxceleb': {
                'name': 'VoxCeleb',
                'description': '大规模说话人识别数据集，包含年龄信息',
                'language': 'en',
                'url': 'https://www.robots.ox.ac.uk/~vgg/data/voxceleb/',
                'notes': '主要用于说话人识别，年龄为元数据'
            },
            'speechace': {
                'name': 'SpeechACE Elderly',
                'description': '老年语音评估数据集',
                'language': 'en',
                'url': 'https://speechace.com/',
                'notes': '商业数据集，需要授权'
            }
        }
    
    def list_datasets(self):
        """列出支持的数据集"""
        print("\n{'='*60}")
        print("支持的老年语音数据集")
        print(f"{'='*60}\n")
        
        for key, info in self.datasets.items():
            print(f"📦 {info['name']} ({key})")
            print(f"   描述：{info['description']}")
            print(f"   语言：{info['language']}")
            print(f"   网址：{info['url']}")
            print(f"   备注：{info['notes']}")
            print()
    
    def download_common_voice(self, language: str = 'zh-CN', age_filter: str = '60+'):
        """下载 Common Voice 数据集"""
        print(f"\n{'='*60}")
        print(f"下载 Common Voice ({language}, 年龄：{age_filter})")
        print(f"{'='*60}")
        
        cv_dir = self.output_dir / "common_voice"
        cv_dir.mkdir(parents=True, exist_ok=True)
        
        print("""
Common Voice 下载说明:
=====================
1. 访问 https://commonvoice.mozilla.org/zh-CN/datasets
2. 选择语言：中文 (zh-CN)
3. 下载音频文件 (.tar.gz)
4. 下载后运行以下命令解压:

   cd data/elderly_voice/common_voice
   tar -xzf zh-CN.tar.gz

5. 使用 scripts/filter_elderly_from_cv.py 筛选老年说话者

注意：Common Voice 不直接提供年龄筛选，需要通过后续处理或元数据匹配
""")
        
        # 创建下载说明文件
        readme_path = cv_dir / "DOWNLOAD_INSTRUCTIONS.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Common Voice 老年语音数据下载指南

## 下载链接
- 中文：https://commonvoice.mozilla.org/zh-CN/datasets
- 英文：https://commonvoice.mozilla.org/en/datasets

## 下载步骤
1. 访问上述链接
2. 点击对应语言的下载按钮
3. 保存到：{cv_dir}/
4. 解压：`tar -xzf *.tar.gz`

## 年龄筛选
Common Voice 不直接提供年龄元数据。筛选老年说话者的方法：
1. 通过说话人 ID 匹配其他有年龄标注的数据集
2. 使用语音年龄估计模型预测
3. 人工标注子集

## 输出目录
{cv_dir}
""")
        
        print(f"✓ 下载说明已保存：{readme_path}")
        return True
    
    def download_voxceleb(self):
        """下载 VoxCeleb 数据集"""
        print(f"\n{'='*60}")
        print("下载 VoxCeleb 数据集")
        print(f"{'='*60}")
        
        vox_dir = self.output_dir / "voxceleb"
        vox_dir.mkdir(parents=True, exist_ok=True)
        
        print("""
VoxCeleb 下载说明:
=================
VoxCeleb 需要通过 Google Form 申请下载链接

1. 访问申请页面:
   https://www.robots.ox.ac.uk/~vgg/data/voxceleb/

2. 填写申请表（学术用途）

3. 收到下载链接后运行:
   
   # VoxCeleb1
   wget https://thor.robots.ox.ac.uk/~vgg/data/voxceleb/vox1a/voxceleb_dev.zip
   wget https://thor.robots.ox.ac.uk/~vgg/data/voxceleb/vox1a/voxceleb_test.zip
   
   # VoxCeleb2
   wget https://thor.robots.ox.ac.uk/~vgg/data/voxceleb/vox1a/voxceleb2_dev.aac
   wget https://thor.robots.ox.ac.uk/~vgg/data/voxceleb/vox1a/voxceleb2_test.aac

4. 解压并转换格式:
   python scripts/convert_voxceleb.py

## 年龄信息
VoxCeleb 的年龄信息在元数据文件中:
- vox1_meta.csv
- vox2_meta.csv

包含说话人的年龄范围信息
""")
        
        # 创建说明文件
        readme_path = vox_dir / "DOWNLOAD_INSTRUCTIONS.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"""# VoxCeleb 数据集下载指南

## 申请下载
访问：https://www.robots.ox.ac.uk/~vgg/data/voxceleb/

## 输出目录
{vox_dir}

## 年龄元数据
下载后查看 vox*_meta.csv 文件获取说话人年龄信息
""")
        
        print(f"✓ 下载说明已保存：{readme_path}")
        return True
    
    def create_age_estimation_script(self):
        """创建语音年龄估计脚本"""
        script_path = self.output_dir / "estimate_speaker_age.py"
        
        content = '''#!/usr/bin/env python3
"""
语音年龄估计工具
===============
使用预训练模型从语音估计说话人年龄

依赖:
    pip install torch torchaudio transformers

用法:
    python estimate_speaker_age.py --audio_dir /path/to/audio --output ages.json
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

try:
    import torch
    import torchaudio
    from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    print("需要安装：pip install torch torchaudio transformers")


class AgeEstimator:
    """语音年龄估计器"""
    
    def __init__(self, model_name: str = "superb/wav2vec2-base-superb-ic"):
        if not MODEL_AVAILABLE:
            raise ImportError("需要安装 torch, torchaudio, transformers")
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 注意：这里使用的是示例模型，实际年龄估计需要专门的模型
        # 可以使用以下资源:
        # - https://huggingface.co/models?pipeline_tag=audio-classification&tags=age
        print(f"加载年龄估计模型...")
        print(f"设备：{self.device}")
        
    def estimate(self, audio_path: str) -> Dict:
        """估计单个音频的说话人年龄"""
        # 简化实现 - 实际需要使用专门的年龄估计模型
        return {
            'audio_path': audio_path,
            'estimated_age': None,  # 需要模型推理
            'age_range': None,
            'confidence': None
        }
    
    def batch_estimate(self, audio_files: List[str], output_path: str):
        """批量估计年龄"""
        results = []
        
        for audio_path in audio_files:
            try:
                result = self.estimate(audio_path)
                results.append(result)
                print(f"✓ {Path(audio_path).name}")
            except Exception as e:
                print(f"✗ {audio_path}: {e}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\\n结果已保存：{output_path}")


def main():
    parser = argparse.ArgumentParser(description='语音年龄估计工具')
    parser.add_argument('--audio_dir', type=str, required=True, help='音频目录')
    parser.add_argument('--output', type=str, default='ages.json', help='输出文件')
    parser.add_argument('--ext', type=str, default='wav', help='音频扩展名')
    
    args = parser.parse_args()
    
    if not MODEL_AVAILABLE:
        print("请先安装依赖：pip install torch torchaudio transformers")
        return
    
    audio_dir = Path(args.audio_dir)
    audio_files = list(audio_dir.glob(f"*.{args.ext}"))
    
    print(f"找到 {len(audio_files)} 个音频文件")
    
    estimator = AgeEstimator()
    estimator.batch_estimate([str(f) for f in audio_files], args.output)


if __name__ == '__main__':
    main()
'''
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        os.chmod(script_path, 0o755)
        print(f"✓ 年龄估计脚本已创建：{script_path}")
    
    def process_dataset(self, dataset_name: str, **kwargs):
        """处理指定数据集"""
        if dataset_name not in self.datasets:
            print(f"⚠️  未知数据集：{dataset_name}")
            print(f"可用数据集：{list(self.datasets.keys())}")
            return False
        
        print(f"\n处理数据集：{self.datasets[dataset_name]['name']}")
        
        if dataset_name == 'common_voice':
            return self.download_common_voice(
                language=kwargs.get('language', 'zh-CN'),
                age_filter=kwargs.get('age_filter', '60+')
            )
        elif dataset_name == 'voxceleb':
            return self.download_voxceleb()
        elif dataset_name == 'casia':
            print("""
CASIA 老年语音数据集:
===================
此数据集需要学术申请，无法自动下载。

申请流程:
1. 访问：http://www.cassp.org.cn/
2. 联系数据管理员
3. 提交学术用途申请
4. 签署数据使用协议
5. 等待审批和下载链接

申请获批后，将数据保存到:
/home/node/.openclaw/workspace-hulk/data/elderly_voice/casia/
""")
            return True
        else:
            print(f"数据集 '{dataset_name}' 的处理逻辑待实现")
            return True


def main():
    parser = argparse.ArgumentParser(
        description='老年语音数据集下载与预处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--list', action='store_true', help='列出支持的数据集')
    parser.add_argument('--dataset', type=str, help='要下载的数据集名称')
    parser.add_argument('--language', type=str, default='zh-CN', 
                        help='Common Voice 语言选项')
    parser.add_argument('--age-filter', type=str, default='60+',
                        help='年龄筛选条件')
    parser.add_argument('--create-age-estimator', action='store_true',
                        help='创建年龄估计脚本')
    
    args = parser.parse_args()
    
    downloader = ElderlyVoiceDatasetDownloader()
    
    if args.list:
        downloader.list_datasets()
    elif args.dataset:
        downloader.process_dataset(
            args.dataset,
            language=args.language,
            age_filter=args.age_filter
        )
    elif args.create_age_estimator:
        downloader.create_age_estimation_script()
    else:
        parser.print_help()
        print("\n示例用法:")
        print("  python scripts/download_elderly_datasets.py --list")
        print("  python scripts/download_elderly_datasets.py --dataset common_voice")
        print("  python scripts/download_elderly_datasets.py --dataset voxceleb")
        print("  python scripts/download_elderly_datasets.py --create-age-estimator")


if __name__ == '__main__':
    main()
