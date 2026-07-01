# 自我进化闭环

市场调研 skill 每完成一个研究项目后，必须沉淀一次复盘。目标不是评价人，而是让下一份报告更可靠、更快、更可复核。

## 触发条件

- 正式报告交付后。
- 用户指出数据、图表、结论、排版或来源问题后。
- `checks/` 校验失败两次以上后。
- 同一类研究需要再次复用时。

## 复盘输入

- `sources.csv`
- `chart-plan.csv`
- `output/full-report.md`
- `output/report.html`
- `output/report.pdf`
- `output/report.docx`
- `research-retrospective.csv`
- 用户反馈、审阅意见或验收记录
- `scripts/run_checks.py` 的输出日志

## 评分维度

每项 1-5 分，低于 4 分必须生成改进动作。

| 维度 | 5 分标准 | 常见扣分 |
|---|---|---|
| sources | 核心数字有 P1/P2 双源、页码或表名可复核 | 只给首页链接、媒体来源支撑核心结论 |
| scope | HS 编码、年份、币种、地区和纳入排除规则清楚 | 混合编码、年份混用、范围漂移 |
| charts | 图表回答明确问题，文件存在，单位和来源完整 | 图表只是装饰、标签重叠、无源数据 |
| claims | 数字结论有 `[Sources: ...]` 或估算说明 | 关键数字无来源、估算公式缺失 |
| strategy | 建议能从数据推导，明确优先级和风险 | 建议泛泛而谈、与证据脱节 |
| delivery | Word/PDF/HTML/Markdown 一致且资产齐全 | 交付格式缺失、图表模糊、目录页码错误 |
| reuse | 数据、图表、来源和方法可被下一项目复用 | 只留下最终稿，没有中间工件 |

## 操作流程

1. 运行 `scripts/run_checks.py <project_dir>`，保存输出。
2. 填写或更新 `research-retrospective.csv`。
3. 运行 `scripts/evolve_project.py <project_dir>` 生成 `notes/evolution-backlog.md`。
4. 将 backlog 中的高优先级问题转成下一轮研究动作。
5. 如果同一问题在 2 个项目中重复出现，改进本 skill 的模板、参考文件或校验脚本。

## 失败分支

| 触发条件 | 一线处理 | 仍失败兜底 |
|---|---|---|
| 缺少复盘表 | 从 `templates/research-retrospective.csv` 复制 | 手动创建同名 CSV，字段必须一致 |
| 校验脚本失败 | 把失败项写入复盘表，状态设为 `open` | 在 backlog 标注 `blocking`，不要声明交付完成 |
| 用户反馈很模糊 | 拆成来源、图表、结论、格式四类问题 | 标注为 `needs-clarification` 并列出待确认问题 |
| 核心数据源冲突 | 回到口径表核对年份、币种、HS 版本 | 使用区间值，并在报告中解释冲突来源 |
| 改进动作无法执行 | 写明外部依赖或缺口 | 降级为风险提示，保留验证优先级 |

## 不要做

- 不要把复盘写成“本次表现良好”的空话。
- 不要只记录校验通过项，失败项更重要。
- 不要用用户反馈替代来源校验。
- 不要因为报告已经导出 PDF 就停止修正源稿。
- 不要把无法复核的数据沉淀为下次可复用资产。
