# AutoFabric Beginner Starter

这是给 macOS + 本地 OpenClaw 用户准备的最小可运行起点。

## 你将得到什么
- FastAPI 后端骨架
- PostgreSQL（Docker/Colima）
- 最小 Rule Core / Outcome Control Layer 骨架
- OpenClaw 执行器接口预留
- 一键启动与验证脚本

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

## 本地 OpenClaw
默认通过环境变量 `OPENCLAW_BASE_URL` 读取，例如：
```bash
export OPENCLAW_BASE_URL=http://127.0.0.1:3000
```

如果你本地 OpenClaw 端口不是 3000，请改成自己的地址。
