# CittaVerse 一念万相 — GEO/SEO 诊断与优化方案

**文档版本**: v1.0  
**生成日期**: 2026-03-08  
**执行负责人**: Hulk 🟢  
**状态**: 待执行

---

## 一、现状诊断

### 1.1 核心问题

| 检查项 | 状态 | 详情 |
|--------|------|------|
| **Google 索引** | ❌ 缺失 | `site:cittaverse.com` 搜索结果为 0 |
| **Bing 索引** | ❌ 缺失 | AI 引擎主要依赖 Bing 索引 |
| **Schema Markup** | ❌ 缺失 | 无 JSON-LD 结构化数据 |
| **Sitemap.xml** | ❌ 缺失 | 搜索引擎无法发现页面 |
| **Robots.txt** | ⚠️ 异常 | 返回 HTML 而非标准 robots 协议 |
| **AI 可见性** | ❌ 零 | ChatGPT/Perplexity/Google AI Overviews 均无引用 |

### 1.2 问题根因

**官网内容质量高，但完全未被搜索引擎抓取** → AI 引擎无法引用不存在的内容。

当前官网优势：
- ✅ 内容结构清晰（科学原理/产品/案例/定价）
- ✅ 有临床数据支撑（23% 认知提升、2000+ 案例）
- ✅ 权威背书（北京大学老年医学中心、JMIR Aging、PubMed）

当前致命短板：
- ❌ 技术 SEO 零基础
- ❌ 外部提及为零
- ❌ 无结构化数据供 AI 提取

---

## 二、GEO 优化方案

### 2.1 第一阶段：技术基础设施（第 1 周）

#### 2.1.1 提交搜索引擎索引

**必须完成**：

| 平台 | URL | 优先级 |
|------|-----|--------|
| Google Search Console | https://search.google.com/search-console | 🔴 高 |
| Bing Webmaster Tools | https://www.bing.com/webmasters | 🔴 高（AI 引擎依赖） |

**操作步骤**：
1. 用 Google 账号登录 Search Console
2. 添加财产 `cittaverse.com`
3. 验证所有权（DNS 记录或 HTML 文件上传）
4. 提交 sitemap.xml（见下文）

---

#### 2.1.2 创建 Sitemap.xml

在网站根目录创建 `/sitemap.xml`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://www.cittaverse.com/</loc>
    <lastmod>2026-03-08</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://www.cittaverse.com/#science</loc>
    <lastmod>2026-03-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://www.cittaverse.com/#product</loc>
    <lastmod>2026-03-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  <url>
    <loc>https://www.cittaverse.com/#cases</loc>
    <lastmod>2026-03-08</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
  <url>
    <loc>https://www.cittaverse.com/#pricing</loc>
    <lastmod>2026-03-08</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>
```

---

#### 2.1.3 部署 Schema Markup

在 `<head>` 标签内添加以下 JSON-LD 代码：

**Organization Schema**（组织信息）：
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "CittaVerse 一念万相",
  "url": "https://www.cittaverse.com",
  "description": "数字化生命回顾疗法，AI 辅助认知训练方案，经临床验证的认知干预产品",
  "foundingDate": "2024",
  "areaServed": "CN",
  "knowsAbout": ["数字疗法", "认知训练", "生命回顾疗法", "AI 健康", "MCI 干预", "老年认知衰退"],
  "sameAs": [
    "https://www.zhihu.com/org/cittaverse",
    "https://mp.weixin.qq.com"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "contactType": "customer service",
    "availableLanguage": "Chinese"
  }
}
</script>
```

