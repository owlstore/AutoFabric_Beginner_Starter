from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any


HTTP_METHODS = {"get", "post", "put", "delete", "patch"}


def _extract_routes_from_file(path: Path, project_root: Path) -> list[dict[str, Any]]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    routes: list[dict[str, Any]] = []

    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue

        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue

            func = dec.func
            if not isinstance(func, ast.Attribute):
                continue

            method = func.attr.lower()
            if method not in HTTP_METHODS:
                continue

            if not isinstance(func.value, ast.Name):
                continue
            if func.value.id != "app":
                continue

            route_path = None
            if dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                route_path = dec.args[0].value

            routes.append(
                {
                    "method": method.upper(),
                    "path": route_path,
                    "handler": node.name,
                    "file": str(path.relative_to(project_root)),
                    "line": node.lineno,
                }
            )

    return routes


def build_api_map(project_path: str) -> dict[str, Any]:
    root = Path(project_path).resolve()
    main_file = root / "app/main.py"

    routes: list[dict[str, Any]] = []
    if main_file.exists():
        routes.extend(_extract_routes_from_file(main_file, root))

    routes = sorted(routes, key=lambda x: (x["path"] or "", x["method"], x["line"]))

    summary = {
        "total_routes": len(routes),
        "methods": {},
    }

    for route in routes:
        summary["methods"][route["method"]] = summary["methods"].get(route["method"], 0) + 1

    return {
        "project_path": str(root),
        "entry_file": "app/main.py" if main_file.exists() else None,
        "routes": routes,
        "summary": summary,
    }


def write_api_map(project_path: str, workspace_dir: str) -> str:
    data = build_api_map(project_path)
    path = Path(workspace_dir) / "api_map.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
