# CittaVerse 应用建议 · 2026-04-02

**基于**: 10 篇 arXiv 前沿论文分析 (2026-03-27 ~ 2026-04-02)  
**目标**: 一念万相 V0.2 产品落地

---

## 执行摘要

### 核心发现
本周前沿研究呈现 5 大趋势，与 CittaVerse 当前需求高度契合：
1. **自主演化系统** — 阿宝应具备自我改进能力，而非静态设计
2. **动态多 Agent 协作** — 回忆引导涉及多角色，需自适应编排
3. **长程连贯性** — 跨会话记忆是用户体验关键
4. **不确定性感知** — 个性化适配需要概率建模
5. **可迁移认知原语** — 用户差异化是底层能力组合，非专用模型

### 立即行动 (P0)
| 行动 | 预期收益 | 实施周期 | 依赖 |
|------|----------|----------|------|
| Scratchpad 长程记忆 | 跨会话连贯性 +50% | 1-2 周 | 无 |
| PsychAgent 三引擎架构参考 | 建立自我改进闭环 | 2-3 周 | 会话日志基础设施 |

### 中期行动 (P1)
| 行动 | 预期收益 | 实施周期 | 依赖 |
|------|----------|----------|------|
| Autoresearch 记忆优化 | 减少手动调参 70% | 3-4 周 | 实验追踪系统 |
| 变分用户偏好建模 | 个性化适配质量 +30% | 2-3 周 | 用户反馈数据 |

---

## P0 行动：立即实施 (1-2 周内)

### 行动 1: Scratchpad 长程记忆机制

**来源**: YC-Bench (2604.01212)  
**核心发现**: Scratchpad 是长程任务成功的最强预测因子

**现状问题**:
- 阿宝当前会话间信息传递依赖完整历史回放
- 关键用户信息（偏好、禁忌、重要锚点）无结构化持久化
- 长对话中上下文截断导致早期重要信息丢失

**实施方案**:
```
┌─────────────────────────────────────────────────────────┐
│                  Scratchpad 结构                        │
├─────────────────────────────────────────────────────────┤
│ 用户画像层                                               │
│  - preferred_name, birth_year, hometown, family_role   │
│  - 叙事偏好 (具体/抽象、积极/中性、详细/简洁)           │
│  - 禁忌话题列表                                         │
│                                                         │
│ 回忆锚点层                                               │
│  - 重要事件索引 (时间、地点、情感强度)                   │
│  - 照片关联 (照片 ID → 回忆主题)                         │
│  - 集体记忆关联 (年代事件、地域事件)                     │
│                                                         │
│ 会话状态层                                               │
│  - 上次会话主题                                         │
│  - 未完成回忆线索                                       │
│  - 情绪安全标记 (近期是否触及敏感话题)                   │
│                                                         │
│ 演化记录层                                               │
│  - 有效引导模式统计                                     │
│  - 失败引导模式统计                                     │
│  - 用户反馈聚合                                         │
└─────────────────────────────────────────────────────────┘
```

**技术实现**:
```python
# 伪代码示例
class UserScratchpad:
    def __init__(self, user_id):
        self.user_id = user_id
        self.profile = UserProfile()
        self.memory_anchors = MemoryAnchorStore()
        self.session_state = SessionState()
        self.evolution_log = EvolutionLog()
    
    def update_after_session(self, session_transcript, outcomes):
        # 提取关键信息更新 scratchpad
        self._extract_preferences(session_transcript)
        self._update_anchors(session_transcript)
        self._log_outcomes(outcomes)
        self._persist()
    
    def get_context_for_new_session(self):
        # 为新会话提供压缩上下文
        return {
            "user_profile": self.profile.summary(),
            "active_anchors": self.memory_anchors.get_recent(),
            "pending_threads": self.session_state.pending_topics,
            "safety_flags": self.session_state.safety_markers
        }
```

**验收标准**:
- [ ] 新会话开始时，阿宝能引用上次会话的关键信息
- [ ] 用户偏好变更后，后续会话立即体现
- [ ] 触及敏感话题后，后续会话自动规避
- [ ] 上下文截断时，关键信息不丢失

**风险**:
- Scratchpad 更新策略过于激进可能引入错误信息
- 需要设计信息衰减机制，避免过时信息永久保留

---

### 行动 2: PsychAgent 三引擎架构参考

**来源**: PsychAgent (2604.00931)  
**核心发现**: 经验驱动的终身学习架构在心理咨询场景优于静态微调

**现状问题**:
- 阿宝当前引导策略是静态 Prompt 设计
- 无法从成功/失败会话中学习
- 新用户冷启动问题