**MedicalEntity Schema**（医疗实体）：
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "MedicalTherapy",
  "name": "数字化生命回顾疗法",
  "description": "基于生命回顾疗法（Reminiscence Therapy）的 AI 辅助认知训练方案",
  "indication": "轻度认知障碍（MCI）早期筛查与干预、老年记忆衰退延缓",
  "clinicalPharmacology": "通过 AI 深度引导对谈持续激活大脑突触，利用长时程增强（LTP）机制增加认知储备",
  "study": [
    {
      "@type": "MedicalStudy",
      "name": "CittaVerse 认知干预临床研究",
      "affiliation": {
        "@type": "MedicalOrganization",
        "name": "北京大学老年医学中心"
      },
      "studySubject": "认知评分平均提升 23%"
    }
  ]
}
</script>
```

**FAQPage Schema**（常见问题）：
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "什么是生命回顾疗法？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "生命回顾疗法（Reminiscence Therapy）是一种通过引导个体回忆过去经历来改善认知功能和情绪状态的心理干预方法。CittaVerse 将其与 AI 技术结合，实现每日可执行的家庭化认知训练。"
      }
    },
    {
      "@type": "Question",
      "name": "CittaVerse 适合哪些人群？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "主要面向 60 岁以上有轻度认知衰退迹象的长者，以及希望预防认知衰退的健康老年人群。也适用于 MCI（轻度认知障碍）早期干预。"
      }
    },
    {
      "@type": "Question",
      "name": "如何开始使用 CittaVerse？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "无需下载应用，微信扫码即可开始体验。系统支持全语音交互，包括各地方言，老人无需学习复杂操作。"
      }
    },
    {
      "@type": "Question",
      "name": "CittaVerse 的临床效果如何？",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "临床数据显示：认知评分平均提升 23%，交互依从性提升 92%，具体叙事细节唤醒增加 34%。已在全国 12 家高端康养社区与三甲医院认知中心落地。"
      }
    }
  ]
}
</script>
```

---

#### 2.1.4 创建标准 Robots.txt

在网站根目录创建 `/robots.txt`：

```
User-agent: *
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: GPTBot
Allow: /

User-agent: CCBot
Allow: /

Sitemap: https://www.cittaverse.com/sitemap.xml
```

---

### 2.2 第二阶段：内容优化（第 2-3 周）

#### 2.2.1 问答式内容重构

**目标**：匹配 AI 查询习惯（平均 23 词长查询）

| 原内容 | 优化后 |
|--------|--------|
| "记忆的科学重构机制" | "CittaVerse 如何通过 AI 技术延缓记忆衰退？" |
| "神经 -AI 双向映射模型" | "AI 认知训练的科学原理是什么？" |
| "临床数据" | "CittaVerse 的临床效果有数据支撑吗？" |

**实施方法**：
- 每个章节添加 H2/H3 问题式标题
- 段落首句直接回答问题（AI 提取优先）
- 保持现有专业深度，不牺牲质量

---

#### 2.2.2 权威引用强化

**当前引用**（需做成可点击链接）：

| 来源 | 链接目标 |
|------|----------|
| 北京大学老年医学中心 | 机构官网或合作新闻稿 |
| JMIR Aging | https://aging.jmir.org/ |
| PubMed | 相关论文链接 |
| GRACE 项目 | 项目说明页或论文 |

**为什么重要**：AI 引擎更信任带外部权威引用的内容。

---

#### 2.2.3 添加 E-E-A-T 信号

| 信号类型 | 实施方式 |
|----------|----------|
| **Experience** | 添加"2000+ 家庭"真实案例详情（匿名化处理） |
| **Expertise** | 创建"科学顾问委员会"页面，列出专家背景 |
| **Authoritativeness** | 发布白皮书/研究报告（PDF 下载） |
| **Trustworthiness** | 添加隐私政策、服务协议、联系方式页面 |

---

### 2.3 第三阶段：外部可见性（第 4-8 周）

#### 2.3.1 内容分发矩阵

| 平台 | 内容类型 | 频率 | 目标 |
|------|----------|------|------|
| **知乎** | 深度回答（数字疗法/认知衰退话题） | 2 篇/周 | 建立专业形象，引流官网 |
| **微信公众号** | 临床案例拆解、用户故事 | 1 篇/周 | 私域沉淀，子女群体触达 |
| **36 氪/机器之心** | 投稿（AI+ 医疗方向） | 1 篇/月 | 行业曝光，获取反向链接 |
| **动脉网** | 数字疗法行业分析 | 1 篇/月 | B 端机构触达 |
| **ResearchGate/arXiv** | 研究论文预印本 | 1 篇/季度 | 学术引用，提升权威性 |

---

#### 2.3.2 品牌提及策略

**核心逻辑**：外部提及比反向链接对 AI 可见性影响高 3 倍。

**执行方法**：
1. 监测竞品/同类产品在 AI 回答中的提及
2. 在相同话题下发布高质量内容
3. 鼓励用户/合作伙伴在社交媒体提及品牌
4. 参与行业报告/白皮书联合发布

---

## 三、预期时间线

| 时间 | 里程碑 | 成功指标 |
|------|--------|----------|
| **第 1 周** | 技术基础设施完成 | Google/Bing 收录官网 |
| **第 2 周** | Schema Markup 部署完成 | 结构化数据测试通过 |
| **第 3 周** | 内容优化完成 | 品牌词搜索出现官网 |
| **第 4-6 周** | 外部内容开始分发 | 知乎/公众号内容上线 |
| **第 8-12 周** | AI 引擎开始引用 | ChatGPT/Perplexity 出现品牌提及 |

