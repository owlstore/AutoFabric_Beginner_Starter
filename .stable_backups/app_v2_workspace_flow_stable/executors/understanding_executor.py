from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.understanding_report_service import build_understanding_report
from app.services.module_map_service import write_module_map
from app.services.module_report_service import build_module_report
from app.services.api_map_service import write_api_map
from app.services.api_report_service import build_api_report
from app.services.data_model_map_service import write_data_model_map
from app.services.data_model_report_service import build_data_model_report
from app.services.architecture_report_service import build_architecture_report
from app.services.system_diagram_service import build_system_diagram
from app.services.entity_relation_service import build_entity_relation
from app.services.integration_map_service import write_integration_map
from app.services.integration_report_service import build_integration_report


TEXT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".md", ".yml", ".yaml",
    ".toml", ".ini", ".sh", ".sql", ".html", ".css"
}

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".autofabric_runs",
}

IGNORE_FILE_SUFFIXES = {
    ".pyc",
    ".bak",
    ".backup",
}

IGNORE_FILE_NAMES = {
    ".DS_Store",
}


def _should_skip(path: Path, root: Path) -> bool:
    rel_parts = path.relative_to(root).parts
    if any(part in IGNORE_DIRS for part in rel_parts):
        return True
    if path.name in IGNORE_FILE_NAMES:
        return True
    if any(path.name.endswith(suffix) for suffix in IGNORE_FILE_SUFFIXES):
        return True
    return False


