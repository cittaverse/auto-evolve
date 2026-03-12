好的，作为认知心理学和人工智能领域的专家研究员，我将为您精确分析并总结这篇论文。

以下是根据您的要求提取和总结的详细信息，以清晰的 Markdown 结构化格式呈现。

---

### 论文分析：《Modeling Memories, Predicting Prospections: Automated Scoring of Autobiographical Detail Narration using Large Language Models》

#### 1. **确切的提示/指令 (The Exact Prompts/Instructions)**

论文中没有使用传统的、在推理时（inference time）提供给模型的文本提示（prompt）。研究人员采用了一种**微调（fine-tuning）**的方法，将任务构建为一个**连续回归问题（continuous regression problem）**，而非分类任务。

因此，该方法不属于 Few-Shot、Zero-Shot 或 Chain-of-Thought 的范畴。模型的“指令”是通过在带有标签的数据集上进行训练而内化的。

*   **输入 (Input)**: 模型直接处理**未经任何预处理的原始访谈转录稿**。这些转录稿包含了访谈者的问题、探针（probes）、参与者的回答、填充词（如 "uh", "um"）、时间戳以及为保护隐私而设置的占位符。
*   **输出 (Output)**: 模型被训练来为每个转录稿输出一个**连续的数值**，该数值代表内部细节（internal details）或外部细节（external details）的总数。研究人员为内部和外部细节分别训练了两个独立的模型适配器（adapters）。

论文在第15页提供了一个虚构的输入示例文本，以展示模型处理的数据格式。这并非一个“提示”，而是模型接收的原始数据样本：

> Q: [1:15] Now can you tell me about me about an event at a specific time and place from your teenage years?
>
> [1:20] Yeah, sure, uh, I remember this one time when my friends and I decided to camp out at [Local Park Name]. We, uh, packed all our stuff, like tents and food, and rode our bikes there after school. I think there were five of us? It was me, [Female Name 1], [Male Name 2], and a couple of others. Anyway, we set up right next to this big tree, and we were just, uh, hanging out, telling stories... even roasted marshmallows on this little fire pit we made. It got pretty late, probably around midnight, and then we realized we forgot sleeping bags. We just ended up using our jackets and, you know, talking until we fell asleep. [2:05]
>
> General Probe: [2:10] Any other details you remember from that event?
>
> [2:12] Oh, yeah, it was freezing! [2:13]

#### 2. **使用的大语言模型 (LLM Models Used)**

*   **使用的具体模型**: 论文中明确指出，他们选择并微调了 Meta 的 **LLaMA-3** 模型。具体来说，是拥有 **80亿（8 billion）参数**的版本。
*   **表现最佳的模型**: 研究中**并未评估多个不同的 LLM**。他们仅使用了 LLaMA-3。因此，在该研究的框架内，LLaMA-3 是唯一使用且表现符合研究目标的模型。

#### 3. **评估指标 (Evaluation Metrics)**

研究人员使用**皮尔逊相关系数 (Pearson's r)** 来评估模型的评分与人类评分员之间的一致性。他们将模型的评分分别与两位人类评分员的平均分以及每位评分员的独立分数进行比较，并以两位人类评分员之间的一致性作为基准。

*   **与人类评分员的最高一致性**:
    *   对于**内部细节 (Internal Details)**，模型评分与人类平均分的最高相关性达到了 **r = 0.87** (95% CI [.82, .91])。
    *   对于**外部细节 (External Details)**，模型评分与人类平均分的最高相关性达到了 **r = 0.84** (95% CI [.77, .89])。
*   **总体表现**: 模型的表现与人类评分员之间的一致性水平相当，甚至在某些情况下（如数据集A的内部细节评分）超过了两位人类评分员之间的一致性（模型 vs. 人类平均 r = 0.87，人类1 vs. 人类2 r = 0.76）。在完全独立的测试集（Dataset C）上，相关性略有下降，但仍然保持了很强的关联性。

#### 4. **评分规则/细微差别 (Scoring Rules/Nuances)**

*   **是否引入新规则**: **没有**。研究明确指出，所有的人工评分和模型训练的目标都严格遵循了传统的 **Levine (2002) 版《自传体访谈 (Autobiographical Interview)》评分手册**。该研究的目标是自动化现有的人工评分流程，而不是修改或创建新的评分标准。
*   **方法上的细微差别/创新**:
    *   与传统人工评分过程相比，最大的“细微差别”在于**自动化方法**本身。该模型的核心创新在于其能够处理**原始、未经处理的（raw, unprocessed）**文本。
    *   这意味着模型在评分时能够自动忽略访谈者的话语、填充词和时间戳等“噪音”，而无需进行耗时的人工数据清洗或预处理步骤。这与之前一些需要干净、格式化文本的自动化方法形成了鲜明对比。