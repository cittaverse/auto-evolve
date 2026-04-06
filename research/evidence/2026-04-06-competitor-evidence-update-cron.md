# 竞品 + 证据库更新报告 — 2026-04-06

**执行时间**: 2026-04-06 07:00 UTC  
**执行人**: Hulk 🟢  
**任务**: 12 竞品持续追踪 + 叙事疗法/MCI/数字传记证据更新  
**扫描窗口**: 2026-04-05 至 2026-04-06 (24 小时新证据)  
**数据源**: 无 (工具链完全不可用)

---

## 执行摘要

### 工具状态 (完全不可用)

| 工具 | 状态 | 错误信息 |
|------|------|----------|
| `web_search` | ❌ | Perplexity API 402 - Credits exhausted |
| `browser` | ❌ | Remote CDP for profile "sidecar" not reachable |
| `web_fetch` | ❌ | Blocked: resolves to private/internal IP (VPN fake-IP) |
| `exec` | ✅ | 仅本地文件操作可用 |

**影响**: **今日无法执行任何外部证据扫描**。所有外部数据源 (arXiv、GitHub、竞品官网) 均不可访问。

**本轮策略**: 基于 04-05 已知状态维持报告，明确标注 V0 验证等级，不伪造新发现。

---

## Bottom Line

**核心结论**: **工具链完全不可用，无法执行新扫描**。维持 04-05 状态，所有外部证据验证等级降级为 V0。

| 关键结论 | 当前状态 | 24h 新证据 | 风险等级 |
|---------|---------|-----------|---------|
| LLM 自传体记忆评分 r=0.87 | ⚠️ 未验证 | 无扫描能力 | 🟡 中 (工具故障) |
| 语音生物标志物 AD 预测>78% | ⚠️ 未验证 | 无扫描能力 | 🟡 中 (工具故障) |
| 神经符号 AI=可审计路径 | ⚠️ 未验证 | 无扫描能力 | 🟡 中 (工具故障) |
| Rememo 竞品 | ⚠️ 未验证 | 无扫描能力 | 🟡 中 (CHI 04-13 倒计时 7 天) |
| 叙事连贯性评估方法 | ⚠️ 未验证 | 无扫描能力 | 🟡 中 (工具故障) |

**总体评估**: ⚠️ **工具链故障导致证据扫描能力完全丧失**。CHI 2026 Rememo 发表进入 7 天倒计时，无法监测竞品动态。

---

## Part I: 工具链故障详情

### 1.1 web_search 故障

**错误**: Perplexity API 402 - Credits exhausted

```
This request requires more credits, or fewer max_tokens.
You requested up to 8000 tokens, but can only afford 32.
To increase, visit https://openrouter.ai/settings/credits
```

**影响**: 无法执行任何 web 搜索，包括 arXiv、PubMed、GitHub 扫描

**持续时间**: 04-06 首次出现 (04-05 仍可用但 bot-detection)

**验证等级**: V4 (动态验证 - 亲自执行报错)

---

### 1.2 browser 故障

**错误**: Remote CDP for profile "sidecar" is not reachable

```
INVALID_REQUEST: Error: Remote CDP for profile "sidecar" 
is not reachable at http://chrome-sidecar:3000/
```

**影响**: 无法访问任何网页，包括 arXiv、竞品官网

**持续时间**: 04-06 首次出现 (04-05 间歇性超时但仍可用)

**验证等级**: V4 (动态验证 - 亲自执行报错)

---

### 1.3 web_fetch 故障

**错误**: Blocked: resolves to private/internal IP address

**原因**: VPN fake-IP 模式将公网域名解析到 198.18.0.0/15

**影响**: 无法抓取任何公开网页内容

**持续时间**: 持续性问题 (04-05 已记录)

**验证等级**: V4 (动态验证 - 亲自执行报错)

---

### 1.4 exec 状态

**状态**: ✅ 可用 (仅本地文件操作)

**限制**: 不支持 system.run 执行外部命令 (host=node 限制)

**验证等级**: V4 (动态验证 - 本文件创建成功)

---

## Part II: 12 竞品追踪状态 (维持 04-05)

