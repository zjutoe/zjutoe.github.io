---
title: KMesh - Locally Updatable Knowledge Patches for Continually Evolving Neural Memory
lang: en
translation_key: kmesh-paper-framework
category: research
permalink: /en/posts/KMesh_Paper_Framework/
---

# KMesh: A Knowledge Network Architecture for Local Updates and Continual Evolution
## Research Framework Draft / Paper-like Research Outline

> **Status note**: This document is not a draft paper. It uses the structure of a paper to organize current research ideas, related work, key hypotheses, and future experimental plans for KMesh.  
> Many of the ideas below are still working hypotheses that require validation. The aim is to keep subsequent research and engineering aligned, rather than to draw conclusions prematurely.

---

## 0. Working Title

**KMesh: Locally Updatable Knowledge Patches for Continually Evolving Neural Memory**

Possible subtitles:

- **Aligning Semantic Locality with Parameter, Computation, and Update Locality**
- **A Knowledge Mesh for Sparse, Composable, and Continually Evolving AI**
- **Local Updates, Global Composition**

---

# 1. Abstract / Core Problem

Current large language models encode extensive knowledge, reasoning capabilities, and language processing capabilities together in a single set of dense neural network parameters.  
This design provides strong unified modeling capabilities, but also creates several fundamental problems:

1. Adding new knowledge usually requires retraining or fine-tuning the entire model;
2. It is difficult to identify precisely which parameters correspond to a particular piece of knowledge;
3. Even when a task involves very little knowledge, the forward/backward pass often still needs to access most or all backbone parameters;
4. Model capacity, GPU memory, training compute, and knowledge capacity are tightly coupled;
5. Local knowledge modifications can easily interfere with existing knowledge, while multiple independent modifications may fail to compose reliably;
6. Large-scale model training relies on techniques such as FSDP, ZeRO, and tensor parallelism to distribute an entire dense tensor, rather than allowing the current task to access only the knowledge parameters it actually needs.

KMesh explores a different architectural hypothesis:

> **Organize knowledge into independently addressable, locally updatable, sparsely activated knowledge patches, and let these patches form a continually evolving knowledge network. A relatively small shared neural computation core selects a small number of relevant patches from this network to read, compose, and update according to the current task.**

KMesh ultimately aims to achieve:

$$
\text{Semantic Locality}
\rightarrow
\text{Parameter Locality}
\rightarrow
\text{Computation Locality}
\rightarrow
\text{Update Locality}
$$

While still preserving:

$$
\text{Global Composability}
$$

The central scientific question is not whether some parameters can be modified locally: research on embeddings, MoE, LoRA, and model editing has already demonstrated that this is feasible in various forms.

What KMesh really needs to test is:

> **Whether a semantically local piece of knowledge can naturally map to a local object in computation and parameter space, while remaining composable with the entire knowledge network after independent local updates.**

---

# 2. Motivation / Why KMesh Is Needed

## 2.1 Current LLMs Mix Knowledge with Computation

For an ordinary Transformer:

$$
y = xW
$$

Even if the current example involves only one local piece of knowledge, the entire dense matrix $$W$$ usually still participates in the forward pass, and backpropagation also affects many parameters.

Therefore:

> “The current task involves only a little knowledge”

Does not automatically translate into:

> “The current task needs only a few parameters and a small amount of computation.”

This is also the context in which systems such as FSDP / ZeRO exist: the full tensor remains part of the computation graph, so it has to be sharded, gathered, and sharded again.

KMesh does not aim to build a smarter FSDP. It attempts to change this premise:

> The current task only needs access to a very small part of the entire knowledge space in the first place.

## 2.2 Must Knowledge Capacity Equal Active Compute Capacity?

Recent work on MoE, Memory Layers, Engram, and related approaches has repeatedly suggested that:

- The total parameter count can be much larger than the parameter count activated per token;
- Memory capacity can be much larger than the backbone's compute capacity;
- Static knowledge can be externalized from neural computation through lookup / sparse memory;
- A very large memory table does not necessarily have to remain resident in GPU HBM.

KMesh aims to take this further:

$$
\text{Conditional Computation}
\rightarrow
\text{Conditional Memory}
\rightarrow
\text{Structured, Editable Knowledge Memory}
$$

## 2.3 Continual Learning Matters More Than One-Time Pretraining

If knowledge updates require periodically retraining the entire model, then:

