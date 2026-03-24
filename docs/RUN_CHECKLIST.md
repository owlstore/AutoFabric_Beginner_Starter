# AutoFabric 运行检查清单

## 后端
- [ ] `.venv` 已激活
- [ ] `curl http://127.0.0.1:8000/health` 返回 `status: ok`

## 数据库
- [ ] PostgreSQL 已启动
- [ ] `pg_isready -h localhost -p 5432` 正常
- [ ] `alembic_version` 表可查询

## Docker
- [ ] `docker compose ps` 显示 `autofabric-app` 为 Up
- [ ] 容器环境变量已注入

## 前端
- [ ] `npm run dev` 已启动
- [ ] 浏览器可打开 `http://localhost:5173/`
- [ ] “开始推进”按钮可正常使用
- [ ] Action Panel 可执行动作
- [ ] 最近 Workspace 列表可切换
- [ ] 目标对象列表 / 结果对象列表可加载

## 关键联调
- [ ] 可以创建新的 Workspace
- [ ] 可以推进 Outcome
- [ ] 可以调用 OpenClaw 执行器
- [ ] 可以在页面看到最近执行结果
