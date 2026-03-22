# Path B Recruitment Material Optimizations

**Date Prepared**: 2026-03-22 04:00 UTC  
**Materials Reviewed**:
- `docs/metamemory_pilot_recruitment_package.md` (6.5KB)
- `docs/pilot_day1_intervention_materials.md` (4.3KB)
- `docs/pilot_day2_4_intervention_materials.md` (5.1KB)
- Community contact list (12 Hangzhou institutions)

**Status**: Ready for V review and approval

---

## Optimization #1: Add WeChat QR Code for Self-Service Screening

### Current State
- Initial contact: Phone call to community center staff
- Follow-up: WeChat message with screening questionnaire link
- Participant action: Click link, fill out 14-question survey

### Proposed Change
Add WeChat Work QR code to recruitment poster that links directly to screening questionnaire.

### Implementation

**Poster Update** (add to bottom of existing poster):

```
┌────────────────────────────────────────────────┐
│                                                │
│   📱 扫码自助筛查                              │
│   ┌──────────────┐                             │
│   │              │                             │
│   │   [QR Code]  │                             │
│   │              │                             │
│   └──────────────┘                             │
│                                                │
│   或致电：沈建良 0571-85125367                 │
│   (文新街道幸福荟)                             │
│                                                │
└────────────────────────────────────────────────┘
```

**QR Code Generation**:
1. Use WeChat Work (企业微信) to generate QR code linking to screening questionnaire
2. Or use any QR generator with link to 腾讯问卷/问卷星
3. Test QR code on multiple devices before printing

### Rationale
- **Reduces friction**: Older adults can engage asynchronously, no phone anxiety
- **Reduces staff workload**: Community center staff don't need to manually forward links
- **Increases reach**: QR code can be shared in WeChat groups, printed on flyers
- **Maintains human option**: Phone number still available for those who prefer it

### Effort & Impact
- **Effort**: ~30 min (QR generation + poster update)
- **Impact**: Medium (may increase screening completion rate by 20-30%)
- **Risk**: Low (QR codes are standard, no privacy concerns if using official tools)

---

## Optimization #2: Add "What's In It For Me" Section

### Current State
Recruitment script focuses on:
- Study purpose (AI + memory research)
- Procedure (4 sessions, 7 days, 30 min each)
- Eligibility (60+, Chinese-speaking, etc.)

**Missing**: Clear, concrete participant benefits

### Proposed Addition

Add this section to recruitment script (after study purpose, before procedure):

```
【参与者收获】

1. 📖 免费获得个人"人生故事书"电子版
   - 约 5000-8000 字，记录您的人生经历
   - 含 AI 生成的个性化插图
   - 可分享给家人朋友，传承家族记忆

2. 🧠 4 次结构化回忆会话
   - 有助于提升情绪和认知活力
   - 在轻松氛围中回顾美好回忆
   - 专业引导员全程陪伴

3. 📊 个性化反馈报告
   - 每次会话后收到叙事质量评分
   - 了解您的叙事风格和优势
   - 获得认知健康建议

4. 💰 完成奖励
   - 完成全部 4 次会话后获得 200 元购物卡
   - 可用于超市、药店、书店等

5. 🌟 社会贡献
   - 为 Alzheimer's 研究和 AI 产品开发做出贡献
   - 帮助未来更多老年人享受科技红利
```

### Rationale
- **2026 evidence** (Yang 2026, IET 2026): Perceived personalization is key adoption driver
- **Behavioral economics**: Concrete benefits reduce ambiguity and increase commitment
- **B2C value prop testing**: This is essentially testing what benefits resonate with target users
- ** reciprocity principle**: Clear benefits make participants feel valued, not just "subjects"

### Effort & Impact
- **Effort**: ~15 min (script update)
- **Impact**: High (may increase screening-to-enrollment conversion by 15-25%)
- **Risk**: Low (benefits are accurate, no over-promising)

---

## Optimization #3: Pre-emptively Address Technology Anxiety

