---
title: KMesh Multi-Expert Knowledge Construction Research Plan
lang: en
translation_key: kmesh-multi-expert-knowledge-construction
category: research
permalink: /en/posts/KMesh_Multi_Expert_Knowledge_Construction_Research_Plan/
---

**Independently Trained Small Models → Shared KMesh → Cross-Domain Composition**

> **Status**: Research plan draft v0.1  
> **Project**: KMesh  
> **Theme**: Use a collection of small, domain-specialized LMs as distributed knowledge compilers to jointly build and continually update a shared KMesh, rather than relying on a single large teacher LM to learn all knowledge.

---

## 1. Research Motivation

KMesh starts from the following hypothesis:

> An AI system's general computation capability and knowledge capacity do not have to remain permanently bound to the same set of dense neural weights.

Traditional foundation models compress general language capabilities, reasoning patterns, world knowledge, and domain knowledge into a single large neural network through large-scale pretraining. This makes knowledge updates expensive, causes knowledge from different domains to occupy backbone parameters together, makes training heavily dependent on large synchronized clusters, and makes changes in individual domains difficult to update independently.

KMesh seeks to change this paradigm:

$$
\text{Small Shared Computation Core} + \text{Large Evolving Knowledge Mesh}
$$

This research takes the idea further:

> **Knowledge from different domains need not be learned collectively by one enormous LM. Multiple small domain LMs can be post-trained independently, then compile what they have learned into compatible KMesh patches that jointly update a shared knowledge network.**

The goal is not to establish:

$$
100\times1B \approx 100B
$$

Instead, it is to validate:

$$
\boxed{\text{Independent Domain Learning} \rightarrow \text{Shared External Knowledge} \rightarrow \text{Cross-Domain Composition}}
$$

---

## 2. Central Research Question

> **Can independently trained small domain models contribute compatible latent knowledge patches to a shared KMesh, such that the resulting system solves cross-domain tasks that none of the individual domain models was trained on?**

---

## 3. Core Hypotheses

### H1. Domain Knowledge Can Be Learned Locally

Small LMs can learn the knowledge and local reasoning patterns of a specialized domain through domain post-training—for example, Math, Code, Systems, Biology, Physics, or Law.

These models do not each need comprehensive general world knowledge. They only need:

$$
\text{shared base capability} + \text{domain specialization}
$$

### H2. Shared Base + Domain Delta Is Preferable to Independent Pretraining

If every domain model starts from random initialization, each must relearn tokenizer semantics, syntax, basic reasoning, instruction following, and common concepts.

The first stage therefore uses:

$$
E_d = B + \Delta_d
$$

Where:

- $$B$$: shared seed/base model;
- $$\Delta_d$$: domain adapter / LoRA / small expert.

### H3. Domain Models Are Knowledge Compilers, Not Runtime Experts

Domain models are primarily used for:

$$
\text{domain data}
\rightarrow
\text{domain post-training}
\rightarrow
\text{reasoning trajectories}
\rightarrow
\text{knowledge patches}
\rightarrow
\text{KMesh}
$$

Once patches have been generated, the domain models can be taken offline. The final deployed system consists primarily of:

$$
\text{small general runtime core} + \text{shared KMesh}
$$

### H4. Merge Knowledge, Not Model Weights

Existing model-merging approaches are prone to parameter interference.

KMesh explores:

$$
E_A \rightarrow P_A,\qquad E_B \rightarrow P_B
$$

The runtime reader must then compose these patches correctly:

$$
\text{Reader}(P_A,P_B)
$$

In other words:

> **Do not merge models; merge knowledge.**

### H5. Cross-Domain Composition Is the Critical Test

Learning within a single domain is not the hardest problem.

The critical question is whether the following combinations work correctly on tasks for which they have never been jointly trained:

$$
P_{\text{math}} + P_{\text{code}}
$$

$$
P_{\text{systems}} + P_{\text{networking}}
$$

$$
P_{\text{biology}} + P_{\text{statistics}}
$$

### H6. A Shared Patch ABI Is Required

The raw latent spaces of different domain experts are not inherently compatible.

KMesh needs a unified:

$$
\boxed{\text{KMesh Patch ABI}}
$$

This may include:

- Canonical patch content;
- Canonical latent representation;
- Provenance;
- Version;
- Query/navigation policy;
- Relations;
- Confidence;
- Validation metadata.

---

## 4. Relation to Existing Research

### 4.1 Branch-Train-Merge (BTM)

BTM branches multiple domain experts from a common seed model, trains them independently in different domains, and then combines them through ensembling / averaging.

Key takeaways:

- Domain training can be embarrassingly parallel;
- Gradient synchronization is not required throughout training;
- Domain models can develop independently with little communication.

