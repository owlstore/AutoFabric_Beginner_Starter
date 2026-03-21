from __future__ import annotations

from pathlib import Path


def build_system_diagram(workspace_dir: str) -> str:
    workspace = Path(workspace_dir)

    content = (
        "# System Diagram\n\n"
        "## 1. 系统模块图\n\n"
        "```mermaid\n"
        "flowchart LR\n"
        "    User[User]\n"
        "    FE[Frontend Workspace UI]\n"
        "    API[FastAPI app/main.py]\n"
        "    Services[Services Layer]\n"
        "    Executors[Executors]\n"
        "    Verifiers[Verifiers]\n"
        "    Models[SQLAlchemy Models]\n"
        "    DB[(PostgreSQL)]\n"
        "    Reports[Understanding Reports]\n\n"
        "    User --> FE\n"
        "    FE --> API\n"
        "    API --> Services\n"
        "    Services --> Executors\n"
        "    Services --> Verifiers\n"
        "    Services --> Models\n"
        "    Models --> DB\n"
        "    Services --> Reports\n"
        "```\n\n"
        "## 2. 主流程图\n\n"
        "```mermaid\n"
        "flowchart TD\n"
        "    A[Submit Goal] --> B[Create Goal]\n"
        "    B --> C[Create Outcome]\n"
        "    C --> D[Execute Outcome]\n"
        "    D --> E[Run Executor]\n"
        "    E --> F[Create Artifact]\n"
        "    F --> G[Run Verifier]\n"
        "    G --> H[Create Verification]\n"
        "    H --> I[Update Outcome]\n"
        "    I --> J[Workspace / Timeline Display]\n"
        "```\n"
    )

    path = workspace / "system_diagram.md"
    path.write_text(content, encoding="utf-8")
    return str(path)
