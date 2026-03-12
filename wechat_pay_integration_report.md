# CittaVerse 微信支付 (WeChat Pay) 整合研究报告

## 1. 执行摘要 (Executive Summary)
本报告旨在为 CittaVerse (`abao-official`) 项目提供整合微信支付的技术方案与风险评估。研究核心结论如下：
- **推荐方案**：采用微信支付的 **Native Pay (原生扫码支付)**。此方案与现有支付宝电脑网站支付的技术路径、用户体验高度一致。
- **状态同步**：可复用现有轮询机制。微信支付提供了“查询订单API”，能够以 `out_trade_no` (商户订单号) 为索引，在无法接收 Webhook 的沙盒环境中，精准地轮询订单状态。
- **主要风险**：双通道并存引入的主要技术风险集中在**状态管理复杂性**、**统一对账**和**差异化错误处理**上。这些风险可通过构建抽象支付层 (Abstraction Layer) 进行有效管理。

---

## 2. 微信支付接入方案对比 (Integration Strategy)

### 2.1. 推荐方案：Native Pay (原生扫码支付)
**结论**：对于 CittaVerse 这类以 PC/H5 网站为主要载体的产品，**Native Pay 是唯一正确且高效的选项**。

**核心逻辑**:
1.  后端调用微信支付统一下单 API，生成支付二维码的链接 (`code_url`)。
2.  前端将此链接渲染为二维码，展示给用户。
3.  用户使用手机微信 App 扫描二维码，完成支付。
4.  后端启动轮询进程，确认支付状态。

此方案完美匹配当前支付宝的扫码支付体验，无需对现有用户流程做任何颠覆性改动。

### 2.2. 方案对比：Native Pay vs. JSAPI Pay
| 特性 | Native Pay (原生扫码支付) | JSAPI Pay (公众号/小程序支付) | CittaVerse 适用性 |
| :--- | :--- | :--- | :--- |
| **使用场景** | PC 网站、H5 页面、实体物料 | **仅限**微信内置浏览器环境 | 🔴 **不适用** |
| **用户流程** | 浏览器 -> 手机扫码 -> 支付 | 微信内网页 -> 直接拉起支付 | 流程不匹配 |
| **技术依赖** | 无，生成标准二维码即可 | 强依赖微信环境，需获取 user `openid` | 增加不必要的复杂度 |
| **开发成本** | 低，与现有架构相似 | 高，需要额外处理微信授权流程 | 投入产出比低 |

---

## 3. 支付状态轮询方案 (Polling-Based Status Verification)

### 3.1. 架构对标：与现有 `auto_verify.py` 对齐
CittaVerse 现有支付宝轮询机制 (`auto_verify.py`) 的核心思想可被 100% 移植到微信支付场景。两者都提供了通过商户订单号查询支付状态的服务器端 API。

### 3.2. 微信支付“查询订单 API”实施要点
- **API Endpoint**: `https://api.mch.weixin.qq.com/pay/orderquery`
- **请求方式**: POST (XML 格式)
- **核心请求参数**:
    - `appid`: 应用 APPID
    - `mch_id`: 商户号
    - `out_trade_no`: **商户订单号** (与支付宝对齐的关键字段)
    - `nonce_str`: 随机字符串
    - `sign`: 签名
- **核心返回参数 (`trade_state`)**:
    - `SUCCESS`: 支付成功
    - `REFUND`: 转入退款
    - `NOTPAY`: 未支付
    - `CLOSED`: 已关闭
    - `USERPAYING`: 用户支付中

**轮询脚本 (`auto_verify_wechat.py` - 伪代码):**
```python
import time

def poll_wechat_status(order_id):
    # 1. 构建请求参数 (appid, mch_id, out_trade_no, ...)
    # 2. 生成并添加 sign 签名
    # 3. 发送 POST 请求到 orderquery API
    # 4. 解析返回的 XML，获取 trade_state
    response = wechat_pay_client.order_query(out_trade_no=order_id)
    return response.get("trade_state")

# --- 主逻辑 ---
max_retries = 30  # 轮询 60s
for i in range(max_retries):
    current_status = poll_wechat_status("ORD_20260307_WXXXX")
    if current_status == "SUCCESS":
        trigger_user_activation("ORD_20260307_WXXXX")
        print("--- WECHAT ACTIVATION COMPLETE ---")
        break
    time.sleep(2) # 间隔2秒
```

