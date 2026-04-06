#!/usr/bin/env python3
"""Pre-Bash Hook — 命令执行前安全检查"""

import json
import sys
import os

# 导入 Hook 引擎
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hook_system import HulkHookEngine


def main():
    try:
        # 从 stdin 读取输入
        input_data = json.load(sys.stdin)
        
        # 示例输入:
        # {
        #   "hook_event": "pre_bash",
        #   "tool_name": "Bash",
        #   "command": "rm -rf /tmp/*",
        #   "cwd": "/home/user/project"
        # }
        
        engine = HulkHookEngine()
        result = engine.evaluate("pre_bash", input_data)
        
        # 输出结果
        if result.get("decision") == "block":
            print(json.dumps({
                "decision": "deny",
                "reason": result.get("reason", "Blocked by hook"),
                "systemMessage": result.get("reason", "")
            }))
        elif result.get("systemMessage"):
            print(json.dumps({
                "systemMessage": result["systemMessage"]
            }))
        else:
            print(json.dumps({}))  # 允许执行
        
        sys.exit(0)
    
    except json.JSONDecodeError:
        print(json.dumps({
            "systemMessage": "⚠️ Hook 输入格式错误"
        }))
        sys.exit(0)
    except Exception as e:
        # 错误时允许执行
        print(json.dumps({
            "systemMessage": f"⚠️ Hook 错误：{str(e)}"
        }))
        sys.exit(0)


if __name__ == "__main__":
    main()
