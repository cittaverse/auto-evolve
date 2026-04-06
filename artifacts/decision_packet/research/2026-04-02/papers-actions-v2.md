# CittaVerse 应用建议 · 2026-04-02 (第二轮)

**基于**: 10 篇 arXiv 论文深化分析 + 关联分析  
**分析时间**: 2026-04-02 13:50 UTC  
**⚠️ 注意**: 因网络工具不可用，本轮为上一轮 (11:00) 的深化扩展，非新论文分析

---

## 执行摘要

### 本轮更新重点

基于第三轮关联分析，更新以下行动建议：

1. **新增**: 分层记忆架构设计 (融合 OmniMem + PsychAgent + Brainstacks + YC-Bench)
2. **细化**: Scratchpad 实现方案 (补充衰减机制和更新策略)
3. **细化**: 变分偏好模型实现路径 (补充共享基构建方法)
4. **新增**: 评估诊断框架设计 (融合 PARE + YC-Bench + OmniMem)

### 优先级更新

| 行动 | 原优先级 | 新优先级 | 变更原因 |
|------|----------|----------|----------|
| Scratchpad 长程记忆 | P0 | P0 | 不变，概念更清晰 |
| PsychAgent 三引擎 | P0 | P0 → P0.5 | 与分层记忆架构合并实施 |
| 变分用户偏好 | P1 | P1 | 不变 |
| 零遗忘 Adapter Stack | - | P1 (新增) | 关联分析识别为关键模块 |
| 自主研究诊断 | P1 | P2 | 降低优先级，依赖较多 |
| 评估基准 | P2 | P1 | 提升优先级，支持迭代 |

---

## P0 行动：立即实施 (1-2 周内)

### 行动 1: Scratchpad 长程记忆机制 (细化版)

**来源**: YC-Bench (2604.01212) + PsychAgent (2604.00931)

**细化设计**:

```python
# 完整实现示例
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np

@dataclass
class DecayConfig:
    """信息衰减配置"""
    half_life_days: float = 30.0  # 半衰期
    min_weight: float = 0.1       # 最小权重
    decay_type: str = "exponential"  # exponential | linear

@dataclass
class MemoryAnchor:
    """回忆锚点"""
    id: str
    timestamp: datetime
    topic: str
    emotion_intensity: float  # 0-1
    details: Dict[str, str]   # 内部细节 (人物、地点、感官)
    photo_ids: List[str] = field(default_factory=list)
    collective_anchor: Optional[str] = None  # 集体记忆关联
    weight: float = 1.0
    
    def apply_decay(self, config: DecayConfig, current_time: datetime):
        """应用时间衰减"""
        age_days = (current_time - self.timestamp).days
        if config.decay_type == "exponential":
            self.weight = max(
                config.min_weight,
                np.exp(-np.log(2) * age_days / config.half_life_days)
            )
        elif config.decay_type == "linear":
            self.weight = max(
                config.min_weight,
                1.0 - age_days / (config.half_life_days * 2)
            )

@dataclass
class SessionState:
    """会话状态"""
    last_topic: Optional[str] = None
    pending_threads: List[str] = field(default_factory=list)
    safety_markers: List[str] = field(default_factory=list)
    last_session_time: Optional[datetime] = None
    consecutive_positive_sessions: int = 0

@dataclass
class EvolutionLog:
    """演化记录"""
    successful_patterns: Dict[str, int] = field(default_factory=dict)
    failed_patterns: Dict[str, int] = field(default_factory=dict)
    user_feedback_aggregate: Dict[str, float] = field(default_factory=dict)
    
    def record_outcome(self, pattern: str, success: bool, feedback_score: float = 0.0):
        if success:
            self.successful_patterns[pattern] = self.successful_patterns.get(pattern, 0) + 1
        else:
            self.failed_patterns[pattern] = self.failed_patterns.get(pattern, 0) + 1
        self.user_feedback_aggregate[pattern] = (
            self.user_feedback_aggregate.get(pattern, 0.0) + feedback_score
        ) / 2  # 简单移动平均

class UserScratchpad:
    """用户 Scratchpad - 长程记忆核心"""
    
    def __init__(self, user_id: str, storage_path: str):
        self.user_id = user_id
        self.storage_path = storage_path
        self.profile = {}  # 用户画像
        self.anchors: List[MemoryAnchor] = []
        self.session_state = SessionState()
        self.evolution_log = EvolutionLog()
        self.decay_config = DecayConfig()
        
    def update_after_session(self, transcript: str, outcomes: Dict):
        """会话后更新"""
        # 1. 提取用户偏好
        self._extract_preferences(transcript)
        
        # 2. 更新回忆锚点
        new_anchors = self._extract_anchors(transcript)
        self.anchors.extend(new_anchors)
        
        # 3. 应用衰减
        self._apply_decay_to_all()
        
        # 4. 记录演化
        self.evolution_log.record_outcome(
            pattern=outcomes.get("pattern", "unknown"),
            success=outcomes.get("success", False),
            feedback_score=outcomes.get("feedback_score", 0.0)
        )
        
        # 5. 更新会话状态
        self.session_state.last_topic = outcomes.get("topic")
        self.session_state.last_session_time = datetime.now()
        if outcomes.get("success", False):
            self.session_state.consecutive_positive_sessions += 1
        else:
            self.session_state.consecutive_positive_sessions = 0
        
        # 6. 持久化
        self._persist()
    
    def get_context_for_new_session(self) -> Dict:
        """为新会话提供压缩上下文"""
        # 按权重排序锚点
        sorted_anchors = sorted(self.anchors, key=lambda a: a.weight, reverse=True)
        top_anchors = sorted_anchors[:10]  # 只取 top 10
        
        # 检查安全标记
        safety_context = {}
        if self.session_state.safety_markers:
            safety_context = {
                "avoid_topics": self.session_state.safety_markers,
                "note": "近期触及敏感话题，请温和引导"
            }
        
        return {
            "user_profile": self._profile_summary(),
            "active_anchors": [self._anchor_summary(a) for a in top_anchors],
            "pending_threads": self.session_state.pending_threads,
            "last_topic": self.session_state.last_topic,
            "safety_context": safety_context,
            "effective_patterns": self._get_effective_patterns()
        }
    
    def _apply_decay_to_all(self):
        """对所有锚点应用衰减"""
        current_time = datetime.now()
        for anchor in self.anchors:
            anchor.apply_decay(self.decay_config, current_time)
        # 移除权重过低的锚点
        self.anchors = [
            a for a in self.anchors 
            if a.weight > self.decay_config.min_weight + 0.05
        ]
    
    def _persist(self):
        """持久化到存储"""
        import json
        data = {
            "user_id": self.user_id,
            "profile": self.profile,
            "anchors": [self._anchor_to_dict(a) for a in self.anchors],
            "session_state": self._session_state_to_dict(),
            "evolution_log": self._evolution_log_to_dict(),
            "last_updated": datetime.now().isoformat()
        }
        with open(f"{self.storage_path}/{self.user_id}.json", "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    # ... 辅助方法省略 ...
```

**验收标准**:
- [ ] 新会话开始时，阿宝能引用上次会话的关键信息 (人工测试 10 次，成功率 >90%)
- [ ] 用户偏好变更后，后续会话立即体现 (人工测试 5 次，成功率 >90%)
- [ ] 触及敏感话题后，后续会话自动规避 (人工测试 5 次，成功率 100%)
- [ ] 30 天未提及的锚点权重衰减至 0.5 以下 (单元测试)
- [ ] 权重 <0.15 的锚点被自动清理 (单元测试)

**风险与缓解**:
| 风险 | 缓解措施 |
|------|----------|
| Scratchpad 更新引入错误信息 | 会话后批量更新 + 人工审核抽样 (5%) |
| 衰减策略过于激进 | 可调半衰期参数 + 重要锚点手动保护标记 |
| 存储膨胀 | 定期清理低权重锚点 + 压缩旧会话摘要 |

---

