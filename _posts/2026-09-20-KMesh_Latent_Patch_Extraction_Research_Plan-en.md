---
title: KMesh Latent Patch Extraction Research Plan
lang: en
translation_key: kmesh-latent-patch-extraction
permalink: /en/posts/KMesh_Latent_Patch_Extraction_Research_Plan/
---

**Teacher Reasoning Trace → Persistent Task-Level Knowledge Patch**

> **Status**: Research plan draft v0.1  
> **Goal**: Define and validate an operational latent knowledge patch for KMesh: one extracted from a teacher LM's reasoning process, without storing raw Q/K/V token by token. It should remain stable on the timescale of a task/subtask and support repeated reading and reuse by a student LM across subsequent tokens and layers.

---

## 1. Core Problem

KMesh's long-term goal is to partially externalize knowledge from the dense parameters of large models, enabling knowledge to be:

- Independently addressed;
- Locally updated;
- Sparsely activated;
- Reused across tasks;
- Composed with other patches;
- Stored in tiers across GPU / RAM / SSD;
- Continually evolved through use.

A key question in the teacher–student approach is:

> **Can the large number of token-level hidden states / Q / K / V / attention patterns that a teacher forms during a reasoning episode be compressed into a small number of stable, task-level latent slots that serve as a knowledge patch the student can read over the long term?**

This patch should not merely be the teacher's instantaneous activation for a particular token, nor should it simply store the full raw KV cache.

What we hope to obtain is:

$$
\text{Teacher reasoning trajectory}
\rightarrow
\text{compact persistent patch}
\rightarrow
\text{Student repeated reuse}
$$

---

## 2. Working Hypotheses

### H1. Task-Level Stable Latent Exists

While the teacher's token-level activations change continually as it completes a task/subtask, they contain low-dimensional information that remains useful across multiple tokens.

This information should be more stable than a single token's activation and reusable across different phrasings and contexts.

### H2. Patch Should Persist Longer Than a Token

A knowledge patch should operate on a timescale significantly longer than a token.

Typical lifetimes:

- A reasoning episode;
- A subtask;
- Tens to thousands of tokens;
- Remaining readable across multiple subsequent student layers.

The KMesh runtime should therefore use:

$$
\text{slow working-set routing}
+
\text{fast token-level reading}
$$

Rather than retrieving and loading patches anew from RAM/SSD for every token.

### H3. Teacher Q/K/V Contain Different Kinds of Information

A rough functional interpretation:

- **K**: when this knowledge should be found;
- **V**: what information it provides once found;
- **Q**: what to look for next, given the current knowledge state.

A KMesh patch should therefore store or learn more than just “knowledge content”:

> **Which other knowledge this knowledge should usually relate to.**

But the teacher's raw Q is an instantaneous, strongly context-dependent, layer-specific quantity. A more reasonable approach is therefore:

> Distill a persistent query policy from the teacher's Q / K / attention behavior, rather than storing raw Q token by token.

### H4. Hidden / Residual State Is a Better Canonical Source Than Raw K/V

The teacher's residual / hidden state precedes the Q/K/V projections and is closer to a general internal representation.

A candidate long-term path:

$$
\text{Teacher hidden/residual trace}
\rightarrow
\text{Patch Compiler}
\rightarrow
Z_P
$$

The student itself then takes:

$$
Z_P
$$

And compiles it into its own layer-specific:

$$
K_P^{S,\ell},V_P^{S,\ell},Q_P^{S,\ell}
$$

Or a more general query policy.

### H5. Compact Oracle Patch Should Exist Before We Learn to Extract It

Before training a Patch Compiler, we should first answer:

> **Can the student already obtain sufficient task-level assistance through 4/8/16 latent slots?**

Therefore, first optimize student-side latent slots directly:

$$
Z_P^*
=
\arg\min_Z
L_{\text{task}}(Student(x,Z))
$$

If even this oracle patch cannot significantly help the student, teacher → patch extraction should not be prioritized.

---

## 3. A Candidate Abstraction for KMesh Patches

A long-term candidate:

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

Where:

- `id_i`: stable Patch ID;
- `content_i`: interpretable text / structured content;
- `Z_i`: canonical latent content;
- `Π_i^Q`: persistent query / navigation policy;
- `relations_i`: explicit or statistical relations with other patches;
- `version_i`: version;
- `provenance_i`: source.

The first stage of experiments does not need to implement every field.

---

## 4. Runtime Semantics of Patches

### 4.1 Load Once, Read Many

At a subtask boundary, load:

$$
Z_P
$$

Compile it once into what selected student readers need:

$$
K_P^{(\ell)},V_P^{(\ell)}
$$

Then read it repeatedly over hundreds of tokens:

$$
\alpha_{t,i}^{(\ell)}
=
\operatorname{softmax}
(
Q_t^{(\ell)}K_{P_i}^{(\ell)T}
)
$$

While the patch content itself remains unchanged.

### 4.2 Coarse Residency, Fine-Grained Reading

The resident working set

$$
W_\tau
$$

is updated on a longer timescale.

Each token / layer performs dynamic attention only within the resident working set.

That is:

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

For a patch that is only passive memory,

$$
P=(K,V)
$$

is sufficient.

But KMesh aims to support:

$$
P_A
\rightarrow
P_B
\rightarrow
P_C
$$

This kind of multi-hop knowledge navigation.

A longer-term patch should therefore have some form of:

$$
\Pi_i^Q
$$

Combined with the current task state:

$$
Q_i(t)
=
f(\Pi_i^Q,g_t)
$$

To express:

> After using this knowledge, what should be sought next?

---

## 5. What Should a Teacher Trace Record?

Record internal states from selected layers while the teacher carries out a full reasoning episode.

A candidate trace:

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

Where:

- $$H$$: residual / hidden states;
- $$Q$$: query trajectory;
- $$K$$: addressing representation;
- $$V$$: payload representation;
- $$A$$: attention logits / weights / attended structure.

### 5.1 Storing Post-RoPE Q/K by Default Is Not Recommended

If the model uses RoPE, post-RoPE Q/K contains token-position rotations.

Averaging across tokens would mix together:

- semantic variation;
- positional rotation;



Prioritize:

- hidden / residual state;
- pre-RoPE Q/K;
- V;
- attention logits / relations;
- attention output.

### 5.2 Dumping All Layers Is Not Recommended as a Long-Term Approach

Record at most a few representative layers in the first stage.

Reasons:

- High I/O volume;
- Inconsistent representation spaces across layers;
- Difficulty interpreting contributions afterward;
- A tendency to make the Patch Compiler more complex.

Initial recommendations:

- early-middle layer;
- middle layer;
- middle-late layer;

For a total of 3–4 candidate layers.

Choose the specific layer indices by their relative position in the teacher's depth, rather than hard-coding absolute layer indices.

---

## 6. Research Stage 0: Oracle Patch

This is the highest priority.

### 6.1 Purpose

Test:

> **Whether the student's patch interface can actually carry task-level auxiliary information in very few latent slots.**

### 6.2 Method

Freeze the student backbone.

For each task / task family, create:

$$
Z\in\mathbb R^{m\times d}
$$

Where:

$$
m\in\{1,4,8,16\}
$$

Optimize $$Z$$ directly using the task loss.

For example:

$$
Z^*
=
\arg\min_Z
L_{\text{answer}}
$$

Possible patch injection options:

- 1 layer;
- 3 layers;
- A side-path reader;
- cross-attention memory.

### 6.3 Required Controls

#### No Patch

The student's original capabilities.

#### Text Patch

Provide the same knowledge to the student as text context.

#### Random Latent

Random vectors of the same size.

#### Oracle Latent

Patch slots optimized directly through gradients.

### 6.4 Key Questions

1. Are 4/8/16 slots sufficient?
2. Can the same patch be reused across multiple queries?
3. Can a patch remain useful for 256/512/1024 tokens?
4. After a single injection, are repeated refreshes needed later?
5. At which layers is patch injection most effective?
6. Can multiple patches compose?

### 6.5 Conditions for Continuing

If, compared with:

- no patch;
- random patch;
- text patch;

the oracle latent does not significantly improve performance on held-out tasks from the same knowledge family, pause teacher latent extraction and prioritize redesigning the student's patch interface.

---

## 7. Research Stage 1: Non-Learned Extraction Baselines

Test simple pooling before training a complex Patch Compiler.

### 7.1 Single Marker Token

Append the following to the teacher's input:

```text
<KMESH_PATCH>
```

Take this token's hidden state at a selected layer:

$$
Z=h_{\text{marker}}^{(\ell)}
$$

If the student can use it, this is the simplest reusable latent patch.

### 7.2 Mean Pooling

For the episode's hidden states at a selected layer:

$$
z_\ell
=
\frac1T
\sum_t h_t^{(\ell)}
$$

Compare:

- all-token mean;
- answer/reasoning-only mean;
- masked mean;
- final-window mean.

### 7.3 Exponential Moving Average

$$
z_t
=
\beta z_{t-1}
+
(1-\beta)h_t
$$

Test:

$$
\beta \in
\{0.9,0.99,0.999\}
$$

To see whether a persistent state outperforms ordinary averaging.

### 7.4 Fixed Temporal Sampling

For example, take hidden states from each episode at:

- 25%;
- 50%;
- 75%;
- end;

Then concatenate / project them.

### 7.5 Selected-Head / Function-Vector Style Pooling

Analyze the outputs or attention behavior of a few attention heads to find heads with clear task-level utility.

Rather than requiring the student to copy raw Q/K/V, test:

> Whether the teacher already forms a compact task representation in a small number of heads.

---

## 8. Research Stage 2: Learned Patch Compiler

Enter this stage if the oracle patch is clearly effective but simple pooling still falls far short of the oracle.

### 8.1 Basic Architecture

Input:

$$
\mathcal T
=
\text{teacher trace}
$$

First project the different layers / heads:

$$
x_{t,\ell,h}
=
P_{\ell,h}(
H,Q,K,V,A
)
$$

Then use

$$
m
$$

learned patch queries:

$$
R=[r_1,\ldots,r_m]
$$

to perform cross-attention:

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

Producing a fixed-size representation:

$$
Z_P\in\mathbb R^{m\times d_P}
$$

### 8.2 Keep the Initial Architecture as Small as Possible

Constrain the first version of the Patch Compiler to:

- 1–2 cross-attention layers;
- A small hidden size;
- A parameter count far smaller than the student's;
- No growth into another large model.

Otherwise, it would be impossible to establish that gains come from patch extraction rather than hidden additional computational capacity.

---

## 9. How Should Teacher Q/K/V Be Used?

### 9.1 Hidden / Residual as Main Content Signal

Use:

$$
H
$$

as the main source of patch content.

Reasons:

- It precedes the Q/K/V projections;
- It is more general;
- It transfers more naturally across readers;
- It contains the integrated state after attention + MLP.

### 9.2 Q/K as Navigation Signal

Use Q/K primarily to learn:

> knowledge navigation / relation structure.

The student's raw Q is not required to equal the teacher's raw Q.

It is more reasonable to transfer the relation geometry encoded by:

$$
QK^\top
$$



For example, the teacher attention target:

$$
A_T
=
\operatorname{softmax}
(
Q_TK_T^\top
)
$$

student patch reader:

$$
A_S
=
\operatorname{softmax}
(
Q_SK_S^\top
)
$$

We can add:

$$
L_{\text{relation}}
=
D_{KL}(A_T\|A_S)
$$

### 9.3 V as Payload Signal

V / attention output can provide an auxiliary signal about:

> What content the teacher is actually passing to subsequent computation at the current point.



But we do not directly assume that raw V is a canonical patch.

---

## 10. Training Objectives for the Patch Compiler

Do not make “reconstruct all teacher activations” the primary objective.

The core objective is:

> Enable the student to complete the task using the patch while preserving the teacher's necessary relational behavior.

Suggested objective:

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

The student's final task output.

This is the primary loss.

### 10.2 Teacher Behavior Loss

Possible distillation targets:

- answer logits;
- intermediate attention relation;
- selected patch ranking;
- next-knowledge retrieval behavior.

The internal coordinates need not be identical.

### 10.3 Cross-Context Consistency

For the same knowledge / skill expressed in different phrasings and contexts:

$$
\mathcal T_1,
\mathcal T_2,
\mathcal T_3
$$

The traces should produce similar patches:

$$
Z_1\approx Z_2\approx Z_3
$$

Possible approaches:

- cosine consistency;
- contrastive loss;
- matching / set loss.

### 10.4 Composition Loss

If

$$
P_A+P_B
$$

should jointly solve a problem, train the student to use both for held-out compositions.

Avoid having patches merely memorize the answers to individual tasks.

### 10.5 Bottleneck Loss

Control the patch's:

- Number of slots;
- dimension;
- norm;
- information capacity.

The goal is to find:

> The smallest persistent latent state that is still sufficiently useful.

---

## 11. Temporal Structure

Simple mean pooling assumes that an entire episode has only one state, which may not hold.

### 11.1 First Version

Use a fixed number of learned slots:

$$
m=4/8/16
$$



Let the slots learn different phases themselves.

### 11.2 Later Version: Change-Point Aware

If the reasoning trajectory is found to have distinct phases:

$$
S_1\rightarrow S_2\rightarrow S_3
$$

Explore:

- hidden cosine change;
- attention distribution shift;
- Q distribution shift;

To detect phase boundaries.

Compress the different phases into:

$$
z_1,z_2,z_3
$$

Then form a patch.

