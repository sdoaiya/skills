# Codex Skills 仓库说明

这个仓库用于管理本机 `~/.codex/skills` 下已经安装的 skills，主要用途有 3 个：

1. 作为本地 skill 集合的 Git 备份。
2. 作为技能更新、审计和回滚记录。
3. 作为对外推送到 `origin` 的聚合仓库。

## 仓库结构

- `.system/`
  内置系统 skills，通常随 Codex 或内置能力分发，不建议未经确认直接整体覆盖。
- `paper-spine*`
  PaperSpine 系列 skills，覆盖论文写作、重写、翻译、LaTeX、审计等完整链路。
- 其他目录
  本地安装、手工维护或第三方来源的 skills。

## 远端说明

- `origin`: `https://github.com/sdoaiya/skills.git`
- `openai-skills`: `https://github.com/openai/skills.git`
- `paperspine`: `https://github.com/WUBING2023/PaperSpine.git`

说明：

- `origin` 是当前聚合仓库的实际推送目标。
- `openai-skills` 和 `paperspine` 主要作为上游参考源，不要直接整仓 `pull` 到当前目录。
- 若需要同步上游，请先拉取上游，再按目录选择性更新对应 skill。

## Skills 总览

下面按用途把当前仓库中的主要 skills 列清楚，方便快速判断“该用哪个”。

### 1. 路由、规划与执行总控

| 目录 | 作用 |
|---|---|
| `zhongwen-zongkong` | 中文总控。中文开发任务的默认入口，负责路由、并行判断、技能链展示和收尾验证。 |
| `chinese-dev-guide` | 早期中文开发路由器，用于中文任务的目标重述和技能分发。 |
| `plan` | 通用规划 skill，适合先出方案、分步骤设计实现路径。 |
| `ralplan` | `plan` 的别名增强版，用于共识式规划。 |
| `ralph` | 持续执行型工作流，强调循环推进直到任务完成。 |
| `team` | 多工人编排 skill，适合长任务、多子任务、共享任务清单场景。 |
| `deep-interview` | 在执行前做深度追问和澄清，适合需求含糊、边界不清的任务。 |

### 2. 编码、重构与质量控制

| 目录 | 作用 |
|---|---|
| `karpathy-guidelines` | 卡帕西式编码准则，强调先想清楚、最小改动、可验证收尾。 |
| `ai-slop-cleaner` | 清理“AI 味过重”的实现，做去臃肿、去套娃、去冗余重构。 |
| `darwin-skill` | Skill 优化器，用于给 `SKILL.md` 打分、评审、迭代优化。 |
| `cancel` | 取消活动中的 OMX / 自动执行模式，快速停掉相关工作流。 |

### 3. Codex / 桌面环境诊断

| 目录 | 作用 |
|---|---|
| `codex-computer-use` | 修复 Codex Desktop 的 Computer Use、Any App、浏览器桥接等问题。 |
| `codex-session-restore` | 修复线程丢失、对话不显示、会话可见性异常等问题。 |
| `fix-codex-windows` | 修复 Windows 上 Codex 窗口透明、黑块、圆角残留等桌面显示问题。 |

### 4. 文档、研究与正式交付

| 目录 | 作用 |
|---|---|
| `document-formatting` | 中文文档排版总控，适合公文、报告、论文、PPT、表格等格式整理。 |
| `hv-analysis` | 横纵分析法，适合做产品、公司、概念或人物的系统性深度研究。 |
| `market-research` / `市场调研` | 市场调研与出海研究 skill，适合行业研究、国别进入、竞争格局和正式报告交付。 |
| `country-trade-guides` | 检索和引用本地 2025 国别贸易指南，用于 PDF 证据提取和国别对比。 |
| `graphify` | 将代码、文档、论文、图片等转成知识图谱、聚类结果和审计报告。 |

### 5. G 端、中台与经营判断

| 目录 | 作用 |
|---|---|
| `eyscrm_gend_codenav_skill` | G 端中台知识记忆与协同 skill，沉淀项目事实、红线、模板和组织语境。 |
| `easygr-perspective` | EasyGR 决策镜片，适合政府合作、区域起盘、闭环设计、协同边界和复盘判断。 |

