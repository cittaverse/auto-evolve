# Metrics Directory - GEO 指标追踪

> 索引：所有 GEO 指标相关报告和配置

---

## 📊 报告文件

| 文件 | 类型 | 日期 | 说明 |
|------|------|------|------|
| [DASHBOARD.md](./DASHBOARD.md) | 看板 | 持续更新 | 实时指标看板 (手动维护) |
| [baseline-2026-03-09.md](./baseline-2026-03-09.md) | 基线 | 2026-03-09 | 初始基线报告 |
| [summary-2026-03-09.md](./summary-2026-03-09.md) | 周度 | 2026-03-09 | 首次周度追踪 |
| [SETUP.md](./SETUP.md) | 配置 | 2026-03-09 | 自动化配置指南 |

---

## 📁 文件命名规范

- `baseline-YYYY-MM-DD.md` - 基线报告 (仅一次)
- `summary-YYYY-MM-DD.md` - 周度追踪 (每周日)
- `monthly-YYYY-MM.md` - 月度汇总 (每月 1 日)
- `cron.log` - Cron 执行日志

---

## 🤖 自动化

**Cron 配置**:
```bash
# 每周日 09:00 UTC (17:00 北京时间)
0 9 * * 0 cd /home/node/.openclaw/workspace-hulk && ./scripts/track-metrics.sh weekly
```

**手动执行**:
```bash
./scripts/track-metrics.sh weekly   # 周度追踪
./scripts/track-metrics.sh monthly  # 月度汇总
./scripts/fetch-github-stats.sh cittaverse/pipeline  # GitHub 统计
```

---

## 📈 核心指标

| 类别 | 指标 | 频率 |
|------|------|------|
| GitHub | Stars/Forks/Views/Clones | 周度 |
| 搜索引擎 | Google 索引/关键词排名 | 周度 |
| 内容 | Markdown 文件数/字数 | 周度 |
| 迭代 | 已完成轮次/成功率 | 每次迭代 |

---

## 🔗 相关文档

- [GEO_PROTOCOL.md](../GEO_PROTOCOL.md) - 迭代协议
- [memory/geo-iteration-*.md](../memory/) - 迭代学习记录
- [shared/BULLETIN.md](../shared/BULLETIN.md) - 跨 Agent 公告

---

*Directory Index v1.0 | Created: 2026-03-09*
