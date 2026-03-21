# API Report

## 1. 总体情况
- 入口文件：`app/main.py`
- 路由总数：8
- GET 数量：5
- POST 数量：3

## 2. 路由清单
- `GET /artifacts` -> `list_artifacts` (`app/main.py:322`)
- `POST /entry/submit` -> `submit_entry` (`app/main.py:469`)
- `GET /executions` -> `list_executions` (`app/main.py:300`)
- `POST /outcomes/{outcome_id}/execute` -> `execute_outcome` (`app/main.py:597`)
- `POST /outcomes/{outcome_id}/progress` -> `progress_outcome` (`app/main.py:571`)
- `GET /outcomes/{outcome_id}/timeline` -> `get_outcome_timeline` (`app/main.py:366`)
- `GET /verifications` -> `list_verifications` (`app/main.py:344`)
- `GET /workspaces` -> `list_workspaces` (`app/main.py:522`)

## 3. 接口层结论
- 当前接口主要集中在 `app/main.py`，说明 API 还处于单入口集中式管理阶段。
- 当前系统同时具备查询型接口和执行型接口。
- `/entry/submit`、`/outcomes/.../execute`、`/outcomes/.../progress` 构成核心操作链。
- `/workspaces` 与 `/outcomes/{outcome_id}/timeline` 构成核心展示链。

## 4. 下一步建议
- 将 `app/main.py` 中的接口逐步拆分到 router 模块。
- 建立接口到 service 的映射表。
- 梳理前端调用哪些后端接口。
