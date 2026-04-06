#!/usr/bin/env python3
"""
Hulk v2.0 投递脚本 — 将 GEO 迭代结果投递到 Discord

使用方式:
    python3 delivery.py --message "消息内容"
    python3 delivery.py --file logs/last_delivery.txt
"""

import argparse
import subprocess
import sys
from pathlib import Path

def send_discord_message(message: str):
    """发送 Discord 消息"""
    try:
        # 使用 openclaw message 工具 (完整路径)
        # 根据 /Users/moondy/.openclaw/cron/jobs.json 配置
        result = subprocess.run([
            '/Users/moondy/.nvm/versions/node/v22.22.2/bin/openclaw', 'message', 'send',
            '--target', 'user:1466465999950971044',
            '--message', message
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Discord 消息已发送")
            return True
        else:
            print(f"❌ 发送失败：{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 异常：{e}")
        return False

def send_discord_file(file_path: str):
    """发送 Discord 文件"""
    try:
        result = subprocess.run([
            'openclaw', 'message', 'send',
            '--channel', 'discord',
            '--file', file_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Discord 文件已发送")
            return True
        else:
            print(f"❌ 发送失败：{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 异常：{e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Hulk v2.0 投递脚本")
    parser.add_argument("--message", "-m", type=str, help="消息内容")
    parser.add_argument("--file", "-f", type=str, help="文件路径")
    args = parser.parse_args()
    
    if args.message:
        success = send_discord_message(args.message)
    elif args.file:
        # 读取文件内容作为消息
        content = Path(args.file).read_text(encoding='utf-8')
        success = send_discord_message(content)
    else:
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
