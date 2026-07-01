#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
memory_store.py
本地轻量记忆库，用于读取、检索、追加更新 eyscrm_gend_codenav_skill 的结构化知识。
设计原则：可读、可追溯、append-only、便于 Codex 二次开发。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import date
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = ROOT / "data" / "memory_bank.json"
PROJECTS_PATH = ROOT / "data" / "projects.json"
LOG_PATH = ROOT / "logs" / "evolution_log.md"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def flatten(obj: Any, prefix: str = "") -> List[Tuple[str, str]]:
    """把嵌套JSON拍平为 path/text，方便轻量搜索。"""
    rows: List[Tuple[str, str]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            rows.extend(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            rows.extend(flatten(v, f"{prefix}[{i}]"))
    else:
        rows.append((prefix, str(obj)))
    return rows


def search_memory(query: str, limit: int = 20) -> List[Dict[str, str]]:
    """关键词轻量检索；Codex可替换为向量检索。"""
    memory = load_json(MEMORY_PATH)
    projects = load_json(PROJECTS_PATH)

    q = query.lower().strip()
    tokens = [t for t in re.split(r"\s+", q) if t]
    if not tokens:
        return []

    candidates = []
    for source_name, data in [("memory_bank", memory), ("projects", projects)]:
        for path, text in flatten(data):
            hay = f"{path} {text}".lower()
            score = sum(1 for t in tokens if t in hay)
            # 中文场景下，完整query命中加权
            if q in hay:
                score += 3
            if score > 0:
                candidates.append({
                    "source": source_name,
                    "path": path,
                    "text": text,
                    "score": str(score),
                })

    candidates.sort(key=lambda x: int(x["score"]), reverse=True)
    return candidates[:limit]


def get_project(project_id: str) -> Dict[str, Any] | None:
    projects = load_json(PROJECTS_PATH)
    for p in projects.get("active_projects", []):
        if p.get("id") == project_id:
            return p
    return None


def append_evolution_log(update: Dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"\n## {update.get('date', date.today().isoformat())} | {update.get('category', 'unknown')} | {update.get('operation', 'add')}",
        "",
        f"- Source: {update.get('source', 'unknown')}",
        f"- Confidence: {update.get('confidence', 'pending')}",
        f"- Reason: {update.get('reason', '')}",
        "",
        "```json",
        json.dumps(update.get("content", {}), ensure_ascii=False, indent=2),
        "```",
        ""
    ]
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))


def apply_update(update: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    简化版更新逻辑：
    - add/revise：把content追加到 memory_bank.meta.memory_updates 中，并记录日志；
    - archive/confirm/flag_pending：同样追加，不做破坏性覆盖。
    真正合并逻辑建议由 Codex 根据项目需要扩展。
    """
    required = ["date", "category", "operation", "content", "source", "confidence"]
    missing = [k for k in required if k not in update]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    memory = load_json(MEMORY_PATH)
    memory.setdefault("meta", {})
    memory["meta"]["last_updated"] = update["date"]
    memory.setdefault("_memory_updates", [])
    memory["_memory_updates"].append(update)

    if not dry_run:
        save_json(MEMORY_PATH, memory)
        append_evolution_log(update)

    return {
        "ok": True,
        "dry_run": dry_run,
        "message": "Update appended. Review and merge manually if needed.",
        "update": update
    }


def export_context(task: str, limit: int = 30) -> Dict[str, Any]:
    """为具体任务导出精简上下文。"""
    hits = search_memory(task, limit=limit)
    return {
        "task": task,
        "recommended_context": hits,
        "rules": [
            "当前任务中的用户最新信息优先于记忆库。",
            "政府/协会/国资材料必须启用风险红线。",
            "涉及金额、数量、政策、名单，不确定则标注待核验。",
            "完成后判断是否需要追加MemoryUpdate。"
        ]
    }
