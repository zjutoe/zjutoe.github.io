---
title: "AI Infra Day 1: Distributed Data Parallel (DDP)"
lang: en
translation_key: ai-infra-day1-ddp
permalink: /en/posts/AI_Infra_Day1_DDP/
---
# Version 1: Manual DDP
- Multiprocess launch: use `torchrun`, with each process corresponding to a rank. Each rank has a global rank ID and a local rank ID. All ranks belong to the same process group.
- Characteristics: each rank maintains a full model replica and keeps its parameters consistent with the other ranks by synchronizing gradients and applying the same local updates. Data processing is distributed.
- When synchronization happens: after the model's forward/backward pass and before `optimizer.step()`.
- How synchronization works: use `all_reduce` to sum the data across ranks with `dist.all_reduce(..., op=dist.ReduceOp.SUM)`, then divide by the total number of ranks (`world_size`) to take the average.
- Underlying synchronization library: `torch.distributed` → NVIDIA Collective Communications Library (NCCL).
- Reference code: [train manual](https://github.com/zjutoe/ml-lab/blob/master/experiments/ddp_minimal/train_manual_sync.py)
# Version 2: Automatic DDP
- `from torch.nn.parallel import DistributedDataParallel as DDP`
- Wrap the model: `model = DDP(model, ...)`.
- Automatic synchronization: during `loss.backward()`, DDP synchronizes gradients through mechanisms such as autograd hooks, so the gradients are already synchronized before `optimizer.step()`.
- `optimizer.step()` runs locally on each rank; it is not a distributed operation.
- Buckets: DDP packs gradient data into buckets and synchronizes them in groups.
- Compute–communication overlap: while computing gradients during `loss.backward()`, DDP also synchronizes buckets whose computation has finished. For example, in a 10-layer network, once layer 10 is finished and computation begins on layer 9, the gradients for layer 10 can be synchronized.
- Reference code: [train DDP](https://github.com/zjutoe/ml-lab/blob/master/experiments/ddp_minimal/train_ddp.py)
# Different Synchronization Operations
- `broadcast`: send data from one rank to the others.
- `all_reduce`: all ranks participate in an operation to obtain a result such as `SUM` or `MAX`.
- `all_gather`: collect data from every rank so that all ranks receive a complete copy, without performing any other computation.
- `reduce_scatter`: first reduce the data, then split the result into shards and distribute them to different ranks.
- Logically, `all_reduce = reduce_scatter + all_gather`.
