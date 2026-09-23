---
title: KMesh：以可局部更新的知识补丁构建持续演进的神经记忆
lang: zh-CN
translation_key: kmesh-paper-framework
category: research
permalink: /posts/KMesh_Paper_Framework/
---

# KMesh：面向局部更新与持续演进的知识网络架构
## ——研究框架草案 / Paper-like Research Outline

> **状态说明**：本文档不是论文初稿，而是借用论文结构整理目前关于 KMesh 的研究思路、相关工作、关键假设和后续实验计划。  
> 其中很多观点仍然只是待验证的工作假设，目的在于帮助后续研究和工程实现保持一致，而不是提前下结论。

---

## 0. Working Title

**KMesh: Locally Updatable Knowledge Patches for Continually Evolving Neural Memory**

可选副标题：

- **Aligning Semantic Locality with Parameter, Computation, and Update Locality**
- **A Knowledge Mesh for Sparse, Composable, and Continually Evolving AI**
- **Local Updates, Global Composition**

---

# 1. Abstract / 核心问题

当前大语言模型把大量知识、推理能力和语言处理能力混合编码在同一套密集神经网络参数中。  
这种设计带来了很强的统一建模能力，但也造成几个根本问题：

1. 新知识通常需要重新训练或微调整个模型；
2. 很难明确定位某一条知识对应哪些参数；
3. 即使一次任务只涉及极少量知识，forward/backward 往往仍需要访问大部分或全部主干参数；
4. 模型容量、GPU 显存、训练计算和知识容量高度耦合；
5. 局部知识修改容易干扰已有知识，而多个独立修改又可能无法稳定组合；
6. 大规模模型训练依赖 FSDP、ZeRO、tensor parallel 等手段去分摊整个 dense tensor，而不是让当前任务只访问真正需要的知识参数。

KMesh 探索另一种架构假设：

> **将知识组织成可独立寻址、局部更新、稀疏激活的 knowledge patches，并让这些 patches 组成一个持续演进的知识网络。一个相对较小的共享神经计算核心根据当前任务，从知识网络中选择少量相关 patch 进行读取、组合和更新。**

KMesh 希望最终实现：

$$
\text{Semantic Locality}
\rightarrow
\text{Parameter Locality}
\rightarrow
\text{Computation Locality}
\rightarrow
\text{Update Locality}
$$

同时仍然保持：

$$
\text{Global Composability}
$$

核心科学问题不是“能否局部修改一些参数”，因为 embedding、MoE、LoRA、model editing 等研究已经证明这一点在不同形式下可行。

KMesh 真正要验证的是：

> **能否让语义上局部的一份知识，自然映射成计算和参数上的局部对象，并在独立局部更新后仍然与整个知识网络保持可组合性。**

---

# 2. Motivation / 为什么需要 KMesh

## 2.1 当前 LLM 将知识与计算混在一起

对于普通 Transformer：

$$
y = xW
$$

即使当前样本只涉及一条局部知识，dense matrix $$W$$ 仍通常整体参与 forward，反向传播也会影响大量参数。

因此：

> “当前任务只涉及少量知识”

并不能自动转化为：

> “当前任务只需要少量参数和计算”。

这也是 FSDP / ZeRO 等系统存在的背景：完整 tensor 仍然是计算图的一部分，只能把它分片、聚合、再分片。

KMesh 的目标不是做一个更聪明的 FSDP，而是尝试改变这个前提：

> 当前任务本来就只需要访问整个知识空间中的很小一部分。

## 2.2 知识容量是否必须等于活跃计算容量？

近年的 MoE、Memory Layers、Engram 等工作已经不断提示：

- 总参数量可以远大于每 token 激活参数量；
- 记忆容量可以远大于主干计算容量；
- 静态知识可以通过 lookup / sparse memory 方式从神经计算中外置；
- 很大的 memory table 不一定必须常驻 GPU HBM。

KMesh 希望继续推进：

$$
\text{Conditional Computation}
\rightarrow
\text{Conditional Memory}
\rightarrow
\text{Structured, Editable Knowledge Memory}
$$

## 2.3 持续学习比一次性预训练更重要

如果知识更新必须周期性重新训练整个模型，那么：

