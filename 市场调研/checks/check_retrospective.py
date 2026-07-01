from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


REQUIRED_COLUMNS = [
    "item_id",
    "category",
    "score",
    "evidence",
    "issue",
    "next_action",
    "owner",
    "status",
]
VALID_CATEGORIES = {"sources", "scope", "charts", "claims", "strategy", "delivery", "reuse"}
VALID_STATUSES = {"open", "in_progress", "closed", "needs-evidence", "needs-clarification", "blocking"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate market-research retrospective table.")
    parser.add_argument("csv_path", type=Path, help="Path to research-retrospective.csv")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.csv_path.exists():
        print(f"[FAIL] Missing retrospective file: {args.csv_path}")
        return 1

    with args.csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != REQUIRED_COLUMNS:
            print("[FAIL] research-retrospective.csv columns do not match expected template.")
            print("Expected:", ", ".join(REQUIRED_COLUMNS))
            print("Found   :", ", ".join(reader.fieldnames or []))
            return 1
        rows = list(reader)

    if not rows:
        print("[FAIL] research-retrospective.csv has no data rows.")
        return 1

    errors: list[str] = []
    seen_ids: set[str] = set()
    open_items = 0

    for index, row in enumerate(rows, start=2):
        item_id = row["item_id"].strip()
        if not item_id:
            errors.append(f"Row {index}: item_id is required.")
        elif item_id in seen_ids:
            errors.append(f"Row {index}: duplicate item_id '{item_id}'.")
        else:
            seen_ids.add(item_id)

        category = row["category"].strip()
        if category not in VALID_CATEGORIES:
            errors.append(f"Row {index}: invalid category '{category}'.")

        try:
            score = int(row["score"].strip())
        except ValueError:
            errors.append(f"Row {index}: score must be an integer from 1 to 5.")
            score = 0
        if score < 1 or score > 5:
            errors.append(f"Row {index}: score must be from 1 to 5.")

        status = row["status"].strip()
        if status not in VALID_STATUSES:
            errors.append(f"Row {index}: invalid status '{status}'.")
        if status != "closed":
            open_items += 1

        for column in ("evidence", "issue", "owner"):
            if not row[column].strip():
                errors.append(f"Row {index}: {column} is required.")

        if score < 4 and not row["next_action"].strip():
            errors.append(f"Row {index}: next_action is required when score is below 4.")

        if status == "closed" and score < 4:
            errors.append(f"Row {index}: low-score items cannot be closed.")

    if errors:
        print("[FAIL] research-retrospective.csv validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"[OK] research-retrospective.csv passed with {len(rows)} rows and {open_items} open item(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
