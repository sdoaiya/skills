from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


REQUIRED_OUTPUT_FILES = [
    "full-report.md",
    "report.html",
    "report.pdf",
    "report.docx",
]
COPY_DIRS = [
    "data",
    "charts",
    "sources",
]
OPTIONAL_FILES = [
    "README.md",
    "hs-scope.csv",
    "sources.csv",
    "chart-plan.csv",
    "country-scorecard.csv",
    "report-outline.md",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package a market research project into a delivery bundle."
    )
    parser.add_argument("project_dir", type=Path, help="Research project root directory")
    parser.add_argument(
        "--bundle-name",
        default="",
        help="Name of the packaged delivery directory and zip file",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=None,
        help="Directory where the packaged bundle should be created. Defaults to project_dir/dist",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing packaged directory or zip file",
    )
    return parser.parse_args()


def ensure_required_outputs(project_dir: Path) -> Path:
    output_dir = project_dir / "output"
    if not output_dir.exists():
        raise FileNotFoundError(f"Missing output directory: {output_dir}")
    missing = [name for name in REQUIRED_OUTPUT_FILES if not (output_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required output files: " + ", ".join(str(output_dir / name) for name in missing)
        )
    return output_dir


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def package_project(project_dir: Path, destination: Path, bundle_name: str, force: bool) -> tuple[Path, Path]:
    output_dir = ensure_required_outputs(project_dir)
    destination.mkdir(parents=True, exist_ok=True)
    package_dir = destination / bundle_name
    archive_base = destination / bundle_name
    zip_path = destination / f"{bundle_name}.zip"

    if package_dir.exists():
        if not force:
            raise FileExistsError(f"Package directory already exists: {package_dir}")
        shutil.rmtree(package_dir)
    if zip_path.exists():
        if not force:
            raise FileExistsError(f"Package archive already exists: {zip_path}")
        zip_path.unlink()

    package_dir.mkdir(parents=True, exist_ok=True)

    for file_name in REQUIRED_OUTPUT_FILES:
        shutil.copy2(output_dir / file_name, package_dir / file_name)

    for dir_name in COPY_DIRS:
        src_dir = project_dir / dir_name
        if src_dir.exists():
            copy_tree(src_dir, package_dir / dir_name)

    for file_name in OPTIONAL_FILES:
        src_file = project_dir / file_name
        if src_file.exists():
            shutil.copy2(src_file, package_dir / file_name)

    manifest_path = package_dir / "PACKAGE_CONTENTS.txt"
    manifest_lines = [
        f"project_dir={project_dir}",
        f"bundle_name={bundle_name}",
        "",
        "included_files:",
    ]
    for path in sorted(package_dir.rglob("*")):
        if path.is_file():
            manifest_lines.append(str(path.relative_to(package_dir)))
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")

    archive_file = shutil.make_archive(str(archive_base), "zip", root_dir=destination, base_dir=bundle_name)
    return package_dir, Path(archive_file)


def main() -> int:
    args = parse_args()
    project_dir = args.project_dir.resolve()
    destination = (args.destination.resolve() if args.destination else project_dir / "dist")
    bundle_name = args.bundle_name or f"{project_dir.name}-delivery"

    try:
        package_dir, archive_path = package_project(project_dir, destination, bundle_name, args.force)
    except (FileNotFoundError, FileExistsError) as exc:
        print(f"[FAIL] {exc}")
        return 1

    print(f"[OK] Delivery package created: {package_dir}")
    print(f"[OK] ZIP archive created: {archive_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
