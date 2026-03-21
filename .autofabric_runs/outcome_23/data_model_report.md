# Data Model Report

## 1. 总体情况
- 模型数量：6
- 关系数量：5

## 2. 模型清单
### Goal (`goals`)
- 文件：`app/models/goal.py`
- `id` [PK]
- `raw_input`
- `parsed_goal`
- `goal_type`
- `risk_level`
- `created_at`
- `outcomes`

### Outcome (`outcomes`)
- 文件：`app/models/outcome.py`
- `id` [PK]
- `goal_id` [FK -> goals.id]
- `title`
- `status`
- `current_result`
- `next_action`
- `risk_boundary`
- `created_at`
- `updated_at`
- `goal`
- `executions`
- `artifacts`
- `verifications`
- `flow_events`

### Execution (`executions`)
- 文件：`app/models/execution.py`
- `id` [PK]
- `outcome_id` [FK -> outcomes.id]
- `executor_name`
- `task_name`
- `status`
- `input_payload`
- `output_payload`
- `started_at`
- `finished_at`
- `created_at`
- `outcome`

### Artifact (`artifacts`)
- 文件：`app/models/artifact.py`
- `id` [PK]
- `outcome_id` [FK -> outcomes.id]
- `artifact_type`
- `file_path`
- `artifact_ref`
- `artifact_metadata`
- `created_at`
- `outcome`

### Verification (`verifications`)
- 文件：`app/models/verification.py`
- `id` [PK]
- `outcome_id` [FK -> outcomes.id]
- `verifier_name`
- `status`
- `checks`
- `summary`
- `verified_at`
- `created_at`
- `outcome`

### FlowEvent (`flow_events`)
- 文件：`app/models/flow_event.py`
- `id` [PK]
- `outcome_id` [FK -> outcomes.id]
- `from_status`
- `to_status`
- `trigger_type`
- `note`
- `created_at`
- `outcome`

## 3. 关系清单
- `outcomes.goal_id` -> `goals.id`
- `executions.outcome_id` -> `outcomes.id`
- `artifacts.outcome_id` -> `outcomes.id`
- `verifications.outcome_id` -> `outcomes.id`
- `flow_events.outcome_id` -> `outcomes.id`

## 4. 数据结构结论
- 当前系统以 `goals` 为起点，以 `outcomes` 为执行中心。
- `executions`、`artifacts`、`verifications`、`flow_events` 都围绕 `outcomes` 展开。
- 这是一种典型的“目标 -> 结果 -> 执行证据/验证证据/流转记录”结构。

## 5. 下一步建议
- 为模型增加 ORM relationship，提升查询与序列化便利性。
- 输出实体关系图（ER 简图）。
- 将前端展示字段与后端模型字段建立映射。
