from __future__ import annotations

import argparse
import sys
from pathlib import Path


REQUIRED_FILES = [
    "full-report.md",
    "report.html",
    "report.pdf",
    "report.docx",
]
REQUIRED_DIRS = [
    "data",
    "charts",
    "sources",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate market-research delivery package.")
    parser.add_argument("output_dir", type=Path, help="Path to delivery root directory")
    return parser.parse_args()


def has_direct_layout(base_dir: Path) -> bool:
    return all((base_dir / file_name).exists() for file_name in REQUIRED_FILES) and all(
        (base_dir / dir_name).exists() and (base_dir / dir_name).is_dir() for dir_name in REQUIRED_DIRS
    )


def has_project_layout(base_dir: Path) -> bool:
    output_dir = base_dir / "output"
    return all((output_dir / file_name).exists() for file_name in REQUIRED_FILES) and all(
        (base_dir / dir_name).exists() and (base_dir / dir_name).is_dir() for dir_name in REQUIRED_DIRS
    )


def main() -> int:
    args = parse_args()
    if not args.output_dir.exists():
        print(f"[FAIL] Missing delivery directory: {args.output_dir}")
        return 1

    if has_direct_layout(args.output_dir):
        print(f"[OK] Delivery package is complete: {args.output_dir}")
        return 0

    if has_project_layout(args.output_dir):
        print(f"[OK] Project delivery layout is complete: {args.output_dir}")
        return 0

    errors: list[str] = []
    errors.extend(
        f"Missing direct-layout file: {args.output_dir / file_name}"
        for file_name in REQUIRED_FILES
        if not (args.output_dir / file_name).exists()
    )
    errors.extend(
        f"Missing direct-layout directory: {args.output_dir / dir_name}"
        for dir_name in REQUIRED_DIRS
        if not ((args.output_dir / dir_name).exists() and (args.output_dir / dir_name).is_dir())
    )
    errors.extend(
        f"Missing project-layout file: {args.output_dir / 'output' / file_name}"
        for file_name in REQUIRED_FILES
        if not (args.output_dir / "output" / file_name).exists()
    )
    errors.extend(
        f"Missing project-layout directory: {args.output_dir / dir_name}"
        for dir_name in REQUIRED_DIRS
        if not ((args.output_dir / dir_name).exists() and (args.output_dir / dir_name).is_dir())
    )

    print("[FAIL] Delivery package validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
