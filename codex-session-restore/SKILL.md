---
name: codex-session-restore
description: Diagnose and repair Codex Desktop conversation visibility after provider or relay switches. Use when local Codex threads exist in state_5.sqlite, sessions, archived_sessions, or session_index.jsonl but do not appear in the Desktop sidebar, especially when pinning made them visible temporarily.
---

# Codex Session Restore

## Overview

Use this skill to restore local Codex Desktop conversations without relying on pinned threads. The main repair is to align three stores: `state_5.sqlite`, JSONL rollouts under `sessions` or `archived_sessions`, and `.codex-global-state.json` sidebar grouping metadata.

## Workflow

1. Locate the active Codex home, normally `%USERPROFILE%\.codex`.
2. Back up before writes. For app code, use the built-in backup flow; for a direct repair, run `scripts/repair_codex_sessions.py`, which creates a `.codex-global-state.json.*.bak` backup.
3. Restore database and JSONL visibility first when needed: active rows should be unarchived, use the current provider/model, and have a valid rollout path in `session_index.jsonl`.
4. Repair Desktop sidebar grouping without pinning:
   - Threads whose `cwd` is under `%USERPROFILE%\Documents\Codex` belong in `projectless-thread-ids`.
   - Their `thread-workspace-root-hints[id]` should point to `%USERPROFILE%\Documents\Codex`.
   - Their `thread-projectless-output-directories[id]` should be `<cwd>\outputs`.
   - Project threads should be removed from `projectless-thread-ids` and have their workspace root present in `electron-saved-workspace-roots`, `project-order`, and `active-workspace-roots`.
5. Do not treat `pinned-thread-ids` as a fix. Pinning is only a visibility workaround and should not be modified unless the user explicitly asks.
6. Verify by listing threads in Codex Desktop, checking the sidebar grouping, and confirming that index-only records without JSONL bodies are reported as unrecoverable rather than fabricated.

## Direct Repair Script

Dry run:

```powershell
python C:\Users\zdy25\.codex\skills\codex-session-restore\scripts\repair_codex_sessions.py --dry-run
```

Apply to the default Codex home:

```powershell
python C:\Users\zdy25\.codex\skills\codex-session-restore\scripts\repair_codex_sessions.py
```

Keep the repaired state stable while the already-running Codex Desktop process may still flush an old in-memory global state:

```powershell
python C:\Users\zdy25\.codex\skills\codex-session-restore\scripts\repair_codex_sessions.py --clear-restored-pins --watch-seconds 120
```

Target a different Codex home:

```powershell
python C:\Users\zdy25\.codex\skills\codex-session-restore\scripts\repair_codex_sessions.py --codex-home D:\backup\.codex
```

The script repairs only `.codex-global-state.json` sidebar metadata. It does not modify thread bodies, `state_5.sqlite`, or `session_index.jsonl`. It leaves `pinned-thread-ids` alone unless `--clear-restored-pins` is passed.