- Larger models are more expensive to update;
- More frequent additions of knowledge increase maintenance costs;
- Personalized models struggle to grow continually;
- Resource-constrained devices such as desktops, laptops, and cellphones find it difficult to maintain their own AI independently over the long term.

KMesh aims to support:

```text
Add a patch
Modify a patch
Revert a patch
Locally train a few patches
Update local relations
↓
The entire knowledge network keeps working
```

Instead of:

```text
New knowledge
↓
Repeat large-scale training
```

This aligns with the long-term vision of **AI for Everyone**: allowing AI capabilities to grow without always depending on enormous GPU clusters.

---

# 3. Central Hypotheses

## H1. Knowledge Locality

A specific task usually needs access to only a small fraction of the knowledge in the entire knowledge network.

$$
|W_t| \ll |\mathcal K|
$$

Here, $$\mathcal K$$ is the entire knowledge network, and $$W_t$$ is the working set required by the current task.

## H2. Update Locality

Adding or modifying knowledge need not require retraining the entire knowledge system; only a few patches and their local relations need to be updated.

## H3. Computation Locality

If knowledge is organized into addressable patches, unselected patches can be entirely excluded from the current forward/backward pass.

This is stronger than LoRA, where parameters are frozen but still participate in the forward pass.

## H4. Global Composability

Although knowledge is stored and updated locally, tasks can dynamically compose multiple independent patches into previously unseen knowledge combinations.

This is one of the most difficult hypotheses, and also a central risk highlighted by A³E.

## H5. Functional Relations Can Be Learned

Relations between patches should not be determined solely by text embedding similarity.

During actual model execution, runtime signals reveal which patches often activate together, which activate in sequence, which combinations produce synergy, and which produce conflict. These signals can help the knowledge graph gradually develop a more functionally meaningful topology.

## H6. Abstraction Can Emerge Without Fixed Hierarchy

KMesh does not distinguish “summary patches,” “ordinary patches,” “high-level patches,” and “low-level patches” in advance. All patches use a unified representation.

Some patches may gradually become logical core nodes because they are reused across tasks, connect multiple knowledge regions, or guide the use of many specific pieces of knowledge. Different Transformer layers / readers may develop different reading preferences, allowing a functional division of labor in abstraction to emerge.

---

# 4. Related Work

KMesh is not a concept developed from scratch; it brings together several existing lines of research.

## 4.1 Sparse Embedding / Recommender Systems

Embedding tables have long supported:

```text
A huge parameter space
↓
Read a few rows by ID
↓
Update only the accessed rows
```

Both word2vec and recommender-system embedding tables have demonstrated that it is entirely feasible to have a large total parameter capacity while processing only a tiny fraction of the parameters in each forward/backward pass.

The challenge for KMesh is that knowledge has no explicit user_id / word_id; it must be addressed through semantics and reasoning state.

## 4.2 Mixture of Experts

Work such as Sparsely-Gated MoE, Switch Transformer, and DeepSeekMoE demonstrates that:

$$
\text{Large Total Capacity}
\neq
\text{Large Activated Compute}
$$

Only a few experts participate in computation for the current token.

MoE can be understood as **parameter locality induced by routing**. KMesh aims to move from conditional compute toward **conditional knowledge**.

## 4.3 Product-Key Memory / Memory Layers at Scale

Product-Key Memory directly adds large-scale sparse key-value memory to Transformers.

**Memory Layers at Scale** goes further to explore:

- Sharing the same memory across multiple Transformer layers;
- Activating only a few entries in a large memory;
- Partially decoupling memory capacity from the backbone's computational capabilities.

This directly supports two KMesh hypotheses: memory can be shared across layers, and knowledge-like capacity does not have to be packed entirely into FFN / dense weights.

## 4.4 End-to-End Memory Networks

End-to-End Memory Networks demonstrate that a model can perform multi-hop reads from external memory and reason through multiple rounds of memory access.

This is close to KMesh's multi-patch composition. The difference is that KMesh also concerns itself with continual updates to the memory itself, long-term relations between patches, and support for paging and local patch training.

## 4.5 Engram

DeepSeek's Engram is one of the recent works most relevant to KMesh.

It divides model capacity into:

$$
\text{Conditional Computation}
+
\text{Conditional Memory}
$$

And uses N-gram hashing to directly access a huge memory table.

Important lessons from Engram for KMesh:

