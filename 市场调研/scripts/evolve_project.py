from __future__ import annotations

import argparse
import csv
import datetime as dt
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


RETROSPECTIVE_COLUMNS = [
    "item_id",
    "category",
    "score",
    "evidence",
    "issue",
    "next_action",
    "owner",
    "status",
]
PRIORITY_BY_SCORE = {
    1: "P0",
    2: "P1",
    3: "P2",
    4: "P3",
    5: "P4",
}
CHECK_FAIL_PATTERN = re.compile(r"^\[FAIL\]\s*(.+)$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a self-evolution backlog from checks, retrospective rows, and user feedback."
    )
    parser.add_argument("project_dir", type=Path, help="Research project root directory")
    parser.add_argument(
        "--checks-log",
        type=Path,
        default=None,
        help="Optional path to a saved run_checks output log.",
    )
    parser.add_argument(
        "--feedback",
        type=Path,
        default=None,
        help="Optional path to user feedback or review notes.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output Markdown path. Defaults to project_dir/notes/evolution-backlog.md.",
    )
    return parser.parse_args()


def read_retrospective(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing retrospective file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != RETROSPECTIVE_COLUMNS:
            raise ValueError("research-retrospective.csv columns do not match expected template.")
        return list(reader)


def safe_read(path: Path | None) -> str:
    if not path:
        return ""
    if not path.exists():
        return f"[missing file: {path}]"
    return path.read_text(encoding="utf-8", errors="replace")


def categorize_feedback(text: str) -> Counter[str]:
    categories = {
        "sources": ("来源", "引用", "出处", "source", "citation", "数据源"),
        "scope": ("口径", "范围", "HS", "年份", "币种", "scope"),
        "charts": ("图", "图表", "chart", "visual", "标签"),
        "claims": ("结论", "数字", "测算", "估算", "claim"),
        "strategy": ("建议", "策略", "进入", "优先级", "strategy"),
        "delivery": ("格式", "Word", "PDF", "HTML", "排版", "目录"),
        "reuse": ("复用", "模板", "沉淀", "资产", "reuse"),
    }
    lowered = text.lower()
    counts: Counter[str] = Counter()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in lowered:
                counts[category] += 1
    return counts


def parse_score(row: dict[str, str]) -> int:
    try:
        return int(row["score"].strip())
    except ValueError:
        return 0


def build_backlog(
    project_dir: Path,
    rows: list[dict[str, str]],
    checks_log: str,
    feedback: str,
) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    by_category: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_category[row["category"].strip()].append(row)

    failing_checks = CHECK_FAIL_PATTERN.findall(checks_log)
    feedback_counts = categorize_feedback(feedback)
    low_score_rows = [row for row in rows if parse_score(row) < 4 or row["status"].strip() != "closed"]
    low_score_rows.sort(key=lambda row: (parse_score(row), row["category"], row["item_id"]))

    average_score = sum(parse_score(row) for row in rows) / len(rows) if rows else 0
    lines: list[str] = [
        f"# 自我进化 Backlog - {project_dir.name}",
        "",
        f"- 生成时间：{now}",
        f"- 复盘项：{len(rows)}",
        f"- 平均评分：{average_score:.1f}/5",
        f"- 未关闭或低分项：{len(low_score_rows)}",
        f"- 校验失败摘要：{len(failing_checks)} 项",
        "",
        "## 评分概览",
        "",
        "| 类别 | 项数 | 平均分 | 未关闭项 |",
        "|---|---:|---:|---:|",
    ]

    for category in sorted(by_category):
        category_rows = by_category[category]
        avg = sum(parse_score(row) for row in category_rows) / len(category_rows)
        open_count = sum(1 for row in category_rows if row["status"].strip() != "closed")
        lines.append(f"| {category} | {len(category_rows)} | {avg:.1f} | {open_count} |")

    lines.extend(["", "## 优先改进项", ""])
    if low_score_rows:
        lines.extend(["| 优先级 | 类别 | 问题 | 下一步 | 负责人 | 状态 |", "|---|---|---|---|---|---|"])
        for row in low_score_rows:
            score = parse_score(row)
            priority = PRIORITY_BY_SCORE.get(score, "P0")
            issue = row["issue"].strip()
            next_action = row["next_action"].strip() or "补充可执行改进动作"
            lines.append(
                f"| {priority} | {row['category'].strip()} | {issue} | {next_action} | {row['owner'].strip()} | {row['status'].strip()} |"
            )
    else:
        lines.append("暂无未关闭或低分项。")

    lines.extend(["", "## 校验失败导入", ""])
    if failing_checks:
        for item in failing_checks:
            lines.append(f"- {item}")
    else:
        lines.append("- 未提供校验日志，或日志中没有 `[FAIL]`。")

    lines.extend(["", "## 用户反馈信号", ""])
    if feedback.strip():
        if feedback_counts:
            for category, count in feedback_counts.most_common():
                lines.append(f"- {category}: 命中 {count} 个关键词")
        else:
            lines.append("- 已提供反馈，但未命中默认分类关键词；请人工归类。")
    else:
        lines.append("- 未提供用户反馈文件。")

    lines.extend(
        [
            "",
            "## 下次研究默认动作",
            "",
            "1. 先处理 P0/P1 项，再扩写新章节。",
            "2. 对低分维度补齐来源、图表或交付资产后重新运行 `scripts/run_checks.py`。",
            "3. 若同类问题第二次出现，更新本 skill 的模板、参考文件或校验脚本。",
            "4. 保留本文件，作为下一次同类研究的输入。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    project_dir = args.project_dir.resolve()
    retrospective_path = project_dir / "research-retrospective.csv"
    output_path = args.output.resolve() if args.output else project_dir / "notes" / "evolution-backlog.md"

    try:
        rows = read_retrospective(retrospective_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[FAIL] {exc}")
        return 1

    checks_log = safe_read(args.checks_log)
    feedback = safe_read(args.feedback)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_backlog(project_dir, rows, checks_log, feedback), encoding="utf-8")

    print(f"[OK] Evolution backlog created: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
