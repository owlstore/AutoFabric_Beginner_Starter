# RUN CHECKLIST

## 启动前
- [ ] 已进入项目根目录 `~/Desktop/AutoFabric_Beginner_Starter`
- [ ] 使用 Python 3.13 虚拟环境
- [ ] PostgreSQL 已启动
- [ ] `DATABASE_URL` 已设置为本地 autofabric 数据库

## 启动后端
```bash
cd ~/Desktop/AutoFabric_Beginner_Starter
source .venv/bin/activate
export DATABASE_URL=postgresql+psycopg://kim@localhost:5432/autofabric
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000