1. **Knowledge can be externalized**: some static knowledge need not rely on repeated recomputation by Transformer layers.
2. **Retrieval and use should be separate**: after memory is retrieved, contextual gating is still needed to determine whether to use it in the current context.
3. **Memory can use a storage hierarchy**: a large memory can be offloaded to host memory, with prefetching to hide transfer overhead.
4. **Layer placement matters**: reading knowledge earlier can free up effective Transformer compute depth, but reading too early means insufficient context.
5. **There may be an optimal allocation between compute and memory**: memory cannot replace the computational core without limit.

Key differences between KMesh and Engram:

| Engram | KMesh |
|---|---|
| N-gram / hash address | semantic + graph + learned addressing |
| memory entries | knowledge patches |
| No explicit knowledge graph | Dynamic knowledge mesh |
| Primarily static conditional memory | Continual modification and local training |
| address known early | address often depends on reasoning state |
| Edit composition is not a central focus | Composability is a core issue |

## 4.6 Model Editing: ROME / MEMIT / SERAC / GRACE

These works show that specific knowledge can sometimes be edited locally.

- **ROME / MEMIT**: directly modify local Transformer parameters associated with factual associations;
- **SERAC**: externalizes edits and uses them through retrieval + an auxiliary model;
- **GRACE**: builds a continually expandable edit codebook in latent space.

They show that local knowledge modification is not a new concept. KMesh's goal is closer to designing the entire knowledge system from the outset as an architecture that supports local addressing, updates, and composition, rather than performing post-hoc repair after a dense model has been trained.

## 4.7 MEMOIR

MEMOIR is closer to KMesh's local-update hypothesis: each edit modifies only a particular subset of parameters in residual memory, and sparse activation selects the relevant parameters, with the aim of reducing interference among sequential edits.

It suggests that mapping different knowledge updates to different parameter regions is a viable research direction. However, it still does not fully resolve how patches form naturally, how long-term relations between patches are established, multi-hop composition, dynamic paging, or global knowledge evolution.

## 4.8 A³E: Compositional Model Editing

A³E exposes the issue that KMesh most needs to take seriously:

> Two edits succeeding individually does not mean that they will remain correct when combined.

Existing methods can suffer from knowledge loss, interference, knowledge sinking, and failures to compose independent edits correctly.

This tells us directly that:

$$
\text{Local Update}
\neq
\text{Global Compatibility}
$$

Therefore, KMesh should not treat the ability to modify patches locally as success. What really needs to be tested is whether any relevant patches can still collaborate in unseen combinations after many sequential local updates.

## 4.9 Hebbian Learning / Fast Weights

The Hebbian principle—“fire together, wire together”—provides a classic precedent for KMesh's dynamic relation learning.

KMesh can extend this idea to the level of knowledge objects: if two patches participate together in computation across many tasks, they should gradually develop a stronger functional association.

This can be viewed as **patch-level Hebbian association**.

## 4.10 DNC / Relational Memory / Attention-as-Graph

Work on Differentiable Neural Computers, Relational Memory Cores, and attention-based relational models shows that relations between memory slots can be modeled explicitly, memory relations can be updated dynamically, and an attention matrix can be understood as input-dependent soft adjacency.

KMesh's further proposal is:

```text
runtime transient relation
↓
Long-term accumulation
↓
persistent patch graph
```

In other words, **attention-to-association consolidation**.

## 4.11 RAPTOR / GraphRAG

RAPTOR and GraphRAG show that local chunk retrieval alone is insufficient for some global questions, and that building multiresolution summaries or a global graph structure can improve handling of questions spanning multiple regions.

KMesh does not intend to adopt a fixed, strictly hierarchical summary tree, but these works support an important point: beyond local knowledge access, some form of global reachability and cross-region abstraction is needed.

---

# 5. KMesh Architecture / Architectural Outline

## 5.1 Knowledge Patch

A patch is a knowledge object that can be independently addressed, read, updated, versioned, and connected through relations.

A candidate representation:

$$
P_i = (id_i,C_i,k_i,U_i,E_i,v_i)
$$

Where:

- `id_i`: stable Patch ID
- `C_i`: interpretable content / source / conditions / provenance
- `k_i`: retrieval representation
- `U_i`: neural memory representation
- `E_i`: relations
- `v_i`: version

A patch need not be a single fact. It can be a fact, rule, condition, exception, concept, procedure, skill, or reusable abstraction, but these types are not enforced in the first stage.

## 5.2 Unified Patch Pool

