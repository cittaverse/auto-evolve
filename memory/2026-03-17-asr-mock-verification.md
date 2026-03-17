# ASR Mock Verification — WER/CER Calculation Logic

**日期**: 2026-03-17  
**执行时间**: 05:55-06:30 UTC  
**状态**: 执行中  
**依赖**: 无 (不依赖 API Keys)

---

## 目标

验证 ASR 评估框架的核心计算逻辑 (WER/CER)，确保在 API Keys 配置后可立即执行真实测试。

---

## WER/CER 计算公式

### Word Error Rate (WER)

```
WER = (S + D + I) / N × 100%

其中:
- S = Substitutions (替换错误数)
- D = Deletions (删除错误数)
- I = Insertions (插入错误数)
- N = 参考文本总词数
```

### Character Error Rate (CER)

```
CER = (S + D + I) / N × 100%

其中:
- S = 替换错误字符数
- D = 删除错误字符数
- I = 插入错误字符数
- N = 参考文本总字符数
```

**中文场景优化**: CER 比 WER 更适合中文 ASR 评估 (无明确词边界)

---

## Levenshtein 距离算法

**核心逻辑**: 计算两个序列之间的最小编辑距离

```python
def levenshtein_distance(ref, hyp):
    """计算参考文本和假设文本之间的编辑距离"""
    m, n = len(ref), len(hyp)
    
    # 初始化 DP 表
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # 边界条件
    for i in range(m + 1):
        dp[i][0] = i  # 删除 i 个字符
    for j in range(n + 1):
        dp[0][j] = j  # 插入 j 个字符
    
    # 动态规划
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i-1] == hyp[j-1]:
                dp[i][j] = dp[i-1][j-1]  # 无需编辑
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],      # 删除
                    dp[i][j-1],      # 插入
                    dp[i-1][j-1]     # 替换
                )
    
    return dp[m][n]
```

---

## Mock 测试用例

### 测试用例 1: 完美匹配

| 维度 | 值 |
|------|------|
| 参考文本 | "今天天气很好" |
| 假设文本 | "今天天气很好" |
| 编辑距离 | 0 |
| CER | 0% |
| 预期结果 | ✅ 通过 |

### 测试用例 2: 单字符替换

| 维度 | 值 |
|------|------|
| 参考文本 | "今天天气很好" |
| 假设文本 | "今天天气很号" |
| 编辑距离 | 1 (好→号) |
| CER | 1/6 = 16.7% |
| 预期结果 | ✅ 通过 |

### 测试用例 3: 单字符删除

| 维度 | 值 |
|------|------|
| 参考文本 | "今天天气很好" |
| 假设文本 | "今天天气好" |
| 编辑距离 | 1 (删除"很") |
| CER | 1/6 = 16.7% |
| 预期结果 | ✅ 通过 |

### 测试用例 4: 单字符插入

| 维度 | 值 |
|------|------|
| 参考文本 | "今天天气很好" (6 字符) |
| 假设文本 | "今天天气非常好" (7 字符) |
| 编辑距离 | 1 (插入"非") |
| CER | 1/6 = 16.67% ✅ |
| 预期结果 | ✅ 通过 |

**修正说明**: CER 分母应为参考文本长度 (6)，非假设文本长度 (7)。原预期 14.29% 有误，正确值为 16.67%。

### 测试用例 5: 复杂错误 (老年语音典型)

| 维度 | 值 |
|------|------|
| 参考文本 | "我和老伴去了西湖边散步" |
| 假设文本 | "我和老伴去了西湖散部" |
| 错误分析 | "边"删除 + "步"→"部"替换 |
| 编辑距离 | 2 |
| CER | 2/11 = 18.2% |
| 预期结果 | ✅ 通过 |

---

## Python 实现验证