- 模型越大，更新越昂贵；
- 新知识加入越频繁，维护成本越高；
- 个体化模型难以持续成长；
- desktop / laptop / cellphone 等资源受限设备很难长期独立维护自己的 AI。

KMesh 希望支持：

```text
添加一个 patch
修改一个 patch
撤销一个 patch
局部训练若干 patch
更新局部关系
↓
整体知识网络继续工作
```

而不是：

```text
新知识
↓
重新做大规模训练
```

这与长期的 **AI for Everyone** 愿景一致：让 AI 的能力增长不必始终依赖巨型 GPU 集群。

---

# 3. Central Hypotheses / 核心假设

## H1. Knowledge Locality

一个具体任务通常只需要访问整个知识网络中的一小部分知识。

$$
|W_t| \ll |\mathcal K|
$$

其中 $$\mathcal K$$ 是整个知识网络，$$W_t$$ 是当前任务所需 working set。

## H2. Update Locality

新增或修改知识时，不必重新训练整个知识系统，只需要更新少量 patch 及其局部关系。

## H3. Computation Locality

如果知识被组织成可寻址 patch，则未被选择的 patch 可以完全不参与本轮 forward/backward。

这比“只冻结参数但仍参与 forward”的 LoRA 更强。

## H4. Global Composability

虽然知识局部存储和更新，但任务可以动态组合多个独立 patch，形成未见过的新知识组合。

这是最困难的假设之一，也是 A³E 所提示的核心风险。

## H5. Functional Relations Can Be Learned

patch 之间的关系不应该只由文本 embedding similarity 决定。

模型实际运行过程中：哪些 patch 经常共同激活、哪些 patch 经常顺序激活、哪些组合带来协同、哪些组合产生冲突，这些运行时信号可以帮助知识图逐渐形成更有功能意义的拓扑。

## H6. Abstraction Can Emerge Without Fixed Hierarchy

KMesh 不预先区分“摘要 patch”“普通 patch”“高层 patch”“低层 patch”。所有 patch 使用统一表示。

某些 patch 可能因为跨任务复用、连接多个知识区域、能够指导大量具体知识的使用，逐渐成为逻辑上的核心节点。不同 Transformer layer / reader 可能形成不同的读取偏好，从而出现功能上的抽象分工。

---

# 4. Related Work / 相关研究

KMesh 并不是从零开始的概念，而是多条已有研究线的汇合。

## 4.1 Sparse Embedding / Recommender Systems

Embedding table 很早就实现了：

```text
巨大参数空间
↓
按 ID 读取少量 rows
↓
只更新被访问的 rows
```

word2vec、推荐系统 embedding table 都已经证明：总参数容量很大，而单次 forward/backward 只处理极少部分参数，是完全可行的。

KMesh 的挑战在于：知识没有显式 user_id / word_id，必须通过语义和推理状态进行寻址。

## 4.2 Mixture of Experts

Sparsely-Gated MoE、Switch Transformer、DeepSeekMoE 等工作证明：

$$
\text{Large Total Capacity}
\neq
\text{Large Activated Compute}
$$

只有少数 expert 参与当前 token 的计算。

MoE 可以被理解成 **parameter locality induced by routing**。KMesh 希望从 conditional compute 进一步推进到 **conditional knowledge**。

## 4.3 Product-Key Memory / Memory Layers at Scale

Product-Key Memory 直接向 Transformer 中加入大规模稀疏 key-value memory。

**Memory Layers at Scale** 更进一步探索：

- 多个 Transformer 层共享同一 memory；
- 大 memory 只激活少量 entries；
- memory capacity 与主干网络计算能力部分解耦。

这对 KMesh 的两个假设提供直接支持：memory 可以跨层共享；knowledge-like capacity 不必全部塞进 FFN / dense weights。

## 4.4 End-to-End Memory Networks

End-to-End Memory Networks 展示了一个模型可以对外部记忆进行多跳读取，并通过多轮 memory access 完成推理。

这与 KMesh 的 multi-patch composition 很接近。区别在于 KMesh 进一步关心 memory 本身持续更新、patch 之间有长期关系、patch 可以分页和局部训练。

## 4.5 Engram

DeepSeek 的 Engram 是 KMesh 最相关的近期工作之一。

它将模型容量拆成：

$$
\text{Conditional Computation}
+
\text{Conditional Memory}
$$

