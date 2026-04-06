#!/usr/bin/env python3
"""
修复 AISHELL 标注文件

问题：aishell_transcript_v0.8.txt 被下载为 HTML 而非纯文本
解决：从 resource_aishell.tgz 中提取正确的标注文件

Usage:
    python fix_aishell_transcript.py --data_dir /path/to/data_aishell

作者：Hulk 🟢
日期：2026-04-04
"""

import os
import sys
import argparse
import tarfile
from pathlib import Path


def download_transcript_from_huggingface(data_dir: Path) -> bool:
    """从 HuggingFace 下载标注文件"""
    import urllib.request
    
    transcript_dir = data_dir / "transcript"
    transcript_dir.mkdir(exist_ok=True)
    transcript_file = transcript_dir / "aishell_transcript_v0.8.txt"
    
    url = "https://huggingface.co/datasets/AISHELL/AISHELL-1/raw/main/data_aishell/transcript/aishell_transcript_v0.8.txt"
    
    try:
        print(f"📥 从 HuggingFace 下载标注文件...")
        urllib.request.urlretrieve(url, str(transcript_file))
        
        # 验证
        with open(transcript_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"✓ 标注文件已下载：{transcript_file}")
        print(f"✓ 标注行数：{len(lines)}")
        print(f"✓ 前 5 行示例:")
        for line in lines[:5]:
            print(f"  {line.strip()[:80]}")
        
        return True
        
    except Exception as e:
        print(f"❌ 下载失败：{e}")
        return False


def extract_transcript_from_tgz(data_dir: Path) -> bool:
    """从 tgz 文件中提取标注 (fallback)"""
    tgz_path = data_dir / "resource_aishell.tgz"
    
    if not tgz_path.exists():
        print(f"⚠️  未找到 tgz 文件：{tgz_path}")
        return download_transcript_from_huggingface(data_dir)
    
    transcript_dir = data_dir / "transcript"
    transcript_dir.mkdir(exist_ok=True)
    
    try:
        with tarfile.open(tgz_path, 'r:gz') as tar:
            # 查找标注文件
            transcript_member = None
            for member in tar.getmembers():
                if 'transcript' in member.name.lower() and member.name.endswith('.txt'):
                    transcript_member = member
                    break
            
            if transcript_member is None:
                print("⚠️  在 tgz 中未找到标注文件，尝试从 HuggingFace 下载")
                return download_transcript_from_huggingface(data_dir)
            
            # 提取文件
            transcript_file = transcript_dir / "aishell_transcript_v0.8.txt"
            with tar.extractfile(transcript_member) as source:
                with open(transcript_file, 'wb') as target:
                    target.write(source.read())
            
            print(f"✓ 标注文件已提取：{transcript_file}")
            
            # 验证
            with open(transcript_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            print(f"✓ 标注行数：{len(lines)}")
            print(f"✓ 前 5 行示例:")
            for line in lines[:5]:
                print(f"  {line.strip()[:80]}")
            
            return True
            
    except Exception as e:
        print(f"⚠️  提取失败：{e}，尝试从 HuggingFace 下载")
        return download_transcript_from_huggingface(data_dir)


def main():
    parser = argparse.ArgumentParser(description='修复 AISHELL 标注文件')
    parser.add_argument('--data_dir', type=str, 
                        default='/Users/moondy/.openclaw/workspace-hulk/data_aishell',
                        help='AISHELL 数据目录')
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    
    if not data_dir.exists():
        print(f"❌ 数据目录不存在：{data_dir}")
        sys.exit(1)
    
    print(f"📁 数据目录：{data_dir}")
    
    # 检查现有标注文件
    transcript_file = data_dir / "transcript" / "aishell_transcript_v0.8.txt"
    if transcript_file.exists():
        with open(transcript_file, 'r', encoding='utf-8') as f:
            content = f.read(500)
        
        if '<!DOCTYPE html>' in content or '<html' in content:
            print("⚠️  检测到标注文件为 HTML 格式，需要修复")
            success = extract_transcript_from_tgz(data_dir)
        else:
            print("✓ 标注文件格式正确")
            success = True
    else:
        print("⚠️  标注文件不存在，尝试从 tgz 提取")
        success = extract_transcript_from_tgz(data_dir)
    
    if success:
        print("\n✓ 标注文件修复完成")
        sys.exit(0)
    else:
        print("\n❌ 标注文件修复失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
