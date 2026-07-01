from __future__ import annotations

import csv
import re
import shutil
import sys
from pathlib import Path

import fitz


SKILL_ROOT = Path(__file__).resolve().parent.parent
REFERENCES = SKILL_ROOT / "references"
TEXT_DIR = REFERENCES / "extracted"


PINYIN_HINTS = {
    "阿尔及利亚": "aerjiliya",
    "阿根廷": "agenting",
    "阿联酋": "alianqiu",
    "埃及": "aiji",
    "澳大利亚": "aodaliya",
    "巴基斯坦": "bajisitan",
    "巴拿马": "banama",
    "巴西": "baxi",
    "比利时": "bilishi",
    "波兰": "bolan",
    "德国": "deguo",
    "俄罗斯": "eluosi",
    "法国": "faguo",
    "菲律宾": "feilvbin",
    "哥伦比亚": "gelunbiya",
    "哈萨克斯坦": "hasakesitan",
    "韩国": "hanguo",
    "荷兰": "helan",
    "加拿大": "jianada",
    "加纳": "jiana",
    "柬埔寨": "jianpuzhai",
    "捷克": "jieke",
    "吉尔吉斯斯坦": "jierjisisitan",
    "利比里亚": "libiliya",
    "马来西亚": "malaixiya",
    "美国": "meiguo",
    "孟加拉国": "mengjialaguo",
    "秘鲁": "bilu",
    "缅甸": "miandian",
    "墨西哥": "moxige",
    "南非": "nanfei",
    "尼日利亚": "niriliya",
    "日本": "riben",
    "瑞典": "ruidian",
    "沙特阿拉伯": "shatealabo",
    "泰国": "taiguo",
    "土耳其": "tuerqi",
    "乌兹别克斯坦": "wuzibiekesitan",
    "西班牙": "xibanya",
    "希腊": "xila",
    "新加坡": "xinjiapo",
    "匈牙利": "xiongyali",
    "以色列": "yiselie",
    "意大利": "yidali",
    "印度": "yindu",
    "印度尼西亚": "yindunixiya",
    "英国": "yingguo",
    "越南": "yuenan",
    "智利": "zhili",
    "中国": "zhongguo",
    "联合国采购": "un-procurement",
}


def compact_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf(pdf_path: Path) -> tuple[str, int]:
    doc = fitz.open(pdf_path)
    pages: list[str] = []
    for index, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages.append(f"\n\n--- PAGE {index} ---\n{text}")
    return compact_text("".join(pages)), doc.page_count


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: build_extracts.py <raw_manifest.csv>")
        return 1
    raw_manifest = Path(sys.argv[1]).resolve()
    if not raw_manifest.exists():
        print(f"[FAIL] Missing manifest: {raw_manifest}")
        return 1

    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_dir = REFERENCES / "pdfs"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    with raw_manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    out_rows: list[dict[str, str]] = []
    for row in rows:
        pdf_name = row["id"]
        country = row["country"]
        raw_pdf = raw_manifest.parent / pdf_name
        copied_pdf = pdf_dir / pdf_name
        if raw_pdf.exists() and not copied_pdf.exists():
            shutil.copy2(raw_pdf, copied_pdf)

        text, pages = extract_pdf(copied_pdf)
        text_file = pdf_name.replace(".pdf", ".txt")
        (TEXT_DIR / text_file).write_text(text + "\n", encoding="utf-8")
        out_rows.append(
            {
                "id": pdf_name,
                "country": country,
                "country_pinyin": PINYIN_HINTS.get(country, ""),
                "pages": str(pages),
                "text_file": text_file,
                "pdf_file": str(Path("references") / "pdfs" / pdf_name),
                "source_path": row["source_path"],
                "bytes": row["bytes"],
            }
        )
        print(f"[OK] {country}: pages={pages}, chars={len(text)}")

    manifest_path = REFERENCES / "guide_manifest.csv"
    with manifest_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "country", "country_pinyin", "pages", "text_file", "pdf_file", "source_path", "bytes"],
        )
        writer.writeheader()
        writer.writerows(out_rows)

    index_lines = [
        "# 2025 年国别贸易指南索引",
        "",
        f"- 指南数量：{len(out_rows)}",
        "- 原始目录：`E:\\工作\\01-项目管理\\优品库项目\\国别贸易指南\\25年国别贸易指南`",
        "- 检索脚本：`scripts/search_guides.py --country <国家> --query <关键词>`",
        "",
        "| 国家/主题 | 页数 | 全文抽取 | 原始 PDF |",
        "|---|---:|---|---|",
    ]
    for item in out_rows:
        index_lines.append(f"| {item['country']} | {item['pages']} | `references/extracted/{item['text_file']}` | `{item['pdf_file']}` |")
    (REFERENCES / "guide_index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    print(f"[OK] Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
