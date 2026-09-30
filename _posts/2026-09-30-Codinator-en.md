---
title: "Codinator: A Coding Harness for Stronger and Weaker Model Collaboration"
description: Codex provides the interface, planning, and independent acceptance review, while Pi runs a weaker model to implement code, with a controller coordinating checks, revisions, and evidence retention.
lang: en
translation_key: codinator
category: notes
permalink: /en/posts/Codinator/
---

## Overview

[Codinator](https://github.com/zjutoe/codinator) was designed to enable **collaboration between Codex and Pi—that is, between stronger and weaker models**.
Codex uses a stronger model for requirements analysis, task planning, and independent acceptance review. Pi uses a weaker model (currently Bonsai)
to implement the code and revise it in response to review feedback. The controller connects implementation, checks, acceptance review, and revisions into a workflow that can keep running
and retain a traceable record, reducing the burden of manually assigning tasks, tracking progress, and repeatedly passing along review feedback.

**Codex is the sole user interface**: the main Codex session is where users discuss requirements, assign tasks, query status, and handle exceptions.
A separate background service handles implementation through Pi + Bonsai, required checks, independent acceptance review by Codex, and automatic revisions.
Closing the main interface does not pause background tasks. A task can be accepted only after it passes independent review.

The project supports pausing tasks and explicitly resuming them, controls on the scope of changes and execution budgets, sandbox isolation, and evidence retention for each round.
With explicit authorization, it can also commit code and perform a fast-forward merge after acceptance review passes.

## Runtime Environment

Codinator targets Linux, with a single user and tasks running serially. It requires Python 3.11+ and installed copies of
`pi`, `codex`, `git`, and `bwrap`, with authentication configured where needed. The Python runtime has no third-party dependencies.
Pi performs implementation tasks through RPC, while Codex handles acceptance through a separate review process; both are scheduled by the controller.

## Workflow

```text
ready → implementing → checking → reviewing → accepted
             ↑                       │
             └──── needs_changes ────┘
```