KMesh does not assume separate summary, fact, and skill pools; it uses a unified patch space.

Some patches may become logical cores through broad reuse, but this should emerge from training and actual use rather than being determined by manual labels.

## 5.3 Patch Graph / Knowledge Mesh

Multiple kinds of relations can exist between patches. Storing only a scalar “similarity” is not recommended.

What is more likely needed is:

$$
E_{ij}=\{s_{semantic},s_{coactivation},s_{transition},s_{synergy},s_{conflict}\}
$$

- **Semantic relation**: similar content or closely related concepts;
- **Coactivation relation**: frequently read together when solving tasks;
- **Transition relation**: reading $$P_i$$ is often followed by reading $$P_j$$;
- **Synergy relation**: using both together produces an effect greater than the simple sum of their individual contributions;
- **Conflict / competition relation**: using or updating them jointly tends to produce negative interference.

The resulting graph may be a **multi-relational dynamic knowledge graph**.

---

# 6. Runtime Retrieval / Reading During Inference

KMesh proposes at least two stages:

```text
Candidate Retrieval
↓
Contextual Gating
↓
Actual Use
```

That is:

$$
\operatorname{Retrieve}(q)\rightarrow\{P_i\}
$$

Then:

$$
\alpha_i=\operatorname{Gate}(h,P_i)
$$

Finally:

$$
h'=h+\sum_i\alpha_iV(P_i)
$$

This draws on Engram: retrieval is responsible only for recall; the current hidden state determines whether the memory is actually applicable.

---

# 7. Multi-layer Reading / Access Across Layers

KMesh does not require `P123 belongs to Layer 6`. A more likely arrangement is:

```text
Patch P123
├── Reader@Layer2
├── Reader@Layer6
└── Reader@Layer10
```

The shared patch $$U_i$$ is interpreted by different layer-specific readers:

$$
K_i^{(\ell)}=U_iW_K^{(\ell)}
$$

$$
V_i^{(\ell)}=U_iW_V^{(\ell)}
$$

This allows the same knowledge to be accessed across layers, lets different layers develop different reading preferences, and decouples memory from Transformer layers.

---

# 8. Global Abstraction

KMesh does not use a strict “facts → regional summaries → overall summary” hierarchy.

It favors nodes with different functional scopes emerging naturally within a graph. Some patches may span multiple regions, be reused frequently across tasks, guide subsequent retrieval, or carry transferable rules, thereby becoming logically “high-level nodes.”

However:

> **graph centrality ≠ abstraction**

Degree, PageRank, and access frequency cannot be treated directly as a “level of abstraction.” What really needs to be tested is whether a patch provides stable, transferable structure in new tasks that differ on the surface.

---

# 9. Stage-wise Retrieval / Reading Preferences Across Stages

One working hypothesis is that different Transformer layers / readers will develop different patterns of knowledge access.

For example, some stages may favor local, specific knowledge, others widely reusable rules; some may perform a fresh global search, while others perform multi-hop expansion along the current graph.

KMesh does not, however, prescribe a fixed hierarchy in advance.

Each layer can learn:

$$
p_\ell=(1-\gamma_\ell)p_\ell^{global}+\gamma_\ell p_\ell^{graph}
$$

Here, `global` means retrieving afresh from the entire patch space, `graph` means expanding through neighbors of the currently activated patches, and $$\gamma_\ell$$ is learnable.

---

# 10. Local Update / Local Knowledge Updates

The ideal goal:

$$
P_i^v\rightarrow P_i^{v+1}
$$

Update only the patch's own representation, a few readers / adapters if necessary, and relevant relations around the patch, rather than retraining the entire network.

But a local edit alone is not the ultimate goal. What really needs to be addressed is:

$$
\boxed{\text{Local Update}+\text{Compatibility Preservation}}
$$

---

# 11. Coactivation Graph / Learning Relations from Coactivation

This is one of the most important new ideas at present.

Suppose that at layer $$\ell$$, $$a_i^{(\ell)}$$ represents the effective activation strength of patch $$P_i$$.

We can accumulate:

$$
C_{ij}\leftarrow C_{ij}+a_ia_j
$$

To build long-term co-use statistics.

However, raw coactivation counts cannot simply be used directly: popular patches would form spurious hubs, and simultaneous activation may indicate either complementarity or competition.

Normalization could therefore be considered:

$$
R_{ij}=\log\frac{P(i,j)}{P(i)P(j)}
$$