### 6. 应用、爬取与浏览器能力

| 目录 | 作用 |
|---|---|
| `chatgpt-apps` | ChatGPT Apps SDK 开发与排障，适合 MCP 服务端 + Widget 类应用。 |
| `playwright` | 浏览器自动化 skill，适合页面操作、截图、抓取、UI 流程调试。 |
| `scrapling` | Scrapling 生态相关 skill，适合抓取、解析、MCP 配置和浏览器抓取场景。 |

### 7. 设计、图像与内容资产

| 目录 | 作用 |
|---|---|
| `ui-ux-pro-max` | UI/UX 设计增强 skill，适合网页、仪表盘、组件和视觉规范工作。 |
| `guizang-social-card-skill` | 社交卡片生成 skill，适合小红书图文、公众号封面、社媒轮播图。 |
| `hatch-pet` | Codex 宠物生成与封装，适合角色图、精灵图集、宠物包产出。 |
| `ppt-master` | PPT / SVG 内容生产系统，适合模板、页面、图形资产和多格式演示交付。 |

### 8. SEO 与网站诊断

| 目录 | 作用 |
|---|---|
| `seo-audit` | SEO 审计与诊断 skill，适合排查排名、索引、页面速度和技术 SEO 问题。 |

### 9. 人物 / 视角类能力入口

| 目录 | 作用 |
|---|---|
| `nuwa-skill` | 女娲造人入口，基于人物或需求蒸馏新的“人物视角 skill”。 |

### 10. PaperSpine 论文工作流家族

| 目录 | 作用 |
|---|---|
| `paper-spine` | PaperSpine 总入口，负责论文 / 报告端到端构建。 |
| `paper-spine-intake` | 收集配置、输入和写作参数。 |
| `paper-spine-research` | 做要求研究、材料下载和优秀样本学习。 |
| `paper-spine-build` | 基于材料直接生成论文或报告主体。 |
| `paper-spine-rewrite` | 对既有稿件做重写与结构重构。 |
| `paper-spine-citation` | 补参考文献与论据支撑。 |
| `paper-spine-latex` | 负责 LaTeX 装配、引用、图表和编译安全。 |
| `paper-spine-translate` | 负责整包中文翻译与逐行翻译交付。 |
| `paper-spine-humanize` | 做降 AI 痕迹改写。 |
| `paper-spine-audit` | 审计产物是否缺项、逻辑是否浅、证据是否不足。 |
| `paper-spine-ui` | 启动外部配置界面。 |
| `paper-spine-update` | 更新或重装 PaperSpine。 |

## 常见任务如何选 Skill

如果你不确定该调用哪个，可以直接按下面这张速查表判断：

