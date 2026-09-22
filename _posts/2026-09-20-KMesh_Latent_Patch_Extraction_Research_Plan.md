---
title: KMesh Latent Patch Extraction Research Plan
lang: zh-CN
translation_key: kmesh-latent-patch-extraction
category: research
permalink: /posts/KMesh_Latent_Patch_Extraction_Research_Plan/
---

**Teacher Reasoning Trace → Persistent Task-Level Knowledge Patch**

> **状态**：研究计划草案 v0.1  
> **目标**：为 KMesh 定义并验证一种可操作的 latent knowledge patch：它从 teacher LM 的推理过程中提取，但不是逐 token 保存 raw Q/K/V；它应当在 task/subtask 时间尺度上保持稳定，并能被 student LM 在后续多个 token、多个 layer 中持续读取和复用。

---

## 1. 核心问题

KMesh 的长期目标是把知识从大模型的密集参数中部分外置，使知识能够：

- 独立寻址；
- 局部更新；
- 稀疏激活；
- 跨任务复用；
- 与其他 patch 组合；
- 在 GPU / RAM / SSD 之间分层存储；
- 随使用过程持续演化。

在 teacher–student 路线中，一个关键问题是：

> **Teacher 在一次 reasoning episode 中形成的大量 token-level hidden states / Q / K / V / attention patterns，能否被压缩成少量、稳定、task-level 的 latent slots，并作为 student 的长期可读 knowledge patch？**

这个 patch 不应只是 teacher 某一 token 的瞬时 activation，也不应简单保存完整 raw KV cache。

我们希望得到的是：

$$
\text{Teacher reasoning trajectory}
\rightarrow
\text{compact persistent patch}
\rightarrow
\text{Student repeated reuse}
$$

---

## 2. 工作假设

### H1. Task-Level Stable Latent Exists

Teacher 在完成一个 task/subtask 时，虽然 token-level activation 持续变化，但其中存在跨越多个 token 持续有效的低维信息。

这些信息应当比单个 token activation 更稳定，并能够在不同表述、不同上下文下复用。

### H2. Patch Should Persist Longer Than a Token

Knowledge patch 的时间尺度应当明显长于 token。

典型生命周期：

- 一个 reasoning episode；
- 一个 subtask；
- 数十到数千个 token；
- 在 student 后续多个 layer 中持续可读。

因此 KMesh runtime 应采用：

$$
\text{slow working-set routing}
+
\text{fast token-level reading}
$$

而不是每个 token 都重新从 RAM/SSD 检索和加载 patch。

### H3. Teacher Q/K/V Contain Different Kinds of Information

粗略功能解释：

- **K**：什么时候这份知识应该被找到；
- **V**：找到后，它提供什么信息；
- **Q**：基于当前知识状态，接下来应该寻找什么。

因此 KMesh patch 不应只保存“知识内容”，还应保存或学习：

> **这份知识通常应该与哪些其他知识发生关系。**

但 raw teacher Q 是强上下文相关、layer-specific 的瞬时量，所以更合理的是：

> 从 teacher 的 Q / K / attention behavior 中提炼 persistent query policy，而不是逐 token 保存 raw Q。

### H4. Hidden / Residual State Is a Better Canonical Source Than Raw K/V

Teacher residual / hidden state 位于 Q/K/V 投影之前，更接近一种通用内部表示。

长期候选路径：

$$
\text{Teacher hidden/residual trace}
\rightarrow
\text{Patch Compiler}
\rightarrow
Z_P
$$

然后 student 自己把：

$$
Z_P
$$

编译成自身 layer-specific 的：

$$
K_P^{S,\ell},V_P^{S,\ell},Q_P^{S,\ell}
$$

或更一般的 query policy。

### H5. Compact Oracle Patch Should Exist Before We Learn to Extract It

在训练 Patch Compiler 之前，应先回答：

> **Student 是否本来就可以通过 4/8/16 个 latent slots，获得足够的 task-level 辅助能力？**

因此首先直接优化 student-side latent slots：

$$
Z_P^*
=
\arg\min_Z
L_{\text{task}}(Student(x,Z))
$$

