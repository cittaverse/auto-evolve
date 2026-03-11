# Auto-Evolve Framework

> **让每个 AI Agent 都具备自我进化能力**  
> **A framework for AI agent self-evolution**

[![GitHub stars](https://img.shields.io/github/stars/cittaverse/auto-evolve)](https://github.com/cittaverse/auto-evolve/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/cittaverse/auto-evolve)](https://github.com/cittaverse/auto-evolve/network)
[![License](https://img.shields.io/github/license/cittaverse/auto-evolve)](https://github.com/cittaverse/auto-evolve/blob/main/LICENSE)

---

## 🎯 核心理念

**传统 AI Agent**：需要人工设定任务，无法自主发现优化机会

**Auto-Evolve Agent**：自主决定"做什么→怎么做→验证效果→沉淀经验"

---

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/cittaverse/auto-evolve
cd auto-evolve
pip install -r requirements.txt
```

### 配置

```yaml
# config/my_project.yaml
domain: github
project: your_username/your_repo
goals:
  - metric: stars
    baseline: 0
    target: 50
    timeframe_days: 30

auto_cron: true
```

### 运行

```bash
python -m auto_evolve --config config/my_project.yaml
```

---

## 📊 实战验证：GEO 项目

**GEO (GitHub Engine Optimization)** 是 Auto-Evolve 的第一个应用场景。

### 5 轮迭代成果

| 轮次 | 主题 | 核心产出 | 耗时 |
|------|------|----------|------|
| #1 | 基础能力 + 中文资源 | demo + 10 资源 + FAQ | ~3min |
| #2 | 代码质量 + 学术资源 | tests+CI + 6 期刊 + 市场趋势 | ~2min |
| #3 | SEO 优化 + 外部引用 | SEO README + Scholar 链接 + Pages | ~2min |
| #4 | 社区建设 + 效果展示 | 使用指南 + 贡献示例 + 仪表板 | ~42min |
| #5 | 外部引流 + 文章发布 | Topics + 导航站 + 发布包 | ~2min |

**累计**：
- 15 次 Git commits
- 15 个新增文件
- ~100,000+ 字文档
- 100% 迭代成功率

### 相关仓库

- **GEO 案例**: https://github.com/cittaverse/pipeline
- **资源列表**: https://github.com/cittaverse/awesome-digital-therapy
- **核心文档**: https://github.com/cittaverse/core
- **指标仪表板**: https://github.com/cittaverse/core/blob/main/docs/traction.md

---

## 🧠 核心架构

```
┌─────────────────────────────────────────┐
│         Auto-Evolve Core                │
├─────────────────────────────────────────┤
│  Goal → Strategy → Execute → Verify    │
│   ↑                              │     │
│   │←─────── Learn ←──────────────┘     │
│   │                                     │
│   └──── Knowledge Base ←───────────────┘│
└─────────────────────────────────────────┘
```

### 六大模块

| 模块 | 职责 | 关键方法 |
|------|------|----------|
| Goal Setter | 定义可量化目标 | `define_goals()`, `validate_goal()` |
| Strategy Planner | 选择最优策略 | `generate_strategies()`, `select_best()` |
| Execute Engine | 执行动作 | `execute()`, `retry()`, `rollback()` |
| Verify Checker | 验证结果 | `verify()`, `generate_report()` |
| Learn Module | 提取经验 | `extract_lessons()`, `suggest_improvements()` |
| Knowledge Base | 存储检索 | `store()`, `retrieve()` |

---

## 📐 应用场景

| 场景 | 目标指标 | 状态 |
|------|----------|------|
| **GitHub 优化** | Stars/Views | ✅ 已验证 (GEO) |
| 内容 SEO | 搜索排名/流量 | 📋 设计中 |
| 代码质量 | 测试覆盖率 | 📋 设计中 |
| 文档完善 | API 覆盖率 | 📋 设计中 |

---

## 📚 文档

- [技术文章](docs/articles/auto-evolve-framework-article.md) - 完整框架介绍
- [GEO 案例](docs/GEO_ITERATION_SUMMARY.md) - 5 轮迭代详情
- [发布指南](docs/articles/README_PUBLISHING.md) - 多平台发布流程

---

## 🗺️ 路线图

| Phase | 里程碑 | 状态 | 预计完成 |
|-------|--------|------|----------|
| Phase 1 | GEO 验证完成 | ✅ 完成 | 2026-03-10 |
| Phase 2 | 框架原型发布 | 🔄 进行中 | 2026-03-24 |
| Phase 3 | 多场景验证 | 📋 待开始 | 2026-04-21 |
| Phase 4 | agenthub 提交 | 📋 待开始 | 2026-05-19 |

---

## 🤝 社区参与

### 参与方式

- ⭐ **Star 仓库** - 支持项目
- 🐛 **报告问题** - 发现 Bug
- 💡 **分享场景** - 你的应用案例
- 🔧 **贡献代码** - PR 欢迎

### 联系方式

| 渠道 | 链接 |
|------|------|
| GitHub Issues | https://github.com/cittaverse/auto-evolve/issues |
| 知乎 | [@袭知郎](https://www.zhihu.com/people/xi-zhi-lang-44) |
| 邮箱 | cittaverse@gmail.com |

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- **灵感来源**: [agenthub](https://github.com/karpathy/agenthub) by @karpathy
- **核心思想**: 让 AI Agent 从"执行命令的工具"变成"一起进化的伙伴"

---

**最后更新**: 2026-03-11  
**版本**: v0.1

---

*如果这个项目对你有帮助，欢迎 Star 支持！🌟*