| 任务类型 | 优先 skill | 常见组合 |
|---|---|---|
| 中文开发请求，不知道怎么开工 | `zhongwen-zongkong` | `zhongwen-zongkong` + `karpathy-guidelines` |
| 先出方案、路线图、分步骤执行计划 | `plan` | `zhongwen-zongkong` + `plan` |
| 需求模糊，需要先追问清楚 | `deep-interview` | `zhongwen-zongkong` + `deep-interview` |
| 普通代码实现、修 bug、做最小改动 | `karpathy-guidelines` | `zhongwen-zongkong` + `karpathy-guidelines` |
| 觉得代码太 AI、太啰嗦、太套娃 | `ai-slop-cleaner` | `karpathy-guidelines` + `ai-slop-cleaner` |
| 想优化一个 skill 自己的质量 | `darwin-skill` | `darwin-skill` 单独用，必要时再配 `karpathy-guidelines` |
| 需要多个 agent / worker 分工协作 | `team` | `zhongwen-zongkong` + `team` |
| 文档、公文、方案、Word/PDF/PPT 排版 | `document-formatting` | `zhongwen-zongkong` + `document-formatting` |
| 做行业研究、出海研究、正式报告 | `市场调研` | `zhongwen-zongkong` + `市场调研` |
| 做产品 / 公司 / 概念的系统深度研究 | `hv-analysis` | `zhongwen-zongkong` + `hv-analysis` |
| 需要从国别贸易 PDF 中找证据 | `country-trade-guides` | `市场调研` + `country-trade-guides` |
| 需要把资料整理成知识图谱 | `graphify` | `zhongwen-zongkong` + `graphify` |
| G 端、中台、项目协同知识调用 | `eyscrm_gend_codenav_skill` | `eyscrm_gend_codenav_skill` + `easygr-perspective` |
| 做政府合作判断、区域打法、协同闭环、项目复盘 | `easygr-perspective` | `eyscrm_gend_codenav_skill` + `easygr-perspective` |
| 做 ChatGPT Apps / MCP + Widget 应用 | `chatgpt-apps` | `chatgpt-apps` + `openai-docs`（若当前环境可见） |
| 浏览器自动化、抓页面、做截图 | `playwright` | `zhongwen-zongkong` + `playwright` |
| 网页抓取、HTML 解析、采集脚本 | `scrapling` | `zhongwen-zongkong` + `scrapling` |
| 设计网页、组件、仪表盘、视觉样式 | `ui-ux-pro-max` | `zhongwen-zongkong` + `ui-ux-pro-max` |
| 生成社交卡片、公众号封面、小红书图文 | `guizang-social-card-skill` | `guizang-social-card-skill` 单独用 |
| 生成宠物、角色 sprite、宠物包 | `hatch-pet` | `hatch-pet` + `imagegen`（若当前环境可见） |
| 做 PPT、SVG 模板、演示型图文产物 | `ppt-master` | `document-formatting` + `ppt-master` |
| 做 SEO 审计或排查排名问题 | `seo-audit` | `zhongwen-zongkong` + `seo-audit` |
| 论文、报告、比赛稿件端到端写作 | `paper-spine` | `paper-spine` + 其内部子 skill |
| 想生成某个人物的“思维方式 skill” | `nuwa-skill` | `nuwa-skill` 单独用 |
| Codex 桌面环境、线程、控制能力出了问题 | `codex-computer-use` / `codex-session-restore` / `fix-codex-windows` | 先选最贴近问题的那个 |

## 推荐组合

下面这些组合比较常用：

- 中文代码任务：
  `zhongwen-zongkong` + `karpathy-guidelines`
- 中文代码任务且需求不清：
  `zhongwen-zongkong` + `deep-interview` + `karpathy-guidelines`
- 文档 / 报告交付：
  `zhongwen-zongkong` + `document-formatting`
- 市场研究并要引用国别指南：
  `zhongwen-zongkong` + `市场调研` + `country-trade-guides`
- G 端方案或经营判断：
  `eyscrm_gend_codenav_skill` + `easygr-perspective`
- 复杂长任务需要多工人：
  `zhongwen-zongkong` + `team`
- 论文类正式产出：
  `paper-spine` + 对应子 skill

## 选择原则

- 如果是中文非平凡任务，默认先从 `zhongwen-zongkong` 开始。
- 如果任务核心是“怎么写代码 / 怎么做最小改动”，优先配 `karpathy-guidelines`。
- 如果任务核心是“出正式交付物”，优先看 `document-formatting`、`市场调研`、`ppt-master`、`paper-spine`。
- 如果任务核心是“做判断而不是搬资料”，优先看 `hv-analysis`、`easygr-perspective`、`eyscrm_gend_codenav_skill`。
- 如果任务核心是“需要自动操作网页或浏览器”，优先看 `playwright`。
- 如果任务核心是“需要多角色并行推进”，优先看 `team`。

## 更新注意事项

- 不要直接从 `openai-skills` 或 `paperspine` 对当前仓库执行整仓 `git pull`。
- 当前仓库是“本机已安装 skills 的聚合形态”，目录布局和上游仓库不完全一致。
- `.system` 内的内容只有在手工确认后再同步，避免把本机额外脚本或资源误覆盖掉。

## 更新后建议检查

```powershell
git status --short
Get-ChildItem -Path $env:USERPROFILE\.codex\skills -Recurse -Filter SKILL.md
```

每个 skill 目录下都应有可读的 `SKILL.md`，并且 front matter 至少包含：

- `name`
- `description`
