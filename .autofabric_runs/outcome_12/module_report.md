# Module Report

## 1. 总体结构
- 后端存在：是
- 前端存在：是
- 迁移系统存在：是
- 测试目录存在：是

## 2. 后端入口
- `app/main.py`
- `app/api/main.py`

## 3. 后端模块
- API 文件数：3
- Schema 文件数：10
- Service 文件数：31
- Executor 文件数：3
- Verifier 文件数：2
- Model 文件数：8
- DB 文件数：1
- Core 文件数：2

### 关键 Service
- `app/services/__init__.py`
- `app/services/action_executor.py`
- `app/services/action_panel_builder.py`
- `app/services/api_map_service.py`
- `app/services/api_report_service.py`
- `app/services/architecture_report_service.py`
- `app/services/data_model_map_service.py`
- `app/services/data_model_report_service.py`
- `app/services/execution_hint_builder.py`
- `app/services/execution_record_service.py`
- `app/services/executor_bootstrap.py`
- `app/services/executor_event_writer.py`

### Executors
- `app/executors/build_executor.py`
- `app/executors/openclaw_executor.py`
- `app/executors/understanding_executor.py`

### Verifiers
- `app/verifiers/docker_verifier.py`
- `app/verifiers/understanding_verifier.py`

### Models
- `app/models/artifact.py`
- `app/models/base.py`
- `app/models/entities.py`
- `app/models/execution.py`
- `app/models/flow_event.py`
- `app/models/goal.py`
- `app/models/outcome.py`
- `app/models/verification.py`

## 4. 前端模块
### 入口
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/index.html`

### API / Adapter
- `frontend/src/api/client.js`
- `frontend/src/adapters/workspaceAdapter.js`

### Components
- `frontend/src/components/ActionPanel.jsx`
- `frontend/src/components/EntryForm.jsx`
- `frontend/src/components/ExecutorPanel.jsx`
- `frontend/src/components/GoalsListPanel.jsx`
- `frontend/src/components/HeaderStatusBar.jsx`
- `frontend/src/components/OutcomesListPanel.jsx`
- `frontend/src/components/ParsedGoalCard.jsx`
- `frontend/src/components/StatusMessage.jsx`
- `frontend/src/components/WorkspaceDetails.jsx`
- `frontend/src/components/WorkspaceList.jsx`
- `frontend/src/components/WorkspaceSummary.jsx`
- `frontend/src/components/workspaceUi.js`

## 5. 模块级结论
- 当前项目已经形成后端、前端、执行器、验证器、服务编排、模型与数据库迁移的完整工程骨架。
- `services/` 是当前系统最核心的业务编排层。
- `executors/` 与 `verifiers/` 说明系统已经具备执行-校验双阶段机制。
- `frontend/src/components/` 表明前端工作台已按面板化结构组织。

## 6. 下一步建议
- 继续识别 FastAPI 路由与接口清单。
- 继续识别数据库实体关系。
- 建立前后端接口映射表。
- 输出正式架构图和逻辑流转图。
