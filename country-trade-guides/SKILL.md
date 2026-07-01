---
name: country-trade-guides
description: 用于检索、引用和提炼本地 2025 年国别贸易指南。适用于出海市场研究、国别市场进入、贸易环境、进口准入、采购机会、风险提示、重点国家对比、报告引用补充，以及需要从本地 PDF 国别指南中提取原文证据的任务。
---

# 国别贸易指南

把本地 `25年国别贸易指南` 的 51 份 PDF 沉淀为可检索资料库。默认用于市场调研和出海报告中的国别引用，不替代海关、统计局、UN Comtrade、WITS 等贸易数据源。

## 资源

- `references/guide_index.md`：国家/主题索引，列出 51 份指南、页数、全文抽取文件和 PDF 副本。
- `references/guide_manifest.csv`：机器可读清单，含国家名、拼音关键词、文本文件、PDF 文件和原始路径。
- `references/extracted/`：从每份 PDF 抽取出的全文文本。
- `references/pdfs/`：PDF 副本，文件名按 `guide_001.pdf` 形式保存。
- `scripts/search_guides.py`：按国家和关键词检索片段。
- `scripts/build_extracts.py`：重新从原始 PDF 批量抽取文本并生成索引。

## 使用流程

1. 先读 `references/guide_index.md`，确认目标国家是否在库中。
2. 用检索脚本抓取原文片段：

```bash
python scripts/search_guides.py --country 印度尼西亚 --query "工程机械 基建 进口 准入" --limit 8
```

3. 报告写作时只引用与结论直接相关的片段，并标注国家指南名称和 PDF/抽取文本文件。
4. 对国别市场进入建议，至少提取四类信息：宏观与贸易环境、准入或认证、渠道/采购机会、风险与注意事项。
5. 若指南与最新官方数据冲突，优先使用最新官方数据；指南只作为国别背景和制度环境参考。

## 常用检索

```bash
python scripts/search_guides.py --list
python scripts/search_guides.py --country 沙特 --query "基建 项目 采购"
python scripts/search_guides.py --country 哈萨克 --query "矿山 工程机械 进口"
python scripts/search_guides.py --country 联合国采购 --query "工程 机械 供应商 注册"
python scripts/search_guides.py --query "关税 认证 准入" --limit 12
```

## 引用规则

- 正文引用不要写成空泛的“据国别指南显示”。必须写清国家、主题和信息类型。
- 图表或表格下方可写：`资料来源：2025 年国别贸易指南（印度尼西亚），references/extracted/guide_048.txt。`
- 若使用原文数字，保留年份和口径；若指南没有年份，写成背景判断，不写成最新统计。
- 指南适合支撑制度、营商、采购、风险、渠道类判断；核心贸易规模仍优先使用海关、UN Comtrade、WITS、ITC Trade Map 等数据源。

## 失败分支

| 触发条件 | 处理方式 |
|---|---|
| 检索不到国家 | 运行 `--list` 查看国家名；可用拼音或简称再搜 |
| 检索不到关键词 | 换同义词，如 `准入/认证/关税/进口/采购/项目/基建/矿山` |
| 文本抽取乱码或缺页 | 打开 `references/pdfs/guide_xxx.pdf` 人工核对 |
| 需要最新数字 | 不用指南作最终数字，转查海关、统计局或国际数据库 |
| 需要批量更新 | 用 `scripts/build_extracts.py <raw_manifest.csv>` 重建索引 |

## 不要做

- 不要把指南中的背景信息当作实时贸易数据。
- 不要把单个国家指南的描述泛化到整个区域。
- 不要只摘有利信息；风险、准入限制和付款问题要一起提取。
- 不要把抽取文本中的页眉、页脚、目录噪声写进报告。
- 不要在没有核对年份和口径的情况下引用数字。
