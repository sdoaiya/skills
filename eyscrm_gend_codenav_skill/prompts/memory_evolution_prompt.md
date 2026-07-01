# 记忆自我进化 Prompt

当用户给出新信息、纠正表达、确认最终版或删除某项时，执行：

1. 判断新信息属于长期记忆、项目状态、短期任务还是临时内容。
2. 长期记忆：写入 memory_bank。
3. 项目状态：写入 projects。
4. 临时内容：不写入长期记忆。
5. 任何更新都必须生成 MemoryUpdate：
   - date
   - category
   - operation
   - content
   - source
   - confidence
   - reason
6. 不允许编造未确认事实。
7. 不允许无痕覆盖旧内容，必须追加日志或标记 archived。