并使用 N-gram hash 直接访问巨大 memory table。

Engram 对 KMesh 的重要启发：

1. **知识可以外置**：部分静态知识不必依赖 Transformer 层不断重新计算。
2. **Retrieve 与 Use 应分开**：memory 被召回之后，还需要 contextual gating 判断当前语境下是否真正使用。
3. **Memory 可以分层存储**：大 memory 可以 offload 到 host memory，并通过 prefetch 隐藏传输开销。
4. **Layer placement 重要**：较早读取知识可以释放 Transformer 的有效计算深度，但过早读取时上下文不足。
5. **Compute 与 Memory 之间可能存在最佳分配比例**：memory 并不能无限替代计算核心。

KMesh 与 Engram 的核心区别：

| Engram | KMesh |
|---|---|
| N-gram / hash address | semantic + graph + learned addressing |
| memory entries | knowledge patches |
| 无显式知识图 | 动态 knowledge mesh |
| 主要是静态条件记忆 | 持续修改和局部训练 |
| address known early | address often depends on reasoning state |
| 不重点处理 edit composition | composability 是核心问题 |

## 4.6 Model Editing: ROME / MEMIT / SERAC / GRACE

这些工作证明 specific knowledge can sometimes be locally edited。

- **ROME / MEMIT**：直接修改 Transformer 中与 factual association 有关的局部参数；
- **SERAC**：将 edits 外置，通过 retrieval + auxiliary model 使用；
- **GRACE**：在 latent space 中建立可持续增长的 edit codebook。

它们说明知识局部修改并不是一个新概念。KMesh 的目标更接近从一开始就把整个知识系统设计成可局部寻址、更新和组合的架构，而不是在 dense model 训练完之后再进行 post-hoc repair。

## 4.7 MEMOIR

MEMOIR 更接近 KMesh 的 local-update 假设：每个 edit 只修改 residual memory 中特定参数子集，并通过 sparse activation 选择相关参数，目标是降低多个 sequential edits 的相互干扰。

它说明不同知识更新映射到不同参数区域，是一个可行的研究方向。但它仍没有完全解决 patch 如何自然形成、patch 之间如何建立长期关系、multi-hop composition、动态分页、全局知识演进。

## 4.8 A³E: Compositional Model Editing

A³E 暴露了 KMesh 最需要重视的问题：

> 两条 edit 单独都成功，不代表它们放在一起仍然正确。

已有方法会出现 knowledge loss、interference、knowledge sinking、independent edits 无法正确组合。

这直接告诉我们：

$$
\text{Local Update}
\neq
\text{Global Compatibility}
$$

因此，KMesh 不应把“能局部修改 patch”当作成功。真正需要验证的是：经过大量 sequential local updates 后，任意相关 patch 仍然能够在未见组合中协作。

## 4.9 Hebbian Learning / Fast Weights

Hebbian principle——“fire together, wire together”——为 KMesh 的动态关系学习提供经典先例。

KMesh 可以把这种思想提升到知识对象层：如果两个 patch 在很多任务中共同参与计算，它们之间应该逐渐形成更强的 functional association。

这可以看作 **patch-level Hebbian association**。

## 4.10 DNC / Relational Memory / Attention-as-Graph

Differentiable Neural Computer、Relational Memory Core、attention-based relational models 等工作说明：memory slot 之间可以显式建模关系，memory relation 可以动态更新，attention matrix 可以被理解为输入相关的 soft adjacency。

KMesh 的进一步设想是：

```text
runtime transient relation
↓
长期积累
↓
persistent patch graph
```

即 **attention-to-association consolidation**。

## 4.11 RAPTOR / GraphRAG

RAPTOR 和 GraphRAG 说明：只做局部 chunk retrieval 对某些全局问题不够，建立多分辨率摘要或全局图结构可以改善跨区域问题。

KMesh 不准备采用固定的严格层次摘要树，但这些工作支持一个重要观点：局部知识访问之外，需要某种全局可达性和跨区域抽象。

---

# 5. KMesh Architecture / 架构草案

## 5.1 Knowledge Patch

一个 patch 是可以独立寻址、读取、更新、版本化、建立关系的知识对象。

候选表示：

