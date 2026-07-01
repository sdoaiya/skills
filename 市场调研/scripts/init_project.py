from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_ROOT / "templates"

DEFAULT_DIRS = [
    "data/raw",
    "data/processed",
    "charts",
    "sources",
    "output",
    "notes",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a market research project scaffold from the skill templates."
    )
    parser.add_argument("project_dir", type=Path, help="Target directory for the research project")
    parser.add_argument("--topic", default="", help="Research topic or report title")
    parser.add_argument("--region", default="", help="Target market or region")
    parser.add_argument("--timeframe", default="", help="Time window, for example 2020-2025")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing template files in the target directory",
    )
    return parser.parse_args()


def ensure_directories(project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    for relative in DEFAULT_DIRS:
        (project_dir / relative).mkdir(parents=True, exist_ok=True)


def copy_templates(project_dir: Path, force: bool) -> list[Path]:
    copied: list[Path] = []
    for template in TEMPLATES_DIR.iterdir():
        if not template.is_file():
            continue
        target = project_dir / template.name
        if target.exists() and not force:
            continue
        shutil.copy2(template, target)
        copied.append(target)
    return copied


def render_readme(project_dir: Path, topic: str, region: str, timeframe: str) -> Path:
    title = topic or project_dir.name
    region_text = region or "待填写"
    timeframe_text = timeframe or "待填写"
    readme_path = project_dir / "README.md"
    readme = f"""# {title}

## 研究任务

- 主题：{title}
- 区域：{region_text}
- 时间窗口：{timeframe_text}

## 目录说明

- `hs-scope.csv`：定义 HS 编码、纳入排除规则和产品范围。
- `sources.csv`：登记来源、证据等级、章节映射和复核方式。
- `chart-plan.csv`：规划每张图回答的问题、来源和输出路径。
- `country-scorecard.csv`：记录国别评分与优先级。
- `research-retrospective.csv`：记录交付后复盘、评分和改进动作。
- `report-outline.md`：白皮书写作骨架。
- `data/raw/`：原始下载数据。
- `data/processed/`：清洗后的分析表。
- `charts/`：图表 PNG 或 SVG。
- `sources/`：PDF 摘要、摘录和引用附件。
- `output/`：最终交付文件。
- `notes/`：研究笔记、访谈纪要和估算草稿。

## 建议执行顺序

1. 填写 `hs-scope.csv` 和 `sources.csv`。
2. 在 `data/raw/` 与 `data/processed/` 维护原始与清洗数据。
3. 完成 `chart-plan.csv` 并将图表输出到 `charts/`。
4. 基于 `report-outline.md` 扩写主稿，最终输出到 `output/full-report.md`。
5. 生成 `output/report.html`、`output/report.pdf`、`output/report.docx`。
6. 运行校验脚本，确保来源、图表、主稿和交付目录完整。
7. 更新 `research-retrospective.csv` 并运行自我进化脚本生成 `notes/evolution-backlog.md`。

## 校验命令

```bash
python "{SKILL_ROOT / 'checks' / 'check_sources.py'}" "{project_dir / 'sources.csv'}" --require-sections 4 7
python "{SKILL_ROOT / 'checks' / 'check_charts.py'}" "{project_dir / 'chart-plan.csv'}" "{project_dir / 'sources.csv'}"
python "{SKILL_ROOT / 'checks' / 'check_claims.py'}" "{project_dir / 'output' / 'full-report.md'}"
python "{SKILL_ROOT / 'checks' / 'check_delivery.py'}" "{project_dir}"
python "{SKILL_ROOT / 'checks' / 'check_retrospective.py'}" "{project_dir / 'research-retrospective.csv'}"
python "{SKILL_ROOT / 'scripts' / 'evolve_project.py'}" "{project_dir}"
```
"""
    readme_path.write_text(readme, encoding="utf-8")
    return readme_path


def main() -> int:
    args = parse_args()
    project_dir = args.project_dir.resolve()

    ensure_directories(project_dir)
    copied = copy_templates(project_dir, args.force)
    readme_path = render_readme(project_dir, args.topic, args.region, args.timeframe)

    print(f"[OK] Project initialized: {project_dir}")
    print(f"[OK] README created: {readme_path}")
    if copied:
        print("[OK] Copied templates:")
        for path in copied:
            print(f"- {path}")
    else:
        print("[OK] No templates copied because target files already existed.")
        if not args.force:
            print("Use --force to overwrite existing templates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
