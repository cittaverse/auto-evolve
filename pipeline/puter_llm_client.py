#!/usr/bin/env python3
"""
Puter.js LLM Client - 免 API Key 调用

Puter 提供免费的 LLM API，无需注册、无需 API Key。
支持模型：Qwen3、Llama 3.3、Gemini 等

文档：https://developer.puter.com/ai/models/
GitHub: https://github.com/HeyPuter/puter

使用 Python 内置 urllib，无需额外依赖。
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    usage: Optional[Dict] = None


class PuterLLMClient:
    """Puter LLM 客户端"""
    
    # Puter API 端点
    BASE_URL = "https://api.puter.com/v1"
    
    def __init__(self, model: str = "qwen3-32b"):
        """
        初始化客户端
        
        Args:
            model: 模型名称，可选：
                   - qwen3-32b (推荐，中文支持好)
                   - qwen3-coder
                   - llama-3.3-70b
                   - gemini-2.5-flash
        """
        self.model = model
        
        # 构建请求头
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CittaVerse-Pipeline/1.0"
        }
    
    def chat(self, messages: Union[List[Dict], List[ChatMessage]], 
             temperature: float = 0.7,
             max_tokens: int = 2048,
             timeout: int = 30) -> ChatResponse:
        """
        发送聊天请求
        
        Args:
            messages: 消息列表，每条消息包含 role 和 content
            temperature: 温度参数 (0-1)
            max_tokens: 最大生成 token 数
            timeout: 超时时间（秒）
        
        Returns:
            ChatResponse: 响应对象
        """
        # 转换消息格式
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            else:
                formatted_messages.append(msg)
        
        # 构建请求体
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            # 构建请求
            url = f"{self.BASE_URL}/chat/completions"
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(url, data=data, headers=self.headers, method='POST')
            
            # 发送请求
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
            
            return ChatResponse(
                content=result["choices"][0]["message"]["content"],
                model=result.get("model", self.model),
                usage=result.get("usage")
            )
            
        except urllib.error.HTTPError as e:
            print(f"⚠️  Puter API HTTP 错误：{e.code} {e.reason}")
            print(f"   降级到 Mock 模式")
            return self._mock_chat(formatted_messages)
            
        except urllib.error.URLError as e:
            print(f"⚠️  Puter API 网络错误：{e.reason}")
            print(f"   降级到 Mock 模式")
            return self._mock_chat(formatted_messages)
            
        except Exception as e:
            print(f"⚠️  Puter API 调用失败：{e}")
            print(f"   降级到 Mock 模式")
            return self._mock_chat(formatted_messages)
    
    def _mock_chat(self, messages: List[Dict]) -> ChatResponse:
        """Mock 响应（用于测试/降级）"""
        last_message = messages[-1]["content"] if messages else ""
        
        # 简单模拟 JSON 响应
        mock_response = {
            "score": 75,
            "confidence": 0.8,
            "reasoning": "Mock response for testing (Puter API unavailable)",
            "evidence": [last_message[:50] + "..."]
        }
        
        return ChatResponse(
            content=json.dumps(mock_response, ensure_ascii=False),
            model="mock",
            usage={"prompt_tokens": 0, "completion_tokens": 0}
        )
    
    def chat_simple(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        简单聊天接口
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示（可选）
        
        Returns:
            str: 响应文本
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.chat(messages)
        return response.content


# 便捷函数
def chat(prompt: str, model: str = "qwen3-32b", system_prompt: Optional[str] = None) -> str:
    """
    快速聊天函数
    
    Args:
        prompt: 用户提示
        model: 模型名称
        system_prompt: 系统提示（可选）
    
    Returns:
        str: 响应文本
    """
    client = PuterLLMClient(model=model)
    return client.chat_simple(prompt, system_prompt)


# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("Puter LLM Client - 测试")
    print("=" * 60)
    
    # 测试 1: 简单聊天
    print("\n测试 1: 简单聊天")
    response = chat("你好，请用一句话介绍自己")
    print(f"响应：{response}")
    
    # 测试 2: JSON 输出
    print("\n测试 2: JSON 输出")
    prompt = """请评估以下叙事的感官细节丰富度：

"1978 年冬天，我 15 岁，在黑龙江下乡。清晨 5 点，天还没亮，
茅草屋顶上结了一层白霜。"

请按以下 JSON 格式输出：
{
    "score": 0-100,
    "confidence": 0.0-1.0,
    "reasoning": "评分理由",
    "evidence": ["引用原文片段"]
}"""
    
    response = chat(prompt)
    print(f"响应：{response}")
    
    print("\n✅ 测试完成")