**实施方案**:
```
┌─────────────────────────────────────────────────────────┐
│              阿宝终身学习架构 (参考 PsychAgent)          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Memory-Augmented Planning Engine             │   │
│  │    - 维护跨会话回忆线索图                         │   │
│  │    - 规划下次会话的引导策略                       │   │
│  │    - 确保回忆叙事的连续性                         │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                               │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 2. Skill Evolution Engine                       │   │
│  │    - 从成功会话提取有效引导模式                   │   │
│  │    - 从失败会话识别需要避免的策略                 │   │
│  │    - 聚类用户类型，识别不同类型的最优策略         │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                               │
│                         ▼                               │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 3. Reinforced Internalization Engine            │   │
│  │    - 通过 DPO/GRPO 将有效模式内化到模型          │   │
│  │    - 定期更新引导策略 Prompt                     │   │
│  │    - A/B 测试验证新策略效果                      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**实施阶段**:

**阶段 1 (Week 1-2)**: Memory-Augmented Planning
- 实现回忆线索图数据结构
- 实现会话间连续性检查
- 集成到当前阿宝对话流程

**阶段 2 (Week 3-4)**: Skill Evolution
- 建立会话质量评估指标（用户参与度、回忆深度、情绪正向）
- 实现成功/失败模式提取 pipeline
- 建立用户类型聚类

**阶段 3 (Week 5-6)**: Reinforced Internalization
- 搭建 DPO 训练 pipeline
- 设计 A/B 测试框架
- 实现策略灰度发布

**验收标准**:
- [ ] 新用户的引导质量在 3 次会话内显著提升
- [ ] 整体用户留存率提升 15%+
- [ ] 人工审核发现的有效引导模式被系统自动识别

**风险**:
- 技能演化可能引入偏见（如过度适配某类用户）
- 需要建立安全审查机制，防止演化出有害引导策略

---

## P1 行动：中期实施 (2-4 周内)

### 行动 3: Autoresearch 记忆优化

**来源**: OmniMem (2604.01007)  
**核心发现**: 自主研究 pipeline 自动发现记忆架构优化，F1 提升 +411%

**应用场景**:
- 自动探索记忆检索策略（关键词检索 vs 语义检索 vs 混合）
- 自动优化记忆组织方式（时间线 vs 主题 vs 情感）
- 自动诊断检索失败并修复

**实施方案**:
```python
# 伪代码示例
class MemoryAutoresearch:
    def __init__(self):
        self.design_space = {
            "retrieval": ["keyword", "semantic", "hybrid", "graph"],
            "organization": ["timeline", "topic", "emotion", "anchor"],
            "scoring": ["recency", "relevance", "emotion_intensity"]
        }
        self.baseline_f1 = 0.35  # 当前检索 F1
    
    def run_experiment(self, config):
        # 在历史会话数据上评估配置
        f1 = self._evaluate_retrieval(config)
        return f1
    
    def diagnose_and_propose(self, failure_cases):
        # 分析失败案例，提出架构修改
        # 如 OmniMem 发现 bug 修复贡献 +175%
        if self._detect_bug(failure_cases):
            return self._propose_bugfix()
        elif self._detect_architecture_limit(failure_cases):
            return self._propose_architecture_change()
        else:
            return self._propose_prompt_change()
    
    def autonomous_loop(self, num_experiments=50):
        configs_evaluated = []
        for i in range(num_experiments):
            if i < 10:
                config = self._random_sample()
            else:
                config = self._propose_from_history(configs_evaluated)
            
            f1 = self.run_experiment(config)
            configs_evaluated.append((config, f1))
            
            if i % 10 == 0:
                diagnosis = self.diagnose_and_propose(
                    self._get_failure_cases(configs_evaluated)
                )
        
        return self._select_best(configs_evaluated)
```

**验收标准**:
- [ ] 自动发现的配置优于人工设计配置
- [ ] 实验 pipeline 可无人值守运行
- [ ] 诊断报告可解释（非黑盒）

---

### 行动 4: 变分用户偏好建模

**来源**: VRF (2604.00997)  
**核心发现**: 不确定性感知的用户偏好建模在少样本场景显著优于点估计

**应用场景**:
- 新用户冷启动（反馈数据稀缺）
- 偏好冲突检测（用户言行不一致）
- 个性化引导策略选择

**实施方案**:
```python
# 伪代码示例
class VariationalUserPreference:
    def __init__(self, shared_bases):
        # 共享偏好基（从所有用户学习）
        self.shared_bases = shared_bases  # K 个偏好原型
        
    def encode_user(self, user_interactions):
        # 变分编码器：输出用户偏好分布 q(z|x)
        mu, log_var = self.encoder(user_interactions)
        return mu, log_var
    
    def compute_weights(self, user_dist):
        # 通过 Wasserstein 距离匹配共享基
        weights = []
        for base in self.shared_bases:
            w = wasserstein_distance(user_dist, base)
            weights.append(w)
        return softmax(weights)
    
    def get_preference_with_uncertainty(self, user_id):
        mu, log_var = self.user_embeddings[user_id]
        return {
            "preference": mu,
            "uncertainty": torch.exp(log_var),
            "confidence": 1 / (1 + torch.exp(log_var))
        }
    
    def guide_with_uncertainty(self, user_id, context):
        pref = self.get_preference_with_uncertainty(user_id)
        if pref["uncertainty"] > threshold:
            # 高不确定性：使用探索策略
            return self._explore_strategy(context)
        else:
            # 低不确定性：使用适配策略
            return self._exploit_strategy(pref["preference"], context)