This stage is not required in the first round.

---

## 12. Student Patch Reader

The Patch Compiler and student reader must be separate.

### 12.1 Input

$$
Z_P
$$

is the persistent canonical patch.

### 12.2 Compile on Load

When the patch is loaded onto the GPU, compute once:

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

Cache these K/V for selected reader layers.

### 12.3 Token-Level Use

For each token:

$$
Q_t^{(\ell)}
=
W_{Q,\ell}^{S}h_t
$$

Read:

$$
\alpha_{t,P}
=
\operatorname{softmax}
(
Q_tK_P^\top
)
$$

Without re-encoding the patch.

### 12.4 Query Policy Extension

Later research could add:

$$
\Pi_P^Q
$$

For use in:

$$
Q_P(t)
=
f(
\Pi_P^Q,
g_t
)
$$

Representing:

> After using this knowledge, what should be retrieved next?

This mechanism connects to the KMesh graph / multi-hop retrieval.

---

## 13. Dataset Design

Do not start directly with large-scale open-world data in the first stage.

Controlled data is needed to validate patch utility.

### 13.1 Synthetic Rule World

Continue using KMesh E0 data.

Advantages:

- Clear ground truth;
- The patches that must compose are known;
- Counterfactual updates can be constructed;
- Multi-hop behavior can be measured.

This is suitable for initially validating the latent patch interface.

### 13.2 Small Real-World Task Families

Add real-world tasks in the second stage, such as:

- Wikidata factual relations;
- HotpotQA multi-hop;
- Small coding API / rule tasks;
- MQuAKE knowledge updates.

Every patch must have:

- source;
- task family;
- held-out queries;
- composition tests.

---

## 14. Teacher Data Collection

The teacher should be an open-weight model so that its internal activations can be accessed.

### 14.1 Required Logs

For each reasoning episode, save:

- input / prompt;
- teacher output;
- selected layer hidden states;
- pre-RoPE Q/K;
- V;
- attention logits or top-k attention structure;
- optional MLP activations;
- task result / verifier result.

### 14.2 Avoid Full Trace Storage When Possible

First extract summary statistics / selected states online.

Retain full raw traces for only a small number of examples for analysis.

Otherwise, storage and I/O will quickly become the main costs.

---

## 15. Core Experiments

### Experiment A: Does Compact Oracle Patch Exist?

Compare:

- no patch;
- text patch;
- random latent;
- 1-slot oracle;
- 4-slot oracle;
- 8-slot oracle;
- 16-slot oracle.

Metrics:

- held-out task accuracy;
- cross-context reuse;
- composition;
- patch read FLOPs;
- patch bytes.

### Experiment B: Which Teacher Signal Is Most Useful?

Keep the student and patch size fixed.

Compare:

- hidden only;
- Q/K relation only;
- V only;
- hidden + Q/K relation;
- hidden + Q/K/V;
- hidden + attention output.

Do not compare raw coordinate reconstruction.

### Experiment C: Simple Smoothing vs Learned Compiler

Compare:

1. marker token;
2. mean pooling;
3. EMA;
4. fixed temporal sampling;
5. selected-head pooling;
6. learned 4-slot resampler;
7. learned 8-slot resampler;
8. oracle upper bound.

### Experiment D: Patch Persistence

After generating a patch once, test the student over:

- 64 tokens;
- 256 tokens;
- 512 tokens;
- 1024 tokens;

without refreshing the patch.

Observe whether utility decays quickly over time.

### Experiment E: Cross-Context Reuse

The teacher generates a patch from context A.

The student uses it in:

- B;
- C;
- D;

On tasks with different surface forms but the same underlying knowledge / skill.

This is the key experiment for distinguishing:

> task knowledge patch

From:

> compressed episode cache



### Experiment F: Multi-Patch Composition

Extract the following separately from independent teacher episodes:

$$
P_A,
P_B,
P_C
$$

The student uses the following on tasks that have never been jointly trained:

$$
P_A+P_B
$$

Or:

$$
P_A+P_B+P_C
$$

To test composability.

---

## 16. Ablations

At a minimum, include:

### Teacher Layer

Different source layers.

### Patch Size

1 / 4 / 8 / 16 / 32 slots.

### Student Reader Layer

early / middle / late / multi-layer.

### Patch Refresh Frequency

never / 1024 / 512 / 128 token.

### Teacher Signals

H / QK relation / V / combination.

### Compiler Capacity

linear / MLP / 1-layer cross-attn / 2-layer cross-attn.

---

## 17. Metrics

### Quality

- task accuracy;
- exact match;
- verifier pass;
- multi-hop accuracy.

