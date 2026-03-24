# AutoFabric Beginner Starter

这是给 macOS + 本地 OpenClaw 用户准备的最小可运行起点。

## 你将得到什么
- FastAPI 后端骨架
- PostgreSQL（Docker/Colima）
- 最小 Rule Core / Outcome Control Layer 骨架
- OpenClaw 执行器接口预留
- 一键启动与验证脚本
- Manus-like autopilot 工作台与统一 mission API

## 最快启动
```bash
cd AutoFabric_Beginner_Starter
bash scripts/00_bootstrap_macos.sh
bash scripts/01_init_project.sh
bash scripts/02_run_local.sh
bash scripts/03_verify_local.sh
```

## 访问地址
- API 文档: http://127.0.0.1:8000/docs
- 健康检查: http://127.0.0.1:8000/health

## 统一入口（推荐）
为避免“页面改了但你看到没变化”的问题，请统一使用下面的一键命令：
```bash
npm run dev:up
```
然后只访问这一个地址：
- 主工作台: http://127.0.0.1:5173

辅助命令：
```bash
npm run dev:status
npm run dev:down
npm run dev:where
```

## 全链路自动验收（E2E Gate）
启动服务后可直接执行一键门禁：
```bash
npm run gate:e2e
```

脚本会自动完成：创建项目 -> 导入需求 -> 澄清问答 -> 规格/原型 -> 编排/下发 -> 运行态推进 -> 产物/代码包/验证/交付，并输出：
- `runtime/gate_runs/.../gate_report.md`
- `runtime/gate_runs/.../gate_result.json`

可选环境变量：
```bash
RUN_ID=demo01 MAX_SIM_ROUNDS=30 REQUIREMENT_TEXT="做一个任务看板系统" npm run gate:e2e
```

如果要一次验证三套标准模板，可直接执行：
```bash
npm run gate:templates
```

矩阵门禁当前覆盖：
- `order_admin`
- `task_kanban`
- `tool_web_app`

矩阵结果会输出：
- `runtime/gate_runs/template_kit_matrix_.../matrix_report.md`
- `runtime/gate_runs/template_kit_matrix_.../matrix_result.json`

前端 E2E 也拆成了两档：
```bash
npm run frontend:e2e:smoke
npm run frontend:e2e:fullflow
```

- `smoke`：页面结构与基础交互，适合门禁和矩阵验收
- `fullflow`：真实输入需求到看到交付结果，适合单独回归 UI 全链路

## 前端启动（单独）
如果只想启动主前端：
```bash
npm run frontend:dev
```

`quark-browser` 仅作为备用实验前端，不作为默认工作台入口。

## 本地 OpenClaw
默认通过环境变量 `OPENCLAW_BASE_URL` 读取，例如：
```bash
export OPENCLAW_BASE_URL=http://127.0.0.1:3000
```

如果你本地 OpenClaw 端口不是 3000，请改成自己的地址。

## Manus Autopilot API
新增统一入口后，可以直接通过下面三个接口驱动整条多阶段流水线：

- `POST /manus/projects/bootstrap`
- `GET /manus/projects/{project_id}/workspace`
- `POST /manus/projects/{project_id}/autopilot`

如果本地没有配置 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`，系统会自动退回 `mock` provider，保证需求分析、原型、编排、执行、测试和交付这条演示链路仍然可跑。
