from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


MODEL_FILES = [
    "app/models/goal.py",
    "app/models/outcome.py",
    "app/models/execution.py",
    "app/models/artifact.py",
    "app/models/verification.py",
    "app/models/flow_event.py",
]


def _parse_model_file(path: Path) -> dict[str, Any] | None:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        table_name = None
        fields: list[dict[str, Any]] = []

        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == "__tablename__":
                        if isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                            table_name = stmt.value.value

            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                field_name = stmt.target.id
                raw = ast.get_source_segment(source, stmt) or ""

                field_info = {
                    "name": field_name,
                    "raw": raw.strip(),
                    "primary_key": "primary_key=True" in raw,
                    "foreign_key": None,
                }

                if "ForeignKey(" in raw:
                    start = raw.find('ForeignKey("')
                    if start >= 0:
                        start += len('ForeignKey("')
                        end = raw.find('")', start)
                        if end > start:
                            field_info["foreign_key"] = raw[start:end]

                fields.append(field_info)

            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id
                        raw = ast.get_source_segment(source, stmt) or ""
                        if "Column(" in raw:
                            field_info = {
                                "name": field_name,
                                "raw": raw.strip(),
                                "primary_key": "primary_key=True" in raw,
                                "foreign_key": None,
                            }
                            if "ForeignKey(" in raw:
                                start = raw.find('ForeignKey("')
                                if start >= 0:
                                    start += len('ForeignKey("')
                                    end = raw.find('")', start)
                                    if end > start:
                                        field_info["foreign_key"] = raw[start:end]
                            fields.append(field_info)

        return {
            "class_name": node.name,
            "table_name": table_name,
            "fields": fields,
        }

    return None


def build_data_model_map(project_path: str) -> dict[str, Any]:
    root = Path(project_path).resolve()
    models: list[dict[str, Any]] = []
    relations: list[dict[str, Any]] = []

    for rel_path in MODEL_FILES:
        path = root / rel_path
        if not path.exists():
            continue

        parsed = _parse_model_file(path)
        if not parsed:
            continue

        parsed["file"] = rel_path
        models.append(parsed)

        table_name = parsed.get("table_name")
        for field in parsed.get("fields", []):
            fk = field.get("foreign_key")
            if fk:
                relations.append(
                    {
                        "from_table": table_name,
                        "from_field": field["name"],
                        "to": fk,
                    }
                )

    return {
        "project_path": str(root),
        "models": models,
        "relations": relations,
        "summary": {
            "model_count": len(models),
            "relation_count": len(relations),
        },
    }


def write_data_model_map(project_path: str, workspace_dir: str) -> str:
    data = build_data_model_map(project_path)
    path = Path(workspace_dir) / "data_model_map.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