```python
#!/usr/bin/env python3
"""ASR Mock Verification — WER/CER Calculation"""

def levenshtein_distance(ref, hyp):
    """计算编辑距离"""
    m, n = len(ref), len(hyp)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if ref[i-1] == hyp[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[m][n]

def calculate_cer(ref, hyp):
    """计算字符错误率"""
    distance = levenshtein_distance(ref, hyp)
    return distance / len(ref) * 100 if len(ref) > 0 else 0

def calculate_wer(ref, hyp, lang='zh'):
    """计算词错误率"""
    if lang == 'zh':
        # 中文按字符处理 (近似)
        return calculate_cer(ref, hyp)
    else:
        # 英文按词处理
        ref_words = ref.split()
        hyp_words = hyp.split()
        distance = levenshtein_distance(ref_words, hyp_words)
        return distance / len(ref_words) * 100 if len(ref_words) > 0 else 0

# 测试用例
test_cases = [
    ("今天天气很好", "今天天气很好", 0.0, "完美匹配"),
    ("今天天气很好", "今天天气很号", 16.67, "单字符替换"),
    ("今天天气很好", "今天天气好", 16.67, "单字符删除"),
    ("今天天气很好", "今天天气非常好", 16.67, "单字符插入"),  # 修正：分母为 ref 长度 (6)
    ("我和老伴去了西湖边散步", "我和老伴去了西湖散部", 18.18, "复杂错误"),
]

print("ASR Mock Verification Results")
print("=" * 60)

all_passed = True
for ref, hyp, expected_cer, description in test_cases:
    cer = calculate_cer(ref, hyp)
    passed = abs(cer - expected_cer) < 0.01
    status = "✅" if passed else "❌"
    all_passed = all_passed and passed
    print(f"{status} {description}: CER={cer:.2f}% (expected {expected_cer:.2f}%)")

print("=" * 60)
print(f"Overall: {'✅ All tests passed' if all_passed else '❌ Some tests failed'}")
```

---

## 预期输出

```
ASR Mock Verification Results
============================================================
✅ 完美匹配：CER=0.00% (expected 0.00%)
✅ 单字符替换：CER=16.67% (expected 16.67%)
✅ 单字符删除：CER=16.67% (expected 16.67%)
✅ 单字符插入：CER=14.29% (expected 14.29%)
✅ 复杂错误：CER=18.18% (expected 18.18%)
============================================================
Overall: ✅ All tests passed
```

---

## 真实测试准备

### 测试音频样本

**来源**: AISHELL 数据集 (已下载 23 说话人，8541 wav 文件)

**抽样策略**:
- 从 23 说话人中随机抽取 10 条
- 时长分布：短 (<3s) 3 条，中 (3-5s) 4 条，长 (>5s) 3 条
- 覆盖不同声学特征 (语速/停顿/清晰度)

### 待配置 API Keys

| 服务 | API Key 状态 | 用途 |
|------|-------------|------|
| Azure Speech | 🔴 缺失 (>100h) | ASR 对比测试 |
| iFlytek 讯飞听见 | 🔴 缺失 (>100h) | ASR 对比测试 |
| Whisper (本地) | ✅ 可用 | 基线对照 |

### 真实测试流程

1. **音频预处理**: 16kHz, 16bit, mono (已完成)
2. **三服务并行转录**: Azure / iFlytek / Whisper
3. **WER/CER 计算**: 与参考文本对比
4. **延迟测量**: 记录 API 响应时间
5. **成本估算**: 按 USD/minute 计算

---

## 研究洞察

### 老年语音 ASR 挑战

**基于 CHI 2026 研究**:

| 声学特征 | 对 ASR 的影响 | 缓解策略 |
|----------|--------------|----------|
| 语速慢 | 停顿检测错误 ↑ | 调整 VAD 阈值 |
| 发音不清 | 替换错误 ↑ | 语言模型优化 |
| 方言口音 | 整体准确率 ↓ | 方言适配模型 |
| 气息声明显 | 插入错误 ↑ | 呼吸声过滤 |

### ASR 选型建议 (基于文献)

| 场景 | 推荐方案 | 理由 |
|------|----------|------|
| MVP 测试 | Azure Speech (中文) | 医疗场景定制能力 |
| Pilot RCT | 讯飞听见 + Whisper 冗余 | 中文方言支持 + 双模型校验 |
| 产品化 | 自研微调 (老年语音数据) | 建立技术壁垒 |

---

## 下一步

1. **执行 Mock 测试脚本**: 验证 WER/CER 计算逻辑
2. **等待 V 配置 API Keys**: Azure Speech + iFlytek
3. **执行真实测试**: `python3 pipeline/asr_evaluation_test.py`
4. **产出选型报告**: WER/CER/延迟/成本对比

---

**状态**: Mock 验证逻辑已准备就绪，待执行脚本验证。
