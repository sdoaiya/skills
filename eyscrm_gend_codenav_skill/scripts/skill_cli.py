#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from pathlib import Path
from memory_store import search_memory, get_project, load_json, PROJECTS_PATH, apply_update, export_context


def main():
    parser = argparse.ArgumentParser(description="G端中台知识记忆与协同Skill CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_search = sub.add_parser("search", help="搜索记忆库")
    p_search.add_argument("query")
    p_search.add_argument("--limit", type=int, default=20)

    p_project = sub.add_parser("project", help="查看项目卡片")
    p_project.add_argument("project_id")

    sub.add_parser("list-projects", help="列出活跃项目")

    p_update = sub.add_parser("update", help="追加记忆更新")
    p_update.add_argument("--file", required=True, help="MemoryUpdate JSON文件")
    p_update.add_argument("--dry-run", action="store_true")

    p_export = sub.add_parser("export-context", help="按任务导出上下文")
    p_export.add_argument("--task", required=True)
    p_export.add_argument("--limit", type=int, default=30)

    args = parser.parse_args()

    if args.cmd == "search":
        print(json.dumps(search_memory(args.query, args.limit), ensure_ascii=False, indent=2))

    elif args.cmd == "project":
        p = get_project(args.project_id)
        print(json.dumps(p or {"error": "project not found"}, ensure_ascii=False, indent=2))

    elif args.cmd == "list-projects":
        projects = load_json(PROJECTS_PATH)
        print(json.dumps(projects.get("active_projects", []), ensure_ascii=False, indent=2))

    elif args.cmd == "update":
        update = json.loads(Path(args.file).read_text(encoding="utf-8"))
        result = apply_update(update, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.cmd == "export-context":
        print(json.dumps(export_context(args.task, args.limit), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