### Generalization

- held-out phrasing;
- held-out entity;
- held-out composition;
- cross-task transfer.

### Patch Efficiency

- bytes per patch;
- slots per patch;
- read FLOPs;
- compile FLOPs;
- load latency.

### Persistence

- accuracy vs tokens since load;
- utility half-life.

### Portability

- same patch across multiple students;
- reader size;
- retraining cost.

### Composition

- pair composition;
- 3-way composition;
- composition after sequential patch updates.

---

## 18. Failure Modes

### F1. Oracle Patch Does Not Help

This indicates that the student's patch interface is not strong enough, or that the task itself cannot be represented by a small latent memory.

Prioritize changing the reader, not the Patch Compiler.

### F2. Mean Pooling Equals Oracle

This is a good result.

It indicates that the task-level state is simple and does not require a complex compiler.

### F3. Learned Compiler Works Only on Same Prompt

This indicates that what is extracted is an episode cache, not reusable knowledge.

Strengthen cross-context training.

### F4. Deep Teacher Layers Hurt

This may indicate that the teacher representation is too model-specific.

Try middle layers, multi-layer pooling, and relation distillation.

### F5. Patch Utility Quickly Decays

Possible requirements:

- recurrent refresh;
- task state interaction;
- query policy;
- multi-stage patch.

### F6. Multi-Patch Composition Fails

This is one of the most important risks.

It needs to be addressed in conjunction with:

- KMesh relation graph;
- coactivation training;
- A³E-style composition evaluation;
- graph-guided compatibility training.

---

## 19. Implementation Plan

Suggested additions to the repository:

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

- [ ] The student supports fixed latent slots;
- [ ] A patch can be read continuously throughout an episode;
- [ ] Support 1/4/8/16 slots;
- [ ] The patch's physical loading location does not affect results.

### M1 — Oracle Patch

- [ ] Task-specific latent slots can be directly optimized;
- [ ] Plot the patch size → quality curve;
- [ ] Validate cross-context reuse;
- [ ] Validate multi-patch composition.

**Go/No-Go:**
If the oracle patch cannot deliver clear gains, do not proceed to complex teacher extraction.

### M2 — Teacher Trace Recorder

- [ ] hidden state capture;
- [ ] pre-RoPE Q/K;
- [ ] V;
- [ ] attention relation;
- [ ] configurable layer/head selection.

### M3 — Non-Learned Patch Extraction

- [ ] marker token;
- [ ] mean;
- [ ] EMA;
- [ ] fixed sampling;
- [ ] selected-head pooling.

### M4 — Learned Patch Compiler

- [ ] fixed-slot cross-attention resampler;
- [ ] 4/8/16 slots;
- [ ] student task loss;
- [ ] cross-context consistency;
- [ ] relation distillation.

### M5 — Persistent Query Policy

- [ ] Learn patch navigation from the teacher's Q/K behavior;
- [ ] The patch generates a next-patch query;
- [ ] Integrate with the KMesh coactivation graph.

---

## 21. Research Claims We Should NOT Make Yet

At the current stage, do not claim that:

- A general knowledge latent has been found;
- Teacher Q/K/V can be compressed losslessly;
- A patch can be used directly across arbitrary models;
- KMesh can replace foundation-model pretraining;
- 4/8 slots are sufficient to store complex knowledge;
- A task vector is equivalent to a knowledge patch;
- Local updates have solved global composability.

What we actually need to test now is:

> **Whether there exists a compact, persistent, reusable task-level latent state that lets a small student reuse knowledge and knowledge-navigation behavior from a teacher reasoning episode that have value across contexts.**

---

## 22. Central Research Question

> **Can a teacher model’s token-level reasoning trajectory be compiled into a small persistent latent patch that preserves both what the teacher knows and how that knowledge should connect to other knowledge, and can a smaller student reuse that patch across many downstream tokens and contexts?**

Chinese version (translated):

> **Can a teacher LM's token-level internal trajectory during a reasoning episode be compiled into a small number of persistent latent knowledge patches that preserve both “what is known” and “which other knowledge it should relate to,” and allow a smaller student to reuse them repeatedly across subsequent tokens and different contexts?**

---

## 23. Immediate Next Step

Do not train a Patch Compiler as the first step.

First complete:

1. student patch reader;
2. oracle patch optimization;
3. The three sets of experiments on patch size / persistence / composition.

Only after confirming that:

$$
\text{small persistent latent patch exists}
$$

should we invest in teacher Q/K/V trace extraction and Patch Compiler research.

This will substantially reduce research risk and make all subsequent results easier to interpret.