$$
P_i = (id_i,C_i,k_i,U_i,E_i,v_i)
$$

其中：

- `id_i`: stable Patch ID
- `C_i`: 可解释内容 / 来源 / 条件 / provenance
- `k_i`: retrieval representation
- `U_i`: neural memory representation
- `E_i`: relations
- `v_i`: version

patch 不一定是一条事实。它可以是 fact、rule、condition、exception、concept、procedure、skill、reusable abstraction，但第一阶段不强制这些类型。

## 5.2 Unified Patch Pool

KMesh 不预设独立的 summary pool、fact pool、skill pool，而是一个统一 patch space。

某些 patch 可能因为广泛复用而成为逻辑核心，但这应当由训练和实际使用产生，而不是由人工标注决定。

## 5.3 Patch Graph / Knowledge Mesh

patch 之间可以存在多种关系。不建议只存一个 scalar “similarity”。

更可能需要：

$$
E_{ij}=\{s_{semantic},s_{coactivation},s_{transition},s_{synergy},s_{conflict}\}
$$

- **Semantic relation**：内容相似、概念相近；
- **Coactivation relation**：在解决任务时经常共同被读取；
- **Transition relation**：读取 $$P_i$$ 后，经常进一步读取 $$P_j$$；
- **Synergy relation**：二者共同使用时，效果超过单独贡献简单相加；
- **Conflict / competition relation**：二者在联合使用或更新时容易产生负干扰。

最终 graph 可能是一个 **multi-relational dynamic knowledge graph**。

---

# 6. Runtime Retrieval / 推理时读取

KMesh 建议采用至少两阶段：

```text
Candidate Retrieval
↓
Contextual Gating
↓
Actual Use
```

即：

$$
\operatorname{Retrieve}(q)\rightarrow\{P_i\}
$$

然后：

$$
\alpha_i=\operatorname{Gate}(h,P_i)
$$

最后：

$$
h'=h+\sum_i\alpha_iV(P_i)
$$

这借鉴 Engram：retrieval 只负责 recall，当前 hidden state 决定 memory 是否真正适用。

---

# 7. Multi-layer Reading / 多层访问

KMesh 不要求 `P123 belongs to Layer 6`，更可能是：

```text
Patch P123
├── Reader@Layer2
├── Reader@Layer6
└── Reader@Layer10
```

共享 patch $$U_i$$ 由不同 layer-specific reader 解释：

$$
K_i^{(\ell)}=U_iW_K^{(\ell)}
$$

$$
V_i^{(\ell)}=U_iW_V^{(\ell)}
$$

这允许同一知识跨层访问、不同层形成不同读取偏好，并让 memory 与 Transformer 层解耦。

---

# 8. Global Abstraction / 全局抽象

KMesh 不采用严格的“事实 → 区域摘要 → 总摘要”层次。

更倾向于一个图中自然出现不同功能范围的节点。某些 patch 可能跨多个区域、在不同任务中频繁复用、帮助指导后续检索、承载可迁移规则，因此成为逻辑上的“高层节点”。

但：

> **graph centrality ≠ abstraction**

不能把 degree、PageRank、access frequency 直接当成“抽象程度”。真正需要验证的是某个 patch 是否能在表面不同的新任务中提供稳定可迁移的结构。

---

# 9. Stage-wise Retrieval / 分阶段读取偏好

一个工作假设是不同 Transformer layer / reader 会形成不同知识访问模式。

例如某些阶段偏向局部具体知识，某些阶段偏向广泛复用规则，某些阶段重新进行全局搜索，某些阶段沿当前 graph 做 multi-hop expansion。

但 KMesh 不预先规定固定层级。

可以让每一层学习：

$$
p_\ell=(1-\gamma_\ell)p_\ell^{global}+\gamma_\ell p_\ell^{graph}
$$

其中 `global` 是重新从整个 patch space 检索，`graph` 是沿当前已激活 patch 的邻居扩展，$$\gamma_\ell$$ 可学习。

---

# 10. Local Update / 局部知识更新

理想目标：

$$
P_i^v\rightarrow P_i^{v+1}
$$

只更新 patch 自身表示、少量 reader / adapter（如果必要）、patch 周围相关关系，而不是重新训练整个网络。

但局部 edit 本身不是最终目标。真正需要解决：

