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
  - FastAPI 入口
  - health / goals / workspaces / outcomes / executors 等接口
- `app/services/execution_hint_builder.py`
  - 执行器建议构建逻辑
  - 已兼容 `dict / str` 混合输入
- `app/core/db.py`
  - 数据库连接
  - `get_db()`
- `app/models/goal.py`
- `app/models/outcome.py`
- `app/models/flow_event.py`

### 前端关键文件

- `frontend/src/App.jsx`
  - 主页面与主交互逻辑
- `frontend/src/components/WorkspaceList.jsx`
  - 左侧最近 Workspace 列表
- `frontend/src/components/WorkspaceSummary.jsx`
  - 右侧 Workspace 概览
- `frontend/src/components/ParsedGoalCard.jsx`
  - 解析结果卡片
- `frontend/src/components/workspaceUi.js`
  - badge / 文案 / 样式统一函数
- `frontend/src/adapters/workspaceAdapter.js`
  - 前端数据适配层，统一处理 `dict / str / null`

---

## 4. 运行前准备

### 4.1 PostgreSQL

确保本机 PostgreSQL 已启动，并存在数据库：

- database: `autofabric`

例如：

```bash
createdb autofabric