| # | 产品名称 | 最后追踪 | 24h 变化 | 状态 | 备注 |
|---|----------|----------|---------|------|------|
| 1 | **Rememo** | 2026-04-05 | ⚠️ 未验证 (工具故障) | 🟡 CHI 2026 倒计时 7 天 | arXiv:2602.17083v1 (02-19) |
| 2 | **Sophia** | 2025-12-20 | ⚠️ 未验证 | 🟢 稳定 | arXiv:2512.18202 |
| 3 | **LLM-MCI-detection** | 2026-03-08 | ⚠️ 未验证 | 🟢 稳定 | GitHub 项目 |
| 4 | **LLMCARE (2025)** | 2026-03-08 | ⚠️ 未验证 | 🟢 稳定 | GitHub 项目 |
| 5 | **Alzheimer-s-Detection** | 2026-03-08 | ⚠️ 未验证 | 🟢 稳定 | GitHub 项目 |
| 6 | **DiaMond** | 2026-03-08 | ⚠️ 未验证 | 🟢 稳定 | GitHub 项目 |
| 7 | **StoryFile** | TBD | ⚠️ 未验证 | 🟡 工具故障 | 官网抓取不可用 |
| 8 | **LegacyLab** | TBD | ⚠️ 未验证 | 🟡 工具故障 | 官网抓取不可用 |
| 9 | **MemoryLane** | TBD | ⚠️ 未验证 | 🟡 工具故障 | 官网抓取不可用 |
| 10 | **Eldera** | TBD | ⚠️ 未验证 | 🟡 工具故障 | 官网抓取不可用 |
| 11 | **Rendever** | TBD | ⚠️ 未验证 | 🟡 工具故障 | 官网抓取不可用 |
| 12 | **Unmind/Headspace** | TBD | ⚠️ 未验证 | 🟡 工具故障 | 官网抓取不可用 |

**说明**: 
- 所有竞品今日状态均为"未验证"(V0)
- Rememo CHI 2026 倒计时 7 天 (04-13 至 04-17)，无法监测最新状态
- 消费级竞品 (7-12) 需 browser 恢复后单独导航抓取

**验证等级**: V0 (未验证 - 工具故障)

---

## Part III: 证据库状态 (维持 04-05)

### 3.1 叙事疗法证据

**本轮扫描**: 未执行 (工具链完全不可用)

**状态**: 维持 04-05 结论 (478 篇 arXiv 叙事连贯性文献，3 篇⭐⭐新增)

**最后已知状态**:
- arXiv:2603.29661 (叙事提取) - 03-31
- arXiv:2603.28082 (多图像故事可视化) - 03-30
- arXiv:2603.20003 (XAI 叙事生成) - 03-20

**验证等级**: V0 (未验证)

---

### 3.2 MCI 干预证据

**本轮扫描**: 未执行

**状态**: 维持 04-05 (语音生物标志物、PROCESS Challenge 2025)

**验证等级**: V0 (未验证)

---

### 3.3 神经符号 AI 证据

**本轮扫描**: 未执行

**状态**: 维持 04-04 (5 篇背书论文)

**验证等级**: V0 (未验证)

---

### 3.4 多 Agent 评估证据

**本轮扫描**: 未执行

**状态**: 维持 04-04 (+ DITING)

**验证等级**: V0 (未验证)

---

### 3.5 数字传记证据

**本轮扫描**: 未执行

**状态**: 维持 04-05

**验证等级**: V0 (未验证)

---

## Part IV: 验证等级说明

| 等级 | 描述 | 今日占比 |
|------|------|---------|
| V0 | 未验证/仅推断 | **100%** (所有外部证据) |
| V1 | 单来源确认 | 0% |
| V2 | 多来源交叉确认 | 0% |
| V3 | 静态复核 | 0% |
| V4 | 动态验证/可复现 | **仅工具故障本身** |

**说明**: 今日因工具链完全不可用，所有外部证据无法验证，维持上一轮已知状态。

---

## Part V: 行动建议

### P0 - 紧急 (24 小时内)

| 行动项 | 理由 | 截止 | 负责人 |
|--------|------|------|--------|
| **openrouter.ai credits 充值** | web_search 402 错误，失去搜索能力 | 04-06 | V |
| **browser/sidecar 修复** | CDP 连接不可达，失去网页访问能力 | 04-06 | V |
| **VPN fake-IP 配置调整** | web_fetch 持续被阻断 | 04-06 | V |
| **CHI 2026 Rememo 监测预案** | 7 天后会议开始，工具故障期间可能错过关键更新 | 04-10 | Hulk (待工具恢复) |

### P1 - 高优先级 (本周内)

| 行动项 | 理由 | 截止 | 负责人 |
|--------|------|------|--------|
| **证据补扫 (全部)** | 04-06 完全未扫描，需补 48 小时证据 | 04-08 | Hulk |
| **消费级竞品 (7-12) browser 手动扫描** | 需单独导航抓取官网 | 04-08 | Hulk |
| **MCI 证据补扫** | 04-05 未完成，04-06 继续失败 | 04-08 | Hulk |

### P2 - 中优先级 (两周内)

| 行动项 | 理由 | 截止 | 负责人 |
|--------|------|------|--------|
| **GitHub 竞品 (3-6) 状态扫描** | 需 exec 或 web_search | 04-14 | Hulk |
| **神经符号 AI 扩展搜索** | "neurosymbolic"无结果，需扩展搜索词 | 04-14 | Hulk |

---

## Part VI: 结论

### 6.1 核心结论

1. ❌ **工具链完全不可用** (web_search ❌ + browser ❌ + web_fetch ❌) — 证据扫描能力丧失
2. ⚠️ **CHI 2026 Rememo 倒计时 7 天** — 无法监测竞品动态，存在信息滞后风险
3. ⚠️ **所有外部证据验证等级降级为 V0** — 维持 04-05 已知状态，未确认是否有新证据
4. ✅ **exec 本地文件操作可用** — 可创建报告，但无法执行外部扫描