如果这个 oracle patch 都无法显著帮助 student，则不应优先投入 teacher → patch extraction。

---

## 3. KMesh Patch 的候选抽象

长期候选：

$$
P_i=
(
id_i,
content_i,
Z_i,
\Pi_i^Q,
relations_i,
version_i,
provenance_i
)
$$

其中：

- `id_i`：稳定 Patch ID；
- `content_i`：可解释文本/结构化内容；
- `Z_i`：canonical latent content；
- `Π_i^Q`：persistent query / navigation policy；
- `relations_i`：与其他 patch 的显式或统计关系；
- `version_i`：版本；
- `provenance_i`：来源。

第一阶段实验不必实现全部字段。

---

## 4. Patch 的运行时语义

### 4.1 Load Once, Read Many

在 subtask 边界加载：

$$
Z_P
$$

一次性编译为 student 某些 reader 所需的：

$$
K_P^{(\ell)},V_P^{(\ell)}
$$

之后数百 token 反复读取：

$$
\alpha_{t,i}^{(\ell)}
=
\operatorname{softmax}
(
Q_t^{(\ell)}K_{P_i}^{(\ell)T}
)
$$

而 patch 内容本身保持不变。

### 4.2 Coarse Residency, Fine-Grained Reading

驻留工作集：

$$
W_\tau
$$

在较长时间尺度上更新。

每个 token / layer 只在驻留 working set 内进行动态 attention。

即：

```text
global retrieval / prefetch
        ↓
resident patches
        ↓
token-level Q/K attention
        ↓
cheap repeated reading
```

### 4.3 Query Policy

如果 patch 只是 passive memory：

$$
P=(K,V)
$$

即可。

但 KMesh 希望支持：

$$
P_A
\rightarrow
P_B
\rightarrow
P_C
$$

这种 multi-hop knowledge navigation。

因此更长期的 patch 应具备某种：

$$
\Pi_i^Q
$$

结合当前 task state：

$$
Q_i(t)
=
f(\Pi_i^Q,g_t)
$$

表达：

> 使用这份知识后，接下来应该寻找什么。

---

## 5. Teacher Trace 应该记录什么？

Teacher 进行完整 reasoning episode 时，记录精选 layer 的内部状态。

候选 trace：

$$
\mathcal T=
\{
H^{(\ell)},
Q^{(\ell)},
K^{(\ell)},
V^{(\ell)},
A^{(\ell)}
\}
$$

其中：

- $$H$$：residual / hidden states；
- $$Q$$：query trajectory；
- $$K$$：addressing representation；
- $$V$$：payload representation；
- $$A$$：attention logits / weights / attended structure。

### 5.1 不建议默认保存 post-RoPE Q/K

如果模型使用 RoPE，post-RoPE Q/K 含 token position rotation。

跨 token 做平均会把：

- semantic variation；
- positional rotation；

混在一起。

优先考虑：

- hidden / residual state；
- pre-RoPE Q/K；
- V；
- attention logits / relations；
- attention output。

### 5.2 不建议全层 dump 作为长期方案

第一阶段最多记录少量代表层。

原因：

- I/O 很大；
- layer space 不一致；
- 后续难以解释贡献；
- 容易让 Patch Compiler 变复杂。

初始建议：

- early-middle layer；
- middle layer；
- middle-late layer；

共 3–4 个候选层。

具体层号根据 teacher 深度比例选择，而不是写死绝对层号。

---

## 6. Research Stage 0: Oracle Patch

这是最高优先级。

### 6.1 目的

验证：

> **student 的 patch interface 是否真的可以用很少 latent slots 承载 task-level 辅助信息。**

### 6.2 方法

冻结 student backbone。

为每个 task / task family 创建：

$$
Z\in\mathbb R^{m\times d}
$$

其中：

$$
m\in\{1,4,8,16\}
$$

直接用 task loss 优化 $$Z$$。

例如：

$$
Z^*
=
\arg\min_Z
L_{\text{answer}}
$$

可选择让 patch 注入：

- 1 个 layer；
- 3 个 layer；
- 旁路 reader；
- cross-attention memory。

### 6.3 必做对照

#### No Patch

