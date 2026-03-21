from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _rel_list(base: Path, pattern: str) -> list[str]:
    return sorted(
        str(p.relative_to(base))
        for p in base.glob(pattern)
        if p.is_file()
    )


def build_module_map(project_path: str) -> dict[str, Any]:
    root = Path(project_path).resolve()

    backend = {
        "entrypoints": [],
        "api_files": [],
        "schema_files": [],
        "service_files": [],
        "executor_files": [],
        "verifier_files": [],
        "model_files": [],
        "db_files": [],
        "core_files": [],
        "util_files": [],
    }

    frontend = {
        "entrypoints": [],
        "api_files": [],
        "adapter_files": [],
        "component_files": [],
        "config_files": [],
    }

    if (root / "app/main.py").exists():
        backend["entrypoints"].append("app/main.py")
    if (root / "app/api/main.py").exists():
        backend["entrypoints"].append("app/api/main.py")

    backend["api_files"] = _rel_list(root, "app/api/**/*.py")
    backend["schema_files"] = _rel_list(root, "app/schemas/**/*.py")
    backend["service_files"] = _rel_list(root, "app/services/**/*.py")
    backend["executor_files"] = _rel_list(root, "app/executors/**/*.py")
    backend["verifier_files"] = _rel_list(root, "app/verifiers/**/*.py")
    backend["model_files"] = _rel_list(root, "app/models/**/*.py")
    backend["db_files"] = _rel_list(root, "app/db/**/*.py")
    backend["core_files"] = _rel_list(root, "app/core/**/*.py")
    backend["util_files"] = _rel_list(root, "app/utils/**/*.py")

    if (root / "frontend/src/main.jsx").exists():
        frontend["entrypoints"].append("frontend/src/main.jsx")
    if (root / "frontend/src/App.jsx").exists():
        frontend["entrypoints"].append("frontend/src/App.jsx")
    if (root / "frontend/index.html").exists():
        frontend["entrypoints"].append("frontend/index.html")

    frontend["api_files"] = _rel_list(root, "frontend/src/api/**/*.js")
    frontend["adapter_files"] = _rel_list(root, "frontend/src/adapters/**/*.js")
    frontend["component_files"] = sorted(
        _rel_list(root, "frontend/src/components/**/*.js") +
        _rel_list(root, "frontend/src/components/**/*.jsx")
    )
    frontend["config_files"] = sorted(
        [
            p for p in [
                "frontend/package.json" if (root / "frontend/package.json").exists() else None,
                "frontend/vite.config.js" if (root / "frontend/vite.config.js").exists() else None,
                "frontend/src/config.js" if (root / "frontend/src/config.js").exists() else None,
            ] if p
        ]
    )

    return {
        "project_path": str(root),
        "architecture": {
            "backend_present": (root / "app").exists(),
            "frontend_present": (root / "frontend").exists(),
            "migration_present": (root / "alembic").exists(),
            "tests_present": (root / "tests").exists(),
        },
        "backend": backend,
        "frontend": frontend,
    }


def write_module_map(project_path: str, workspace_dir: str) -> str:
    data = build_module_map(project_path)
    path = Path(workspace_dir) / "module_map.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)