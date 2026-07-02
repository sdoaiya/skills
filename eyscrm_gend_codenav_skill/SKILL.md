---
name: eyscrm_gend_codenav_skill
description: G端中台知识记忆与协同 Skill，用于沉淀并调用 G端、GR中台、优品库、AI试点、产业带下沉、政府项目、文档风格和风险红线等上下文。
metadata:
  short-description: G端中台知识记忆与协同
---

# G端中台知识记忆与协同 Skill

## 1. Skill定位

本 Skill 用于让 Codex / AI Agent 调用当前沉淀的 G端、GR中台、优品库、AI试点、产业带下沉、项目方案、文档风格与风险红线等知识，实现：

1. 跨任务共享上下文；
2. 生成政府汇报、内部方案、培训方案、台账结构、合同报价、Codex自动化需求时自动带入业务背景；
3. 将新增信息沉淀为可追溯、可版本化的记忆；
4. 通过演进日志和更新规则实现“自我进化”。

> 本 Skill 不替代真实数据库。它是一个本地可读写的知识包。接入 WPS 多维表格、钉钉多维表格、CRM、销售工具包时，应由 Codex 另行编写适配器。

---

## 2. 推荐目录结构

```text
eyscrm_gend_codenav_skill/
├── SKILL.md
├── README.md
├── manifest.json
├── data/
│   ├── memory_bank.json
│   └── projects.json
├── schemas/
│   ├── memory_update.schema.json
│   ├── task_intake.schema.json
│   └── project_card.schema.json
├── scripts/
│   ├── memory_store.py
│   └── skill_cli.py
├── prompts/
│   ├── task_router_prompt.md
│   ├── memory_evolution_prompt.md
│   └── government_material_prompt.md
├── templates/
│   ├── government_report_outline.md
│   ├── codex_automation_prd.md
│   └── project_review.md
├── examples/
│   └── codex_usage.md
└── logs/
    └── evolution_log.md
```

---

## 3. Codex调用原则

### 3.1 每次任务开始前

Codex 应先读取：

1. `manifest.json`
2. `data/memory_bank.json`
3. `data/projects.json`
4. 与任务相关的模板和 prompt

然后执行以下判断：

- 任务属于政府汇报、活动方案、合作谈判、合同报价、台账、通知海报、内部总结还是自动化开发；
- 目标对象是政府、协会、国资、企业、内部管理层、销售还是交付；
- 是否涉及政策、金额、企业数量、政府背书、项目承诺等高风险内容；
- 是否需要引用已有项目背景；
- 是否需要更新记忆。

### 3.2 记忆调用优先级

优先级从高到低：

1. 用户在当前任务中明确提供的最新信息；
2. 已确认的项目数据：`confidence=confirmed`；
3. 当前项目状态：`data/projects.json`；
4. 长期偏好与风格：`data/memory_bank.json`；
5. 历史方案和模板；
6. 未确认信息：只可作为“待确认”或“参考”，不得直接作为最终事实。

### 3.3 EasyGR 调用规则

当任务不仅是“查资料”，而是需要 **做判断、重构方案、拆打法、定边界、抓闭环、看复制** 时，Codex 应把 `C:\Users\zdy25\.codex\skills\easygr-perspective\SKILL.md` 视为高阶决策镜片。

默认先经过 EasyGR 镜片的场景：

1. 政府合作方案与厅局汇报材料；
2. 区域起盘、产业带下沉、样板区打法；
3. 活动设计、活动复盘、活动转化诊断；
4. G端与销售的边界、承接、协同机制；
5. 重点项目推进、阶段复盘、问题重构；
6. 中台组织设计、岗位拆分、培训体系、台账体系；
7. 领导汇报版、内部判断版、项目复盘版。

调用顺序建议：

1. 先读 `data/memory_bank.json` 和 `data/projects.json` 获取事实；
2. 再用 EasyGR 判断问题本质属于入口、承接、闭环、复制中的哪一类；
3. 最后按对象切换表达：
   - 对政府：去销售化、讲公共价值；
   - 对内部：强结果化、讲责任、讲节奏、讲口径。

