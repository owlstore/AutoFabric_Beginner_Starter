from __future__ import annotations

from pathlib import Path


def build_entity_relation(workspace_dir: str) -> str:
    workspace = Path(workspace_dir)

    content = (
        "# Entity Relation\n\n"
        "```mermaid\n"
        "erDiagram\n"
        "    GOALS ||--o{ OUTCOMES : has\n"
        "    OUTCOMES ||--o{ EXECUTIONS : has\n"
        "    OUTCOMES ||--o{ ARTIFACTS : has\n"
        "    OUTCOMES ||--o{ VERIFICATIONS : has\n"
        "    OUTCOMES ||--o{ FLOW_EVENTS : has\n\n"
        "    GOALS {\n"
        "        int id PK\n"
        "        text raw_input\n"
        "        jsonb parsed_goal\n"
        "        string goal_type\n"
        "        string risk_level\n"
        "        datetime created_at\n"
        "    }\n\n"
        "    OUTCOMES {\n"
        "        int id PK\n"
        "        int goal_id FK\n"
        "        string title\n"
        "        string status\n"
        "        jsonb current_result\n"
        "        text next_action\n"
        "        text risk_boundary\n"
        "        datetime created_at\n"
        "        datetime updated_at\n"
        "    }\n\n"
        "    EXECUTIONS {\n"
        "        int id PK\n"
        "        int outcome_id FK\n"
        "        string executor_name\n"
        "        string task_name\n"
        "        string status\n"
        "    }\n\n"
        "    ARTIFACTS {\n"
        "        int id PK\n"
        "        int outcome_id FK\n"
        "        string artifact_type\n"
        "        text file_path\n"
        "        text artifact_ref\n"
        "    }\n\n"
        "    VERIFICATIONS {\n"
        "        int id PK\n"
        "        int outcome_id FK\n"
        "        string verifier_name\n"
        "        string status\n"
        "    }\n\n"
        "    FLOW_EVENTS {\n"
        "        int id PK\n"
        "        int outcome_id FK\n"
        "        string from_status\n"
        "        string to_status\n"
        "        string trigger_type\n"
        "    }\n"
        "```\n"
    )

    path = workspace / "entity_relation.md"
    path.write_text(content, encoding="utf-8")
    return str(path)
