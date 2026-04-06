#!/usr/bin/env python3
"""Pre-File-Write Hook — 文件写入前检查"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from hook_system import HulkHookEngine


def main():
    try:
        input_data = json.load(sys.stdin)
        
        # 示例输入:
        # {
        #   "hook_event": "pre_file_write",
        #   "tool_name": "Write",
        #   "file_path": ".env",
        #   "content": "API_KEY=secret"
        # }
        
        engine = HulkHookEngine()
        result = engine.evaluate("pre_file_write", input_data)
        
        if result.get("decision") == "block":
            print(json.dumps({
                "decision": "deny",
                "reason": result.get("reason", ""),
                "systemMessage": result.get("reason", "")
            }))
        elif result.get("systemMessage"):
            print(json.dumps({"systemMessage": result["systemMessage"]}))
        else:
            print(json.dumps({}))
        
        sys.exit(0)
    
    except Exception as e:
        print(json.dumps({"systemMessage": f"⚠️ Hook 错误：{str(e)}"}))
        sys.exit(0)


if __name__ == "__main__":
    main()
