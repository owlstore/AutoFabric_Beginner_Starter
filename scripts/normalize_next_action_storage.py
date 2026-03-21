from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from app.core.db import SessionLocal
from app.models.outcome import Outcome


def main() -> None:
    db = SessionLocal()
    updated = 0

    try:
        outcomes = db.execute(select(Outcome).order_by(Outcome.id.asc())).scalars().all()
        for outcome in outcomes:
            if isinstance(outcome.next_action, dict):
                outcome.next_action = json.dumps(outcome.next_action, ensure_ascii=False)
                db.add(outcome)
                updated += 1

        db.commit()
        print("=== normalize next_action summary ===")
        print(f"updated={updated}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
