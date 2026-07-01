from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
REFERENCES = SKILL_ROOT / "references"
MANIFEST = REFERENCES / "guide_manifest.csv"
TEXT_DIR = REFERENCES / "extracted"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search local 2025 country trade guide text extracts."
    )
    parser.add_argument("--country", default="", help="Country name keyword, e.g. 印尼, 哈萨克")
    parser.add_argument("--query", default="", help="Keyword query. Use spaces for OR terms.")
    parser.add_argument("--limit", type=int, default=8, help="Maximum snippets to print")
    parser.add_argument("--context", type=int, default=90, help="Characters around each match")
    parser.add_argument("--list", action="store_true", help="List available countries")
    return parser.parse_args()


def load_manifest() -> list[dict[str, str]]:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"Missing manifest: {MANIFEST}")
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def make_terms(query: str) -> list[str]:
    return [term for term in re.split(r"\s+", query.strip()) if term]


def find_snippets(text: str, terms: list[str], context: int, limit: int) -> list[str]:
    if not terms:
        return []
    snippets: list[str] = []
    lowered = text.lower()
    for term in terms:
        start = 0
        term_lower = term.lower()
        while len(snippets) < limit:
            idx = lowered.find(term_lower, start)
            if idx == -1:
                break
            a = max(0, idx - context)
            b = min(len(text), idx + len(term) + context)
            snippets.append(normalize(text[a:b]))
            start = idx + len(term)
    return snippets


def main() -> int:
    args = parse_args()
    rows = load_manifest()
    if args.list:
        for row in rows:
            print(f"{row['country']}\t{row['text_file']}\tpages={row['pages']}")
        return 0

    country_filter = args.country.strip()
    terms = make_terms(args.query)
    if not country_filter and not terms:
        print("[FAIL] Provide --country, --query, or --list.")
        return 1

    matches = [
        row
        for row in rows
        if not country_filter or country_filter in row["country"] or country_filter.lower() in row["country_pinyin"].lower()
    ]
    if not matches:
        print(f"[FAIL] No country matched: {country_filter}")
        return 1

    printed = 0
    for row in matches:
        text_path = TEXT_DIR / row["text_file"]
        if not text_path.exists():
            continue
        text = text_path.read_text(encoding="utf-8", errors="replace")
        if terms:
            snippets = find_snippets(text, terms, args.context, args.limit - printed)
        else:
            snippets = [normalize(text[: args.context * 4])]
        for snippet in snippets:
            printed += 1
            print(f"[{row['country']} | {row['text_file']} | {row['source_path']}]")
            print(snippet)
            print()
            if printed >= args.limit:
                return 0

    if printed == 0:
        print("[OK] Country found, but no query snippets matched.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
