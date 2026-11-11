# 设置事务：两轮独立配对

原创 Python 小游戏设置持久化任务，模拟数据/回调所有权、先持久化再提交、失败恢复与重入拒绝；不是商业生产任务的代表性样本。input、要求与完整 grader 在派发前冻结，protocol.json 保留 hash。原始无修复输入的共同检查全部失败，阴性结果见 negative-results.json。

```text
python tools/repeated_eval.py prepare --output "新的试验目录" --repetitions 2
python tools/repeated_eval.py grade --artifacts "试验目录" --output "新的验收目录" --metadata "本轮元数据.json"
```

需用独立新上下文完成每组任务，同一模型/工具、相同原始输入，A 不读自定义技能，B 按需读指定技能。不要把 grader、其他组产物或旧结论提供给代理。工具不自行调用模型，不产生模型账单。

本次 outputs 中是四份真实修改与脱敏自测/审查记录，不含原始主机日志。使用 --artifacts evals/transactions/outputs --metadata evals/transactions/run-metadata.json 可复验历史产物；不要将历史模型/技能/返工信息套在新实验上。未提供本轮 metadata 则模型、技能和返工保持未验证/未知；缺失费用保持 null。

两轮 B 使用 0.4.0-preview；没有评估新增 0.5 工具。两轮交替派发顺序，组内并发，父级也在执行其他工作；计时包含阅读、自测、文档、等待和主机负载，不是纯模型耗时。实际结果见 ../../docs/transactions-results.json，解释见 ../../docs/PAIRED-EVALUATION.md。
