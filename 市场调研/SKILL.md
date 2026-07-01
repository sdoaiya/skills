---
name: market-research
description: 用于生成高可信、数据可查、图表丰富、排版专业且可复盘进化的市场调研/行业研究/出海分析/白皮书报告。适用于用户指定行业、产品、HS 编码或目标国家的全球市场分析、国别市场进入、竞争格局、TAM/SAM/SOM、市占率、贸易流向、政策与风险分析、研究复盘、自我进化 backlog，并支持 Word、PDF、HTML 等正式交付格式。
---

# 市场调研

用于把一个市场研究问题推进到可交付的正式报告，而不是聊天式摘要。默认输出中文，除非用户指定其他语言。

## 适用场景

- 任意行业/产品的出海、全球市场、国别市场进入、产业链和竞争格局分析。
- 白皮书、行业研究报告、投资/战略备忘录、市场进入建议书。
- 需要官方、学术、可复核数据，并配套丰富图表、地图、表格和专业排版。
- 需要导出为 Word、PDF、HTML，或同时保留 Markdown/数据表/图表资产。

## 触发后的首要动作

1. 明确研究对象、目标受众、报告用途、目标区域、时间窗口、交付格式和深度。
2. 如果用户没有给出格式，默认交付 `Word + PDF + HTML + Markdown 源稿`。
3. 如果用户没有给出行业口径，先建立 `产品/HS编码/地区/年份/纳入规则` 底表。
4. 对出海、全球贸易、国别进入或 HS 编码分析任务，读取 `references/industry-overseas.md`。
5. 对所有正式报告，读取 `references/source-and-evidence.md` 与 `references/visual-reporting.md`。
6. 对 Word/PDF/HTML 交付，读取 `references/delivery-formats.md`。
7. 对交付后复盘、用户反馈处理或持续优化任务，读取 `references/self-evolution.md`。
8. 优先复制并填写 `templates/` 下的标准模板，至少包含 `sources.csv`、`chart-plan.csv`、`hs-scope.csv`、`country-scorecard.csv`、`research-retrospective.csv` 和 `report-outline.md`。
9. 交付前运行 `checks/` 下的校验脚本，确认来源、图表、关键数字和交付文件齐全。
10. 交付后运行 `scripts/evolve_project.py`，基于校验结果、复盘表和用户反馈生成下一轮改进 backlog。
11. 如果需要快速起项目，运行 `scripts/init_project.py` 自动创建目录、复制模板并生成任务说明。
12. 如果需要整理正式交付包，运行 `scripts/package_delivery.py` 汇总 `output/`、`data/`、`charts/`、`sources/` 并生成 ZIP 归档。
13. 如果需要一条命令跑完全部基础校验，运行 `scripts/run_checks.py`。

## 研究工作流

1. **口径定义**：定义市场边界、产品线、HS 编码、目标国家、年份、贸易流向、币种和汇率口径。
2. **数据源登记**：建立来源清单，标注来源类型、发布机构、年份、URL/文件路径、可复核方式、证据等级。
3. **官方数据采集**：优先使用海关、UN Comtrade、World Bank WITS、ITC Trade Map、国家统计机构、行业协会、上市公司年报。
4. **国别材料抽取**：对用户本地或公开的官方国别指南抽取宏观、产业、贸易环境、准入、风险、采购机会。
5. **交叉验证**：所有关键数字至少做双源校验；冲突时解释统计口径、年份、币种、样本范围差异。
6. **模型与评分**：建立市场规模、增长、竞争份额、需求驱动、风险和进入优先级模型。
7. **图表资产规划**：在写报告前生成图表清单，每个图表绑定问题、数据源、图表类型、结论和最终位置。
8. **章节写作**：先写报告骨架，再分章节扩展；每个重要结论必须有数据、图表或来源支撑。
9. **多格式交付**：先形成 Markdown/HTML 主稿和可复用图表资产，再导出 Word/PDF，避免截图式不可维护输出。
10. **验收**：检查字数、引用、图表数量、来源可查性、格式完整性、目录、页眉页脚、图表说明和导出文件。
11. **自我进化**：用交付结果、校验日志和用户反馈更新 `research-retrospective.csv`，运行 `scripts/evolve_project.py` 生成 `notes/evolution-backlog.md`；重复出现的问题必须反向改进模板、参考文件或校验脚本。

## 模板与校验

默认模板目录：

- `templates/sources.csv`：来源登记表。
- `templates/chart-plan.csv`：图表规划表。
- `templates/hs-scope.csv`：HS 编码与产品口径底表。
- `templates/country-scorecard.csv`：国别评分卡。
- `templates/research-retrospective.csv`：交付后复盘、评分和改进动作表。
- `templates/report-outline.md`：白皮书主稿骨架。

默认校验目录：

- `checks/check_sources.py`：检查来源登记表字段、证据等级和章节覆盖。
- `checks/check_charts.py`：检查图表规划表、来源映射和图表文件存在性。
- `checks/check_claims.py`：检查主稿中的关键数字、来源引用和估算标记。
- `checks/check_delivery.py`：检查 Markdown、HTML、PDF、Word 及交付目录完整性。
- `checks/check_retrospective.py`：检查复盘表字段、评分、状态和低分改进动作。

