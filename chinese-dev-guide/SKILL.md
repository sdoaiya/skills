---
name: chinese-dev-guide
description: Default Chinese orchestrator for non-trivial new tasks, especially when the user asks in Chinese or wants routing, planning, implementation, review, debugging, or "按你的建议来". Trigger first for natural Chinese development requests, restate the goal in Chinese, choose the workflow, prefer multi-worker/parallel execution when useful, and route to the right installed skills.
---

# Chinese Dev Guide

Interpret natural Chinese development requests, explain the recommended path in Chinese, and route work to the right installed skills without requiring explicit skill names. Treat `karpathy-guidelines` as the default coding mindset and prefer multi-worker or parallel execution inside Codex App when the task can be split safely.

## Default Behavior

Always do these first:

1. Restate the user's goal in plain Chinese.
2. Recommend one workflow path and briefly explain why it fits.
3. Print exactly one routing status line before further guidance:
   `已选择技能链路：...（原因：...）`
4. Route to one primary skill chain instead of stacking overlapping planners.
5. Prefer multi-worker execution for non-trivial tasks with independent lanes.
6. Keep guiding the user through the next step; ask only for missing, high-impact preferences.

Default user model:

- Treat the user as a beginner unless they clearly signal otherwise.
- Do not require the user to know skill names, tmux, or internal workflow details.
- Prefer Chinese by default unless the user asks for another language.

## Routing Guide

| Request shape | Preferred path | Notes |
|---|---|---|
| Broad, ambiguous, or under-scoped work | `deep-interview --quick` | Clarify scope before planning or coding. |
| Scope is clear and needs an implementation plan | `superpowers:writing-plans` | Default planning path in Codex App. |
| High-risk planning: auth, migrations, irreversible changes, public APIs | `ralplan` | Use stronger planning review before execution. |
| Knowledge graph, cross-file architecture mapping, doc/paper/code relationship mining | `graphify` via `/graphify <path>` | Use when the user asks for "知识图谱", "模块关系图", "跨文档关联", or similar corpus-mapping requests. |
| Normal implementation or bug fix | `superpowers:test-driven-development` then `superpowers:subagent-driven-development` | Default execution path in the app; split investigation, implementation, and verification when possible. |
| Multiple independent bugs, files, features, or research lanes | `superpowers:dispatching-parallel-agents` | Prefer this multi-worker path whenever the work can be decomposed safely. |
| "Review this change" or "评审一下" | Use review mindset first; if the target is a plan, use `plan --review` | Findings first, not implementation first. |
| "Keep going until done", "一直跟到做完", "不要停" | `ralph` | Use persistent completion mode with verification. |
| Explicit tmux/worker orchestration request | Recommend `team` only in CLI/tmux contexts | Do not default to `team` in Codex App. |
| Simple direct question such as time, definitions, or quick facts | Answer directly | Do not over-trigger the full development workflow. |

## Environment Guardrails

- In Codex App, prefer Superpowers for execution, parallelism, and completion checks.
- Prefer available parallel tools or subagents for independent reads, searches, implementation lanes, validation lanes, and review lanes.
- Use oh-my-codex skills mainly for clarification, high-rigor planning, and persistent orchestration entry points.
- Use `team` for durable CLI/tmux workers when the user explicitly asks for multi-worker mode, the task is long-running, or the environment supports it cleanly.
- If the user explicitly names a compatible skill, respect it and explain any environment caveat briefly.

## Quality Defaults

**REQUIRED DEFAULTS:**

- Use `karpathy-guidelines` as the baseline coding and review discipline.
- Use `superpowers:test-driven-development` before adding or changing behavior.
- Use `superpowers:subagent-driven-development` or `superpowers:dispatching-parallel-agents` by default for non-trivial work with separable parts.
- Use `superpowers:verification-before-completion` before any completion claim.

Apply these principles throughout:

- Think before coding: state assumptions and surface ambiguity instead of guessing.
- Simplicity first: choose the smallest solution that satisfies the request.
- Surgical changes: touch only what the task requires.
- Goal-driven execution: turn vague requests into verifiable checks.

## Example Triggers

- "帮我做个登录页"
- "这个接口老报错，帮我查一下"
- "我想先规划一下再做"
- "你直接推荐最稳的方案"
- "继续按你刚才建议的来"
- "评审一下这个改动"

## Common Mistakes

- Do not launch both `ralplan` and `superpowers:writing-plans` for the same planning step by default.
- Do not route simple Chinese requests into heavy workflow chains when a direct answer is enough.
- Do not force `team` when lightweight parallel tool calls or subagents are enough.
- Do not assume the user understands internal skill names; translate the path into plain Chinese first.