---

## 四、追踪指标

### 4.1 技术指标

| 指标 | 工具 | 目标值 |
|------|------|--------|
| 索引页面数 | Google Search Console | >10 |
| Schema 验证 | Google Rich Results Test | 100% 通过 |
| 页面加载速度 | PageSpeed Insights | >80 分 |

### 4.2 AI 可见性指标

| 指标 | 测量方法 | 目标值 |
|------|----------|--------|
| **Share of Answer** | 手动查询 ChatGPT/Perplexity（品牌词 + 品类词） | 12 周内>30% |
| **AI 引用次数** | 每周查询 10 个相关问题的回答 | 12 周内>5 次/周 |
| **AI 引流流量** | Google Analytics（referral: chatgpt.com, perplexity.ai） | 持续增长 |

### 4.3 业务指标

| 指标 | 目标值 | 测量周期 |
|------|--------|----------|
| 官网访问量 | 月增长 20% | 周 |
| 小程序体验扫码 | 月增长 15% | 周 |
| 付费转化 | 2-3% | 月 |

---

## 五、风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 搜索引擎收录延迟 | 中 | 中 | 同时提交 Google+Bing，主动提交 URL |
| AI 引擎不引用 | 中 | 高 | 加强外部提及，发布权威报告 |
| 竞品抢占生态位 | 高 | 高 | 加速执行，优先完成技术基础设施 |
| 内容被判定为医疗广告 | 低 | 高 | 确保所有声明有临床数据支撑，添加免责声明 |

---

## 六、执行状态

### 6.1 GitHub GEO 部署 ✅ 已完成 (2026-03-08)

| 任务 | 状态 | 链接 |
|------|------|------|
| 创建 `cittaverse/pipeline` 仓库 | ✅ | https://github.com/cittaverse/pipeline |
| 创建 `cittaverse/awesome-digital-therapy` 仓库 | ✅ | https://github.com/cittaverse/awesome-digital-therapy |
| 创建 `cittaverse/core` 仓库 | ✅ | https://github.com/cittaverse/core |
| 部署 GEO-optimized README | ✅ | 3 个仓库均已推送 |
| 配置 Topics 标签 | ✅ | 每个仓库 10 个精准标签 |
| 提交搜索引擎索引 | ✅ | Google + Bing 已 ping |

**预期索引时间**：48 小时内 Google/Bing 可检索

---

## 七、下一步行动

### 7.1 官网技术优化（本周内）

- [ ] 创建 sitemap.xml 并上传至网站根目录
- [ ] 创建 robots.txt 并上传至网站根目录
- [ ] 注册 Google Search Console 并验证所有权
- [ ] 注册 Bing Webmaster Tools 并验证所有权
- [ ] 部署 Organization Schema Markup
- [ ] 在官网首页添加 GitHub 仓库链接（反向链接）

### 7.2 内容分发（下周开始）

- [ ] 知乎发布"数字疗法如何延缓记忆衰退"深度回答
- [ ] 公众号发布临床案例拆解文章
- [ ] 联系动脉网/机器之心投稿

### 7.3 本周待确认

- [ ] 确认官网技术栈（便于生成精确 Schema 代码）
- [ ] 确认知乎/公众号账号信息

---

## 附录 A：GEO vs SEO 对比

| 维度 | 传统 SEO | GEO（生成式引擎优化） |
|------|----------|----------------------|
| **输出格式** | 链接列表 | 合成叙事回答 |
| **用户行为** | 点击跳转 | 直接获取答案 |
| **查询长度** | 平均 4 词 | 平均 23 词 |
| **成功指标** | 排名、CTR、流量 | 引用、品牌提及、Share of Voice |
| **优化重点** | 关键词、反向链接 | 内容结构、权威信号、可提取性 |
| **核心问题** | "我们在第一页吗？" | "我们在回答里吗？" |

---

## 附录 B：参考资源

- [Google Search Central - Schema Markup](https://developers.google.com/search/docs/appearance/structured-data)
- [GEO: Generative Engine Optimization (arXiv 论文)](https://arxiv.org/pdf/2311.09735)
- [LLMrefs - GEO 2026 指南](https://llmrefs.com/generative-engine-optimization)
- [Onely - GEO 12 步检查清单](https://www.onely.com/blog/generative-engine-optimization-geo-checklist-optimize/)

---

*文档结束*
