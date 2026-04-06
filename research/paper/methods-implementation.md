# 实现细节 (Implementation Details)

## 技术栈

系统的技术选型遵循**云原生、高可用、易扩展**原则，核心组件如下：

### 3.4.1 后端服务

| 组件 | 技术选型 | 版本 | 用途 |
|------|----------|------|------|
| 运行时 | Node.js | 24.x | 主服务运行时 |
| Web 框架 | Fastify | 4.x | HTTP API |
| 数据库 | PostgreSQL | 15.x | 关系型数据 |
| 图数据库 | Neo4j | 5.x | 记忆图谱存储 |
| 缓存 | Redis | 7.x | 会话缓存、队列 |
| LLM 网关 | 自研 | - | 多模型路由、限流 |
| 任务队列 | BullMQ | 5.x | 异步评分任务 |

### 3.4.2 前端

| 组件 | 技术选型 | 版本 |
|------|----------|------|
| 小程序框架 | Taro | 3.x |
| UI 组件库 | NutUI | 4.x |
| 状态管理 | Zustand | 4.x |
| 构建工具 | Vite | 5.x |

### 3.4.3 基础设施

| 组件 | 服务商 | 规格 |
|------|--------|------|
| 云服务器 | 阿里云 ECS | 4 核 8G × 2 |
| 容器编排 | ACK（K8s） | 3 节点集群 |
| 对象存储 | OSS | 标准存储 |
| CDN | 阿里云 CDN | 全站加速 |
| 监控 | ARMS + SLS | 应用监控 + 日志 |

## 部署架构

系统采用**微服务架构**，按功能拆分为五个服务：

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (Ingress)  │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│   API Gateway │ │   WebSocket   │ │   Static      │
│   Service     │ │   Service     │ │   Files (OSS) │
└───────┬───────┘ └───────┬───────┘ └───────────────┘
        │                 │
        ▼                 ▼
┌───────────────┐ ┌───────────────┐
│ Conversation  │ │   Scoring     │
│   Service     │ │   Service     │
└───────┬───────┘ └───────┬───────┘
        │                 │
        └────────┬────────┘
                 ▼
        ┌─────────────────┐
        │   PostgreSQL    │
        │     + Neo4j     │
        │     + Redis     │
        └─────────────────┘
```

### 3.4.4 容器化配置

每个服务独立打包为 Docker 镜像，使用多阶段构建优化镜像大小：

```dockerfile
# Build stage
FROM node:24-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY src/ ./src/

# Runtime stage
FROM node:24-alpine
WORKDIR /app
COPY --from=builder /app /app
USER node
CMD ["node", "src/index.js"]
```

### 3.4.5 Kubernetes 配置要点

- **副本数**：API Gateway × 3，Conversation × 2，Scoring × 2
- **资源限制**：每 Pod CPU 500m-1000m，内存 512Mi-1Gi
- **健康检查**：HTTP GET /healthz，间隔 10s，超时 5s
- **自动扩缩容**：基于 CPU 使用率（目标 70%），最小 2 副本，最大 10 副本
- **灰度发布**：使用 Istio 进行流量分割，新版本 10% → 50% → 100%

## 性能优化

### 3.4.6 延迟优化

| 优化项 | 措施 | 效果 |
|--------|------|------|
| LLM 响应 | 流式输出 + 前端逐字渲染 | 首字延迟 < 500ms |
| 数据库查询 | 热点数据 Redis 缓存 | P95 < 50ms |
| 评分任务 | 异步队列，后台处理 | 不阻塞对话 |
| 静态资源 | CDN 加速 + 浏览器缓存 | 加载时间 < 1s |

### 3.4.7 成本控制

| 策略 | 实现方式 | 节省比例 |
|------|----------|----------|
| Prompt 压缩 | 对话历史滑动窗口（最近 10 轮） | 40% token |
| 模型路由 | 简单任务用 Flash 模型，复杂任务用 Plus | 30% 成本 |
| 响应缓存 | 相同输入缓存 24 小时 | 15% 请求 |
| 批量评分 | 多轮对话合并评分 | 20% token |

## 隐私与安全

### 3.4.8 数据加密

- **传输加密**：全站 HTTPS（TLS 1.3）
- **存储加密**：PostgreSQL TDE，敏感字段 AES-256
- **密钥管理**：阿里云 KMS，定期轮换

### 3.4.9 访问控制

- **认证**：微信小程序登录 + JWT
- **授权**：RBAC 模型，用户仅能访问自身数据
- **审计**：所有数据访问记录日志，保留 180 天

### 3.4.10 合规性

- **个人信息保护法**：明示收集目的，提供删除接口
- **数据安全法**：数据境内存储，跨境需审批
- **等保 2.0**：通过三级等保测评

## 可复现性

为促进学术复现，我们提供以下资源：

1. **代码仓库**：核心算法开源（GitHub: cittaverse/narrative-scorer）
2. **Prompt 模板**：六维度评分 prompt 完整版本（附录 B）
3. **示例数据**：脱敏后的 100 段叙事样本（Zenodo DOI: xxx）
4. **Docker 镜像**：评分服务镜像（Docker Hub: cittaverse/scorer:v1.0）

复现步骤：
```bash
# 1. 克隆仓库
git clone https://github.com/cittaverse/narrative-scorer.git
cd narrative-scorer

# 2. 配置环境变量
export LLM_API_KEY=your_key
export DATABASE_URL=postgresql://...

# 3. 启动服务
docker-compose up -d

# 4. 运行测试
npm test

# 5. 调用评分 API
curl -X POST http://localhost:3000/score \
  -H "Content-Type: application/json" \
  -d '{"text": "我的童年..."}'
```
