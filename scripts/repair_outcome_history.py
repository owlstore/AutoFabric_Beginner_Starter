from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.db import SessionLocal
from app.models.goal import Goal
from app.models.outcome import Outcome
from app.models.execution import Execution
from app.models.artifact import Artifact
from app.models.verification import Verification
from app.models.flow_event import FlowEvent


def ensure_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return {}
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def event_exists(events: list[FlowEvent], from_status: str | None, to_status: str, trigger_type: str) -> bool:
    for event in events:
        if (
            event.from_status == from_status
            and event.to_status == to_status
            and event.trigger_type == trigger_type
        ):
            return True
    return False


def main() -> None:
    db = SessionLocal()

    repaired_result_count = 0
    created_initial_event_count = 0
    created_completed_event_count = 0
    skipped_non_understanding_count = 0

    try:
        outcomes = db.execute(
            select(Outcome)
            .options(
                joinedload(Outcome.goal),
                joinedload(Outcome.executions),
                joinedload(Outcome.artifacts),
                joinedload(Outcome.verifications),
                joinedload(Outcome.flow_events),
            )
            .order_by(Outcome.id.asc())
        ).unique().scalars().all()

        for outcome in outcomes:
            goal = outcome.goal
            if not goal:
                continue

            if goal.goal_type != "system_understanding":
                skipped_non_understanding_count += 1
                continue

            current_result = ensure_dict(outcome.current_result)
            next_action = ensure_dict(outcome.next_action)

            artifact = outcome.artifacts[-1] if outcome.artifacts else None
            verification = outcome.verifications[-1] if outcome.verifications else None
            has_execution = len(outcome.executions) > 0
            events = sorted(outcome.flow_events, key=lambda x: x.id)

            if outcome.status == "completed":
                rebuilt = {
                    "stage": "analysis_context_collected",
                    "summary": "System understanding context collected.",
                }

                if artifact:
                    artifact_meta = ensure_dict(getattr(artifact, "artifact_metadata", None))
                    rebuilt["artifact"] = {
                        "ref": artifact.artifact_ref,
                        "type": artifact.artifact_type,
                        **artifact_meta,
                    }

                if verification:
                    verification_summary = ensure_dict(verification.summary)
                    rebuilt["verification"] = {
                        "status": verification.status,
                        **verification_summary,
                    }

                if current_result != rebuilt:
                    outcome.current_result = rebuilt
                    repaired_result_count += 1

                if not event_exists(events, None, "draft", "goal_created"):
                    db.add(
                        FlowEvent(
                            outcome_id=outcome.id,
                            from_status=None,
                            to_status="draft",
                            trigger_type="goal_created",
                            note="Initial outcome created.",
                        )
                    )
                    created_initial_event_count += 1

                if not event_exists(events, "draft", "completed", "execute_outcome") and has_execution:
                    db.add(
                        FlowEvent(
                            outcome_id=outcome.id,
                            from_status="draft",
                            to_status="completed",
                            trigger_type="execute_outcome",
                            note="Backfilled completed event.",
                        )
                    )
                    created_completed_event_count += 1

            elif outcome.status == "draft":
                expected = {
                    "stage": "goal_captured",
                    "summary": "Goal captured. Execution not started yet.",
                }
                if current_result != expected:
                    outcome.current_result = expected
                    repaired_result_count += 1

                if not event_exists(events, None, "draft", "goal_created"):
                    db.add(
                        FlowEvent(
                            outcome_id=outcome.id,
                            from_status=None,
                            to_status="draft",
                            trigger_type="goal_created",
                            note="Initial outcome created.",
                        )
                    )
                    created_initial_event_count += 1

            if isinstance(next_action, dict):
                outcome.next_action = json.dumps(next_action, ensure_ascii=False)

            db.add(outcome)

        db.commit()

        print("=== repair summary ===")
        print(f"repaired_result_count={repaired_result_count}")
        print(f"created_initial_event_count={created_initial_event_count}")
        print(f"created_completed_event_count={created_completed_event_count}")
        print(f"skipped_non_understanding_count={skipped_non_understanding_count}")
        print("repair done")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
