from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


IMPORT_RE = re.compile(
    r"""import\s+.*?\s+from\s+["'](?P<path>\.[^"']+)["']"""
)

JS_EXTS = {".js", ".jsx", ".ts", ".tsx"}

# 匹配：
# fetch(`${API_BASE}/workspaces`)
# fetch(`${API_BASE}/workspace/${goalId}`, { method: "POST" })
# fetch("/workspaces")
FETCH_CALL_RE = re.compile(
    r'''fetch\(\s*(?P<url>`[^`]+`|["'][^"']+["'])\s*(?:,\s*(?P<options>\{.*?\}))?\s*\)''',
    re.S,
)

METHOD_RE = re.compile(r'''method\s*:\s*["'](?P<method>GET|POST|PUT|DELETE|PATCH)["']''', re.I)

# 匹配 axios.get("/x") / client.post("/x")
DIRECT_CLIENT_RE = re.compile(
    r'''(?P<client>axios|client)\.(?P<method>get|post|put|delete|patch)\(\s*(?P<url>`[^`]+`|["'][^"']+["'])''',
    re.I,
)

TEMPLATE_API_BASE_PREFIX_RE = re.compile(r'^\$\{API_BASE\}')
TEMPLATE_VAR_RE = re.compile(r'\$\{([^}]+)\}')


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _find_frontend_files(root: Path) -> list[Path]:
    frontend_src = root / "frontend" / "src"
    if not frontend_src.exists():
        return []

    results: list[Path] = []
    for p in frontend_src.rglob("*"):
        if p.is_file() and p.suffix.lower() in JS_EXTS:
            results.append(p)
    return sorted(results)


def _extract_imports(text: str) -> list[str]:
    imports = []
    for m in IMPORT_RE.finditer(text):
        imports.append(m.group("path"))
    return imports


def _strip_quotes(raw: str) -> str:
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"'", '"', "`"}:
        return raw[1:-1]
    return raw


def _normalize_template_path(path_text: str) -> str | None:
    """
    把：
      ${API_BASE}/workspaces
      ${API_BASE}/workspace/${goalId}
    归一化成：
      /workspaces
      /workspace/{goalId}
    """
    text = path_text.strip()

    text = TEMPLATE_API_BASE_PREFIX_RE.sub("", text)
    if text.startswith("http://") or text.startswith("https://"):
        # 只保留路径部分
        idx = text.find("/", text.find("//") + 2)
        text = text[idx:] if idx != -1 else "/"

    if not text.startswith("/"):
        return None

    def repl(match: re.Match[str]) -> str:
        var_name = match.group(1).strip()
        return "{" + var_name + "}"

    text = TEMPLATE_VAR_RE.sub(repl, text)
    text = re.sub(r"/+", "/", text)
    return text.rstrip("/") or "/"


def _extract_http_calls(text: str) -> list[dict[str, str]]:
    calls: list[dict[str, str]] = []

    for m in FETCH_CALL_RE.finditer(text):
        raw_url = _strip_quotes(m.group("url"))
        options = m.group("options") or ""
        method_match = METHOD_RE.search(options)
        method = (method_match.group("method").upper() if method_match else "GET")

        normalized = _normalize_template_path(raw_url)
        if normalized:
            calls.append(
                {
                    "method": method,
                    "path": normalized,
                    "source": "fetch",
                }
            )

    for m in DIRECT_CLIENT_RE.finditer(text):
        raw_url = _strip_quotes(m.group("url"))
        method = m.group("method").upper()
        normalized = _normalize_template_path(raw_url)
        if normalized:
            calls.append(
                {
                    "method": method,
                    "path": normalized,
                    "source": m.group("client"),
                }
            )

    # 去重
    dedup: dict[tuple[str, str], dict[str, str]] = {}
    for c in calls:
        dedup[(c["method"], c["path"])] = c
    return sorted(dedup.values(), key=lambda x: (x["path"], x["method"]))


def _load_api_routes(workspace_dir: str) -> list[dict[str, str]]:
    api_map_path = Path(workspace_dir) / "api_map.json"
    if not api_map_path.exists():
        return []
    data = json.loads(api_map_path.read_text(encoding="utf-8"))
    routes = []
    for route in data.get("routes", []):
        if route.get("path") and route.get("method"):
            routes.append(
                {
                    "method": str(route["method"]).upper(),
                    "path": route["path"],
                }
            )
    return routes


def _path_matches(frontend_path: str, backend_path: str) -> tuple[bool, str]:
    if frontend_path.rstrip("/") == backend_path.rstrip("/"):
        return True, "exact"

    # 把 {goalId} 和 {outcome_id} 这种都视为动态段
    fe_parts = frontend_path.strip("/").split("/")
    be_parts = backend_path.strip("/").split("/")

    if len(fe_parts) != len(be_parts):
        return False, ""

    for fe, be in zip(fe_parts, be_parts):
        fe_dyn = fe.startswith("{") and fe.endswith("}")
        be_dyn = be.startswith("{") and be.endswith("}")
        if fe == be:
            continue
        if fe_dyn and be_dyn:
            continue
        return False, ""

    return True, "templated"


def build_integration_map(project_path: str, workspace_dir: str) -> dict[str, Any]:
    root = Path(project_path).resolve()
    frontend_files = _find_frontend_files(root)
    backend_routes = _load_api_routes(workspace_dir)

    frontend_usage: list[dict[str, Any]] = []
    matched_routes: list[dict[str, Any]] = []
    unmatched_frontend_calls: list[dict[str, Any]] = []

    seen_matches: set[tuple[str, str, str]] = set()

    for file_path in frontend_files:
        text = _read_text(file_path)
        calls = _extract_http_calls(text)
        imports = _extract_imports(text)

        rel = str(file_path.relative_to(root))
        entry = {
            "file": rel,
            "imports": imports,
            "http_calls": calls,
        }
        frontend_usage.append(entry)

        for call in calls:
            found = False
            for route in backend_routes:
                if call["method"] != route["method"]:
                    continue
                ok, match_type = _path_matches(call["path"], route["path"])
                if ok:
                    key = (rel, route["method"], route["path"])
                    if key not in seen_matches:
                        matched_routes.append(
                            {
                                "frontend_file": rel,
                                "frontend_method": call["method"],
                                "frontend_path": call["path"],
                                "api_method": route["method"],
                                "api_path": route["path"],
                                "match_type": match_type,
                            }
                        )
                        seen_matches.add(key)
                    found = True
            if not found:
                unmatched_frontend_calls.append(
                    {
                        "frontend_file": rel,
                        "method": call["method"],
                        "path": call["path"],
                    }
                )

    return {
        "project_path": str(root),
        "frontend_files_scanned": len(frontend_files),
        "frontend_usage": frontend_usage,
        "matched_routes": matched_routes,
        "unmatched_frontend_calls": unmatched_frontend_calls,
        "summary": {
            "files_with_http_calls": sum(1 for x in frontend_usage if x["http_calls"]),
            "matched_route_count": len(matched_routes),
            "unmatched_frontend_call_count": len(unmatched_frontend_calls),
        },
    }


def write_integration_map(project_path: str, workspace_dir: str) -> str:
    data = build_integration_map(project_path=project_path, workspace_dir=workspace_dir)
    path = Path(workspace_dir) / "integration_map.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)
