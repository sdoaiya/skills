from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
CHECKS_DIR = SKILL_ROOT / "checks"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run all baseline market-research checks for a project directory."
    )
    parser.add_argument("project_dir", type=Path, help="Research project root directory")
    parser.add_argument(
        "--require-sections",
        nargs="*",
        default=["4", "7"],
        help="Sections that must be covered by at least one source entry.",
    )
    parser.add_argument(
        "--require-chart-files",
        action="store_true",
        help="Require all chart-plan output_path files to exist.",
    )
    parser.add_argument(
        "--min-dual-source-lines",
        type=int,
        default=1,
        help="Minimum number of quantitative lines that should carry 2+ sources.",
    )
    return parser.parse_args()


def run_command(label: str, command: list[str]) -> tuple[str, int, str]:
    completed = subprocess.run(command, capture_output=True)
    stdout = decode_output(completed.stdout)
    stderr = decode_output(completed.stderr)
    output = (stdout + stderr).strip()
    return label, completed.returncode, output


def decode_output(raw: bytes) -> str:
    for encoding in ("utf-8", "gbk", sys.getdefaultencoding()):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def main() -> int:
    args = parse_args()
    project_dir = args.project_dir.resolve()

    sources_csv = project_dir / "sources.csv"
    chart_plan_csv = project_dir / "chart-plan.csv"
    report_path = project_dir / "output" / "full-report.md"

    checks: list[tuple[str, list[str]]] = [
        (
            "sources",
            [
                sys.executable,
                str(CHECKS_DIR / "check_sources.py"),
                str(sources_csv),
                "--require-sections",
                *args.require_sections,
            ],
        ),
        (
            "charts",
            [
                sys.executable,
                str(CHECKS_DIR / "check_charts.py"),
                str(chart_plan_csv),
                str(sources_csv),
                *(["--require-files"] if args.require_chart_files else []),
            ],
        ),
        (
            "claims",
            [
                sys.executable,
                str(CHECKS_DIR / "check_claims.py"),
                str(report_path),
                "--min-dual-source-lines",
                str(args.min_dual_source_lines),
            ],
        ),
        (
            "delivery",
            [
                sys.executable,
                str(CHECKS_DIR / "check_delivery.py"),
                str(project_dir),
            ],
        ),
    ]

    failures = 0
    for label, command in checks:
        check_name, return_code, output = run_command(label, command)
        prefix = "[OK]" if return_code == 0 else "[FAIL]"
        print(f"{prefix} {check_name}")
        if output:
            print(output)
        if return_code != 0:
            failures += 1

    if failures:
        print(f"[FAIL] run_checks completed with {failures} failing check(s).")
        return 1

    print("[OK] run_checks completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
