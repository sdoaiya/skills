#!/usr/bin/env python3
"""Repair Codex Desktop sidebar grouping metadata without pinning threads."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Any


def norm(value: str) -> str:
    return os.path.normcase(os.path.abspath(value))


def inside_or_same(child: str, parent: str) -> bool:
    child_norm = norm(child)
    parent_norm = norm(parent)
    return child_norm == parent_norm or child_norm.startswith(parent_norm + os.sep)


def as_list(value: Any) -> list[str]:
    return [item for item in value] if isinstance(value, list) and all(isinstance(item, str) for item in value) else []


def as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def add_unique(values: list[str], value: str) -> bool:
    if value in values:
        return False
    values.append(value)
    return True


def remove_value(values: list[str], value: str) -> bool:
    before = len(values)
    values[:] = [item for item in values if item != value]
    return len(values) != before


def find_git_root(cwd: str) -> str | None:
    current = Path(cwd).resolve()
    while True:
        if (current / ".git").exists():
            return str(current)
        if current.parent == current:
            return None
        current = current.parent


def remove_nested_roots(values: list[str], root: str) -> bool:
    before = len(values)
    values[:] = [item for item in values if item == root or not inside_or_same(item, root)]
    return len(values) != before


def collect_jsonl_cwds(codex_home: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for root_name in ("sessions", "archived_sessions"):
        root = codex_home / root_name
        if not root.exists():
            continue
        for file_path in root.rglob("*.jsonl"):
            try:
                with file_path.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        if not line.strip():
                            continue
                        try:
                            row = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        payload = row.get("payload")
                        if row.get("type") != "session_meta" or not isinstance(payload, dict):
                            continue
                        thread_id = payload.get("id")
                        cwd = payload.get("cwd")
                        if isinstance(thread_id, str) and isinstance(cwd, str) and cwd:
                            result[thread_id] = cwd
                            break
            except OSError:
                continue
    return result


def read_thread_cwds(codex_home: Path, jsonl_cwds: dict[str, str]) -> dict[str, str]:
    db_path = codex_home / "state_5.sqlite"
    if not db_path.exists():
        raise FileNotFoundError(f"Missing Codex database: {db_path}")
    with sqlite3.connect(db_path) as db:
        rows = db.execute("SELECT id, cwd, archived FROM threads").fetchall()
    result: dict[str, str] = {}
    for thread_id, cwd, archived in rows:
        if archived != 0:
            continue
        if isinstance(cwd, str) and cwd:
            result[str(thread_id)] = cwd
        elif str(thread_id) in jsonl_cwds:
            result[str(thread_id)] = jsonl_cwds[str(thread_id)]
    return result


def choose_workspace_root(cwd: str, existing_roots: list[str]) -> str:
    git_root = find_git_root(cwd)
    if git_root:
        return git_root
    matches = [root for root in existing_roots if root and inside_or_same(cwd, root)]
    matches.sort(key=lambda item: len(norm(item)), reverse=True)
    return matches[0] if matches else cwd


def remove_restored_pins(state: dict[str, Any], thread_ids: set[str]) -> bool:
    pinned = as_list(state.get("pinned-thread-ids"))
    filtered = [thread_id for thread_id in pinned if thread_id not in thread_ids]
    if len(filtered) == len(pinned):
        return False
    state["pinned-thread-ids"] = filtered
    return True


def repair(
    codex_home: Path,
    user_home: Path,
    dry_run: bool,
    clear_restored_pins: bool = False,
) -> tuple[int, Path | None]:
    state_path = codex_home / ".codex-global-state.json"
    state: dict[str, Any] = {}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))

    jsonl_cwds = collect_jsonl_cwds(codex_home)
    thread_cwds = read_thread_cwds(codex_home, jsonl_cwds)

    projectless_ids = as_list(state.get("projectless-thread-ids"))
    workspace_hints = as_dict(state.get("thread-workspace-root-hints"))
    output_dirs = as_dict(state.get("thread-projectless-output-directories"))
    saved_roots = as_list(state.get("electron-saved-workspace-roots"))
    project_order = as_list(state.get("project-order"))
    active_roots = as_list(state.get("active-workspace-roots"))
    projectless_root = str(user_home / "Documents" / "Codex")

    touched = 0
    active_thread_ids = set(thread_cwds)
    for thread_id, cwd in thread_cwds.items():
        changed = False
        if inside_or_same(cwd, projectless_root):
            changed = add_unique(projectless_ids, thread_id) or changed
            if workspace_hints.get(thread_id) != projectless_root:
                workspace_hints[thread_id] = projectless_root
                changed = True
            output_dir = str(Path(cwd) / "outputs")
            if output_dirs.get(thread_id) != output_dir:
                output_dirs[thread_id] = output_dir
                changed = True
            changed = add_unique(saved_roots, projectless_root) or changed
            changed = add_unique(project_order, projectless_root) or changed
            changed = add_unique(active_roots, projectless_root) or changed
        else:
            root = choose_workspace_root(cwd, saved_roots)
            changed = remove_value(projectless_ids, thread_id) or changed
            if thread_id in output_dirs:
                del output_dirs[thread_id]
                changed = True
            if workspace_hints.get(thread_id) != root:
                workspace_hints[thread_id] = root
                changed = True
            changed = remove_nested_roots(saved_roots, root) or changed
            changed = remove_nested_roots(project_order, root) or changed
            changed = remove_nested_roots(active_roots, root) or changed
            changed = add_unique(saved_roots, root) or changed
            changed = add_unique(project_order, root) or changed
            changed = add_unique(active_roots, root) or changed
        if changed:
            touched += 1

    pins_changed = clear_restored_pins and remove_restored_pins(state, active_thread_ids)

    if (touched == 0 and not pins_changed) or dry_run:
        return touched, None

    state["projectless-thread-ids"] = projectless_ids
    state["thread-workspace-root-hints"] = workspace_hints
    state["thread-projectless-output-directories"] = output_dirs
    state["electron-saved-workspace-roots"] = saved_roots
    state["project-order"] = project_order
    state["active-workspace-roots"] = active_roots

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = codex_home / "history_sync_backups" / "global-state" / f".codex-global-state.{stamp}.bak"
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    if state_path.exists():
        shutil.copy2(state_path, backup_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return touched, backup_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair Codex Desktop sidebar metadata without pinning threads.")
    parser.add_argument("--codex-home", default=str(Path.home() / ".codex"))
    parser.add_argument("--user-home", default=str(Path.home()))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--clear-restored-pins", action="store_true")
    parser.add_argument("--watch-seconds", type=int, default=0)
    parser.add_argument("--watch-interval", type=float, default=1.0)
    args = parser.parse_args()

    codex_home = Path(args.codex_home)
    user_home = Path(args.user_home)
    deadline = time.monotonic() + max(args.watch_seconds, 0)
    total_touched = 0
    backups: list[Path] = []
    while True:
        touched, backup_path = repair(codex_home, user_home, args.dry_run, args.clear_restored_pins)
        total_touched += touched
        if backup_path:
            backups.append(backup_path)
        if args.watch_seconds <= 0 or time.monotonic() >= deadline:
            break
        time.sleep(max(args.watch_interval, 0.2))

    mode = "would update" if args.dry_run else "updated"
    print(f"{mode} {total_touched} thread display mappings")
    for backup_path in backups:
        print(f"backup: {backup_path}")


if __name__ == "__main__":
    main()
