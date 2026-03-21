# Architecture Report

## 1. 系统总体定位
- 项目路径：`/Users/kim/Desktop/AutoFabric_Beginner_Starter`
- 目标：Analyze this order dashboard service
- 系统类型：`fullstack_engineering_project`
- 架构判断：全栈工程化项目（FastAPI 后端 + Vite/React 前端）

## 2. 后端架构
- 运行入口：`app/main.py`
- API 数量：0
- Service 文件数：34
- Executor 文件数：3
- Verifier 文件数：2
- Model 文件数：9

### 后端关键特征
- 当前接口集中在 `app/main.py`，属于单入口集中式 API 管理。
- `services/` 是业务编排中心。
- `executors/` 与 `verifiers/` 形成执行-校验双阶段机制。
- `models/` + `alembic/` 说明数据层已具备迁移和实体抽象基础。

## 3. 前端架构
- 前端入口数量：3
- 组件数量：12
- API/Adapter 文件数量：2

### 前端关键特征
- 前端以工作台面板结构组织。
- 已存在 API client 与 adapter，说明前后端交互已开始分层。
- 组件命名围绕 workspace / goal / outcome / executor 展开。

## 4. 主业务链路
1. 用户提交目标到 `/entry/submit`。
2. 系统创建 `Goal` 和初始 `Outcome`。
3. 用户执行 `/outcomes/{outcome_id}/execute`。
4. 系统调用 executor 生成 artifact。
5. verifier 执行校验并沉淀 verification。
6. `/workspaces` 与 `/outcomes/{outcome_id}/timeline` 展示结果。

## 5. 数据模型关系
- 模型数量：6
- 关系数量：5
- `outcomes.goal_id` -> `goals.id`
- `executions.outcome_id` -> `outcomes.id`
- `artifacts.outcome_id` -> `outcomes.id`
- `verifications.outcome_id` -> `outcomes.id`
- `flow_events.outcome_id` -> `outcomes.id`

## 6. 当前架构优势
- 已形成从目标、执行、产物、验证到展示的完整闭环。
- 已具备多层理解能力，可自动生成项目/模块/API/数据模型报告。
- 执行与校验职责已拆分，为后续接入真实 Agent/Worker 奠定基础。

## 7. 当前薄弱点
- API 仍集中在 `app/main.py`，需要 router 化。
- ORM relationship 尚未补齐。
- 前后端接口映射尚未自动建立。
- understanding 目前偏静态扫描，尚未做到更深层语义分析。

## 8. 下一步建议
- 拆分 API router。
- 为模型补充 relationship。
- 自动生成前后端接口映射表。
- 接入更真实的执行器与分析器。
