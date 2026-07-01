# eyscrm_gend_codenav_skill

这是一个面向 Codex / AI Agent 的本地知识 Skill 包，用于沉淀并调用 G端中台、优品库、AI试点、产业带下沉、政府项目、文档风格、风险红线等上下文。

## 适合场景

- 生成政府汇报方案
- 生成培训/活动方案
- 生成合作谈判思路
- 生成合同/报价/考核指标
- 设计 WPS 多维表格字段
- 设计 Codex 自动化任务
- 维护项目记忆与版本演进

## 快速开始

```bash
cd eyscrm_gend_codenav_skill
python scripts/skill_cli.py search "优品库"
python scripts/skill_cli.py list-projects
python scripts/skill_cli.py export-context --task "生成AI试点专项小组分工表"
```

## 重要说明

本包为本地结构化知识包，不直接连接 WPS、Gmail、CRM 或销售工具包。需要 Codex 另行开发适配器。