KMesh takes this further: instead of requiring a final merge back into one set of weights, it extracts knowledge into shared patches.

### 4.2 Branch-Train-MiX (BTX)

BTX recombines independently trained domain models into an MoE and trains routing.

It shows that the capabilities of independent experts can be coordinated by a unified runtime.

KMesh differs in that experts primarily serve as patch producers, rather than remaining the main components of the final runtime.

### 4.3 Branch-Train-Stitch (BTS)

BTS connects frozen domain experts using lightweight stitch layers.

Takeaways:

- Independent expert representations can be realigned through small interfaces;
- Experts can be added or removed.

This is closely related to KMesh's Patch ABI / student reader.

### 4.4 AdapterFusion

Adapters are trained independently first, and then their composition is learned.

KMesh aims to move this composition from adapter weights to external knowledge patches.

### 4.5 MoE Shared Experts

Recent MoE analyses suggest that there may be a small group of experts shared across domains, while peripheral experts lean more toward domain-specific knowledge.

This is consistent with:

$$
\text{small shared reasoning core} + \text{many peripheral knowledge modules}
$$

KMesh further explores externalizing this peripheral knowledge into patches.

### 4.6 Federated / Continual Learning

Federated continual learning also studies domain expertise across different clients and their collective collaboration.

The distinction is:

> Traditional methods primarily aggregate weights or gradients; KMesh primarily aggregates addressable knowledge patches.

---

## 5. Proposed Architecture

### 5.1 Shared Seed Model

The first stage uses a small shared base:

- 300M
- 0.5B
- 1B
- 3B

The recommended size for the first round is:

$$
0.5B\sim1B
$$

The goal is to study the mechanism, rather than pursue absolute performance.

### 5.2 Domain Experts

For each domain:

$$
E_d = B + \Delta_d
$$

Where $$\Delta_d$$ may be:

- LoRA;
- An adapter;
- A small expert;
- A selective fine-tuning module.

Prioritize LoRA / adapters for the first round.

### 5.3 Domain Patch Writer

Each domain expert produces a candidate patch in a unified format through:

$$
\text{domain reasoning trace}
\rightarrow
\text{Patch Writer}
\rightarrow
P_i
$$

### 5.4 Shared KMesh

Multiple experts jointly submit patch proposals to a shared KMesh:

```text
Expert A ─┐
Expert B ─┼→ Candidate Patches → KMesh Consolidator → Shared KMesh
Expert C ─┘
```

### 5.5 KMesh Consolidator

Responsible for:

- Canonicalization;
- Deduplication;
- Version management;
- Provenance;
- Conflict detection;
- Compatibility validation;
- Graph updates;
- Promotion / rejection.

A domain model is only a **patch proposer**, not an authoritative source of truth.

---

## 6. Patch Compatibility Strategy

### 6.1 Shared Seed Geometry

In the first round, all experts must branch from the same base.

This keeps their representation spaces closer together and reduces the difficulty of alignment.

### 6.2 Domain-to-KMesh Projection

For each domain expert:

$$
h_d \xrightarrow{A_d} z_{\mathrm{KMesh}}
$$

Where $$A_d$$ should remain lightweight.

The goal:

> Domain-specific latent → shared canonical KMesh latent.

### 6.3 Canonical Content Backup

Each latent patch also retains:

- Textual / symbolic content;
- Provenance;
- Source;
- Domain latent;
- Canonical KMesh latent.

This allows recompilation when the student / expert changes in the future.

---

## 7. Cross-Domain Bridge Patches

Different domains can easily become knowledge islands, so bridge formation requires dedicated study.

### 7.1 Real Cross-Domain Tasks

When a task activates patches from multiple domains:

$$
P_A + P_B
$$

This creates coactivation / transition relations.

### 7.2 Dedicated Cross-Domain Post-Training

Construct tasks combining:

- Math + code;
- Systems + networking;
- Biology + statistics;
- Physics + numerical methods.

### 7.3 Coordinator / Generalist

Allow a medium-sized generalist that:

- Is not responsible for learning all knowledge;
- Specializes in complex cross-domain composition;
- Queries multiple domain experts when needed;
- Forms bridge patches.

---

## 8. Conflict Handling

Multiple experts will inevitably produce conflicts.

The process cannot be:

```text
emit patch → directly commit
```

Instead, it should be:

```text
candidate patch
     ↓
deduplication
     ↓
provenance check
     ↓
semantic conflict detection
     ↓
version / condition resolution
     ↓
validation
     ↓
promotion
```

---

## 9. Research Stage E0: Two-Domain Proof of Concept

### Domains

Recommended starting domains:

- Math;
- Code.