student 原始能力。

#### Text Patch

相同知识通过文本 context 给 student。

#### Random Latent

同尺寸随机向量。

#### Oracle Latent

直接梯度优化的 patch slots。

### 6.4 关键问题

1. 4/8/16 slots 是否足够？
2. 同一 patch 能否跨多个 query 复用？
3. 一个 patch 能否持续 256/512/1024 token 有效？
4. 注入一次后，后续是否需要重复刷新？
5. patch 注入在哪些层最有效？
6. 多 patch 能否组合？

### 6.5 继续条件

如果 oracle latent 相比：

- no patch；
- random patch；
- text patch；

不能显著提升同一知识族的 held-out tasks，则暂停 teacher latent extraction，优先重做 student patch interface。

---

## 7. Research Stage 1: Non-Learned Extraction Baselines

在训练复杂 Patch Compiler 前，先测试简单 pooling。

### 7.1 Single Marker Token

Teacher 输入末尾增加：

```text
<KMESH_PATCH>
```

取某层该 token 的 hidden state：

$$
Z=h_{\text{marker}}^{(\ell)}
$$

如果 student 能利用，这是最简单的可复用 latent patch。

### 7.2 Mean Pooling

对某层 episode hidden states：

$$
z_\ell
=
\frac1T
\sum_t h_t^{(\ell)}
$$

可比较：

- all-token mean；
- answer/reasoning-only mean；
- masked mean；
- final-window mean。

### 7.3 Exponential Moving Average

$$
z_t
=
\beta z_{t-1}
+
(1-\beta)h_t
$$

测试：

$$
\beta \in
\{0.9,0.99,0.999\}
$$

看持续状态是否优于普通平均。

### 7.4 Fixed Temporal Sampling

例如每个 episode 取：

- 25%；
- 50%；
- 75%；
- end；

的 hidden states，再拼接/投影。

### 7.5 Selected-Head / Function-Vector Style Pooling

分析少数 attention heads 的输出或 attention behavior，寻找具有明显 task-level utility 的 head。

不要求 student 复制 raw Q/K/V，而是测试：

> teacher 是否已经在少量 head 中形成 compact task representation。

---

## 8. Research Stage 2: Learned Patch Compiler

如果 oracle patch 明显有效，而简单 pooling 仍与 oracle 有较大差距，进入这一阶段。

### 8.1 基本架构

输入：

$$
\mathcal T
=
\text{teacher trace}
$$

先对不同 layer/head 投影：

$$
x_{t,\ell,h}
=
P_{\ell,h}(
H,Q,K,V,A
)
$$

然后使用：

$$
m
$$

个 learned patch queries：

$$
R=[r_1,\ldots,r_m]
$$

做 cross-attention：

$$
Z_P
=
\operatorname{CrossAttn}
(
R,
\mathcal T,
\mathcal T
)
$$

得到固定大小：

$$
Z_P\in\mathbb R^{m\times d_P}
$$

### 8.2 初始架构应尽量小

第一版限制 Patch Compiler：

- 1–2 层 cross-attention；
- 小 hidden size；
- 参数规模远小于 student；
- 不能演化成另一个大模型。

否则无法证明收益来自 patch extraction，而不是隐藏的额外计算能力。

---

## 9. Teacher Q/K/V 如何使用？

### 9.1 Hidden / Residual as Main Content Signal

把：

$$
H
$$

作为 patch 内容的主来源。

原因：

- 位于 Q/K/V 投影之前；
- 更通用；
- 跨 reader 迁移更自然；
- 包含 attention + MLP 后的综合状态。

### 9.2 Q/K as Navigation Signal

Q/K 主要用于学习：

> knowledge navigation / relation structure。

不要求 student raw Q 等于 teacher raw Q。

更合理的是迁移：

$$
QK^\top
$$

所体现的 relation geometry。

例如 teacher attention target：

$$
A_T
=
\operatorname{softmax}
(
Q_TK_T^\top
)
$$

student patch reader：

$$
A_S
=
\operatorname{softmax}
(
Q_SK_S^\top
)
$$

可加入：

$$
L_{\text{relation}}
=
D_{KL}(A_T\|A_S)
$$

