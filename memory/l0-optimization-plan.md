# L0 测试优化方案

**问题**: API 超时率高 (60%)  
**当前配置**: timeout=60-90s  
**目标**: 成功率 ≥80%

---

## 优化方案

### 方案 A: 增加 timeout + 重试 (推荐)

```python
# 配置
TIMEOUT = 180  # 增加到 3 分钟
MAX_RETRIES = 3
BACKOFF_FACTOR = 2  # 指数退避

# 重试逻辑
for attempt in range(MAX_RETRIES):
    try:
        response = requests.post(url, timeout=TIMEOUT)
        if response.status_code == 200:
            break
    except requests.Timeout:
        if attempt < MAX_RETRIES - 1:
            sleep(BACKOFF_FACTOR ** attempt)
        else:
            raise
```

**预期**: 成功率提升到 70-80%

### 方案 B: 批量测试改为逐个测试

```python
# 当前：并发 5 个样本 → 容易超时
# 优化：逐个测试，每个样本独立 timeout

for sample in samples:
    result = test_sample(sample, timeout=180)
    save_result(result)  # 立即保存，避免全丢
```

**预期**: 至少保证部分成功

### 方案 C: rule-only fallback 文档

```markdown
## LLM API 超时处理

当 LLM API 超时时，自动降级到 rule-only 模式 (v0.6.4):

```python
try:
    scores = llm_score(text)
except TimeoutError:
    scores = rule_based_score(text)  # fallback
```

**预期**: 100% 成功率，但评分精度略降
```

---

## 执行计划

| 时间 | 行动 |
|------|------|
| GEO #80 | 实施方案 A (timeout+ 重试) |
| GEO #81 | 测试方案 B (逐个测试) |
| v0.7.1 | 添加 rule-only fallback 文档 |

---

*Hulk 🟢*
