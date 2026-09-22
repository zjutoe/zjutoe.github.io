---
title: CapKnow - Capability Knowledge Space Certificate Laboratory
lang: en
translation_key: capknow
category: research
permalink: /en/posts/CapKnow/
---

This project studies a controlled question: if a system's capability states have structure, can observing responses to only a small number of tasks identify its complete capability state and yield a reproducible, verifiable **capability certificate**?

The current project is a small-scale research laboratory with enumerable states and manually defined structure. Phases 2–7 have produced independently reviewed evidence on deterministic and probabilistic methods and structural compression. Phase 8 failed its Toy LM feasibility gate and was stopped as a valid negative result. Phase 9 currently consists only of a committed protocol proposal, with no implementation or experimental validation. The project has no validation results on real or open LLMs.

Repository: [CapKnow](https://github.com/zjutoe/CapKnow.git)

## Research Objects

Let the task universe be $$Q$$, a capability state be $$K\subseteq Q$$, and the family of admissible states be $$\mathcal K\subseteq 2^Q$$. The task response $$Y(K,q)$$ maps a latent state to observable behavior.

- `Task`: an executable or observable probe.
- `KnowledgeState`: a candidate capability configuration.
- `KnowledgeSpace`: the admissible states and their structural constraints.
- Response signature: a state's response vector over all or some of the tasks.
- Fixed certificate: a single subset of tasks asked of every subject that still distinguishes all candidate states.
- Adaptive certificate: tasks chosen based on previous answers, with each decision-tree leaf uniquely identifying a state.

The research follows the order “verify identifiability first, then discuss low-cost certificates.” If different states still produce the same signature over the full task set, neither a fixed nor an adaptive certificate can uniquely recover the state. Under noise, the goal instead becomes posterior inference under a given response model and prior.

## Current Phases and Evidence Status

| Phase | Research Focus | Current Conclusion |
| --- | --- | --- |
| Phase 1 | Knowledge spaces, state validation, and deterministic responses | Chain, tree, and unstructured worlds and a basic simulator have been established |
| Phase 2 | Full-information identifiability | The three standard worlds are identifiable; the auditor detects deliberately constructed collisions between complete response vectors |
| Phase 3 | Exact fixed certificates | The minimum sizes for chain/tree/unstructured are `4/4/3`, respectively; all require the full task set |
| Phase 4 | Adaptive certificates | Under equal weighting of states, chain/tree have a lower average depth than the fixed certificate size; unstructured has no such advantage |
| Phase 5 | Noisy probabilistic inference | The Bayesian fixed/adaptive inference loop and zero-noise consistency have been validated; there is no general conclusion about which is better |
| Phase 6 | Executable DSL bridge | Primitives, compositions, and held-out compositions have well-defined execution semantics; the rules are still manually defined |
| Phase 7 | Structural compressibility | Fixed compression holds in the block world; the prefix family also achieves adaptive average savings on the tested grid |
| Phase 8 | Toy LM feasibility | `11/24` cells passed; the formal result is `FAILED`/stopped; no model selection and no 010D |
| Phase 9 | Decomposed learned-behavior bridge | A protocol proposal has been committed; it has not been implemented or run, and no experimental artifact has been produced |
