---
name: dangerous_rm_rf
enabled: true
event: pre_bash
conditions:
  - field: command
    operator: regex_match
    pattern: "rm\\s+(-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*)\\s+/"
action: block
timeout: 5
---
⚠️ **危险命令检测**

检测到高危命令：`rm -rf /`

**风险**: 这会删除系统根目录文件，可能导致系统崩溃或数据丢失。

**建议**:
- 使用具体路径：`rm -rf ./specific_dir`
- 在 Docker 容器中测试
- 使用虚拟机进行测试

---
name: curl_pipe_bash
enabled: true
event: pre_bash
conditions:
  - field: command
    operator: regex_match
    pattern: "curl.*\\|.*(?:ba)?sh"
action: warn
timeout: 5
---
⚠️ **管道执行警告**

检测到管道执行命令：`curl ... | bash`

**风险**: 直接执行远程脚本可能存在安全隐患。

**建议**:
- 先下载审查：`curl -O url && cat script.sh`
- 使用包管理器安装
- 验证脚本签名

---
name: sudo_rm_rf
enabled: true
event: pre_bash
conditions:
  - field: command
    operator: regex_match
    pattern: "sudo.*rm\\s+-rf"
action: block
timeout: 5
---
🚨 **极高危命令检测**

检测到 sudo + rm -rf 组合！

**风险**: 以 root 权限删除文件，可能导致系统无法恢复。

**建议**:
- 绝对不要执行此命令
- 使用包管理器卸载软件
- 使用 Timeshift 等工具备份后操作