Reasons:

- Data is readily available;
- Verifiers are well defined;
- Cross-domain tasks are easy to construct.

### Models

Both experts use the same base, with a parameter count of:

$$
0.5B\sim1B
$$

Train two domain adapters:

$$
E_{\text{math}}
$$

And:

$$
E_{\text{code}}
$$

### Goal

Independently produce the two patch sets:

$$
P_{\text{math}}
$$

And:

$$
P_{\text{code}}
$$

Then test whether their combination can solve tasks that none of the individual experts was trained on:

$$
P_{\text{math}} + P_{\text{code}}
$$

---

## 10. E0 Baselines

### B0. Base Only

The shared base, with no experts and no KMesh.

### B1. Domain Expert

Directly invoke the corresponding domain expert.

### B2. Multi-Expert Ensemble

Run inference with both experts, then aggregate their outputs.

### B3. Adapter / Expert Fusion

Combine at the parameter level.

### B4. Textual RAG

Provide knowledge from both domains to the base as text.

### B5. KMesh Patches

The two independent experts contribute only patches; the runtime core reads both patches.

---

## 11. E0 Key Tests

### 11.1 Single-Domain Transfer

Does a Math patch improve the base's performance on held-out math tasks?

### 11.2 Cross-Domain Composition

Can independently trained Math / Code patches compose on new tasks?

### 11.3 No Joint Retraining

Key constraint:

> $$P_M$$ and $$P_C$$ must not be jointly trained during their generation.

### 11.4 Patch Replacement

Update only:

$$
P_M^v \rightarrow P_M^{v+1}
$$

Verify that:

- Code-only tasks do not change significantly;
- Cross-domain tasks correctly reflect the math update.

---

## 12. Research Stage E1: 8-Domain Scaling

Expand to:

1. Math
2. Code
3. Systems
4. Networking
5. Physics
6. Biology
7. Law
8. General Knowledge

Main research questions:

- Does compatibility decline as the number of experts grows?
- Do domain islands form?
- Can the coactivation graph automatically form bridges?
- Is a coordinator needed?
- Does a small set of shared core patches emerge?

---

## 13. Research Stage E2: Heterogeneous Experts

The same base is no longer required.

For example:

- A 0.5B model A;
- A 1B model B;
- A 3B model C;
- Different architectures.

Each model uses its own projection into the canonical KMesh latent:

$$
A_d
$$

The goal:

> Verify whether KMesh knowledge is truly independent of any particular model.

---

## 14. Research Stage E3: Distributed Knowledge Training

Make expert training truly distributed:

```text
Node 1 → Math
Node 2 → Code
Node 3 → Biology
Node 4 → Systems
...
```

Exchange only:

- Patches;
- Graph updates;
- Validation metadata.

Do not perform:

- Step-level gradient synchronization;
- Full-model AllReduce.

Measure:

- Network traffic;
- Wall-clock scaling;
- Patch merge latency;
- Update throughput.

---

## 15. Knowledge Contribution Protocol

A domain expert submits:

```text
PatchProposal
├── patch_id_candidate
├── canonical_content
├── latent_representation
├── provenance
├── domain
├── confidence
├── task_evidence
├── query_policy
└── initial_relation_evidence
```

The Consolidator returns:

```text
accepted
rejected
merged
superseded
conflict
needs_validation
```

---

## 16. Graph Construction

Domain experts do not need to know the complete set of global relations in advance.

The graph primarily derives from:

- Semantic similarity;
- Runtime coactivation;
- Transitions;
- Task outcomes;
- Gradient compatibility;
- Cross-domain task evidence.

A teacher/domain expert may provide an initial prior, but the functional graph should primarily emerge through actual use.

---

## 17. Metrics

### Knowledge Quality

- Domain task accuracy;
- Factual correctness;
- Verifier pass rate.

### Composition

- Pairwise cross-domain composition;
- Three-domain composition;
- Unseen composition.

### Local Update

- Updated parameter count;
- Patch bytes updated;
- FLOPs per update;
- Retention on unrelated tasks.

### Compatibility

- Composition after sequential updates;
- Conflict rate;
- Bridge-patch success.

### Scaling

- Performance vs. number of experts;
- Training cost vs. number of experts;
- Communication volume;
- KMesh size.

### Runtime

- Patch working set;
- Retrieval cost;
- Reader FLOPs;
- Latency;
- Cache hit rate.

---

## 18. Critical Ablations

### Same Base vs Independent Base

Test whether a shared seed is necessary.

### Text Patch vs Latent Patch

Test the benefit of neural patches.

### Joint Training vs Independent Training

Test whether independent domain learning is genuinely composable.

### Explicit Bridge vs Emergent Bridge

