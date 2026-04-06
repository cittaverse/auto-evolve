# Errors & Lessons

## 2026-03-23 — API Key 泄漏扫描遗漏

**事件**: V 要求检查 GitHub 公开项目是否有 API Key 泄漏，我报告"未发现"，但实际 `data/clawhub-500/API-KEYS.md` 包含 Tavily + 阿里云百炼真实密钥。

**原因**:
1. 只扫了 `github-repos/` 目录，遗漏了 `data/` 目录下的仓库
2. 没有先用 `find . -name ".git" -type d` 列出所有仓库再逐一扫描
3. 没有做文件名级别的检查（`*key*` `*secret*` `*token*`）

**正确做法**:
1. 先 `find` 所有 `.git` 目录 → 确定完整仓库列表
2. 文件名扫描：`find . -iname "*key*" -o -iname "*secret*" -o -iname "*token*" -o -iname "*credential*" -o -iname "*.env"`
3. 内容扫描：regex 匹配常见密钥格式
4. Git 历史扫描：`git log -p --all | grep` 常见密钥模式
5. 不要假设目录结构，要穷举

**严重性**: 高 — 真实密钥在公网暴露，需要立即轮换
