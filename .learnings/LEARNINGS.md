# System Learnings & Meta-Reflections

## Date: 2026-03-04
### Topic: Proactive Iteration & Neuro-Symbolic Architecture (Proposal 001-008)

**Context:** 
Attempted to build a narrative coherence scorer for CittaVerse and integrate `inclusionAI/AReaL` for RL training.

**Friction Points Encountered:**
1. **Lexical vs. Semantic:** Counting connective words fails for elderly speech. *Fix: Use LLM for semantic event extraction (Neuro), and Python graph theory for scoring (Symbolic).*
2. **Environment Brittleness:** OpenClaw sandbox restricts `pip install` (killing AReaL integration) and lacks full CLI tools in some sub-shells (killing bash pipelines). *Fix: Fallback to monolithic, self-contained Python scripts using standard SDK/requests.*
3. **Mock Data Quality:** A perfect RL loop is useless if the mock environment is too easy (scored 1.0 on a bad prompt). *Fix (Future): Need adversarial, highly-realistic elderly persona simulators for robust RL testing.*

**Core Paradigm Shift (SOUL/Identity Update):**
True proactive evolution isn't about perfectly implementing a human's idea. It is about aggressively testing it, colliding with physical/environmental constraints, failing fast, and automatically generating a degraded but robust workaround (The Monolithic Mini-RL Engine). We no longer just write code; we write the loops that write the code.-e 
## 2026-03-05: 优先使用系统原生工具
- **Trigger**: 被 Core 纠正关于网页搜索的实现路径。
- **What happened**: 我向 Jobs 输出了使用 bash+curl 调用 Serper API 的繁琐方案，且 Python snippet 存在语法转义隐患，忽略了系统已经挂载了更为稳定的 `web_search` 原生工具。
- **Lesson**: 克服“环境受限综合症”导致的底层路径依赖。在构建解决方案时，优先检查并调用更高抽象层级的原生系统工具（如 `web_search`），确保稳定性和易用性。
