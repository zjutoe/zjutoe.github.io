---
title: Codinator：强弱模型协作编程 Harness
description: 以 Codex 为交互入口，由强模型负责规划与独立验收，Pi 调用较弱模型实施代码，串联检查、返工与证据留存。
lang: zh-CN
translation_key: codinator
category: notes
permalink: /posts/Codinator/
---

## 概述

[Codinator](https://github.com/zjutoe/codinator) 的设计初衷是实现 **Codex 与 Pi 的协作，即强模型与弱模型的协作**。
Codex 使用强模型负责需求分析、任务规划与独立验收，Pi 调用较弱模型（当前为 Bonsai）
负责具体代码实施，并根据审查反馈修正。控制器将实施、检查、验收和返工串联为可持续运行、
可追溯的流程，减少人工派发任务、跟踪进度和反复转交修改意见的负担。

以 **Codex 为唯一交互界面**：在 Codex 主会话中讨论需求、发布任务、查询状态和处理异常；
独立后台服务负责 Pi + Bonsai 实施、必需检查、Codex 独立验收与自动返工。
关闭主界面不会暂停后台任务，任务只有通过独立验收才能被接受。

项目提供任务暂停与显式恢复、修改范围和执行预算控制、沙箱隔离及逐轮证据留存；
经明确授权，还可在验收通过后提交代码并快进合并。

## 运行环境

面向 Linux、单用户、串行任务。需要 Python 3.11+，以及已安装并完成认证的
`pi`、`codex`、`git`、`bwrap`；Python 运行时无第三方依赖。
Pi 通过 RPC 执行实施任务，Codex 通过独立审查进程验收，均由控制器调度。

## 工作流程：执行与恢复

```text
ready → implementing → checking → reviewing → accepted
             ↑                       │
             └──── needs_changes ────┘
```
