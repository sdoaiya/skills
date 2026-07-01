# Codex 使用示例

## 示例1：搜索AI试点上下文

```bash
python scripts/skill_cli.py search "AI试点"
```

## 示例2：导出任务上下文

```bash
python scripts/skill_cli.py export-context --task "生成山东AI外贸赋能工具应用试点专项小组分工表"
```

## 示例3：追加记忆

创建 `update.json`：

```json
{
  "date": "2026-06-24",
  "category": "middle_office_work_ai",
  "operation": "revise",
  "content": {
    "staffing": "保留1名中台，Codex承担数据整理、台账同步、话术生成、归档提醒。"
  },
  "source": "用户确认",
  "confidence": "confirmed",
  "reason": "用户明确要求后续按该组织配置设计自动化方案"
}
```

执行：

```bash
python scripts/skill_cli.py update --file update.json
```

## 示例4：接入WPS多维表格的建议

Codex 可新增 `connectors/wps_adapter.py`，实现：

- read_table(table_id)
- upsert_record(table_id, record)
- diff_records(old, new)
- push_change_to_sales_toolkit(record)
- write_audit_log(change)