While also recording directional relations:

$$
P(P_j@t+1\mid P_i@t)
$$

---

# 12. Causal Synergy / Synergy in Composition

Coactivation alone is not enough.

For important candidate edges, a small number of interventions can be used to estimate:

$$
I_{ij}=L_{-ij}-L_{-i}-L_{-j}+L
$$

Intuitively:

- $$I_{ij}>0$$: possible complementarity / synergy;
- $$I_{ij}<0$$: possible redundancy / substitution;
- Strong negative interaction: possible conflict.

Computing this for every pair of patches is infeasible, so:

> **Coactivation provides cheap candidate discovery; intervention provides sparse causal calibration.**

---

# 13. Why the Graph May Be Critical for Local Updates

The question exposed by A³E is: after an independent edit, which pieces of knowledge will it actually need to compose with in the future?

If KMesh has already established the following from historical use:

```text
P_i
├── P_17
├── P_42
├── P_103
└── P_912
```

Then, when:

$$
P_i^v\rightarrow P_i^{v+1}
$$

Is updated, instead of regression-testing the entire knowledge network, testing can prioritize:

$$
P_i'\oplus P_{17},\quad
P_i'\oplus P_{42},\quad
P_i'\oplus P_{103}
$$

This forms a **Local Compatibility Frontier**:

$$
\text{Local Update}
\rightarrow
\text{Local Compatibility Regression}
$$

If the graph can accurately predict which patches will actually need to compose in the future, this may reduce an $$O(N^2)$$ problem of validating potential combinations to a sparse $$O(\lvert E\rvert)$$ problem of local validation.

---

# 14. Patch Update Objective / Compatibility Training During Updates

When updating $$P_i$$, rather than optimizing only the new knowledge itself:

$$
L_{new}(P_i')
$$

We can sample from its neighbors $$N(P_i)$$ and add:

$$
L=L_{new}+\lambda L_{composition}+\mu L_{locality}
$$

Where:

- **New knowledge loss**: ensures the new knowledge itself is correct;
- **Composition loss**: ensures the new patch still works correctly with historically relevant patches;
- **Locality / retention loss**: ensures unrelated knowledge is not affected unintentionally.

This may be KMesh's central answer to the compositional editing problem.

---

# 15. Graph Update After Patch Modification

After a patch is updated, its old relations should neither all be deleted nor be retained entirely.

One possibility is:

$$
w_{ij}^{new}=\rho_iw_{ij}^{old}
$$

Where:

$$
\rho_i=f(distance(P_i^{old},P_i^{new}))
$$

For small changes, $$\rho\approx1$$; for large changes, $$\rho\ll1$$.

As the new patch is used again, its relations can then be re-estimated using coactivation, transitions, gradient affinity, and interventions.

---

# 16. Self-reinforcement Risk / Graph Self-reinforcement

A dynamic graph has an obvious feedback loop:

```text
Strong edge
↓
More likely to be retrieved
↓
More likely to coactivate
↓
Stronger edge
```

That is:

$$
retrieval\rightarrow coactivation\rightarrow edge\rightarrow more\ retrieval
$$

Edge decay, exploration, popularity normalization, independent semantic retrieval, held-out coactivation statistics, causal validation, and graph-free candidate generation need to be considered to prevent the graph from manufacturing its own “evidence.”

---

# 17. Storage Hierarchy / GPU-RAM-SSD Tiers

KMesh's long-term design:

```text
GPU HBM
↓
Host RAM
↓
NVMe SSD
```

Hot patches reside on the GPU, warm patches in RAM, and cold patches on SSD.

The current task loads only:

$$
W_t\subset\mathcal K
$$

This means the knowledge network's theoretical capacity can be much larger than GPU memory.

---

# 18. Addressing / Addresses and Relocation

Each patch needs a stable logical identity:

$$
PatchRef=(patch\_id,version,local\_slot)
$$

While its current resident address:

$$
ResidentTable[PatchRef]\rightarrow(device,page,offset)
$$

Can change dynamically.

The core principle:

> **stable logical identity, movable physical storage**

Q/K/V should not depend on actual GPU offsets.

At runtime, the system should ensure:

$$
F(x,\mathcal P;layout_1)\approx F(x,\mathcal P;layout_2)
$$

That is, changing the physical layout of the same set of patches does not change the model's semantics.

---

# 19. Prefetch

Engram has the advantage that addresses can be determined in advance from N-grams. KMesh addresses often depend on $$h_\ell$$, so **predictive patch prefetch** may be needed.

An early hidden state:

$$
h_\ell
$$

Predicts:

$$
P(P_i\text{ later needed}\mid h_\ell)
$$

Candidate patches are moved from RAM to the GPU in advance. A later, deeper $$h_{\ell+k}$$ then performs precise gating.

---

# 20. Experiments / Experimental Roadmap

## E0. Unified Patch Retrieval & Composition

Goal: test whether a small Transformer can correctly read and compose a unified patch pool.

Use a synthetic rule world. Patches contain facts, rules, and conditions, but the model receives no explicit “high-level / low-level” labels.

Main tests:

- New worlds;
- Unseen combinations;
- counterfactual patch replacement;
- multi-hop reasoning.

## E0-A. Exact Lookup Baseline

Drawing on Engram:

```text
known key
↓
exact patch
```

If even exact lookup fails to compose correctly, the problem lies in the reader / reasoner. If exact lookup works well but semantic retrieval performs poorly, the problem lies in addressing / retrieval.

## E0-B. Graph Ablation

Compare:

1. No graph
2. Semantic similarity graph
3. Coactivation graph
4. Hybrid graph

Metrics: retrieval recall, composition accuracy, multi-hop success, and counterfactual correctness.

## E0-C. Stage-wise Retrieval

Compare:

- Sharing the same routing preference across all layers;
- Learning routing independently at each layer;
- graph expansion + global retrieval.

Test whether a useful division of labor between stages actually emerges. Attention heatmaps alone are insufficient; validation through layer gate permutation / ablation is required.

---

# 21. E1. Local Update

## E1-A. Content Replacement

Freeze the model:

$$
P_i^v\rightarrow P_i^{v+1}
$$

Test whether new knowledge takes effect immediately, unrelated knowledge is retained, and tasks that depend on the old knowledge change correctly.

## E1-B. Local Neural Patch Update

Train only $$U_i$$ or a few relevant patches, without modifying the entire backbone.

Compare local training cost, edit success, retention, interference, and composition.

---

# 22. E1-C. Sequential Local Updates

Perform sequentially:

```text
P1 update
P2 update
P3 update
...
P1000 update
```

Then test:

```text
P17 + P429 + P812
```

A combination that has never been jointly trained.

This is one of KMesh's most important long-term metrics:

> **Composition after many sequential local updates**

---

# 23. E1-D. Graph-guided Compatibility Training

When updating $$P_i$$, compare:

### baseline
Train only $$P_i$$.

### semantic neighbors
Train jointly with semantically similar patches.

### coactivation neighbors
Train jointly with patches that have historically coactivated.

### hybrid neighbors
Use a combined graph.

Compare new edit success, old knowledge retention, unseen composition, and regression cost.

This can directly test whether the graph actually addresses the composability problem identified by A³E.

---

# 24. E2. Emergent Abstraction

Attempt this only after E0/E1 have been established.

Goal: without supplying abstract rules to the model in advance, let the system form new reusable patches from multiple specific patches.

Test:

- Whether newly generated patches are reused across instances;
- Whether they still work after the specific training instances are removed;
- Whether new abstractions improve unseen combinations;
- Whether they are merely frequent patterns rather than actual structure.

---

# 25. E3. Memory Hierarchy

Add:

```text
GPU
↕
RAM
↕
SSD
```

Validate hot-set residency, prefetch accuracy, page migration, dirty patch writeback, optimizer state residency, relocation invariance, and training throughput.

Compare all-resident memory, RAM offload, and RAM + SSD.

---

# 26. E4. Compute–Knowledge Scaling

Draw on Engram's approach.

Keep the total training budget and activated FLOPs fixed while varying:

$$
\text{Core Capacity}\leftrightarrow\text{Patch Capacity}
$$

Observe factual recall, reasoning, unseen composition, and continual updates.

Find the optimum:

$$
\rho_K^*
$$

That is, the optimal compute / knowledge allocation.

---

# 27. Evaluation Metrics

KMesh should not be evaluated on accuracy alone.

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

Different experiments support conclusions at different levels.

### Success in E0 would show only that
A model can read and compose a unified patch pool. It would not show that local continual learning has been solved.

### Success in E1 would be needed to show that
Patches can be modified locally without global retraining.

### Success in E1-C / E1-D would begin to show that
Knowledge remains composable after many independent local updates. This is the most central evidence for KMesh.

### Success in E2 would be needed to show that
The system may form new abstract knowledge, rather than merely store external facts.

### Success in E3 would be needed to show that
Knowledge capacity can, in practice, exceed GPU residency limits.

---

# 29. Main Risks

## Risk 1. Patch Is Just RAG with Extra Steps

If a patch is merely a text chunk + embedding, KMesh may degenerate into a complicated RAG system. Neural patches, local updates, and composition need to demonstrate additional value.

## Risk 2. Core Model Still Stores Most Reasoning and Knowledge

External patches may merely provide hints, while the actual capabilities remain hidden in the shared Transformer. This needs to be analyzed through patch interventions and core-size scaling.

## Risk 3. Graph Does Not Add Value

Global ANN retrieval may already be good enough. If the graph does not clearly improve composition, routing, or update compatibility, it should not be retained just to make the concept feel complete.

## Risk 4. Dynamic Graph Self-reinforcement

Historical retrieval determines the future graph, creating erroneous hubs.

## Risk 5. Local Update Breaks Global Composition

This is precisely the kind of problem highlighted by A³E, and it is the most critical technical risk in the entire project.

## Risk 6. Sparse Compute Is Hardware Inefficient

Theoretical FLOPs may be low, but tiny GEMMs, random access, RAM traffic, and SSD latency may increase wall-clock time.

## Risk 7. Abstract Patches Become Global Coupling Points

If many tasks depend on a few core patches, updating them may reintroduce global coupling. There may therefore be an inherent tension between “abstraction formation” and “local updates.”

---

# 30. Research Questions

### RQ1
Can knowledge be decomposed into independently addressable and updatable patches while preserving compositional ability?

### RQ2
Which of semantic similarity, coactivation, transitions, and gradient affinity best predict actual knowledge relations?

### RQ3
Can the knowledge graph effectively predict the compatibility frontier that needs to be revalidated after a patch update?

### RQ4
Will different layers naturally develop different strategies for reading knowledge?

### RQ5
Can abstraction patches emerge without prior annotation?

### RQ6
How large an external knowledge network can a small shared core support?

### RQ7
At the same training FLOPs, what is the optimal compute / knowledge capacity ratio?

### RQ8
Can a GPU / RAM / SSD hierarchy maintain sufficiently high practical throughput?

---

# 31. Proposed Research Sequence

The recommendation is not to implement the entire KMesh system at once.

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

Priority:

> **Validate composability first, then optimize storage.**

If independent patches cannot compose reliably, paging, prefetching, and enormous capacity are of no use.

---

# 32. Long-term Vision

If KMesh's core hypotheses hold, future models could move from:

```text
Large Dense / MoE Model
```

To:

```text
Small Shared Reasoning Core
+
Large Evolving Knowledge Mesh
+
Sparse Dynamic Access
```

The scale of knowledge could continue to grow:

$$
|\mathcal K|\rightarrow\infty
$$

While the current GPU working set remains bounded:

$$
|W_t|\ll|\mathcal K|
$$

Knowledge updates could follow:

```text
local patch update
↓
local relation update
↓
local compatibility validation
↓
global system continues to evolve
```

The ultimate aim:

> **Continual growth in capabilities without requiring the computational core, GPU memory, and full-training costs to grow at the same rate.**

This could become one underlying architectural path toward “AI for Everyone”: desktops, laptops, cellphones, and home servers could all have local AI that keeps growing, instead of always relying on downloading or retraining a huge, static, globally coupled model.

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

Translation of the Chinese formulation:

> **KMesh explores organizing knowledge into dynamically connected, locally updatable neural patches, mapping the semantic locality of knowledge to computation and update locality while preserving global composability across knowledge.**

---

# 35. Current Bottom Line

The question most worth prioritizing at present is not:

> “Can KMesh enable a 1B model to beat SOTA?”

But three more fundamental questions:

1. **Can independent pieces of knowledge actually become locatable, trainable patches?**
2. **Can these patches still compose reliably after independent updates?**
3. **Can a graph of knowledge relations reduce global compatibility to a local, manageable compatibility-validation problem?**

Only if these three points hold does KMesh have a basis for discussing:

- Larger knowledge networks;
- GPU/RAM/SSD hierarchies;
- Automatic formation of abstractions;
- Substantially lower training costs;
- Small shared cores;
- On-device and personal AI.

This is also where the next stage of research should remain focused.
