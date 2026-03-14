#!/usr/bin/env python3
import subprocess
import json
import os
from pathlib import Path

pdf_path = Path("/home/node/.openclaw/workspace-hulk/VSNC/原始材料/2025_LLM_Autobiographical_Scoring.pdf")
print(f"PDF 路径：{pdf_path}")
print(f"文件存在：{pdf_path.exists()}")

# 提取文本
result = subprocess.run(['pdftotext', '-layout', str(pdf_path), '-'], capture_output=True, text=True, timeout=60)
text = result.stdout.strip()
print(f"文本长度：{len(text)}")

if len(text) < 50:
    print("文本过短！")
else:
    print("文本长度正常，截取前 500 字...")
    text = text[:8000]
    
    # 调用 API
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    print(f"API Key: {api_key[:15] if api_key else 'None'}...")
    
    import urllib.request
    url = "https://coding.dashscope.aliyuncs.com/v1/chat/completions"
    payload = {
        "model": "qwen3.5-plus",
        "messages": [{"role": "user", "content": "请总结以下学术论文的主要内容，输出 JSON 格式：{\"summary\": \"...\", \"keywords\": []}\n\n" + text[:2000]}],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    
    print("调用 API...")
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("API 响应成功！")
            print(result['choices'][0]['message']['content'][:500])
    except Exception as e:
        print(f"API 错误：{e}")
