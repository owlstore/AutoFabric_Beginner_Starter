createdb autofabric
# AutoFabric Beginner Starter - 运行说明

## 1. 项目目标

这是一个本地智能工作台 Demo，用于完成以下链路：

- 输入自然语言目标
- 后端解析目标，生成 Goal / Outcome / Action Panel
- 前端展示 Workspace 列表
- 点击 Workspace 查看详情
- 推进当前 Outcome
- 调用执行器（OpenClaw bridge 模式）
- 查看结果对象、目标对象与事件流状态

当前版本定位：

- 本地开发可运行
- 可演示主链路
- 可继续扩展
- 尚未进入生产级稳定版本

---

## 2. 当前主链路能力

当前系统已具备：

1. 创建 Workspace
2. 解析 Goal
3. 保存 Goal / Outcome
4. 展示最近 Workspace 列表
5. 点击 Workspace 切换右侧详情
6. 自动加载最近活跃 Workspace
7. 推进 Outcome 状态
8. 调用 OpenClaw 执行器
9. 展示执行结果、推荐原因、事件流等状态

---

## 3. 目录中的关键文件

### 后端关键文件

- `app/main.py`
- `app/services/execution_hint_builder.py`
- `app/core/db.py`
- `app/models/goal.py`
- `app/models/outcome.py`
- `app/models/flow_event.py`

### 前端关键文件

- `frontend/src/App.jsx`
- `frontend/src/components/WorkspaceList.jsx`
- `frontend/src/components/WorkspaceSummary.jsx`
- `frontend/src/components/ParsedGoalCard.jsx`
- `frontend/src/components/workspaceUi.js`
- `frontend/src/adapters/workspaceAdapter.js`

---

## 4. 运行前准备

### 4.1 PostgreSQL

确保本机 PostgreSQL 已启动，并存在数据库：

- database: `autofabric`

例如：

```bash
createdb autofabric