### Current State
- Technology anxiety is **measured** in pre-session survey (5 items)
- But no **proactive reassurance** before first contact

### Proposed Addition

Add this section to initial outreach script (early in conversation, after introductions):

```
【技术门槛说明】

很多叔叔阿姨担心自己不会用智能手机，其实完全不用担心：

✅ 不需要下载任何 APP
   - 只需要用微信就可以

✅ 不需要注册账号
   - 打开链接就能用

✅ 不需要打字
   - 可以用微信语音输入，说话就自动转成文字
   - 也可以直接发语音消息，我们帮您整理

✅ 每次会话 30 分钟
   - 一对一引导，工作人员全程在线
   - 遇到任何问题随时提问，马上有人回答

✅ 有家人协助更好
   - 如果子女/孙辈在旁边帮忙，会更轻松
   - 但即使一个人也可以完成

我们设计的时候就想好了：要让 60 岁以上的叔叔阿姨都能轻松使用。
您已经用过微信了吧？那就没有问题！
```

### Rationale
- **Yang 2026**: Technology anxiety is #1 barrier for older adults adopting digital RT
- **Proactive > reactive**: Addressing concerns before they're raised reduces dropout
- **Social proof**: "We designed this for people like you" builds trust
- **Concrete examples**: Specific statements ("no app download") are more reassuring than vague promises ("it's easy")

### Effort & Impact
- **Effort**: ~10 min (script update)
- **Impact**: High (may reduce pre-Day1 dropout by 20-30%)
- **Risk**: Low (all statements are accurate)

---

## Combined Impact Estimate

| Optimization | Effort | Conversion Impact | Dropout Impact |
|--------------|--------|-------------------|----------------|
| #1 QR Code | 30 min | +20-30% screening completion | — |
| #2 Benefits | 15 min | +15-25% screening→enrollment | — |
| #3 Tech Anxiety | 10 min | — | -20-30% pre-Day1 dropout |
| **Total** | **55 min** | **+35-55% overall enrollment** | **-20-30% dropout** |

**Note**: Impacts are estimates based on 2026 evidence (Yang 2026, IET 2026) and behavioral science principles. Actual impact should be measured during Path B pilot.

---

## Implementation Priority

**If V approves all 3**:
1. **Today (03-22)**: Implement #2 (Benefits) and #3 (Tech Anxiety) — script updates
2. **Tomorrow (03-23)**: Implement #1 (QR Code) — requires WeChat Work setup
3. **Day 1 of recruitment**: Use updated scripts and poster

**If V wants to test incrementally**:
1. Start with #2 (Benefits) — highest impact, lowest effort
2. Measure conversion rate for 3-5 days
3. Add #3 (Tech Anxiety) if pre-Day1 dropout is high
4. Add #1 (QR Code) if screening completion is bottleneck

---

## Measurement Plan

To validate these optimizations, track:

| Metric | Baseline (if available) | Target with Optimizations |
|--------|------------------------|---------------------------|
| Screening questionnaire completion rate | ? | >60% |
| Screening→Enrollment conversion | ? | >50% |
| Pre-Day1 dropout | ? | <10% |
| Day 1→Day 4 completion | ? | >80% |

**Data Collection**:
- Add tracking fields to screening questionnaire (source: QR code vs. phone referral)
- Log dropout reasons (technology anxiety, scheduling, health, other)
- Conduct exit interviews with dropouts (optional, 5 min phone call)

---

## Next Steps

**For V**:
1. Review all 3 optimizations
2. Approve/reject/modify each
3. If approved, Hulk can execute updates within 1 hour
4. If modifications needed, provide feedback and Hulk will revise

**For Hulk** (upon approval):
1. Update `metamemory_pilot_recruitment_package.md` with #2 and #3
2. Generate QR code instructions for #1
3. Update community contact script templates
4. Commit and push changes

---

*Prepared by Hulk 🟢 for V review and execution*
