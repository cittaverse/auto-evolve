# GEO 自主迭代协议

> Generative Engine Optimization 自主迭代闭环

**版本**: 0.1  
**灵感来源**: Karpathy auto-research  
**目标**: 让 GitHub 仓库自主优化，48 小时内被 AI 引擎索引并引用

---

## 核心循环

```
研究 (Research) → 规划 (Plan) → 执行 (Execute) → 验证 (Verify) → 学习 (Learn)
      ↑                                                                                │
      └────────────────────────────────────────────────────────────────────────────────┘
```

**迭代周期**: 30 分钟/轮  
**每日目标**: 3-4 轮完整迭代  
**成功指标**: 7 天内 Google/Bing 索引，14 天内 AI 引擎引用

---

## 阶段 1: 研究 (Research) - 5 分钟

### 输入
- 当前仓库状态
- 竞品仓库分析
- 搜索引擎索引状态

### 任务

#### 1.1 竞品分析
```bash
# 检查竞品仓库更新
curl -s https://api.github.com/repos/{competitor}/contents | jq
```

**关注点**:
- 新增了什么文件？
- README 更新了什么内容？
- Stars/ Forks 增长趋势？

#### 1.2 索引检查
```bash
# Google 索引检查
curl "https://www.google.com/search?q=site:github.com/cittaverse"

# Bing 索引检查
curl "https://www.bing.com/search?q=site:github.com/cittaverse"
```

**指标**:
- 索引页面数
- 排名位置
- 收录内容类型

#### 1.3 关键词研究
```bash
# Serper API 搜索量检查
curl -X POST "https://google.serper.dev/search" \
  -H "X-API-KEY: $SERPER_API_KEY" \
  -d '{"q": "narrative assessment elderly AI"}'
```

**输出**: 高价值关键词列表

### 输出
- 竞品差距分析报告
- 当前索引状态
- 关键词机会列表

---

## 阶段 2: 规划 (Plan) - 5 分钟

### 输入
- 研究报告
- 当前仓库内容
- 历史迭代记录

### 任务

#### 2.1 差距识别
| 维度 | 竞品有 | 我们有 | 优先级 |
|------|--------|--------|--------|
| 示例代码 | ✅ | ❌ | P0 |
| CI/CD | ✅ | ✅ | - |
| 文档站点 | ✅ | ❌ | P1 |
| 社区规范 | ✅ | ✅ | - |

#### 2.2 迭代规划
```yaml
iteration_001:
  target: pipeline
  actions:
    - file: examples/basic.py
      type: create
      priority: P0
    - file: README.md
      type: update
      section: "Quick Start"
      priority: P0
  
iteration_002:
  target: core
  actions:
    - file: docs/github-pages-setup.md
      type: create
      priority: P1
```

#### 2.3 成功标准
- 文件创建/更新完成
- CI 测试通过
- 无 lint 错误

### 输出
- 迭代计划 (YAML 格式)
- 优先级排序
- 成功标准定义

---

## 阶段 3: 执行 (Execute) - 15 分钟

### 输入
- 迭代计划
- 仓库访问权限

### 任务

#### 3.1 内容生成
```python
# 伪代码示例
def generate_content(plan):
    for action in plan['actions']:
        if action['type'] == 'create':
            content = llm_generate(
                prompt=f"Create {action['file']} for GEO optimization",
                context=get_repository_context()
            )
            write_file(action['file'], content)
        
        elif action['type'] == 'update':
            old_content = read_file(action['file'])
            new_section = llm_generate(
                prompt=f"Update {action['section']} in {action['file']}",
                context=old_content
            )
            update_file(action['file'], new_section)
```

#### 3.2 质量检查
```bash
# 代码检查
flake8 src/
mypy src/

# 链接检查
markdown-link-check README.md

# 拼写检查
cspell .
```

#### 3.3 提交推送
```bash
git add -A
git commit -m "GEO iteration #001: [description]"
git push origin main
```

### 输出
- 新文件/更新内容
- CI 测试结果
- Git commit hash

---

## 阶段 4: 验证 (Verify) - 3 分钟

### 输入
- Git commit 记录
- GitHub Actions 日志

### 任务

#### 4.1 CI 验证
```bash
# 检查 GitHub Actions 状态
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/cittaverse/pipeline/actions/runs
```

**通过标准**:
- ✅ 所有测试通过
- ✅ 无 lint 错误
- ✅ 构建成功

#### 4.2 内容验证
```python
# 检查文件是否存在
assert file_exists("examples/basic.py")

# 检查 README 更新
assert "Quick Start" in read_file("README.md")

# 检查链接有效性
for link in extract_links("README.md"):
    assert check_link(link) == 200
```

#### 4.3 索引追踪
```python
# 记录当前状态
log_metrics({
    "iteration": 1,
    "timestamp": "2026-03-08T18:30:00Z",
    "files_changed": 2,
    "lines_added": 150,
    "ci_status": "passed"
})
```

### 输出
- 验证报告
- 指标日志
- 问题列表 (如有)

---

## 阶段 5: 学习 (Learn) - 2 分钟