### 6.2 风险态势

| 风险类型 | 等级 | 说明 |
|---------|------|------|
| **工具链故障** | 🔴 高 | 完全失去外部证据扫描能力 |
| **CHI 2026 Rememo 发表** | 🟡 中 | 7 天后会议开始，无法监测 |
| **证据滞后** | 🟡 中 | 可能错过 24-48 小时新论文 |
| **技术迭代风险** | 🟡 中 | 无法确认是否有突破性新研究 |
| **竞品动态风险** | 🟡 中 | 消费级竞品 (7-12) 验证不完全 |

### 6.3 建议

1. **工具修复最高优先级**: 
   - openrouter.ai credits 充值 (web_search 恢复)
   - browser/sidecar CDP 连接修复
   - VPN fake-IP 配置调整 (web_fetch 恢复)
   
2. **CHI 2026 应急预案**: 工具恢复后立即优先扫描 Rememo 状态，准备论文解读框架

3. **证据补扫计划**: 工具恢复后 48 小时内完成 04-05 至 04-07 证据补扫

4. **降级产出说明**: 本报告中所有外部证据均为 V0 (未验证)，不可作为决策依据

---

## 更新日志

| 日期 | 更新内容 | 验证等级 | 新论文数 | 工具状态 |
|------|----------|----------|----------|---------|
| **2026-04-06** | **工具链完全故障，无扫描** | **V0** | **0 篇** | ❌❌❌ (全灭) |
| 2026-04-05 | arXiv 扫描 (browser ⚠️ 超时) | V1/V3 | 3 篇 (⭐⭐) | ⚠️ (arXiv only, 不稳定) |
| 2026-04-04 | arXiv 扫描 (browser 恢复) | V1 | 11 篇 | ✅ (arXiv only) |
| 2026-04-03 | 工具链故障，无法扫描 | V0 | 0 篇 | ❌❌❌❌❌ |
| 2026-04-02 | 48 小时快速更新 | V1 | 5 篇 | ✅ (arXiv only) |

---

*Hulk 🟢 — 密度即价值*  
*数据截至 2026-04-06 07:00 UTC*  
*工具状态：web_search ❌ (402 credits) | browser ❌ (CDP unreachable) | web_fetch ❌ (fake-IP) | exec ✅ (local only)*  
*本轮新增：**0 篇新论文** (工具故障)*  
*CHI 2026 Rememo 倒计时：**7 天** (04-13 至 04-17)*  
*⚠️ 警告：本报告所有外部证据验证等级为 V0 (未验证)，维持 04-05 已知状态*

---

## 交付说明

**产出文件**: `research/evidence/2026-04-06-competitor-evidence-update-cron.md`

**文件位置**: `/Users/moondy/.openclaw/workspace-hulk/research/evidence/`

**验证**: V4 (动态验证 - 文件已创建成功)

**下一步**: 
1. **工具修复 (V)**: openrouter.ai credits、browser CDP、VPN fake-IP
2. **证据补扫 (Hulk)**: 工具恢复后 48 小时内完成 04-05 至 04-07 证据补扫
3. **CHI 2026 监测 (Hulk)**: 工具恢复后优先扫描 Rememo 状态

---

## 附录：工具故障技术细节

### A.1 web_search 402 错误

**请求**: Perplexity API via OpenRouter  
**错误码**: 402 Payment Required  
**错误信息**: "This request requires more credits, or fewer max_tokens. You requested up to 8000 tokens, but can only afford 32."

**解决方案**: 
- 选项 1: openrouter.ai 充值 (推荐)
- 选项 2: 降低 max_tokens 参数 (可能影响结果质量)
- 选项 3: 切换到其他搜索后端 (如配置了 SERPER_API_KEY)

---

### A.2 browser CDP 错误

**错误**: `INVALID_REQUEST: Error: Remote CDP for profile "sidecar" is not reachable at http://chrome-sidecar:3000/`

**可能原因**:
- sidecar 服务未启动
- 端口 3000 被占用或防火墙阻断
- Docker 网络配置问题
- Chrome 浏览器未运行

**解决方案**:
- 检查 sidecar 服务状态
- 重启 browser 服务
- 检查 Docker 网络配置
- 验证 Chrome 浏览器运行状态

---

### A.3 web_fetch fake-IP 阻断

**错误**: `Blocked: resolves to private/internal/special-use IP address`

**原因**: VPN (Clash) fake-IP 模式将公网域名解析到 198.18.0.0/15 (RFC 2544 benchmark 地址)

**解决方案**:
- 选项 1: 临时关闭 VPN fake-IP 模式
- 选项 2: 配置 web_fetch 走直连 (不经过 VPN)
- 选项 3: 使用 browser 替代 web_fetch (browser 不受此限制)

---

*Hulk 🟢 — 等待工具恢复后继续证据扫描*
