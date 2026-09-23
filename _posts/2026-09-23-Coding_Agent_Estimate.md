---
title: 本地语言模型编程能力评测
description: 由 Codex 规划和审核，以 KMesh 编程任务评测 Qwen 与 Bonsai 本地模型的任务执行完整性和正确性。
lang: zh-CN
translation_key: coding-agent-estimate
category: review
permalink: /posts/Coding_Agent_Estimate/
---

## 测试背景

自 Codex 发布 5.6、6 模型以来，token 消耗太快了，因此尝试用本地语言模型执行编程任务。这次测试的两个模型：

- **Qwen-3.8 27B**。
- **PrismML Bonsai-2 27B**。

初步使用下来效果都还行。PrismML Bonsai占资源很少，在nvidia 3090显卡上能跑得很流畅。编程任务来自 [KMesh](https://github.com/zjutoe/KMesh.git) 项目。

## 任务评测方法

1. 用 **Codex 6（xhigh）** 做任务规划，写好 handoff（任务交接）文档。
2. 本地模型（Qwen 或 Bonsai）根据 handoff 文档执行任务，并按要求自行检验。
3. Codex 审核本地模型的执行结果，需要返工时给出修改提示。
4. 将审核结果交给本地模型返工，再提交 Codex 审核，直到任务通过。
5. 让 Codex 评估整轮执行中，本地模型完成任务的**完整性**和**正确性**。

## Qwen 评测结果

![Qwen 编程任务评测结果截图](/assets/images/coding_agent_estimate/qwen_estimate.webp)

## Bonsai 评测结果

![Bonsai 编程任务评测结果截图](/assets/images/coding_agent_estimate/bonsai_estimate.webp)
