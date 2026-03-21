# API Report

## 1. 总体情况
- 入口文件：`app/main.py`
- 路由总数：1
- GET 数量：1
- POST 数量：0

## 2. 路由清单
- `GET /health` -> `health` (`app/main.py:35`)

## 3. 接口层结论
- 当前接口主要集中在 `app/main.py`，说明 API 还处于单入口集中式管理阶段。
- 当前系统同时具备查询型接口和执行型接口。
- `/entry/submit`、`/outcomes/.../execute`、`/outcomes/.../progress` 构成核心操作链。
- `/workspaces` 与 `/outcomes/{outcome_id}/timeline` 构成核心展示链。

## 4. 下一步建议
- 将 `app/main.py` 中的接口逐步拆分到 router 模块。
- 建立接口到 service 的映射表。
- 梳理前端调用哪些后端接口。
