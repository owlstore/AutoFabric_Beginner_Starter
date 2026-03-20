from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

# 让脚本可从项目根目录直接运行
ROOT = Path(__file__).resolve().parent.parent
import sys
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.models.goal import Goal
from app.models.outcome import Outcome


def parse_json_like(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def normalize_next_action(value: Any) -> dict[str, Any]:
    parsed = parse_json_like(value)

    if isinstance(parsed, dict):
        return {
            "summary": parsed.get("summary") or "Pending next action.",
            "step_type": parsed.get("step_type"),
            "steps": parsed.get("steps") if isinstance(parsed.get("steps"), list) else [],
            "requires_human_confirmation": bool(parsed.get("requires_human_confirmation", False)),
        }

    if isinstance(parsed, str):
        text = parsed.strip()
        return {
            "summary": text or "Pending next action.",
            "step_type": None,
            "steps": [],
            "requires_human_confirmation": False,
        }

    return {
        "summary": "Pending next action.",
        "step_type": None,
        "steps": [],
        "requires_human_confirmation": False,
    }


def normalize_parsed_goal(value: Any) -> dict[str, Any]:
    parsed = parse_json_like(value)

    if not isinstance(parsed, dict):
        parsed = {}

    parser_meta = parsed.get("parser_meta")
    if not isinstance(parser_meta, dict):
        parser_meta = {
            "source": "legacy",
            "llm_enabled": None,
        }
    else:
        parser_meta.setdefault("source", "legacy")
        parser_meta.setdefault("llm_enabled", None)

    parsed["parser_meta"] = parser_meta
    return parsed


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("缺少 DATABASE_URL 环境变量，请先 export DATABASE_URL=...")

    engine = create_engine(database_url, future=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    goal_updated = 0
    outcome_updated = 0

    with SessionLocal() as db:
        assert isinstance(db, Session)

        goals = db.execute(select(Goal)).scalars().all()
        for goal in goals:
            old_value = goal.parsed_goal
            new_value = normalize_parsed_goal(old_value)

            if old_value != new_value:
                goal.parsed_goal = new_value
                goal_updated += 1

        outcomes = db.execute(select(Outcome)).scalars().all()
        for outcome in outcomes:
            old_value = outcome.next_action
            new_obj = normalize_next_action(old_value)

            # 统一存成 JSON 字符串，兼容你当前项目的历史存储方式
            new_value = json.dumps(new_obj, ensure_ascii=False)

            if old_value != new_value:
                outcome.next_action = new_value
                outcome_updated += 1

        db.commit()

    print("数据归一化完成")
    print(f"Goals updated: {goal_updated}")
    print(f"Outcomes updated: {outcome_updated}")


if __name__ == "__main__":
    main()