---

## 4. 双支付通道并存的技术风险与规避策略

### 4.1. 核心风险点
1.  **状态管理复杂性 (State Management Complexity)**:
    - 支付宝和微信支付的订单状态（`trade_status` vs `trade_state`）定义、流转路径存在细微差异。
    - 需要在订单模型中设计一套**统一的、内部标准化的支付状态**，与外部通道状态解耦。
    - 例如，内部状态可定义为 `PENDING`, `PAID`, `FAILED`, `REFUNDED`，外部的 `TRADE_SUCCESS` (支付宝) 和 `SUCCESS` (微信) 均映射到内部的 `PAID` 状态。

2.  **代码逻辑冗余 (Code Redundancy)**:
    - 如果为每个支付渠道都编写一套独立的下单、查询、回调逻辑，将导致大量重复代码，维护成本激增。
    - **风险**：后续新增支付渠道（如 Apple Pay, Stripe）将使系统变得脆弱不堪。

3.  **对账与退款操作碎片化 (Fragmented Reconciliation & Refund)**:
    - 财务对账需要分别拉取两个平台的账单，增加了人工操作的复杂性和出错率。
    - 退款操作需要根据原始支付渠道，调用不同的 API，对客服和运营流程构成挑战。

4.  **错误处理与监控差异 (Differentiated Error Handling)**:
    - 两个渠道的错误码、网络异常、签名失败等问题的排查方式不同。
    - 需要建立统一的支付异常监控和告警体系，而不是针对每个渠道单独配置。

### 4.2. 风险规避策略：构建抽象支付层 (Payment Abstraction Layer)
强烈建议在 CittaVerse 后端构建一个“支付网关”或“抽象支付层”，以隔离和管理不同支付渠道的复杂性。

**设计思路**:
1.  **统一接口 (Unified Interface)**:
    - 定义内部统一的支付接口，例如：`pay()`, `query()`, `refund()`。
    - 业务层代码只调用这些内部接口，无需关心底层是支付宝还是微信。
    - `pay()` 方法接收一个 `channel` 参数 (`alipay` 或 `wechat`)，在方法内部调用对应的 SDK。

2.  **策略模式 (Strategy Pattern)**:
    - 为每种支付渠道实现一个具体的策略类（`AlipayStrategy`, `WechatPayStrategy`）。
    - 每个策略类都实现统一接口，封装各自的 SDK 调用、参数构造、签名逻辑和状态映射。

3.  **统一数据模型 (Unified Data Model)**:
    - 设计统一的支付订单数据表，包含 `channel` 字段以区分支付方式。
    - 建立内部支付状态与渠道原始状态的映射关系表。

4.  **集中化配置 (Centralized Configuration)**:
    - 将支付宝和微信支付的 AppID, MchID, 密钥等配置信息集中管理，而不是散落在代码各处。

**抽象层带来的优势**:
- **高扩展性**: 未来接入新支付渠道，只需新增一个策略类，业务层代码无需改动。
- **高维护性**: 各渠道的逻辑被隔离在各自的模块中，便于独立测试和维护。
- **业务纯净**: 核心业务逻辑与具体的支付实现解耦，更加清晰和健壮。

---

## 5. 最终建议
1.  **立即启动微信支付 Native Pay 方案的整合工作**。技术路径清晰，与现有系统兼容性高。
2.  **同步设计并实施支付抽象层**。这是保障系统长期健康、可扩展的关键一步，其优先级应与功能实现同等重要。
3.  **复用并扩展现有的轮询验证机制**，为微信支付创建专用的轮询脚本，并最终统一由抽象层的 `query()` 方法调度。
