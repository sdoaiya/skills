from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = [
    "chart_id",
    "question",
    "takeaway",
    "source_ids",
    "metric",
    "dimension",
    "chart_type",
    "unit",
    "section",
    "output_path",
    "status",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate market-research chart plan.")
    parser.add_argument("chart_plan", type=Path, help="Path to chart-plan.csv")
    parser.add_argument("sources_csv", type=Path, help="Path to sources.csv")
    parser.add_argument(
        "--require-files",
        action="store_true",
        help="Fail if output_path files do not exist.",
    )
    return parser.parse_args()


def load_source_ids(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row["source_id"].strip() for row in reader if row.get("source_id", "").strip()}


def resolve_output_path(chart_plan: Path, raw_output_path: str) -> Path:
    direct_path = chart_plan.parent / raw_output_path
    if direct_path.exists():
        return direct_path
    return chart_plan.parent.parent / raw_output_path


def main() -> int:
    args = parse_args()
    if not args.chart_plan.exists():
        print(f"[FAIL] Missing chart plan: {args.chart_plan}")
        return 1
    if not args.sources_csv.exists():
        print(f"[FAIL] Missing sources register: {args.sources_csv}")
        return 1

    valid_sources = load_source_ids(args.sources_csv)
    with args.chart_plan.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            print("[FAIL] chart-plan.csv columns do not match expected template.")
            print("Expected:", ", ".join(REQUIRED_COLUMNS))
            print("Found   :", ", ".join(reader.fieldnames or []))
            return 1
        rows = list(reader)

    if not rows:
        print("[FAIL] chart-plan.csv has no data rows.")
        return 1

    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        chart_id = row["chart_id"].strip()
        if not chart_id:
            errors.append(f"Row {index}: chart_id is required.")
        elif chart_id in seen_ids:
            errors.append(f"Row {index}: duplicate chart_id '{chart_id}'.")
        else:
            seen_ids.add(chart_id)

        for column in REQUIRED_COLUMNS[1:]:
            if not row[column].strip():
                errors.append(f"Row {index}: {column} is required.")

        source_ids = [item.strip() for item in row["source_ids"].split("|") if item.strip()]
        if not source_ids:
            errors.append(f"Row {index}: source_ids must contain at least one source.")
        else:
            for source_id in source_ids:
                if source_id not in valid_sources:
                    errors.append(f"Row {index}: unknown source_id '{source_id}'.")

        if args.require_files:
            output_path = resolve_output_path(args.chart_plan, row["output_path"].strip())
            if not output_path.exists():
                errors.append(f"Row {index}: missing chart file '{output_path}'.")

    if errors:
        print("[FAIL] chart-plan.csv validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"[OK] chart-plan.csv passed with {len(rows)} planned charts.")
    if args.require_files:
        print("[OK] All referenced chart files exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