默认脚本目录：

- `scripts/init_project.py`：初始化研究任务目录，复制模板并生成执行说明。
- `scripts/package_delivery.py`：汇总研究资产并生成正式交付目录与 ZIP 文件。
- `scripts/run_checks.py`：串行执行来源、图表、主稿和交付结构校验，并汇总结果。
- `scripts/evolve_project.py`：读取复盘表、校验日志和用户反馈，生成自我进化评分与改进 backlog。

建议执行顺序：

1. 初始化任务目录并复制模板。
2. 填写 `hs-scope.csv` 与 `sources.csv`。
3. 产出清洗数据与 `chart-plan.csv`。
4. 写作 `full-report.md` 或基于 `report-outline.md` 扩写。
5. 生成图表与最终交付文件。
6. 运行 `checks/` 中全部脚本，通过后再声明交付完成。
7. 运行自我进化脚本，把不足项写入下一轮研究 backlog。

初始化示例：

```bash
python scripts/init_project.py D:\research\excavator-indonesia --topic "印尼工程机械市场" --region "印尼" --timeframe "2020-2025"
```

打包示例：

```bash
python scripts/package_delivery.py D:\research\excavator-indonesia --bundle-name excavator-indonesia-v1
```

聚合校验示例：

```bash
python scripts/run_checks.py D:\research\excavator-indonesia --require-sections 4 7 --require-chart-files
```

自我进化示例：

```bash
python scripts/evolve_project.py D:\research\excavator-indonesia --checks-log D:\research\excavator-indonesia\notes\checks.log --feedback D:\research\excavator-indonesia\notes\user-feedback.md
```

## 证据规则

- 重要数据不得只引用媒体、券商、咨询机构或 AI 回答。
- 商业咨询和券商报告只能做框架、假设或旁证，不能单独支撑核心市场规模。
- 每个图表必须标明数据源、年份、口径和单位。
- 缺失数据时可以估算，但必须写明公式、假设、敏感性范围和验证优先级。
- 不能为了完整性编造数据；宁可标注“公开数据不足”。

## 自我进化规则

- 每个正式项目必须保留 `research-retrospective.csv` 和 `notes/evolution-backlog.md`。
- 复盘评分低于 4 分的维度必须有 `next_action`。
- 用户反馈必须归类到来源、口径、图表、结论、策略、交付或复用问题。
- 校验失败项不能只修最终稿；必须追溯到模板、数据表、图表计划或来源登记表。
- 同一失败模式在 2 个项目中重复出现时，更新本 skill 的模板、参考文件或校验脚本。
- 若复盘缺少证据，标注 `needs-evidence`，不要把它当作已解决问题。

## 自我进化反例黑名单

- 不要把复盘写成泛泛总结。
- 不要只记录成功项。
- 不要把“用户没提意见”视为质量通过。
- 不要用商业报告截图替代原始来源。
- 不要把不可复核的数据沉淀为下次默认口径。
- 不要为了提高评分增加装饰性图表或无证据结论。

## 图表最低要求

正式白皮书默认至少包含：

- 1 张全球/区域贸易流向图或地图。
- 3 张趋势图：出口额、进口额、目标国家需求或产品线变化。
- 3 张排名/对比图：国家、产品线、竞争来源国、企业。
- 2 张结构图：产品结构、区域结构、产业链或渠道结构。
- 1 张风险/机会矩阵。
- 1 张市场进入优先级评分矩阵。
- 若有测算，至少 1 张敏感性分析图或场景表。

## 报告结构

默认白皮书结构：

1. 封面
2. Executive Summary
3. 研究范围、数据口径与证据等级
4. 全球市场与贸易格局
5. 中国出口表现
6. 产品线分析
7. 重点区域与国别机会
8. 竞争格局与企业对标
9. 市场进入模式与渠道策略
10. 政策、认证、贸易、信用和售后风险
11. 优先市场评分与战略建议
12. 附录：HS 编码、数据源、测算方法、国别卡片、引用清单

## 交付标准

- 正式报告应排版美观、专业、克制，避免花哨装饰。
- 图表、表格、引用和结论应在同一阅读路径中，不要把证据堆到附录后才解释。
- Word/PDF/HTML 版本内容必须一致；差异只允许来自排版适配。
- 保留可复核工件：原始数据、清洗表、图表 PNG/SVG、Markdown 源稿、引用清单。

## 参考来源

本 skill 综合借鉴以下公开 skill 的方法：

- `147356/agent-skill-industry-research`：中文深度行研、双路径市场测算、红队自检、Word 报告。
- `tingbo-c/invest-research-skills`：数据质量分级、研究方法论、市场测算原则。
- `openai/plugins reports-pdfs-and-slide-automation`：图表资产先行、报告/PDF/Office/HTML 组合交付。
- `product-on-purpose/pm-skills discover-market-sizing`：TAM/SAM/SOM、bottom-up、假设表、敏感性分析。