### 行动 2: 分层记忆架构设计 (新增)

**来源**: OmniMem + PsychAgent + Brainstacks + YC-Bench 融合

**架构设计**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CittaVerse 分层记忆架构                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 1: Scratchpad (快速读写层)                                 │   │
│  │ - 用户画像、会话状态、安全标记                                   │   │
│  │ - 读写延迟: <10ms                                                │   │
│  │ - 存储: 本地 JSON / SQLite                                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    │ 引用                              │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 2: Memory Anchors (回忆线索层)                             │   │
│  │ - 事件索引、情感强度、照片关联                                   │   │
│  │ - 支持跨会话连续性                                               │   │
│  │ - 存储: 向量数据库 (Chroma/Weaviate)                             │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    │ 激活                              │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 3: Cognitive Stacks (认知原语层)                           │   │
│  │ - 用户特异性能力组合 (叙事风格、情感响应、引导模式)              │   │
│  │ - 零遗忘持续学习                                                 │   │
│  │ - 存储: LoRA adapter weights                                     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    │ 优化                              │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ Layer 4: Autoresearch Loop (自主优化层)                          │   │
│  │ - 定期诊断检索/引导失败                                          │   │
│  │ - 自动实验优化配置                                               │   │
│  │ - 存储: 实验追踪 (MLflow/Weights&Biases)                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**实施阶段**:

| 阶段 | 内容 | 周期 | 依赖 |
|------|------|------|------|
| Phase 1 | Layer 1 Scratchpad | 2 周 | 无 |
| Phase 2 | Layer 2 Memory Anchors | 3 周 | Phase 1 |
| Phase 3 | Layer 3 Cognitive Stacks | 4 周 | Phase 1+2 |
| Phase 4 | Layer 4 Autoresearch | 6 周 | Phase 1+2+3 |

---

## P1 行动：中期实施 (2-4 周内)

### 行动 3: 变分用户偏好编码器

**来源**: VRF (2604.00997)

**实现路径**:

```python
# 简化实现示例
import torch
import torch.nn as nn
from torch.distributions import Normal, kl_divergence

class VariationalPreferenceEncoder(nn.Module):
    """变分用户偏好编码器"""
    
    def __init__(self, input_dim: int, latent_dim: int, num_bases: int = 8):
        super().__init__()
        self.latent_dim = latent_dim
        self.num_bases = num_bases
        
        # 变分编码器
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
        )
        self.mu_head = nn.Linear(64, latent_dim)
        self.logvar_head = nn.Linear(64, latent_dim)
        
        # 共享偏好基
        self.preference_bases = nn.Parameter(
            torch.randn(num_bases, latent_dim)
        )
        
        # 权重预测器 (通过 Wasserstein 距离)
        self.weight_predictor = nn.Sequential(
            nn.Linear(latent_dim * 2, 32),
            nn.ReLU(),
            nn.Linear(32, num_bases),
            nn.Softmax(dim=-1)
        )
    
    def encode(self, user_interactions: torch.Tensor) -> tuple:
        """编码用户交互为变分分布"""
        hidden = self.encoder(user_interactions)
        mu = self.mu_head(hidden)
        logvar = self.logvar_head(hidden)
        return mu, logvar
    
    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """重参数化技巧"""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def compute_base_weights(self, user_mu: torch.Tensor) -> torch.Tensor:
        """计算用户偏好与共享基的匹配权重"""
        # 简化：使用欧氏距离替代 Wasserstein 距离
        distances = []
        for base in self.preference_bases:
            dist = torch.norm(user_mu - base, dim=-1)
            distances.append(dist)
        distances = torch.stack(distances, dim=-1)  # [batch, num_bases]
        # 距离越小权重越大
        weights = torch.softmax(-distances, dim=-1)
        return weights
    
    def forward(self, user_interactions: torch.Tensor, training: bool = True):
        mu, logvar = self.encode(user_interactions)
        
        if training:
            z = self.reparameterize(mu, logvar)
        else:
            z = mu  # 推理时使用均值
        
        weights = self.compute_base_weights(z)
        
        # 个性化策略 = 加权共享基
        personalized_preference = torch.matmul(weights, self.preference_bases)
        
        return {
            "preference": personalized_preference,
            "uncertainty": torch.exp(0.5 * logvar),
            "weights": weights,
            "mu": mu,
            "logvar": logvar
        }
    
    def elbo_loss(self, user_interactions: torch.Tensor, recon_loss: torch.Tensor):
        """ELBO 损失 = 重构损失 + KL 散度"""
        mu, logvar = self.encode(user_interactions)
        # KL(q(z|x) || N(0,1))
        kl = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
        return recon_loss + kl

# 训练循环示例
def train_preference_encoder(encoder, dataloader, num_epochs=50):
    optimizer = torch.optim.Adam(encoder.parameters(), lr=1e-3)
    
    for epoch in range(num_epochs):
        total_loss = 0
        for batch in dataloader:
            user_interactions, target_preference = batch
            
            optimizer.zero_grad()
            output = encoder(user_interactions, training=True)
            
            # 重构损失：预测偏好与真实偏好的 MSE
            recon_loss = nn.MSELoss()(output["preference"], target_preference)
            
            # ELBO 损失
            loss = encoder.elbo_loss(user_interactions, recon_loss)
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        print(f"Epoch {epoch+1}/{num_epochs}, Loss: {total_loss/len(dataloader):.4f}")
```