### 9.3 V as Payload Signal

V / attention output 可作为：

> teacher 当前真正向后续计算传递了什么内容

的辅助信号。

但不直接假设 raw V 是 canonical patch。

---

## 10. Patch Compiler 的训练目标

不要以“重建 teacher 全部 activation”为主要目标。

核心目标是：

> 让 student 使用 patch 后完成 task，并保留 teacher 的必要 relation behavior。

建议：

$$
L
=
L_{\text{task}}
+
\lambda_1L_{\text{behavior}}
+
\lambda_2L_{\text{consistency}}
+
\lambda_3L_{\text{composition}}
+
\lambda_4L_{\text{bottleneck}}
$$

### 10.1 Task Loss

$$
L_{\text{task}}
$$

student 最终任务输出。

这是主要损失。

### 10.2 Teacher Behavior Loss

可蒸馏：

- answer logits；
- intermediate attention relation；
- selected patch ranking；
- next-knowledge retrieval behavior。

不要求内部坐标相同。

### 10.3 Cross-Context Consistency

同一知识/技能在不同表述和上下文中：

$$
\mathcal T_1,
\mathcal T_2,
\mathcal T_3
$$

应产生相近 patch：

$$
Z_1\approx Z_2\approx Z_3
$$

可以使用：

- cosine consistency；
- contrastive loss；
- matching / set loss。

### 10.4 Composition Loss

若：

$$
P_A+P_B
$$

应共同解决问题，则训练 student 使用两者完成 held-out composition。

避免 patch 只记住单独任务答案。

### 10.5 Bottleneck Loss

控制 patch：

- slot 数；
- dimension；
- norm；
- information capacity。

目标是找到：

> 最小但足够有用的 persistent latent state。

---

## 11. Temporal Structure

简单 mean pooling 假设整个 episode 只有一个状态，这可能不成立。

### 11.1 First Version

使用固定：

$$
m=4/8/16
$$

learned slots。

让 slots 自己学习不同 phase。

### 11.2 Later Version: Change-Point Aware

如果发现 reasoning trajectory 有明显 phase：

$$
S_1\rightarrow S_2\rightarrow S_3
$$

可研究：

- hidden cosine change；
- attention distribution shift；
- Q distribution shift；

检测阶段边界。

不同阶段压缩为：

$$
z_1,z_2,z_3
$$

再形成 patch。

这一阶段不是首轮必做。

---

## 12. Student Patch Reader

Patch Compiler 与 student reader 必须分开。

### 12.1 Input

$$
Z_P
$$

是 persistent canonical patch。

### 12.2 Compile on Load

patch 被加载到 GPU 时，一次性计算：

$$
K_P^{(\ell)}
=
W_{K,\ell}^{S}Z_P
$$

$$
V_P^{(\ell)}
=
W_{V,\ell}^{S}Z_P
$$

对某些 reader layer 缓存这些 K/V。

### 12.3 Token-Level Use

每个 token：

$$
Q_t^{(\ell)}
=
W_{Q,\ell}^{S}h_t
$$

读取：

$$
\alpha_{t,P}
=
\operatorname{softmax}
(
Q_tK_P^\top
)
$$

不重新 encode patch。

### 12.4 Query Policy Extension

后续研究可增加：

$$
\Pi_P^Q
$$

用于：

$$
Q_P(t)
=
f(
\Pi_P^Q,
g_t
)
$$

表示：

> 使用这份知识以后，下一步应该检索什么。

这一机制与 KMesh graph / multi-hop retrieval 相连。

---

## 13. Dataset Design

第一阶段不要直接使用大规模开放世界数据。

需要可以验证 patch utility 的受控数据。

### 13.1 Synthetic Rule World

继续使用 KMesh E0 数据。

优点：

- ground truth 清晰；
- 知道哪些 patch 必须组合；
- 可以制造 counterfactual update；
- 可以测 multi-hop。

适合先验证 latent patch interface。

### 13.2 Small Real-World Task Families

第二阶段加入真实任务，例如：

- Wikidata factual relations；
- HotpotQA multi-hop；
- 小型 coding API / rule tasks；
- MQuAKE knowledge updates。

