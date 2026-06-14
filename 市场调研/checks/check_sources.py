from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = [
    "source_id",
    "title",
    "publisher",
    "level",
    "year",
    "url_or_path",
    "scope",
    "section",
    "verification_method",
    "limitations",
]
VALID_LEVELS = {"P1", "P2", "P3", "P4", "P5"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate market-research sources register.")
    parser.add_argument("csv_path", type=Path, help="Path to sources.csv")
    parser.add_argument(
        "--require-sections",
        nargs="*",
        default=[],
        help="Section ids that must appear in at least one source row.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.csv_path.exists():
        print(f"[FAIL] Missing sources file: {args.csv_path}")
        return 1

    with args.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            print("[FAIL] sources.csv columns do not match expected template.")
            print("Expected:", ", ".join(REQUIRED_COLUMNS))
            print("Found   :", ", ".join(reader.fieldnames or []))
            return 1
        rows = list(reader)

    if not rows:
        print("[FAIL] sources.csv has no data rows.")
        return 1

    errors: list[str] = []
    seen_ids: set[str] = set()
    covered_sections: set[str] = set()

    for index, row in enumerate(rows, start=2):
        source_id = row["source_id"].strip()
        if not source_id:
            errors.append(f"Row {index}: source_id is required.")
        elif source_id in seen_ids:
            errors.append(f"Row {index}: duplicate source_id '{source_id}'.")
        else:
            seen_ids.add(source_id)

        level = row["level"].strip().upper()
        if level not in VALID_LEVELS:
            errors.append(f"Row {index}: invalid level '{row['level']}'.")

        for column in REQUIRED_COLUMNS[1:]:
            if not row[column].strip():
                errors.append(f"Row {index}: {column} is required.")

        for section in row["section"].split("|"):
            section = section.strip()
            if section:
                covered_sections.add(section)

    missing_sections = [section for section in args.require_sections if section not in covered_sections]
    for section in missing_sections:
        errors.append(f"Required section '{section}' has no mapped source.")

    high_grade = sum(1 for row in rows if row["level"].strip().upper() in {"P1", "P2"})
    if high_grade == 0:
        errors.append("At least one P1 or P2 source is required.")

    if errors:
        print("[FAIL] sources.csv validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"[OK] sources.csv passed with {len(rows)} rows and {high_grade} P1/P2 sources.")
    if args.require_sections:
        print("[OK] Covered required sections:", ", ".join(args.require_sections))
    return 0


if __name__ == "__main__":
    sys.exit(main())