以下场景不必强行调用 EasyGR：

- 纯资料检索；
- 纯格式整理；
- 纯字段搬运；
- 与 G端经营判断无关的机械任务。

### 3.4 EasyGR 模板路由

当任务已经明确需要“直接出成品”时，在调用 EasyGR 镜片判断问题本质后，优先映射到以下模板：

| 任务类型 | EasyGR 模板 | 使用说明 |
|---|---|---|
| 政府汇报、厅局方案、政府购买服务方案、领导压缩汇报 | `C:\Users\zdy25\.codex\skills\easygr-perspective\references\templates\01-government-report-template.md` | 先讲背景和定位，再讲实施路径、可交付内容、阶段成果口径；默认去销售化。 |
| 区域起盘、产业带下沉、样板区推进、某地打法设计 | `C:\Users\zdy25\.codex\skills\easygr-perspective\references\templates\02-regional-playbook-template.md` | 先看区域入口和资源图谱，再拆打法主线、组织分工、阶段节奏和复制条件。 |
| G端与销售分工、活动后承接、线索机制、转化诊断 | `C:\Users\zdy25\.codex\skills\easygr-perspective\references\templates\03-sales-collaboration-template.md` | 先定边界，再定承接流程、SLA、反馈机制和结果口径。 |
| 重点项目复盘、活动复盘、试点复盘、阶段问题诊断 | `C:\Users\zdy25\.codex\skills\easygr-perspective\references\templates\04-project-retrospective-template.md` | 不复述过程，按六段闭环复盘，最后沉淀修正动作和组织资产。 |

路由顺序固定为：

1. 先读取主知识库事实；
2. 再调用 EasyGR 判断问题本质；
3. 再选择最匹配的模板出成品；
4. 如果同时面对政府和内部，允许同一事实基础上输出双版本。

### 3.5 EasyGR 快捷触发词

如果用户直接使用以下短语，视为已经指定模板与语气：

| 用户触发词 | 直接动作 |
|---|---|
| `EasyGR-政府版` | 直接调用政府汇报模板，输出政府/厅局/领导汇报口径。 |
| `EasyGR-区域版` | 直接调用区域打法模板，输出区域起盘/产业带下沉/样板区方案。 |
| `EasyGR-协同版` | 直接调用销售协同模板，输出边界、承接、反馈与结果机制。 |
| `EasyGR-复盘版` | 直接调用项目复盘模板，输出六段闭环复盘与修正动作。 |

解释规则：

1. 快捷词优先级高于普通模板匹配；
2. 快捷词不跳过事实核对和风险红线；
3. 快捷词不代表放弃 EasyGR 判断，仍需先做问题定义，再出成品。

---

## 4. 自我进化机制

本 Skill 支持“append-only with review”演进机制：

### 4.1 何时更新记忆

当出现以下情况时，Codex 应生成一条 `MemoryUpdate`：

- 用户明确说“记住”“以后按这个”“这个作为最终版”“删除某项”“以后不要写某项”；
- 项目状态发生变化，如 active → paused / planning → active；
- 关键数据变化，如报名企业数量、金额、时间节点、人员配置；
- 用户反复纠正某类表达方式；
- 新增高频模板或标准SOP；
- 某个旧信息被明确废弃。

### 4.2 如何更新

禁止直接无痕覆盖。建议流程：

1. 读取 `data/memory_bank.json`；
2. 根据 `schemas/memory_update.schema.json` 生成更新对象；
3. 调用 `scripts/skill_cli.py update --file update.json`；
4. 将更新追加写入 `logs/evolution_log.md`；
5. 对被替代内容添加 `supersedes` 或 `archived` 标记；
6. 重大更新应等待用户确认。

### 4.3 自我进化不等于自动编造

Codex 不得自行新增未经用户确认的事实。可以新增：