**共享基构建方法**:
```python
# 从现有用户聚类得到共享偏好基
from sklearn.cluster import KMeans

def build_shared_bases(all_user_embeddings: np.ndarray, num_bases: int = 8):
    """从现有用户嵌入聚类得到共享基"""
    kmeans = KMeans(n_clusters=num_bases, random_state=42)
    kmeans.fit(all_user_embeddings)
    return kmeans.cluster_centers_  # [num_bases, latent_dim]
```

**验收标准**:
- [ ] 新用户前 3 次会话的引导质量提升 20%+ (A/B 测试)
- [ ] 不确定性估计与真实误差相关 (Pearson r > 0.7)
- [ ] 探索/利用策略切换自然，用户无感知 (人工审核)

---

### 行动 4: 评估基准建设 (优先级提升)

**来源**: PARE (2604.00842) + YC-Bench (2604.01212)

**基准设计**:

```yaml
# CittaVerse-Bench 配置
name: CittaVerse-Bench
version: 0.1
dimensions:
  - name: 回忆引导质量
    metrics:
      - name: 用户参与度
        formula: (用户发言轮次 / 总会话轮次) * 100
        target: "> 40%"
      - name: 回忆深度
        formula: 内部细节数量 (人物 + 地点 + 感官 + 情感)
        target: "> 5 细节/会话"
      - name: 情绪正向
        formula: 正向情绪词占比 - 负向情绪词占比
        target: "> 0.3"
  
  - name: 跨会话连续性
    metrics:
      - name: 关键信息引用准确率
        formula: 正确引用次数 / 应引用次数
        target: "> 85%"
      - name: 未完成线索跟进率
        formula: 跟进线索数 / 待跟进线索数
        target: "> 70%"
  
  - name: 干预时机
    metrics:
      - name: 主动引导适当性
        formula: 用户正面响应次数 / 主动引导次数
        target: "> 60%"
      - name: 打扰率
        formula: 用户负面响应次数 / 主动引导次数
        target: "< 10%"
  
  - name: 个性化适配
    metrics:
      - name: 策略匹配度
        formula: 1 - (用户偏好向量与策略向量夹角 / π)
        target: "> 0.8"

test_suites:
  - name: 冷启动测试
    description: 新用户前 3 次会话
    num_users: 50
    sessions_per_user: 3
  
  - name: 长期连续性测试
    description: 单用户 30 天连续会话
    num_users: 20
    sessions_per_user: 30
  
  - name: 敏感话题处理测试
    description: 触及预设敏感话题的会话
    num_users: 30
    sessions_per_user: 5
```

