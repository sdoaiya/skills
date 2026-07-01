# Codex 集成说明

## 推荐接入方式

1. 将本目录放入 Codex 项目根目录，例如：

```text
your-codex-project/
├── skills/
│   └── eyscrm_gend_codenav_skill/
└── src/
```

2. 在 Codex 任务中加入前置提示：

```text
请先读取 skills/eyscrm_gend_codenav_skill/SKILL.md，并调用 data/memory_bank.json、data/projects.json 作为业务上下文。
```

3. 在需要检索时调用：

```bash
python skills/eyscrm_gend_codenav_skill/scripts/skill_cli.py search "关键词"
```

4. 在完成任务后，如果用户确认了新规则，生成 MemoryUpdate 并追加：

```bash
python skills/eyscrm_gend_codenav_skill/scripts/skill_cli.py update --file update.json
```

## 数据共享建议

- 与 WPS 多维表格共享：新增 connectors/wps_adapter.py；
- 与销售工具包共享：新增 connectors/sales_toolkit_adapter.py；
- 与CRM共享：新增 connectors/crm_adapter.py；
- 与本地文件共享：将项目方案、合同、台账导入 `data/external_index/` 并生成索引。

## 自我进化建议

- 小更新：追加到 `_memory_updates` 和 `logs/evolution_log.md`；
- 大更新：新建 `data/memory_bank.vX.json`；
- 重大规则变更：同步修改 `SKILL.md`；
- 废弃内容：标记 archived，不直接删除。