$$
\boxed{\text{Local Update}+\text{Compatibility Preservation}}
$$

---

# 11. Coactivation Graph / 基于共同激活的关系学习

这是当前最重要的新想法之一。

假设在 layer $$\ell$$，$$a_i^{(\ell)}$$ 表示 patch $$P_i$$ 的有效激活强度。

可以积累：

$$
C_{ij}\leftarrow C_{ij}+a_ia_j
$$

形成长期 co-use 统计。

但不能简单使用 raw coactivation count，因为热门 patch 会形成伪 hub，同时激活也可能代表互补或竞争。

因此可考虑归一化：

$$
R_{ij}=\log\frac{P(i,j)}{P(i)P(j)}
$$

同时记录 directional relation：

$$
P(P_j@t+1\mid P_i@t)
$$

---

# 12. Causal Synergy / 组合协同

仅共同激活还不够。

对于重要候选边，可以用少量 intervention 来估计：

$$
I_{ij}=L_{-ij}-L_{-i}-L_{-j}+L
$$

直观上：

- $$I_{ij}>0$$：可能存在互补 / synergy；
- $$I_{ij}<0$$：可能存在冗余 / substitute；
- strong negative interaction：可能存在 conflict。

不可能对所有 patch 两两计算，因此：

> **coactivation 负责 cheap candidate discovery；intervention 负责 sparse causal calibration。**

---

# 13. Why the Graph May Be Critical for Local Updates

A³E 暴露的问题是：独立 edit 之后，未来到底会和哪些知识组合？

如果 KMesh 已经从历史使用中建立：

```text
P_i
├── P_17
├── P_42
├── P_103
└── P_912
```

那么当：

$$
P_i^v\rightarrow P_i^{v+1}
$$

更新时，不必回归测试整个知识网络，可以优先测试：

$$
P_i'\oplus P_{17},\quad
P_i'\oplus P_{42},\quad
P_i'\oplus P_{103}
$$

这形成 **Local Compatibility Frontier**：

$$
\text{Local Update}
\rightarrow
\text{Local Compatibility Regression}
$$

如果 graph 能准确预测未来真正需要组合的 patch，这可能把 $$O(N^2)$$ 潜在组合验证问题缩减为稀疏的 $$O(\lvert E\rvert)$$ 局部验证问题。

---

# 14. Patch Update Objective / 更新时的兼容性训练

更新 $$P_i$$ 时，不只优化新知识本身：