**验收标准**:
- [ ] 基准可自动化运行 (CI/CD 集成)
- [ ] 评估结果与人工审核一致性 > 80%
- [ ] 支持 A/B 测试对比

---

## P2 行动：长期探索 (1-2 月内)

### 行动 5: 零遗忘 Adapter Stack

**来源**: Brainstacks (2604.01152)

**实施要点**:
- 预定义 5-8 个认知原语 stack
- 实现 null-space projection 训练
- 建立 stack 选择器

### 行动 6: 自主研究诊断 Loop

**来源**: OmniMem (2604.01007)

**实施要点**:
- 定义记忆架构设计空间
- 搭建自动实验 pipeline
- 实现失败诊断和修复建议生成

---

## 资源需求更新

| 行动 | 人力 | 计算资源 | 数据需求 | 优先级 |
|------|------|----------|----------|--------|
| Scratchpad 长程记忆 | 1 工程师 × 2 周 | 低 | 无 | P0 |
| 分层记忆架构 | 1 工程师 × 8 周 (分阶段) | 中 | 会话日志 | P0→P4 |
| 变分用户偏好 | 1 工程师 × 3 周 | 中 | 用户反馈 × 100+ | P1 |
| 评估基准 | 1 工程师 × 2 周 | 低 | 标注会话 × 50+ | P1 |
| 零遗忘 Stack | 1 工程师 × 4 周 | 高 (LoRA 训练) | 领域数据 | P2 |
| 自主研究 Loop | 1 研究 × 6 周 | 高 (50+ 实验) | 标注检索数据 | P2 |

---

## 风险与缓解 (更新)

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Scratchpad 引入错误信息 | 中 | 高 | 会话后批量更新 + 人工审核抽样 (5%) + 衰减机制 |
| 变分模型训练不稳定 | 中 | 中 | 使用成熟框架 + 充分验证 + 早停策略 |
| 评估基准与人工不一致 | 高 | 中 | 迭代校准 + 人工审核抽样 |
| 分层架构复杂度过高 | 高 | 中 | 分阶段实施 + 每阶段验收 |

---

## 本周行动清单

| 时间 | 行动 | 负责人 | 产出 |
|------|------|--------|------|
| 本周内 | Scratchpad 详细设计评审 | 工程团队 | 设计文档 |
| 本周内 | 评估基准指标定义 | 研究团队 | 指标文档 |
| 下周 | Scratchpad 实现启动 | 工程团队 | 代码 PR |
| 下周 | 用户反馈数据收集启动 | 产品团队 | 数据 pipeline |
| 2 周内 | Scratchpad A/B 测试上线 | 工程团队 | 测试结果 |

---

**状态更新**: `state/paper-review-v2.json`
```json
{
  "round": 4,
  "papers_screened": 10,
  "papers_deep_analyzed": 3,
  "synthesis_completed": true,
  "actions_updated": true,
  "key_trends": ["分层记忆架构", "变分个性化", "自主诊断修复", "零遗忘持续学习"],
  "proposed_modules": 5,
  "actions_defined": 6,
  "network_blocked": true,
  "next_full_scan": "2026-04-03T09:00:00Z",
  "last_updated": "2026-04-02T13:55:00Z"
}
```

---

## 附录：网络阻塞说明

**问题**: 无法访问 arXiv 获取最新论文

**原因**:
1. `web_search`: Gemini API Key 无效
2. `web_fetch`: DNS 解析到内部 IP (VPN/Clash fake-IP 模式)
3. `exec`: 不允许在 sandbox/node 执行

**建议**:
- OS 层修复：检查并更新 `GEMINI_API_KEY` 环境变量
- OS 层修复：配置 DNS 绕过规则，允许 arxiv.org 直连
- 或：配置 `tools.exec.host=node` 允许本地命令执行

**临时方案**:
- 基于已有论文深化分析 (本轮采用)
- 延长扫描周期至 14 天，减少新鲜度要求
- V 手动提供论文列表，Hulk 进行分析

---

**交付说明**: 本摘要将自动传递给 V，无需额外消息发送。
