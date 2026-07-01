---
name: document-formatting
description: Chinese document formatting and layout workflow for official documents, meeting materials, academic papers, dissertations, technical reports, bids, contracts, business reports, resumes, PPTs, spreadsheets, posters, and other document-processing tasks. Use when the user asks for 排版, 公文格式, Word/DOCX/PDF/Markdown formatting, typography rules, page setup, title hierarchy, document templates, layout checks, or final formatted output.
---

# Document Formatting

Use this skill to choose the right Chinese document layout rules, convert them into an actionable formatting plan, and produce a polished output or checklist.

## Workflow

1. Identify the document scenario.
   - Official document: use党政机关公文 style first.
   - Academic paper, dissertation, technical report, references: use national standards and institution/journal templates first.
   - Bid, contract, business report, resume, PPT, spreadsheet, poster: use the issuer/platform/template first, then apply the scene defaults.
2. Ask only for missing high-impact constraints.
   - Required when the target has a binding template: issuing unit, school/journal, tender document, client style guide, or final file type.
   - Do not ask if the user wants a general guide or no source file is needed.
3. Load `references/scenario-rules.md` when detailed scene requirements are needed.
4. Produce one of these outputs:
   - Formatting specification: fonts, sizes, margins, line spacing, numbering, page numbers, tables/figures, and export rules.
   - Review checklist: issues to inspect before delivery.
   - Reflowed document: restructure the user's content into the chosen style.
   - Implementation plan for DOCX/PDF/Markdown/PPT/XLSX formatting.
5. Verify the output against the chosen scenario.
   - Check hierarchy consistency, page setup, typography, numbering, table/figure rules, references, page numbers, and template-specific hard constraints.

## Priority Rules

- Prefer the user's explicit template or superior authority requirement over this skill's defaults.
- Prefer current official standards over remembered rules. Browse or verify when the standard version could matter.
- For official documents, keep GB/T 9704-2012 style assumptions unless the user's unit has a stricter template.
- For dissertations, note that GB/T 7713.1-2025 is current from 2026-02-01.
- For references, note that GB/T 7714-2015 remains current until GB/T 7714-2025 takes effect on 2026-07-01.
- Do not invent decorative formatting for formal documents. Use restrained, readable, consistent layouts.

## Output Shape

For a formatting guide, use this compact structure:

```markdown
## 场景与依据
## 页面设置
## 字体与层级
## 段落、编号与页码
## 图表、附件与引用
## 交付前检查清单
```

For a document reflow, preserve the user's meaning and rewrite only structure, headings, punctuation, numbering, and layout notes unless the user asks for content polishing.

## DOCX/PDF Handling

When the user provides files:

- Inspect the file type and existing structure before changing it.
- Use bundled workspace dependencies or standard document libraries when available.
- Preserve unrelated content and existing user edits.
- Export deliverables to the workspace `outputs` directory when a user-facing file is requested.
- Report any font availability issue, especially 方正小标宋简体, 仿宋_GB2312, 楷体_GB2312, and 黑体.

## Chinese Leadership Report DOCX Rules

When producing Chinese analysis reports for leaders or internal decision review:

- Treat it as a restrained internal analysis report: cover, directory, header, footer, page number, numbered sections, figure captions, table captions, and appendix/method notes.
- Prefer title font 方正小标宋简体 when available; body 仿宋_GB2312 or 宋体; first-level headings 黑体; second-level headings 楷体_GB2312 or 黑体 according to the document tone.
- Do not assume setting a font name is enough. Before final delivery, inspect available system fonts, apply the selected title/heading/body fonts, then reopen/read the DOCX styles or runs to verify the intended Chinese font names were actually written.
- If 方正小标宋简体 is unavailable or cannot be verified, use a stable fallback such as 黑体 or Microsoft YaHei and explicitly report the fallback.
- For market-analysis reports, keep textual source citations out of body paragraphs when the user requests a clean leadership version; retain source notes under charts/tables and in the appendix/source notes.
