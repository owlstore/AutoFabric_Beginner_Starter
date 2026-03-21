from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.db import SessionLocal
from app.models.outcome import Outcome


def main() -> None:
    db = SessionLocal()
    try:
        outcome = db.get(Outcome, 1)
        if not outcome:
            print("outcome_id=1 not found")
            return

        outcome.status = "completed"
        outcome.current_result = {
            "stage": "verification_completed",
            "summary": "Keep completed.",
            "artifact": {
                "type": "docker_image",
                "image_tag": "autofabric-outcome-1:latest",
                "artifact_dir": ".autofabric_runs/outcome_1",
            },
            "verification": {
                "status": "passed",
                "image_tag": "autofabric-outcome-1:latest",
            },
        }
        outcome.next_action = """{
  "summary": "Verification passed. The outcome is ready.",
  "step_type": "completed",
  "steps": [
    "Review execution evidence.",
    "Review artifact metadata.",
    "Review verification result."
  ],
  "requires_human_confirmation": false
}"""
        outcome.risk_boundary = "Local only"

        db.add(outcome)
        db.commit()
        db.refresh(outcome)

        print("fixed outcome_id=1")
        print(f"status={outcome.status}")
        print(f"current_result={outcome.current_result}")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