每个 patch 都必须有：

- source；
- task family；
- held-out queries；
- composition tests。

---

## 14. Teacher Data Collection

Teacher 应为开放权重模型，以便访问内部 activation。

### 14.1 Required Logs

每个 reasoning episode 保存：

- input / prompt；
- teacher output；
- selected layer hidden states；
- pre-RoPE Q/K；
- V；
- attention logits or top-k attention structure；
- optional MLP activations；
- task result / verifier result。

### 14.2 Avoid Full Trace Storage When Possible

先在线提取 summary statistics / selected states。

完整 raw trace 只保留少量样本用于分析。

否则 storage 和 I/O 会很快成为主要成本。

---

## 15. Core Experiments

### Experiment A: Does Compact Oracle Patch Exist?

比较：

- no patch；
- text patch；
- random latent；
- 1-slot oracle；
- 4-slot oracle；
- 8-slot oracle；
- 16-slot oracle。

指标：

- held-out task accuracy；
- cross-context reuse；
- composition；
- patch read FLOPs；
- patch bytes。

### Experiment B: Which Teacher Signal Is Most Useful?

固定 student + patch size。

比较：

- hidden only；
- Q/K relation only；
- V only；
- hidden + Q/K relation；
- hidden + Q/K/V；
- hidden + attention output。

不比较 raw coordinate reconstruction。

### Experiment C: Simple Smoothing vs Learned Compiler

比较：

1. marker token；
2. mean pooling；
3. EMA；
4. fixed temporal sampling；
5. selected-head pooling；
6. learned 4-slot resampler；
7. learned 8-slot resampler；
8. oracle upper bound。

### Experiment D: Patch Persistence

生成一次 patch 后，测试 student：

- 64 tokens；
- 256 tokens；
- 512 tokens；
- 1024 tokens；

不刷新 patch。

观察 utility 随时间是否快速衰减。

### Experiment E: Cross-Context Reuse

Teacher 从 context A 生成 patch。

Student 在：

- B；
- C；
- D；

不同表面形式但同一知识/技能的任务中使用。

这是区别：

> task knowledge patch

和：

> compressed episode cache

的关键实验。

### Experiment F: Multi-Patch Composition

分别从独立 teacher episode 提取：

$$
P_A,
P_B,
P_C
$$

student 在从未联合训练过的任务上使用：

$$
P_A+P_B
$$

或：

$$
P_A+P_B+P_C
$$

测试 composability。

---

## 16. Ablations

必须至少包含：

### Teacher Layer

不同 source layer。

### Patch Size

1 / 4 / 8 / 16 / 32 slots。

### Student Reader Layer

early / middle / late / multi-layer。

### Patch Refresh Frequency

never / 1024 / 512 / 128 token。

### Teacher Signals

H / QK relation / V / combination。

### Compiler Capacity

linear / MLP / 1-layer cross-attn / 2-layer cross-attn。

---

## 17. Metrics

### Quality

- task accuracy；
- exact match；
- verifier pass；
- multi-hop accuracy。

### Generalization

- held-out phrasing；
- held-out entity；
- held-out composition；
- cross-task transfer。

### Patch Efficiency

- bytes per patch；
- slots per patch；
- read FLOPs；
- compile FLOPs；
- load latency。

### Persistence

- accuracy vs tokens since load；
- utility half-life。

### Portability

- same patch across multiple students；
- reader size；
- retraining cost。

### Composition

- pair composition；
- 3-way composition；
- composition after sequential patch updates。

---

## 18. Failure Modes

### F1. Oracle Patch Does Not Help

说明 student patch interface 不够强，或 task 本身无法被小 latent memory 表达。

优先改 reader，不改 Patch Compiler。

### F2. Mean Pooling Equals Oracle

这是好结果。

说明 task-level state 很简单，不需要复杂 compiler。

### F3. Learned Compiler Works Only on Same Prompt

说明提取的是 episode cache，不是 reusable knowledge。

加强 cross-context training。

### F4. Deep Teacher Layers Hurt

可能表示 teacher representation 太 model-specific。

