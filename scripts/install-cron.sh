#!/bin/bash
# GEO Cron 安装脚本
# 用法：./install-cron.sh

set -e

WORKSPACE="/home/node/.openclaw/workspace-hulk"
SCRIPTS="$WORKSPACE/scripts"
CRON_FILE="$WORKSPACE/geo-cron"
WRAPPER="$SCRIPTS/cron-wrapper.sh"

echo "🔧 GEO Cron 安装程序"
echo "===================="
echo ""

# 确保包装脚本可执行
chmod +x "$WRAPPER"

# 创建 Cron 配置文件
cat > "$CRON_FILE" << 'EOF'
# GEO 指标追踪系统 - Cron 配置
# 时区：UTC (北京时间 = UTC + 8)
# 安装命令：crontab /home/node/.openclaw/workspace-hulk/geo-cron

SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# 环境变量
# 从系统环境变量读取，不硬编码
# 设置方法：export GITHUB_TOKEN="your_token_here"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"

# ============================================================
# 周度指标追踪 - 每周日 17:00 北京时间 (09:00 UTC)
# 重试：3 次，间隔 60 秒
# ============================================================
0 9 * * 0 /home/node/.openclaw/workspace-hulk/scripts/cron-wrapper.sh /home/node/.openclaw/workspace-hulk/scripts/track-metrics.sh 3 60

# ============================================================
# 月度汇总 - 每月 1 日 18:00 北京时间 (10:00 UTC)
# 重试：3 次，间隔 60 秒
# ============================================================
0 10 1 * * /home/node/.openclaw/workspace-hulk/scripts/cron-wrapper.sh /home/node/.openclaw/workspace-hulk/scripts/track-monthly.sh 3 60

# ============================================================
# GEO 自主迭代 - 每周三 20:00 北京时间 (12:00 UTC)
# 重试：2 次，间隔 120 秒（迭代耗时较长）
# 注意：默认注释，手动取消以启用
# ============================================================
# 0 12 * * 3 /home/node/.openclaw/workspace-hulk/scripts/cron-wrapper.sh /home/node/.openclaw/workspace-hulk/geo-loop.sh 2 120

EOF

echo "✅ Cron 配置文件已创建：$CRON_FILE"
echo ""

# 显示 Cron 配置内容
echo "📋 Cron 配置内容:"
echo "─────────────────────────────────────"
cat "$CRON_FILE"
echo "─────────────────────────────────────"
echo ""

# 安装 Cron
echo "📦 安装 Cron 到系统..."
crontab "$CRON_FILE"

# 验证安装
echo ""
echo "✅ 验证安装:"
crontab -l

echo ""
echo "===================="
echo "🎉 Cron 安装完成!"
echo ""
echo "📝 管理命令:"
echo "   - 查看：crontab -l"
echo "   - 编辑：crontab -e"
echo "   - 删除：crontab -r"
echo ""
echo "📄 日志文件:"
echo "   - metrics/cron-track-metrics.log"
echo "   - metrics/cron-track-monthly.log"
echo ""
echo "⚠️  注意:"
echo "   - 周度追踪：每周日 17:00 北京时间"
echo "   - 月度汇总：每月 1 日 18:00 北京时间"
echo "   - GEO 迭代：默认禁用，编辑 geo-cron 取消注释启用"
