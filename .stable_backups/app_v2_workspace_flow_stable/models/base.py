"""
兼容层：统一给模型提供 Base。
优先复用项目里已经存在的 Base，避免大范围改历史模型。
"""

try:
    from app.db.database import Base  # 常见位置
except Exception:
    try:
        from app.core.db import Base  # 兼容另一套目录
    except Exception as exc:
        raise ImportError(
            "无法从 app.db.database 或 app.core.db 导入 Base，请检查现有数据库定义。"
        ) from exc