尝试中层、multi-layer pooling、relation distillation。

### F5. Patch Utility Quickly Decays

可能需要：

- recurrent refresh；
- task state interaction；
- query policy；
- multi-stage patch。

### F6. Multi-Patch Composition Fails

这是最重要的风险之一。

需要结合：

- KMesh relation graph；
- coactivation training；
- A³E-style composition evaluation；
- graph-guided compatibility training。

---

## 19. Implementation Plan

建议仓库增加：

```text
kmesh/
├── teacher_trace/
│   ├── hooks.py
│   ├── recorder.py
│   ├── qkv_capture.py
│   └── trace_format.py
├── patch/
│   ├── oracle_patch.py
│   ├── pooling.py
│   ├── compiler.py
│   ├── patch_format.py
│   └── query_policy.py
├── student/
│   ├── patch_reader.py
│   ├── patch_attention.py
│   └── resident_cache.py
├── experiments/
│   ├── oracle/
│   ├── pooling/
│   ├── compiler/
│   ├── persistence/
│   └── composition/
└── eval/
    ├── metrics.py
    ├── composability.py
    └── persistence.py
```

---

## 20. Milestones

### M0 — Student Patch Interface

- [ ] student 支持固定 latent slots；
- [ ] patch 可在一个 episode 内持续读取；
- [ ] 支持 1/4/8/16 slots；
- [ ] patch 物理加载位置不影响结果。

### M1 — Oracle Patch

- [ ] task-specific latent slots 可直接优化；
- [ ] 画出 patch size → quality curve；
- [ ] 验证 cross-context reuse；
- [ ] 验证 multi-patch composition。

**Go/No-Go：**
如果 oracle patch 不能达到明显收益，不进入复杂 teacher extraction。

### M2 — Teacher Trace Recorder

- [ ] hidden state capture；
- [ ] pre-RoPE Q/K；
- [ ] V；
- [ ] attention relation；
- [ ] configurable layer/head selection。

### M3 — Non-Learned Patch Extraction

- [ ] marker token；
- [ ] mean；
- [ ] EMA；
- [ ] fixed sampling；
- [ ] selected-head pooling。

### M4 — Learned Patch Compiler

- [ ] fixed-slot cross-attention resampler；
- [ ] 4/8/16 slots；
- [ ] student task loss；
- [ ] cross-context consistency；
- [ ] relation distillation。

### M5 — Persistent Query Policy

- [ ] 从 teacher Q/K behavior 学习 patch navigation；
- [ ] patch 产生 next-patch query；
- [ ] 与 KMesh coactivation graph 联动。

---

## 21. Research Claims We Should NOT Make Yet

当前阶段不要声称：

- 已找到通用 knowledge latent；
- teacher Q/K/V 可以无损压缩；
- patch 能跨任意模型直接使用；
- KMesh 可以替代 foundation-model pretraining；
- 4/8 slots 足以保存复杂知识；
- task vector 就等于知识 patch；
- local update 已解决 global composability。

当前真正要验证的是：

> **是否存在一种 compact, persistent, reusable task-level latent state，使小 student 能够复用 teacher reasoning episode 中具有跨上下文价值的知识和知识导航行为。**

---

## 22. Central Research Question

> **Can a teacher model’s token-level reasoning trajectory be compiled into a small persistent latent patch that preserves both what the teacher knows and how that knowledge should connect to other knowledge, and can a smaller student reuse that patch across many downstream tokens and contexts?**

中文：

> **能否把 teacher LM 在一次推理过程中的 token-level 内部轨迹，编译成少量、持续存在的 latent knowledge patch，使其同时保留“知道什么”和“应与哪些知识发生关系”，并让更小的 student 在后续多个 token 和不同上下文中反复复用？**

---

## 23. Immediate Next Step

第一步不要训练 Patch Compiler。

先完成：

1. student patch reader；
2. oracle patch optimization；
3. patch size / persistence / composition 三组实验。

只有确认：

$$
\text{small persistent latent patch exists}
$$

之后，再投入 teacher Q/K/V trace extraction 和 Patch Compiler 研究。

这会大幅降低研究风险，并让后续所有结果更容易解释。