- 任务结构；
- 模板；
- 自动化字段；
- 根据用户明确表达总结出的偏好；
- 对已有信息的分类、标签和索引。

不得新增：

- 未核实金额；
- 未核实政策依据；
- 未确认政府态度；
- 未确认企业名单；
- 未确认联系人和个人信息。

---

## 5. 政府材料写作红线

用于政府、协会、国资、厅局、园区场景时，默认启用以下红线：

1. 避免“我司我司”的销售口吻；
2. 不承诺政策、补贴、订单、数据增长；
3. 不虚假政府背书；
4. 不夸大AI工具效果；
5. 公益培训不能写成强销售转化；
6. 政府购买服务中避免“卖软件”，应写“公共服务能力提升、企业外贸能力培育、资源对接、试点示范、可交付成果”；
7. 涉及政策、资金、企业数量、地市名单时，必须标注来源或待核验。

---

## 6. 常用任务路由

| 任务类型 | 默认调用数据 | 默认输出风格 |
|---|---|---|
| 政府汇报方案 | company_context, project_tracks, risk_and_compliance | 简洁、政府视角、重点突出 |
| 领导汇报版 | project_tracks, document_style | 3-4页以内、结论先行 |
| 活动/培训方案 | industry_belt_descent, ai_pilot_shandong, templates | 流程清楚、可执行 |
| 合作谈判方案 | company_context, project_tracks | 机会点、利益点、合作路径 |
| 合同/报价 | document_style, project_tracks | 明细具体、付款节点清楚 |
| 台账/表格 | g_end_middle_platform, middle_office_work_ai | 字段清晰、负责人级管理 |
| Codex自动化 | middle_office_work_ai, schemas | PRD+数据结构+接口建议 |
| 图片/海报 | document_style.visual_style | 清晰、少噪点、文字准确 |

补充规则：

- 凡是“怎么起盘、怎么推进、为什么没转化、边界怎么定、样板怎么复制”类问题，默认再叠加 EasyGR 镜片；
- 凡是“政府材料 + 内部经营判断”混合任务，先走主知识库事实，再走 EasyGR 的闭环审查；
- 如果输出同时要面向政府和内部，允许生成双版本：政府版与内部判断版。
- 凡是需要直接出政府汇报、区域打法、销售协同、项目复盘成品时，默认再匹配 EasyGR 模板路由，不从零起草。

---

## 7. 输出时的默认偏好

- 中文；
- 结构化；
- 先给结论，再给路径；
- 政府材料避免销售化；
- 内部材料可以更直接、通俗；
- 需要判断类输出时，优先用 EasyGR 的“先定义、再拆闭环、再落责任、最后看结果口径”；
- 尽量给可落地动作，不写空泛口号；
- 需要生成 Word 时，优先按中文正式方案版式；
- 需要生成图时，优先高清、干净、商务、少色彩、文字清晰。

---

## 8. 快速调用示例

```bash
python scripts/skill_cli.py search "AI试点"
python scripts/skill_cli.py search "产业带下沉"
python scripts/skill_cli.py project ai_pilot_shandong
python scripts/skill_cli.py list-projects
python scripts/skill_cli.py export-context --task "生成济宁优品库政府购买服务方案"
```

---

## 9. 最小Codex系统提示建议

将以下内容放入 Codex 任务前置提示：

```text
你正在调用 eyscrm_gend_codenav_skill。请先读取 SKILL.md、manifest.json、data/memory_bank.json、data/projects.json。
输出任何政府/协会/国资材料时，必须启用 risk_and_compliance 规则。
凡是需要打法判断、项目重构、边界划分、样板复制、活动转化诊断的任务，追加调用 easygr-perspective 作为高阶决策镜片。
涉及项目数据、金额、企业数量、政策依据时，不确定则标注待核验，不要编造。
用户偏好：中文正式方案、结构化、可落地、避免销售化表达，必要时输出Word/PPT/表格/脑图版本。
完成任务后，判断是否需要生成 MemoryUpdate；只有用户明确确认的信息才写入长期记忆。
```
