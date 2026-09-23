---
title: Evaluating Local Language Models for Coding
description: Evaluating the completeness and correctness of Qwen and Bonsai on KMesh coding tasks, with Codex handling planning and review.
lang: en
translation_key: coding-agent-estimate
category: review
permalink: /en/posts/Coding_Agent_Estimate/
---

## Background

Since Codex released its 5.6 and 6 models, token consumption has been too high, so I tried using local language models for coding tasks. The two models tested were:

- **Qwen-3.8 27B**.
- **PrismML Bonsai-2 27B**.

Both models worked reasonably well in initial use. PrismML Bonsai has a small resource footprint and runs smoothly on an NVIDIA 3090 GPU. The coding tasks come from the [KMesh](https://github.com/zjutoe/KMesh.git) project.

## Evaluation Method

1. Use **Codex 6 (xhigh)** to plan the task and prepare a handoff document.
2. Have the local model (Qwen or Bonsai) execute the task based on the handoff document and perform the required checks itself.
3. Have Codex review the local model's results and provide feedback if revisions are needed.
4. Pass the review feedback to the local model for revisions, then submit the results to Codex again. Repeat until the task passes review.
5. Ask Codex to assess the **completeness** and **correctness** of the local model's work across the full execution and review cycle.

## Qwen Evaluation Results

![Screenshot of the Qwen coding task evaluation results (in Chinese)](/assets/images/coding_agent_estimate/qwen_estimate.webp)

## Bonsai Evaluation Results

![Screenshot of the Bonsai coding task evaluation results (in Chinese)](/assets/images/coding_agent_estimate/bonsai_estimate.webp)

## Qwen vs. Bonsai Comparison

![Screenshot comparing the Qwen and Bonsai coding task evaluation results (in Chinese)](/assets/images/coding_agent_estimate/qwen_vs_bonsai_estimate.webp)
