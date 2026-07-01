from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


NUMBER_PATTERN = re.compile(r"\d[\d,]*(?:\.\d+)?(?:%|亿元|万美元|亿美元|万台|台)?")
SOURCE_TAG_PATTERN = re.compile(r"\[Sources?:\s*([A-Za-z0-9\-_ ,|]+)\]")
ESTIMATE_PATTERN = re.compile(r"(估算|测算|假设)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate source tags around quantitative claims.")
    parser.add_argument("report_path", type=Path, help="Path to Markdown report")
    parser.add_argument(
        "--min-dual-source-lines",
        type=int,
        default=1,
        help="Minimum number of quantitative lines that should carry 2+ sources.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.report_path.exists():
        print(f"[FAIL] Missing report file: {args.report_path}")
        return 1

    lines = args.report_path.read_text(encoding="utf-8").splitlines()
    quantitative_lines = 0
    dual_source_lines = 0
    issues: list[str] = []

    for line_number, line in enumerate(lines, start=1):
        if line.lstrip().startswith("#"):
            continue
        if not NUMBER_PATTERN.search(line):
            continue
        quantitative_lines += 1
        source_match = SOURCE_TAG_PATTERN.search(line)
        if source_match:
            source_ids = [item.strip() for item in source_match.group(1).split("|") if item.strip()]
            if len(source_ids) >= 2:
                dual_source_lines += 1
            elif not ESTIMATE_PATTERN.search(line):
                issues.append(f"Line {line_number}: quantitative claim has fewer than 2 sources.")
        elif not ESTIMATE_PATTERN.search(line):
            issues.append(f"Line {line_number}: quantitative claim is missing a [Sources: ...] tag or estimate marker.")

    if quantitative_lines == 0:
        print("[FAIL] No quantitative lines were detected in the report.")
        return 1

    if dual_source_lines < args.min_dual_source_lines:
        issues.append(
            f"Only {dual_source_lines} quantitative lines have 2+ sources; expected at least {args.min_dual_source_lines}."
        )

    if issues:
        print("[FAIL] Report claim validation failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(
        f"[OK] Report claim check passed with {quantitative_lines} quantitative lines and {dual_source_lines} dual-source lines."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