### 输入
- 验证报告
- 历史迭代记录

### 任务

#### 5.1 效果评估
| 指标 | 目标 | 实际 | 状态 |
|------|------|------|------|
| 文件创建 | 2 | 2 | ✅ |
| CI 通过 | 100% | 100% | ✅ |
| 时间控制 | <30min | 28min | ✅ |

#### 5.2 经验沉淀
```markdown
## Iteration #001 Learnings

### 成功
- 示例代码生成质量高
- CI 配置正确

### 问题
- 链接检查发现 2 个失效链接 → 已修复
- 生成内容略长 → 下次限制 500 字以内

### 改进
- 添加链接预检查步骤
- 优化 prompt 长度控制
```

#### 5.3 策略调整
```yaml
# 更新 GEO_PROTOCOL.md
next_iteration:
  max_file_size: 500  # 新增限制
  pre_check_links: true  # 新增步骤
  keep_prompt_concise: true  # 优化点
```

### 输出
- 学习日志
- 策略更新
- 下一轮优化点

---

## 自动化脚本

### 主循环脚本

```bash
#!/bin/bash
# geo-loop.sh - GEO 自主迭代主循环

set -e

ITERATION=${1:-1}
echo "🚀 Starting GEO iteration #$ITERATION"

# Phase 1: Research
echo "📚 Phase 1: Research (5 min)"
./scripts/research.sh

# Phase 2: Plan
echo "📋 Phase 2: Plan (5 min)"
./scripts/plan.sh

# Phase 3: Execute
echo "⚙️ Phase 3: Execute (15 min)"
./scripts/execute.sh

# Phase 4: Verify
echo "✅ Phase 4: Verify (3 min)"
./scripts/verify.sh

# Phase 5: Learn
echo "🧠 Phase 5: Learn (2 min)"
./scripts/learn.sh

echo "✅ Iteration #$ITERATION complete"
echo "📊 Results logged to iteration_logs/"
```

### 调度器

```yaml
# .github/workflows/geo-loop.yml
name: GEO Loop

on:
  schedule:
    - cron: '0 */6 * * *'  # 每 6 小时一次
  workflow_dispatch:

jobs:
  geo-iteration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run GEO Loop
        run: |
          ./geo-loop.sh ${{ github.run_number }}
        
      - name: Commit Results
        run: |
          git config user.name "GEO Bot"
          git config user.email "geo-bot@cittaverse.com"
          git add -A
          git commit -m "GEO iteration #${{ github.run_number }}" || true
          git push
```

---

## 指标追踪

### 核心指标

| 指标 | 目标 | 测量频率 |
|------|------|----------|
| 迭代完成率 | >90% | 每轮 |
| 平均迭代时间 | <30min | 每轮 |
| CI 通过率 | 100% | 每轮 |
| 索引页面增长 | +5 页/轮 | 每日 |
| GitHub Stars 增长 | +10/周 | 每周 |

### 日志格式

```json
{
  "iteration": 1,
  "timestamp": "2026-03-08T18:30:00Z",
  "duration_seconds": 1680,
  "phase_results": {
    "research": {"status": "success", "findings": 3},
    "plan": {"status": "success", "actions": 2},
    "execute": {"status": "success", "files_changed": 2},
    "verify": {"status": "success", "ci_passed": true},
    "learn": {"status": "success", "improvements": 1}
  },
  "metrics": {
    "lines_added": 150,
    "lines_deleted": 20,
    "files_created": 1,
    "files_updated": 1
  }
}
```

---

## 风险控制

### 安全边界

| 风险 | 控制措施 |
|------|----------|
| 无限循环 | 最大迭代次数限制 (10 轮/天) |
| 内容质量下降 | 人工审核开关 |
| API 配额超限 | 速率限制 + 缓存 |
| Git 冲突 | 自动 rebase + 失败回滚 |

### 人工介入点

```
🔴 必须人工：
- 首次迭代前
- 连续 3 次 CI 失败
- 检测到异常内容

🟡 建议人工：
- 每日迭代总结
- 策略重大调整
- 新仓库加入

🟢 完全自动：
- 常规迭代
- 指标记录
- 日志归档
```

---

## 快速开始

### 第一次迭代

```bash
# 1. 克隆仓库
git clone https://github.com/cittaverse/pipeline.git
cd pipeline

# 2. 配置环境
export GITHUB_TOKEN=ghp_xxx
export SERPER_API_KEY=xxx

# 3. 运行第一轮
./geo-loop.sh 1

# 4. 查看结果
cat iteration_logs/iteration_001.json
```

### 持续运行

```bash
# 后台运行 (每 6 小时一轮)
while true; do
  ./geo-loop.sh $((++ITERATION))
  sleep 21600  # 6 小时
done
```

---

## 参考资源

- [Karpathy auto-research](https://github.com/karpathy/autoresearch)
- [GEO Best Practices](https://llmrefs.com/generative-engine-optimization)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

*Version: 0.1 | Last updated: 2026-03-08*

*Inspired by Karpathy's auto-research design*