Test whether cross-domain bridges require human / teacher assistance.

### Coordinator On/Off

Test whether a generalist is necessary.

### Canonical Projection Size

Test whether the Patch ABI can remain lightweight.

---

## 19. Failure Modes

### F1. Independent Patches Cannot Compose

This would indicate:

$$
\text{independent learning} \not\Rightarrow \text{shared composability}
$$

Areas to improve:

- Canonical alignment;
- Composition training;
- Bridge patches;
- Shared reader.

### F2. Shared Base Stores Most Knowledge

If the base retains almost all domain capabilities after all domain patches are removed, external knowledge is not actually playing the primary role.

### F3. Canonical Adapter Becomes Too Large

If $$A_d$$ must be very complex to align representations across models, the value of the KMesh ABI is limited.

### F4. Experts Duplicate Common Knowledge

This requires:

- Deduplication;
- Canonicalization;
- Shared-core separation.

### F5. Domain Islands

Insufficient connections across domains lead to composition failure.

### F6. Conflict Explosion

Domain updates contradict one another, causing Consolidator costs to grow rapidly.

---

## 20. Go / No-Go Criteria

### Stage E0 Go

Before further scaling, at least the following must hold:

1. Both independent domain experts can produce effective patches;
2. Patches clearly help on held-out domain tasks;
3. Patches can compose on cross-domain tasks without joint training;
4. KMesh patches clearly outperform random latents;
5. Local replacement does not significantly disrupt the other domain.

### Stage E1 Go

Before moving to heterogeneous experts:

1. No severe compatibility collapse occurs in the eight-domain setting;
2. The graph produces useful cross-domain bridges;
3. Patch merge / deduplication costs remain manageable;
4. Composition is maintained after sequential updates.

---

## 21. Implementation Structure

Suggested additions:

```text
kmesh/
├── experts/
│   ├── base_model.py
│   ├── domain_adapter.py
│   ├── trainer.py
│   └── registry.py
├── patch_writer/
│   ├── trace_reader.py
│   ├── compiler.py
│   ├── domain_projector.py
│   └── proposal.py
├── mesh/
│   ├── store.py
│   ├── graph.py
│   ├── consolidator.py
│   ├── conflict.py
│   ├── versioning.py
│   └── provenance.py
├── runtime/
│   ├── reader.py
│   ├── router.py
│   ├── coordinator.py
│   └── bridge.py
├── experiments/
│   ├── two_domain/
│   ├── eight_domain/
│   ├── heterogeneous/
│   └── distributed/
└── eval/
    ├── domain.py
    ├── composition.py
    ├── compatibility.py
    └── scaling.py
```

---

## 22. Suggested First Concrete Experiment

### Base

A 0.5B–1B open-weight base.

### Expert A

A Math adapter.

Data:

- GSM-like;
- Symbolic arithmetic;
- Algebraic reasoning.

### Expert B

A Code adapter.

Data:

- Python;
- Algorithm implementation;
- Executable unit-test tasks.

### Cross-Domain Tasks

Construct problems that require both:

$$
\text{math reasoning} + \text{code generation}
$$

Examples include:

- Deriving a formula and then writing a program;
- Implementing numerical algorithms;
- Combinatorial computation;
- Symbolic derivation + executable verification.

Key constraint:

> The Math expert and Code expert never jointly see these cross-domain tasks during training.

---

## 23. Strongest Claim We Eventually Want to Test

> **A large knowledge system does not need to be learned by one large synchronized model. Independent small models can learn local domains, compile their knowledge into a shared external mesh, and create capabilities through composition that none of the individual models possess alone.**

---

## 24. Claims We Should NOT Make Yet

We should not currently claim that:

- Multiple 1B models are equivalent to one 100B model;
- Small models can fully replace large foundation models;
- Domain patches are inherently compatible;
- KMesh has solved cross-domain reasoning;
- The shared base can be made arbitrarily small;
- Large teachers are no longer needed;
- Independent training is necessarily more efficient than joint pretraining.

What we actually need to validate now is:

> **Whether independent domain learning can be transformed, through a shared KMesh, into stable, composable overall capabilities that can be updated incrementally.**

---

## 25. Immediate Next Step

In priority order:

1. Select a small shared base;
2. Set up two domain adapters;
3. Design independent Math / Code training data;
4. Define a unified Patch Proposal / Patch ABI;
5. Train the two experts;
6. Extract patches;
7. Freeze the experts;
8. Use a unified runtime core to test single-domain and cross-domain tasks;
9. Run a composition test with no joint training;
10. Run a one-sided patch update + cross-domain regression test.

Only after E0 succeeds should the research expand to more domains and truly distributed training.