def _collect_top_level(root: Path) -> dict[str, list[str]]:
    files: list[str] = []
    dirs: list[str] = []

    for p in sorted(root.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if p.name in IGNORE_DIRS or p.name in IGNORE_FILE_NAMES:
            continue
        if p.is_dir():
            dirs.append(p.name)
        else:
            if any(p.name.endswith(suffix) for suffix in IGNORE_FILE_SUFFIXES):
                continue
            files.append(p.name)

    return {"files": files, "dirs": dirs}


def _detect_markers(root: Path) -> dict[str, bool]:
    markers = [
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "app",
        "src",
        "pages",
        "components",
        "api",
        "frontend",
        "alembic",
        "tests",
    ]
    result: dict[str, bool] = {}
    for name in markers:
        result[name] = (root / name).exists()
    return result


def _collect_code_files(root: Path, max_files: int = 30) -> list[str]:
    found: list[str] = []

    for path in root.rglob("*"):
        if len(found) >= max_files:
            break
        if not path.is_file():
            continue
        if _should_skip(path, root):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS:
            found.append(str(path.relative_to(root)))

    return found


def _infer_system_type(markers: dict[str, bool]) -> str:
    if markers.get("app") and markers.get("frontend"):
        return "fullstack_engineering_project"
    if markers.get("package.json") and (markers.get("pages") or markers.get("components") or markers.get("src")):
        return "frontend_or_node_service"
    if markers.get("requirements.txt") or markers.get("pyproject.toml") or markers.get("app"):
        return "python_service"
    return "unknown"


def run_understanding_executor(goal_text: str, outcome_id: int, project_path: str = ".") -> dict[str, Any]:
    root = Path(project_path).resolve()
    artifact_dir = Path(f".autofabric_runs/outcome_{outcome_id}")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    top_level = _collect_top_level(root)
    markers = _detect_markers(root)
    code_files = _collect_code_files(root)
    system_type = _infer_system_type(markers)

    summary = {
        "goal_text": goal_text,
        "project_path": str(root),
        "system_type": system_type,
        "top_level": top_level,
        "markers": markers,
        "code_files": code_files,
    }

    summary_path = artifact_dir / "analysis_summary.json"
    tree_path = artifact_dir / "tree.txt"

    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    tree_lines: list[str] = []
    for d in top_level["dirs"]:
        tree_lines.append(f"[DIR]  {d}")
    for f in top_level["files"]:
        tree_lines.append(f"[FILE] {f}")
    tree_path.write_text("\n".join(tree_lines), encoding="utf-8")

    report_path = build_understanding_report(
        outcome_id=outcome_id,
        workspace_dir=str(artifact_dir),
    )
    module_map_path = write_module_map(
        project_path=str(root),
        workspace_dir=str(artifact_dir),
    )
    module_report_path = build_module_report(
        workspace_dir=str(artifact_dir),
    )
    api_map_path = write_api_map(
        project_path=str(root),
        workspace_dir=str(artifact_dir),
    )
    api_report_path = build_api_report(
        workspace_dir=str(artifact_dir),
    )
    data_model_map_path = write_data_model_map(
        project_path=str(root),
        workspace_dir=str(artifact_dir),
    )
    data_model_report_path = build_data_model_report(
        workspace_dir=str(artifact_dir),
    )
    architecture_report_path = build_architecture_report(
        workspace_dir=str(artifact_dir),
    )
    system_diagram_path = build_system_diagram(
        workspace_dir=str(artifact_dir),
    )
    entity_relation_path = build_entity_relation(
        workspace_dir=str(artifact_dir),
    )
    integration_map_path = write_integration_map(
        project_path=str(root),
        workspace_dir=str(artifact_dir),
    )
    integration_report_path = build_integration_report(
        workspace_dir=str(artifact_dir),
    )

    return {
        "executor_name": "system_understanding_worker",
        "task_name": "collect_system_context",
        "status": "completed",
        "input_payload": {
            "target": goal_text,
            "project_path": str(root),
            "workspace_dir": str(artifact_dir),
        },
        "output_payload": {
            "returncode": 0,
            "workspace_dir": str(artifact_dir),
            "summary_path": str(summary_path),
            "tree_path": str(tree_path),
            "report_path": str(report_path),
            "module_map_path": str(module_map_path),
            "module_report_path": str(module_report_path),
            "api_map_path": str(api_map_path),
            "api_report_path": str(api_report_path),
            "data_model_map_path": str(data_model_map_path),
            "data_model_report_path": str(data_model_report_path),
            "architecture_report_path": str(architecture_report_path),
            "system_diagram_path": str(system_diagram_path),
            "entity_relation_path": str(entity_relation_path),
            "integration_map_path": str(integration_map_path),
            "integration_report_path": str(integration_report_path),
            "message": "System understanding context collected.",
        },
        "artifact": {
            "artifact_type": "analysis_context",
            "file_path": str(artifact_dir),
            "artifact_ref": f"understanding-context-{outcome_id}",
            "artifact_metadata": {
                "workspace_dir": str(artifact_dir),
                "summary_path": str(summary_path),
                "tree_path": str(tree_path),
                "report_path": str(report_path),
                "module_map_path": str(module_map_path),
                "module_report_path": str(module_report_path),
                "api_map_path": str(api_map_path),
                "api_report_path": str(api_report_path),
                "data_model_map_path": str(data_model_map_path),
                "data_model_report_path": str(data_model_report_path),
                "architecture_report_path": str(architecture_report_path),
                "system_diagram_path": str(system_diagram_path),
                "entity_relation_path": str(entity_relation_path),
                "integration_map_path": str(integration_map_path),
                "integration_report_path": str(integration_report_path),
                "collected": True,
                "system_type": system_type,
            },
        },
        "current_result": {
            "stage": "analysis_context_collected",
            "summary": f"System understanding context collected. Detected system_type={system_type}.",
            "artifact": {
                "ref": f"understanding-context-{outcome_id}",
                "type": "analysis_context",
                "workspace_dir": str(artifact_dir),
                "summary_path": str(summary_path),
                "report_path": str(report_path),
                "module_map_path": str(module_map_path),
                "module_report_path": str(module_report_path),
                "api_map_path": str(api_map_path),
                "api_report_path": str(api_report_path),
                "data_model_map_path": str(data_model_map_path),
                "data_model_report_path": str(data_model_report_path),
                "architecture_report_path": str(architecture_report_path),
                "system_diagram_path": str(system_diagram_path),
                "entity_relation_path": str(entity_relation_path),
                "integration_map_path": str(integration_map_path),
                "integration_report_path": str(integration_report_path),
            },
        },
    }
