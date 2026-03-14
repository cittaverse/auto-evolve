# Common Voice 数据集下载问题记录

**日期**: 2026-03-14 11:25 UTC  
**执行者**: Hulk 🟢  
**状态**: ⚠️ 阻塞 (外部数据源不可用)

---

## 问题描述

Mozilla Common Voice 中文数据集无法下载，原因：

1. **官方 AWS S3 bucket 已移除**
   - 原 URL: `https://voice-prod-bundler-ee1969a6ce817082ed08d697ba62223d.s3.amazonaws.com/cv-corpus-24.0-2025-04-03/zh-CN.tar.gz`
   - 错误: `NoSuchBucket - The specified bucket does not exist`

2. **Mozilla Data Collective 迁移**
   - 从 CV 23.0 开始，数据集迁移到 https://datacollective.mozillafoundation.org/
   - 该网站无法通过 web_fetch 访问 (private/Internal IP)
   - 可能需要浏览器登录或特殊权限

3. **HuggingFace 镜像失败**
   - `mozilla-foundation/common_voice_13_0` - 返回 15 字节错误
   - `cdn-mozilla-common-voice.s3.amazonaws.com` - 返回 314 字节错误
   - 可能需 HuggingFace 账户认证

---

## 替代方案

### 方案 A: 使用其他公开中文语音数据集 (推荐)

根据之前调研 (memory/2026-03-14-elderly-voice-datasets.md):

| 数据集 | 获取方式 | 适用性 |
|--------|----------|--------|
| **AISHELL-1** | https://www.aishelltech.com/kysjcp | 开源免费，需申请 |
| **ST-CMDS** | https://openslr.org/38/ | OpenSLR 直接下载 |
| **THCHS-30** | http://data.cslt.org/thchs/ | 开源，需申请 |

**行动**: 优先尝试 ST-CMDS (OpenSLR，无需申请)

### 方案 B: 使用 mock 数据验证 ASR 评估框架

- ASR 评估脚本 (`pipeline/asr_evaluation_test.py`) 已支持 mock 模式
- 可先用 mock 数据验证流程
- 等待 API Key 配置后，再执行真实测试

### 方案 C: 手动收集少量测试样本

- 录制 5-10 条中文语音样本 (不同年龄/语速)
- 用于 ASR 评估框架的初步验证
- 适合 MVP 阶段测试

---

## 决策

**短期 (今日)**:
1. ✅ 接受 Common Voice 下载失败
2. ⏳ 尝试 ST-CMDS (OpenSLR) 下载
3. ⏳ 如仍失败，使用 mock 数据验证 ASR 评估框架

**中期 (本周)**:
1. AISHELL-1 申请 (如需更大规模测试)
2. 等待 API Key 配置后执行真实 ASR 测试

**长期**:
1. 产品化阶段：与语音数据供应商合作
2. 自建老年语音数据集 (用户授权采集)

---

## 影响评估

| 任务 | 影响程度 | 缓解措施 |
|------|----------|----------|
| ASR 选型测试 | 🟡 中 (延迟 1-2 天) | 先用 mock 数据验证框架 |
| L0 质检系统 | 🟢 低 (不依赖外部数据) | 使用内部 mock 样本 |
| 产品 Demo | 🟡 中 (缺少真实语音) | 使用录制样本替代 |

---

## 下一步行动

1. **尝试 ST-CMDS 下载** (OpenSLR, 无需申请)
   ```bash
   wget http://www.openslr.org/resources/38/st-cmds.tar.gz -O /home/node/Downloads/st-cmds.tar.gz
   ```

2. **如失败，使用 mock 数据验证 ASR 框架**
   ```bash
   python3 pipeline/asr_evaluation_test.py --mock --samples=10
   ```

3. **更新研究计划**
   - 记录数据获取阻塞
   - 调整 ASR 测试时间表 (03-16 → 03-18)

---

*记录时间：2026-03-14 11:25 UTC*
