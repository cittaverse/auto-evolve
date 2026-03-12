# GEO 自动化追踪配置

> 配置说明：设置自动化的 GEO 指标追踪任务

---

## 📋 Cron 配置

### 每周追踪 (推荐)

```cron
# 每周日 09:00 UTC (17:00 北京时间) 执行 GEO 指标追踪
0 9 * * 0 cd /home/node/.openclaw/workspace-hulk && ./scripts/track-metrics.sh weekly >> /home/node/.openclaw/workspace-hulk/metrics/cron.log 2>&1
```

### 每月汇总

```cron
# 每月 1 日 10:00 UTC 执行月度汇总
0 10 1 * * cd /home/node/.openclaw/workspace-hulk && ./scripts/track-metrics.sh monthly >> /home/node/.openclaw/workspace-hulk/metrics/cron.log 2>&1
```

### GitHub Stars 检查 (可选)

```cron
# 每天 08:00 UTC 抓取 GitHub 统计 (需 API Token)
0 8 * * * cd /home/node/.openclaw/workspace-hulk && ./scripts/fetch-github-stats.sh cittaverse/pipeline >> /home/node/.openclaw/workspace-hulk/metrics/github-stats.log 2>&1
```

---

## 🔧 环境变量配置

### GitHub API Token (可选，但推荐)

获取方式：https://github.com/settings/tokens

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 或添加到 crontab 环境变量
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

**权限要求**:
- ✅ `public_repo` - 读取公开仓库信息
- ✅ `read:org` - 读取组织信息 (可选)

---

## 📁 文件结构

```
/home/node/.openclaw/workspace-hulk/
├── scripts/
│   ├── track-metrics.sh        # 主追踪脚本
│   ├── fetch-github-stats.sh   # GitHub API 抓取
│   └── ...                     # GEO 迭代脚本
├── metrics/
│   ├── DASHBOARD.md            # 指标看板 (手动维护)
│   ├── summary-YYYY-MM-DD.md   # 每周追踪报告 (自动生成)
│   ├── monthly-YYYY-MM.md      # 月度汇总 (自动生成)
│   └── cron.log                # Cron 执行日志
└── memory/
    └── YYYY-MM-DD-geo-iteration-N.md  # 迭代学习记录
```

---

## 🚀 快速启动

### 1. 测试脚本

```bash
cd /home/node/.openclaw/workspace-hulk
./scripts/track-metrics.sh weekly
```

### 2. 配置 Cron

```bash
# 编辑 crontab
crontab -e

# 添加每周追踪任务
0 9 * * 0 cd /home/node/.openclaw/workspace-hulk && ./scripts/track-metrics.sh weekly >> /home/node/.openclaw/workspace-hulk/metrics/cron.log 2>&1

# 保存后验证
crontab -l
```

### 3. 检查 Cron 状态

```bash
# 查看 cron 服务状态
systemctl status cron  # Linux
# 或
sudo service cron status

# 查看 cron 日志
grep CRON /var/log/syslog | tail -20
```

---

## 📊 指标解释

### GitHub 指标

| 指标 | 说明 | 重要性 |
|------|------|--------|
| Stars | 仓库收藏数，反映受欢迎程度 | ⭐⭐⭐ |
| Forks | 仓库 Fork 数，反映开发者兴趣 | ⭐⭐ |
| Views | 页面浏览量 (14 天) | ⭐⭐⭐ |
| Clones | 仓库克隆数 (14 天) | ⭐⭐ |

### 搜索引擎指标

| 指标 | 说明 | 重要性 |
|------|------|--------|
| 索引页面数 | Google 收录的页面数量 | ⭐⭐⭐ |
| 关键词排名 | 目标关键词的搜索排名 | ⭐⭐⭐ |
| 外部引用 | 其他网站/论文的引用数 | ⭐⭐ |

### 内容产出指标

| 指标 | 说明 | 重要性 |
|------|------|--------|
| Markdown 文件数 | 文档数量 | ⭐⭐ |
| 文档总字数 | 内容深度 | ⭐⭐ |
| 迭代轮次 | GEO 迭代执行次数 | ⭐⭐⭐ |

---

## ⚠️ 故障排查

### Cron 不执行

```bash
# 检查 cron 服务
sudo service cron status

# 检查 crontab 语法
crontab -l

# 手动执行脚本测试
./scripts/track-metrics.sh weekly
```

### GitHub API 限流

```
错误：403 rate limit exceeded

解决:
1. 设置 GITHUB_TOKEN 环境变量
2. 无 token 时限制 60 次/小时
3. 有 token 时限制 5000 次/小时
```

### 脚本权限问题

```bash
# 确保脚本可执行
chmod +x ./scripts/track-metrics.sh
chmod +x ./scripts/fetch-github-stats.sh
```

---

## 📈 进阶配置

### Slack/Discord 通知 (可选)

```bash
# 在 track-metrics.sh 末尾添加
if [ "$STARS增长" -gt 10 ]; then
    curl -X POST -H 'Content-type: application/json' \
        --data '{"text":"🎉 GitHub Stars 本周增长超过 10!"}' \
        $WEBHOOK_URL
fi
```

### 自动生成图表 (可选)

```bash
# 使用 gnuplot 或 Python matplotlib
# 将 metrics/summary-*.md 数据可视化
```

---

*配置文档 v1.0 | Created: 2026-03-09 | Owner: Hulk 🟢*