```

**验收标准**:
- [ ] 新用户前 3 次会话的引导质量提升 20%+
- [ ] 不确定性估计与真实误差相关（高不确定性时确实更容易出错）
- [ ] 探索/利用策略切换自然，用户无感知

---

## P2 行动：长期探索 (1-2 月内)

### 行动 5: 多 Agent 回忆协作框架

**来源**: HERA (2604.00901)  
**核心价值**: 动态编排多角色 Agent，提升复杂回忆挖掘质量

**Agent 角色设计**:
| Agent | 职责 | 激活条件 |
|-------|------|----------|
| 引导 Agent | 发起回忆话题，温和追问 | 默认激活 |
| 评估 Agent | 监测情绪安全，防止深挖创伤 | 检测到情绪信号时 |
| 叙事 Agent | 整理回忆素材成故事 | 回忆素材充分时 |
| 锚点 Agent | 关联个人记忆与集体记忆 | 触及年代/地域线索时 |

**编排策略**:
- 全局层：根据回忆阶段动态调整 Agent 拓扑
- 局部层：根据用户反馈优化各 Agent 提示

---

### 行动 6: 回忆引导质量评估基准

**来源**: 空白识别  
**核心价值**: 学术差异化 + 内部迭代指导

**基准设计**:
```
维度 1: 回忆深度
  - 内部细节数量 (人物、地点、感官、情感)
  - 事件分段质量
  - 叙事连贯性

维度 2: 情绪体验
  - 正向情绪激发
  - 情绪安全维护
  - 自我接纳促进

维度 3: 用户参与
  - 对话轮次
  - 用户主动分享比例
  - 会话后满意度

维度 4: 长期价值
  - 回忆可复述性
  - 故事册质量
  - 用户留存
```

---

## 资源需求评估

| 行动 | 人力 | 计算资源 | 数据需求 |
|------|------|----------|----------|
| Scratchpad 长程记忆 | 1 工程师 × 2 周 | 低 | 无 |
| PsychAgent 三引擎 | 1 工程师 × 3 周 + 1 研究 | 中 (DPO 训练) | 会话日志 |
| Autoresearch 记忆 | 1 研究 × 4 周 | 高 (50+ 实验) | 标注检索数据 |
| 变分用户偏好 | 1 工程师 × 3 周 | 中 | 用户反馈 |
| 多 Agent 协作 | 1 工程师 × 4 周 | 中 | 无 |
| 评估基准 | 1 研究 × 4 周 | 低 | 标注会话 |

---

## 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Scratchpad 引入错误信息 | 中 | 高 | 设计信息衰减 + 人工审核抽样 |
| 技能演化引入偏见 | 中 | 高 | 建立公平性约束 + 多样性审计 |
| Autoresearch 计算成本过高 | 高 | 中 | 限制实验预算 + 早停策略 |
| 变分模型训练不稳定 | 中 | 中 | 使用成熟框架 + 充分验证 |
| 多 Agent 编排复杂度过高 | 高 | 中 | 从简单规则开始，逐步演化 |

---

## 下一步

1. **本周内**: 启动 Scratchpad 设计评审
2. **下周**: 开始 PsychAgent 架构详细设计
3. **2 周内**: 完成 Scratchpad 实现并 A/B 测试
4. **4 周内**: PsychAgent 阶段 1 上线

---

**状态更新**: `state/paper-review.json`
```json
{
  "round": 4,
  "papers_screened": 10,
  "papers_abstracted": 10,
  "key_trends": ["自主演化系统", "动态多 Agent 协作", "长程连贯性", "不确定性感知", "可迁移认知原语"],
  "actions_defined": 6,
  "last_updated": "2026-04-02T11:00:00Z"
}
```

---

## 附录：论文索引

| ID | arXiv | 标题 | 优先级 |
|----|-------|------|--------|
| 1 | 2604.01007 | OmniMem | P1 |
| 2 | 2604.00931 | PsychAgent | P0 |
| 3 | 2604.00901 | HERA | P2 |
| 4 | 2604.01212 | YC-Bench | P0 |
| 5 | 2604.01152 | Brainstacks | P1 |
| 6 | 2604.00842 | PARE | P2 |
| 7 | 2604.01073 | Narrative Fingerprints | P2 |
| 8 | 2604.00997 | VRF | P1 |
| 9 | 2604.01113 | CARE | P2 |
| 10 | 2604.01170 | ORCA | P2 |
