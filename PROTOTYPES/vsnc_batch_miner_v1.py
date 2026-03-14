#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VSNC 批量挖掘工具 v1.0
- 低并发 (2-3) 避免 TLS/SSL 连接关闭
- 重试机制 (最多 3 次，指数退避)
- 进度追踪 (ledger.json)
"""

import os
import json
import time
import random
import urllib.request
import ssl
import subprocess
from datetime import datetime
from pathlib import Path

# ============== 配置 ==============
DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY")
BASE_URL = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
MODEL = "qwen3.5-plus"

# 并发控制
MAX_CONCURRENCY = 2  # 降低并发避免 TLS 连接关闭
RETRY_MAX = 3
RETRY_BASE_DELAY = 2  # 秒

# 路径
WORKSPACE = Path("/home/node/.openclaw/workspace-hulk")
VSNC_RAW = WORKSPACE / "VSNC" / "原始材料"
VSNC_OUTPUT = WORKSPACE / "VSNC" / "输出"
LEDGER_PATH = WORKSPACE / "VSNC" / "ledger.json"

# ============== SSL 上下文 ==============
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# ============== 提取提示词 ==============
EXTRACTION_PROMPT = """
你是专业的自传体记忆分析系统。请从以下老年人回忆叙述中提取结构化事件图。

输入是一段老年人的回忆叙述，可能包含：
- 具体事件细节（时间、地点、感知、动作、情感）
- 一般性知识/事实
- 对记忆本身的评论

请输出严格 JSON 格式：
{
  "events": [
    {"id": "e1", "description": "事件描述", "estimated_time": "时间估计", "category": "INTERNAL|EXTERNAL"}
  ],
  "temporal_links": [
    {"source": "e1", "target": "e2", "relation": "BEFORE|AFTER|DURING"}
  ],
  "causal_links": [
    {"source": "e1", "target": "e2", "reason": "因果关系说明"}
  ],
  "summary": {
    "total_internal": 内部细节数量,
    "total_external": 外部细节数量,
    "episodic_ratio": 情节比例 (0-1)
  }
}

确保输出是有效的 JSON。

叙述内容：
"""

# ============== 工具函数 ==============
def load_ledger():
    """加载进度账本"""
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed": [], "failed": [], "progress": {}}

def save_ledger(ledger):
    """保存进度账本"""
    with open(LEDGER_PATH, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, ensure_ascii=False, indent=2)

def call_llm_with_retry(text, retry_count=0):
    """调用 LLM API，带重试和指数退避"""
    try:
        payload = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": EXTRACTION_PROMPT + text}],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }).encode('utf-8')
        
        req = urllib.request.Request(BASE_URL, data=payload, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {DASHSCOPE_API_KEY}')
        req.add_header('User-Agent', 'VSNC-BatchMiner/1.0')
        
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            return json.loads(content)
            
    except Exception as e:
        error_msg = str(e)
        if retry_count < RETRY_MAX:
            delay = RETRY_BASE_DELAY * (2 ** retry_count) + random.uniform(0.5, 1.5)
            print(f"  ⚠️  错误：{error_msg[:50]}... 重试 {retry_count+1}/{RETRY_MAX} ({delay:.1f}s)")
            time.sleep(delay)
            return call_llm_with_retry(text, retry_count + 1)
        else:
            print(f"  ❌ 失败：{error_msg[:80]}...")
            return {"error": error_msg}

def extract_text_from_pdf(pdf_path):
    """从 PDF 提取文本（使用 pdftotext 命令行工具）"""
    try:
        # 使用 pdftotext 命令行工具
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        else:
            print(f"  ⚠️  pdftotext 返回空输出")
            return f"[PDF 解析空输出：{pdf_path.name}]"
    except subprocess.TimeoutExpired:
        return f"[PDF 解析超时：{pdf_path.name}]"
    except FileNotFoundError:
        print(f"  ⚠️  pdftotext 未找到，使用文件名作为占位")
        return f"[PDF 文件：{pdf_path.name}]"
    except Exception as e:
        return f"[PDF 读取错误：{str(e)}]"

def process_pdf(pdf_path, ledger):
    """处理单个 PDF"""
    pdf_name = pdf_path.name
    output_path = VSNC_OUTPUT / f"{pdf_path.stem}_analysis.json"
    
    # 检查是否已处理
    if pdf_name in ledger.get("processed", []):
        print(f"⏭️  跳过：{pdf_name} (已处理)")
        return
    
    print(f"\n📄 处理：{pdf_name}")
    
    # 提取文本
    text = extract_text_from_pdf(pdf_path)
    if len(text) < 50:
        print(f"  ⚠️  文本过短 ({len(text)} chars)，跳过")
        ledger["failed"].append({"file": pdf_name, "reason": "text_too_short"})
        save_ledger(ledger)
        return
    
    # 截取适当长度（避免 token 超限）
    max_chars = 8000
    if len(text) > max_chars:
        text = text[:max_chars] + "..."
    
    # 调用 LLM
    result = call_llm_with_retry(text)
    
    if "error" in result:
        ledger["failed"].append({"file": pdf_name, "reason": result["error"]})
        save_ledger(ledger)
        return
    
    # 保存结果
    output_data = {
        "file": pdf_name,
        "processed_at": datetime.now().isoformat(),
        "text_length": len(text),
        "analysis": result
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    ledger["processed"].append(pdf_name)
    ledger["progress"][pdf_name] = {
        "status": "done",
        "events_count": len(result.get("events", [])),
        "timestamp": datetime.now().isoformat()
    }
    save_ledger(ledger)
    
    # 进度报告
    summary = result.get("summary", {})
    print(f"  ✅ 完成：{len(result.get('events', []))} 个事件，"
          f"内部={summary.get('total_internal', 0)}, "
          f"外部={summary.get('total_external', 0)}, "
          f"比例={summary.get('episodic_ratio', 0):.2f}")

def main():
    print("=" * 60)
    print("VSNC 批量挖掘工具 v1.0")
    print(f"工作目录：{WORKSPACE}")
    print(f"原始材料：{VSNC_RAW}")
    print(f"输出目录：{VSNC_OUTPUT}")
    print("=" * 60)
    
    # 检查 API Key
    if not DASHSCOPE_API_KEY:
        print("❌ 错误：DASHSCOPE_API_KEY 未设置")
        return
    
    # 确保输出目录存在
    VSNC_OUTPUT.mkdir(parents=True, exist_ok=True)
    
    # 加载进度
    ledger = load_ledger()
    print(f"\n📊 进度：已处理 {len(ledger.get('processed', []))} 个，失败 {len(ledger.get('failed', []))} 个")
    
    # 获取待处理文件
    pdf_files = list(VSNC_RAW.glob("*.pdf"))
    if not pdf_files:
        print("⚠️  未找到 PDF 文件")
        print(f"请将 PDF 放入：{VSNC_RAW}")
        return
    
    print(f"📁 发现 {len(pdf_files)} 个 PDF 文件")
    
    # 处理每个文件（串行，低并发）
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}]", end="")
        process_pdf(pdf_path, ledger)
        
        # 速率限制
        if i < len(pdf_files):
            delay = random.uniform(1.0, 2.0)
            print(f"  等待 {delay:.1f}s...")
            time.sleep(delay)
    
    # 最终报告
    print("\n" + "=" * 60)
    print("📊 批量处理完成")
    print(f"  总计：{len(pdf_files)} 个 PDF")
    print(f"  成功：{len(ledger.get('processed', []))} 个")
    print(f"  失败：{len(ledger.get('failed', []))} 个")
    print("=" * 60)

if __name__ == "__main__":
    main()
