---
name: codex-session-restore
description: Restore Codex Desktop conversations after model-provider or relay switches. Use when users ask for “会话恢复”, “一键恢复”, “切回官方后恢复会话”, or when local threads exist in state_5.sqlite and sessions but disappear from the Desktop sidebar.
---

# 会话恢复

## 原则

先备份，再将顶层桌面会话同步到当前 `config.toml` 的 `model_provider`，最后修复 `.codex-global-state.json` 的侧边栏分组。不要用置顶代替修复，不要伪造缺失正文的会话。

## 一键恢复

切换到目标提供方并确认 `%USERPROFILE%\.codex\config.toml` 已保存后运行：

```powershell
python C:\Users\zdy25\.codex\skills\codex-session-restore\scripts\repair_codex_sessions.py
```

脚本只迁移正文存在、未归档、`source=vscode`、`thread_source=user` 的顶层桌面会话。它不会修改子任务、命令型会话、会话正文或历史模型名。

## 诊断与稳定写入

先预检：

```powershell
python C:\Users\zdy25\.codex\skills\codex-session-restore\scripts\repair_codex_sessions.py --dry-run
```

桌面端仍在运行且可能覆盖全局状态时：

```powershell
python C:\Users\zdy25\.codex\skills\codex-session-restore\scripts\repair_codex_sessions.py --watch-seconds 120
```

修复其他 Codex Home 或显式指定提供方：

```powershell
python C:\Users\zdy25\.codex\skills\codex-session-restore\scripts\repair_codex_sessions.py --codex-home D:\backup\.codex --provider openai
```

## 验证

1. 再运行一次 `--dry-run`，两类映射都应为 `0`。
2. 用 Codex Desktop 会话列表确认旧标题重新出现。
3. 对 `skipped ... missing rollout files` 只报告，不生成虚假正文。
4. 只有用户明确要求时才使用 `--clear-restored-pins`。