$$
L_{new}(P_i')
$$

而可以从邻居 $$N(P_i)$$ 中采样，加入：

$$
L=L_{new}+\lambda L_{composition}+\mu L_{locality}
$$

其中：

- **New knowledge loss**：保证新知识本身正确；
- **Composition loss**：保证新 patch 与历史上相关 patch 仍然正确协作；
- **Locality / retention loss**：保证无关知识不受意外影响。

这可能是 KMesh 对 compositional editing 问题的核心回答。

---

# 15. Graph Update After Patch Modification

patch 更新后，旧关系不应全部删除，也不应完全保留。

可以：

$$
w_{ij}^{new}=\rho_iw_{ij}^{old}
$$

其中：

$$
\rho_i=f(distance(P_i^{old},P_i^{new}))
$$

小改动时 $$\rho\approx1$$，大改动时 $$\rho\ll1$$。

之后随着新 patch 被重新使用，再利用 coactivation、transition、gradient affinity、intervention 重新估计关系。

---

# 16. Self-reinforcement Risk / 图自强化风险

动态 graph 存在明显反馈：

```text
edge 强
↓
更容易被 retrieve
↓
更容易共同激活
↓
edge 更强
```

即：

$$
retrieval\rightarrow coactivation\rightarrow edge\rightarrow more\ retrieval
$$

需要考虑 edge decay、exploration、popularity normalization、independent semantic retrieval、held-out coactivation statistics、causal validation、graph-free candidate generation，避免图自己制造“证据”。

---

# 17. Storage Hierarchy / GPU-RAM-SSD 分层

KMesh 的长期设计：

```text
GPU HBM
↓
Host RAM
↓
NVMe SSD
```

热点 patch 放 GPU，温 patch 放 RAM，冷 patch 放 SSD。

当前任务只加载：

$$
W_t\subset\mathcal K
$$

这意味着知识网络理论容量可以远大于 GPU 显存。

---

# 18. Addressing / 地址与重定位

每个 patch 需要稳定的逻辑身份：

$$
PatchRef=(patch\_id,version,local\_slot)
$$

而当前驻留地址：

$$
ResidentTable[PatchRef]\rightarrow(device,page,offset)
$$

可以动态变化。

核心原则：

> **stable logical identity, movable physical storage**

Q/K/V 不应依赖真实 GPU offset。

运行时应保证：

$$
F(x,\mathcal P;layout_1)\approx F(x,\mathcal P;layout_2)
$$

即同一批 patch 换不同物理布局，不改变模型语义。

---

# 19. Prefetch / 预取

Engram 的优势是地址可以由 N-gram 提前确定。KMesh 的地址往往依赖 $$h_\ell$$，因此可能需要 **predictive patch prefetch**。

早期 hidden state：

$$
h_\ell
$$

预测：

$$
P(P_i\text{ later needed}\mid h_\ell)
$$

提前将候选 patch 从 RAM 搬入 GPU。后续更深层 $$h_{\ell+k}$$ 再进行精确 gating。

---

# 20. Experiments / 实验路线

## E0. Unified Patch Retrieval & Composition

目标：验证统一 patch 池能否被小型 Transformer 正确读取和组合。

使用 synthetic rule world。patch 包含 facts、rules、conditions，但模型不接收显式“高层 / 低层”标签。

主要测试：

- 新世界；
- 未见组合；
- counterfactual patch replacement；
- multi-hop reasoning。

## E0-A. Exact Lookup Baseline

借鉴 Engram：

```text
known key
↓
exact patch
```

如果 exact lookup 都无法正确组合，问题在 reader / reasoner；如果 exact lookup 很好而 semantic retrieval 很差，问题在 addressing / retrieval。

## E0-B. Graph Ablation

比较：

1. No graph
2. Semantic similarity graph
3. Coactivation graph
4. Hybrid graph

指标：retrieval recall、composition accuracy、multi-hop success、counterfactual correctness。

## E0-C. Stage-wise Retrieval

比较：

- 全层共享同一个 routing preference；
- 各 layer 独立学习 routing；
- graph expansion + global retrieval。

验证是否真正出现有用的阶段分工。不能只看 attention heatmap，必须通过 layer gate permutation / ablation 验证。

---

# 21. E1. Local Update

## E1-A. Content Replacement

冻结模型：

$$
P_i^v\rightarrow P_i^{v+1}
$$

检验新知识是否立即生效、无关知识是否保持、依赖旧知识的任务是否正确变化。

## E1-B. Local Neural Patch Update

只训练 $$U_i$$ 或少数相关 patch，不修改整个主干。

比较：local training cost、edit success、retention、interference、composition。

---

# 22. E1-C. Sequential Local Updates

连续执行：

```text
P1 update
P2 update
P3 update
...
P1000 update
```

然后测试：

```text
P17 + P429 + P812
```

这种从未联合训练过的组合。

这是 KMesh 最重要的长期指标之一：

> **Composition after many sequential local updates**

---

# 23. E1-D. Graph-guided Compatibility Training

更新 $$P_i$$ 时比较：

### baseline
只训练 $$P_i$$。

### semantic neighbors
与语义相似 patch 联合训练。

### coactivation neighbors
与历史共同激活 patch 联合训练。

### hybrid neighbors
使用综合 graph。

比较：new edit success、old knowledge retention、unseen composition、regression cost。

这可以直接测试 graph 是否真正解决 A³E 指出的 composability 问题。

---

# 24. E2. Emergent Abstraction

只有 E0/E1 成立后再做。

目标：不向模型预先提供抽象规则，让系统从多个具体 patch 中形成新的可复用 patch。

测试：

- 新生成 patch 是否跨实例复用；
- 删除具体训练实例后是否仍然工作；
- 新抽象是否改善未见组合；
- 它是否只是高频 pattern，而非真正结构。

---

# 25. E3. Memory Hierarchy

加入：

```text
GPU
↕
RAM
↕
SSD
```

验证：hot-set residency、prefetch accuracy、page migration、dirty patch writeback、optimizer state residency、relocation invariance、training throughput。

比较：all-resident、RAM offload、RAM + SSD。

---

# 26. E4. Compute–Knowledge Scaling

借鉴 Engram 的思路。

固定 total training budget 和 activated FLOPs，改变：

$$
\text{Core Capacity}\leftrightarrow\text{Patch Capacity}
$$

观察 factual recall、reasoning、unseen composition、continual update。

寻找最优：

$$
\rho_K^*
$$

即最优 compute / knowledge allocation。

---

# 27. Evaluation Metrics

KMesh 不应只看 accuracy。

## Task Quality

- exact task accuracy
- multi-hop accuracy
- unseen composition accuracy

## Local Update

- edit success
- update FLOPs
- updated parameter count
- patch working-set size

## Retention

- unrelated knowledge retention
- regression rate
- catastrophic interference

## Composition

- pair composition
- multi-patch composition
- composition after sequential updates

## Retrieval

- patch recall@k
- retrieval precision
- graph hop efficiency

## Memory System

- GPU resident bytes
- RAM/SSD traffic
- cache hit rate
- prefetch precision / recall
- wall-clock throughput

---

# 28. What Would Count as Evidence for KMesh?

不同实验只支持不同层次的结论。

### E0 成功只能说明
统一 patch pool 可以被模型读取和组合。不能说明 local continual learning 已经解决。

### E1 成功才说明
patch 可以局部修改，而不需要全局 retraining。

### E1-C / E1-D 成功才开始说明
大量独立局部更新之后，知识仍然具有可组合性。这是 KMesh 最核心的证据。

### E2 成功才说明
系统可能形成新的抽象知识，而不仅是存储外部事实。

### E3 成功才说明
知识容量可以实际突破 GPU residency 限制。

---

# 29. Main Risks / 核心风险

## Risk 1. Patch Is Just RAG with Extra Steps

如果 patch 只是文本 chunk + embedding，KMesh 可能退化成复杂 RAG。需要证明 neural patch / local update / composition 有额外价值。

## Risk 2. Core Model Still Stores Most Reasoning and Knowledge

外部 patch 可能只是提示，真正能力仍藏在共享 Transformer 中。需要通过 patch intervention 和 core-size scaling 分析。

## Risk 3. Graph Does Not Add Value

可能 global ANN retrieval 已经够好。如果 graph 没有明显改善 composition、routing、update compatibility，则不应为了概念完整强行保留。

## Risk 4. Dynamic Graph Self-reinforcement

历史 retrieval 决定未来 graph，产生错误 hub。

## Risk 5. Local Update Breaks Global Composition

这正是 A³E 级别的问题，是整个项目最关键的技术风险。

## Risk 6. Sparse Compute Is Hardware Inefficient

理论 FLOPs 少，但 tiny GEMM、random access、RAM traffic、SSD latency 可能让 wall-clock 变慢。

## Risk 7. Abstract Patches Become Global Coupling Points

如果少数核心 patch 被大量任务依赖，更新它们可能重新造成全局耦合。因此“抽象形成”可能与“局部更新”存在内在张力。

---

# 30. Research Questions

### RQ1
知识能否被分解成可以独立寻址和更新的 patch，同时保持组合能力？

### RQ2
semantic similarity、coactivation、transition 和 gradient affinity 中，哪些最能预测真实知识关系？

### RQ3
知识图能否有效预测 patch update 后需要重新验证的 compatibility frontier？

### RQ4
不同 layer 是否会自然形成不同知识读取策略？

### RQ5
是否存在无需预先标注的 emergent abstraction patches？

### RQ6
一个小型共享核心能够支持多大的外部知识网络？

### RQ7
在相同训练 FLOPs 下，最佳 compute / knowledge capacity ratio 是多少？

### RQ8
GPU / RAM / SSD 分层能否保持足够高的实际吞吐？

---

# 31. Proposed Research Sequence

建议不要一次实现完整 KMesh。

```text
Phase 0
Synthetic knowledge world
↓
Unified patch reader
↓
Exact lookup baseline

Phase 1
Semantic retrieval
↓
Graph retrieval
↓
Stage-wise readers

Phase 2
Local patch update
↓
Sequential edits
↓
Composition after edits

Phase 3
Coactivation graph
↓
Graph-guided compatibility training

Phase 4
Emergent abstraction

Phase 5
GPU / RAM / SSD hierarchy

Phase 6
Larger language / code model experiments
```

优先级：

> **先验证 composability，再优化存储。**

如果独立 patch 无法可靠组合，那么分页、prefetch 和超大容量都没有意义。

---

# 32. Long-term Vision

如果 KMesh 的核心假设成立，未来模型可以从：

```text
Large Dense / MoE Model
```

转变为：

```text
Small Shared Reasoning Core
+
Large Evolving Knowledge Mesh
+
Sparse Dynamic Access
```

知识规模可以继续增长：

$$
|\mathcal K|\rightarrow\infty
$$

而当前 GPU working set 仍保持有限：

$$
|W_t|\ll|\mathcal K|
$$

知识更新可以：

```text
local patch update
↓
local relation update
↓
local compatibility validation
↓
global system continues to evolve
```

最终希望实现：

> **能力的持续增长，不再要求计算核心、GPU 显存和全量训练成本以同样速度增长。**

这可能成为 “AI for Everyone” 的一种底层架构路线：desktop、laptop、cellphone、home server 都可以拥有持续成长的本地 AI，而不是始终依赖重新下载或重新训练一个巨大、静态、整体耦合的模型。

---

# 33. Related Work Reading List

## External / Neural Memory

- **End-to-End Memory Networks**  
  https://arxiv.org/abs/1503.08895
- **Product-Key Memory**  
  https://arxiv.org/abs/1907.05242
- **Memory Layers at Scale**  
  https://arxiv.org/html/2412.09764v1
- **Engram**  
  https://arxiv.org/abs/2601.07372
- **Memory³**  
  https://arxiv.org/abs/2407.01178
- **LongMem**  
  https://arxiv.org/abs/2306.07174

## Continual / Model Editing

- **ROME**  
  https://arxiv.org/abs/2202.05262
- **MEMIT**  
  https://arxiv.org/abs/2210.07229
- **SERAC**  
  https://arxiv.org/abs/2206.06520
- **GRACE**  
  https://arxiv.org/abs/2211.11031
- **MEMOIR**  
  https://arxiv.org/abs/2506.07899
- **A³E**  
  https://papers.neurips.cc/paper_files/paper/2025/hash/3d4c0a618d0acd7921493e4f30395c22-Abstract-Conference.html

## Dynamic Association / Structured Memory

- **Differentiable Neural Computers**  
  https://www.nature.com/articles/nature20101
- **Differentiable Plasticity / Hebbian-style learning**  
  https://arxiv.org/abs/1804.02464
- **Relational Memory Core**  
  https://arxiv.org/abs/1806.01822

## Global / Hierarchical Retrieval

- **RAPTOR**  
  https://arxiv.org/abs/2401.18059
- **GraphRAG**  
  https://arxiv.org/abs/2404.16130

## Sparse / Conditional Computation

- **Sparsely-Gated Mixture of Experts**  
  https://arxiv.org/abs/1701.06538
- **DeepSeekMoE**  
  https://arxiv.org/abs/2401.06066
- **RigL**  
  https://arxiv.org/abs/1911.11134

---

# 34. One-Sentence Positioning

> **KMesh explores whether knowledge can be represented as a dynamically connected set of locally updatable neural patches, so that semantic locality becomes computation and update locality while preserving global composability.**

中文：

> **KMesh 探索把知识组织成动态连接、可局部更新的神经 patch，使知识的语义局部性映射为计算和更新局部性，同时保持跨知识的全局组合能力。**

---

# 35. Current Bottom Line

目前最值得优先验证的不是：

> “KMesh 能不能让一个 1B 模型打败 SOTA？”

而是三个更基础的问题：

1. **独立知识能否真正成为可定位、可训练的 patch？**
2. **独立更新之后，这些 patch 是否仍能可靠组合？**
3. **知识关系图能否把全局兼容问题压缩成局部、可管理的兼容性验证问题？**

如果这三点成立，KMesh 才有资格继续讨论：

- 更大的知识网络；
- GPU/RAM/SSD 分层；
- 自动形成抽象；
- 大幅降低训练成本；
- 小型共享核心；
- 端侧与个人 AI。

这也是下一阶段研究最应该保持的聚焦点。
