"""Deterministic fallback LLM provider for local demos and offline development."""
from __future__ import annotations

import json
import re
from textwrap import dedent

from app.llm.provider import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """Rule-based provider that keeps the Manus pipeline usable without API keys."""

    model_name = "mock-local-v1"

    def complete(self, system: str, user: str, **kwargs) -> LLMResponse:
        payload = self.complete_json(system, user, **kwargs)
        return LLMResponse(
            content=json.dumps(payload, ensure_ascii=False, indent=2),
            model=self.model_name,
            usage={"input_tokens": 0, "output_tokens": 0},
            raw=None,
        )

    def complete_json(self, system: str, user: str, **kwargs) -> dict:
        lowered = system.lower()

        if "结构化需求卡" in system:
            return _build_requirement_card(user)
        if "生成 3-5 个有针对性的澄清问题" in system:
            card = _extract_json_values(user)
            return _build_clarification_questions(card[0] if card else {})
        if "根据用户对澄清问题的回答" in system:
            payloads = _extract_json_values(user)
            card = payloads[0] if payloads else {}
            answers = payloads[1] if len(payloads) > 1 else []
            return _refine_requirement_card(card, answers)
        if "设计完整的信息架构" in system:
            payloads = _extract_json_values(user)
            return _build_information_architecture(payloads[0] if payloads else {})
        if "设计模块依赖和 api" in lowered:
            payloads = _extract_json_values(user)
            card = payloads[0] if payloads else {}
            ia = payloads[1] if len(payloads) > 1 else {}
            return _build_module_design(card, ia)
        if "react + tailwind css" in lowered:
            payloads = _extract_json_values(user)
            card = payloads[0] if payloads else {}
            ia = payloads[1] if len(payloads) > 1 else {}
            modules = payloads[2] if len(payloads) > 2 else {}
            return _build_ui_prototype(card, ia, modules)
        if "拆解为可执行的开发任务" in system:
            payloads = _extract_json_values(user)
            card = payloads[0] if payloads else {}
            ia = payloads[1] if len(payloads) > 1 else {}
            modules = payloads[2] if len(payloads) > 2 else {}
            return _build_orchestration_plan(card, ia, modules)
        if "生成生产级代码" in system:
            payloads = _extract_json_values(user)
            job = payloads[0] if payloads else {}
            return _build_execution_payload(job)
        if "生成完整的自动化测试用例" in system:
            payloads = _extract_json_values(user)
            requirement = payloads[0] if payloads else {}
            source_files = payloads[1] if len(payloads) > 1 else []
            return _build_test_payload(requirement, source_files)
        if "代码审查专家" in system:
            payloads = _extract_json_values(user)
            source_files = payloads[0] if payloads else []
            return _build_code_review(source_files)
        if "生成完整的项目文档" in system:
            payloads = _extract_json_values(user)
            requirement = payloads[0] if payloads else {}
            api_design = payloads[1] if len(payloads) > 1 else []
            architecture = payloads[2] if len(payloads) > 2 else {}
            return _build_docs(requirement, api_design, architecture)
        if "生成部署配置文件" in system:
            payloads = _extract_json_values(user)
            requirement = payloads[0] if payloads else {}
            tech_stack = payloads[1] if len(payloads) > 1 else {}
            return _build_deploy_config(requirement, tech_stack)

        return {
            "message": "Mock provider returned a generic JSON payload.",
            "system_preview": system[:120],
            "user_preview": user[:200],
        }


def _extract_json_values(text: str) -> list:
    decoder = json.JSONDecoder()
    values = []
    idx = 0
    while idx < len(text):
        if text[idx] not in "{[":
            idx += 1
            continue
        try:
            value, end = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            idx += 1
            continue
        values.append(value)
        idx += end
    return values


def _normalize_name(text: str, fallback: str = "智能工作台") -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return fallback
    for splitter in ("。", "，", ".", ",", "\n"):
        cleaned = cleaned.split(splitter, 1)[0].strip()
    if re.search(r"[\u4e00-\u9fff]", cleaned):
        return cleaned[:32]
    words = re.findall(r"[A-Za-z0-9]+", cleaned)
    return " ".join(words[:6]).title() or fallback


def _guess_goal_type(text: str) -> str:
    if any(word in text for word in ("修复", "报错", "bug", "错误")):
        return "bug_fix"
    if any(word in text for word in ("集成", "对接", "同步", "接口")):
        return "integration"
    if any(word in text for word in ("分析", "审查", "评估")):
        return "analysis"
    if any(word in text for word in ("功能", "模块", "页面")):
        return "feature"
    return "system_build"


def _guess_risk(text: str) -> str:
    if any(word in text for word in ("支付", "权限", "认证", "审计", "风控", "多租户")):
        return "high"
    if any(word in text for word in ("管理后台", "报表", "工作流", "自动化", "集成")):
        return "medium"
    return "low"


def _guess_complexity(text: str) -> str:
    if any(word in text for word in ("平台", "系统", "多角色", "工作流", "自动化")):
        return "complex"
    if any(word in text for word in ("页面", "功能", "管理")):
        return "medium"
    return "simple"


def _detect_entities(text: str) -> list[str]:
    pairs = [
        ("任务", "Task"),
        ("项目", "Project"),
        ("用户", "User"),
        ("订单", "Order"),
        ("工单", "Ticket"),
        ("知识库", "KnowledgeBase"),
        ("审批", "Approval"),
        ("执行", "ExecutionRun"),
        ("交付", "DeliveryPackage"),
    ]
    entities = [label for keyword, label in pairs if keyword in text]
    return entities or ["Project", "Task", "User"]


def _suggest_stack(text: str) -> dict:
    frontend = "React + Vite"
    backend = "FastAPI"
    database = "PostgreSQL"
    if "移动端" in text:
        frontend = "React Native + Expo"
    if any(word in text for word in ("仪表盘", "后台", "工作台", "看板")):
        frontend = "React + Vite + Tailwind"
    if "实时" in text:
        backend = "FastAPI + WebSocket"
    return {
        "frontend": frontend,
        "backend": backend,
        "database": database,
        "other": "Playwright, Temporal-ready task runner, object storage",
    }


def _build_requirement_card(user_text: str) -> dict:
    text = user_text.strip()
    title = _normalize_name(text)
    entities = _detect_entities(text)
    return {
        "title": title,
        "summary": f"围绕“{title}”构建一个可交付的 MVP，覆盖任务录入、执行跟踪、状态可视化和结果交付。",
        "goal_type": _guess_goal_type(text),
        "risk_level": _guess_risk(text),
        "target_users": "业务运营、项目负责人、执行成员",
        "problem_statement": "当前流程依赖人工同步，缺少统一任务入口、执行可视化与交付沉淀，导致推进效率和可追踪性不足。",
        "functional_requirements": [
            "FR1: 支持创建项目或任务，并记录原始需求描述。",
            "FR2: 支持将任务拆解为阶段步骤，并展示阶段状态与下一步建议。",
            "FR3: 支持生成执行产物、测试结果和交付摘要。",
            "FR4: 支持查看最近活动、风险提示和关键指标。",
        ],
        "non_functional_requirements": [
            "NFR1: 页面需在桌面端和移动端可用。",
            "NFR2: 关键步骤需要保留日志和可追踪状态。",
            "NFR3: 在没有外部模型 Key 时仍需具备本地演示能力。",
        ],
        "tech_stack_suggestion": _suggest_stack(text),
        "estimated_complexity": _guess_complexity(text),
        "key_entities": entities,
    }


def _build_clarification_questions(card: dict) -> dict:
    title = card.get("title") or "当前项目"
    return {
        "questions": [
            {"question": f"{title} 的首个版本更偏内部工作台还是对外产品？", "category": "功能", "why": "明确首发用户与权限边界。"},
            {"question": "需要优先打通哪些关键动作，例如录入、审批、执行还是报表？", "category": "优先级", "why": "帮助压缩 MVP 范围。"},
            {"question": "部署环境倾向本地 Docker、单机云主机，还是需要后续扩展到云原生？", "category": "技术", "why": "决定基础设施复杂度。"},
            {"question": "界面风格更偏专业仪表盘、轻量表单流还是聊天式工作台？", "category": "体验", "why": "决定信息架构和布局。"},
        ]
    }


def _refine_requirement_card(card: dict, answers: list) -> dict:
    normalized_answers = []
    for item in answers:
        if isinstance(item, dict):
            normalized_answers.append(item.get("answer") or item.get("question") or json.dumps(item, ensure_ascii=False))
        else:
            normalized_answers.append(str(item))
    answer_text = "；".join([a for a in normalized_answers if a])
    updated = dict(card)
    updated["summary"] = f"{card.get('summary', '')} 已结合澄清结果补充：{answer_text or '优先交付专业工作台风格的 Web MVP。'}".strip()
    updated["target_users"] = card.get("target_users") or "内部运营与产品协作团队"
    updated["problem_statement"] = (
        card.get("problem_statement")
        or "需要把需求、执行、验证、交付聚合到统一工作台，减少人工切换与信息丢失。"
    )
    extra_nfr = updated.get("non_functional_requirements", [])
    if "NFR4: 默认采用 Web 优先、后续可扩展多端。" not in extra_nfr:
        extra_nfr.append("NFR4: 默认采用 Web 优先、后续可扩展多端。")
    updated["non_functional_requirements"] = extra_nfr
    return updated


def _build_information_architecture(card: dict) -> dict:
    title = card.get("title") or "项目工作台"
    return {
        "pages": [
            {"name": "Mission Control", "purpose": f"总览 {title} 的进度、风险和最近活动", "key_components": ["阶段轨道", "任务指标", "活动时间线"]},
            {"name": "Task Inbox", "purpose": "查看待执行任务与下一步动作", "key_components": ["任务列表", "优先级标签", "过滤器"]},
            {"name": "Artifacts", "purpose": "查看代码、文档、测试和交付物", "key_components": ["文件清单", "预览卡片", "交付摘要"]},
        ],
        "navigation": {
            "type": "sidebar",
            "structure": [
                {"label": "总览", "page": "Mission Control", "icon": "layout-dashboard"},
                {"label": "任务", "page": "Task Inbox", "icon": "list-todo"},
                {"label": "产物", "page": "Artifacts", "icon": "folder-open"},
            ],
        },
        "user_flows": [
            {"name": "新建任务并自动推进", "steps": ["输入目标", "AI 生成需求卡", "自动推进阶段", "查看交付摘要"]},
            {"name": "检查执行状态", "steps": ["进入项目", "查看阶段轨道", "展开活动明细", "定位产物与测试结果"]},
        ],
    }


def _build_module_design(card: dict, ia: dict) -> dict:
    pages = [page.get("name") for page in ia.get("pages", [])]
    return {
        "module_map": [
            {"name": "mission_hub", "responsibilities": ["汇总任务状态", "计算下一步建议"], "depends_on": ["project_store", "activity_feed"]},
            {"name": "activity_feed", "responsibilities": ["记录阶段事件", "生成时间线"], "depends_on": ["project_store"]},
            {"name": "artifact_center", "responsibilities": ["聚合原型、代码、测试、交付文件"], "depends_on": ["project_store"]},
        ],
        "api_design": [
            {"method": "POST", "path": "/manus/projects/bootstrap", "description": "创建项目并启动 autopilot", "request_body": '{"prompt":"..."}', "response": "workspace snapshot"},
            {"method": "GET", "path": "/manus/projects/{id}/workspace", "description": "获取工作台快照", "request_body": None, "response": "overview + artifacts + activity"},
            {"method": "POST", "path": "/manus/projects/{id}/autopilot", "description": "继续推进项目到下一阶段", "request_body": '{"operator_note":"..."}', "response": "workspace snapshot"},
        ],
        "mermaid_architecture": dedent(
            """\
            graph TD
              UI[Manus Workspace] --> API[FastAPI Mission API]
              API --> FLOW[Autopilot Service]
              FLOW --> STORE[(PostgreSQL)]
              FLOW --> FILES[Generated Artifacts]
              FLOW --> LLM[LLM Provider or Local Mock]
            """
        ),
        "mermaid_er": dedent(
            """\
            erDiagram
              PROJECT ||--o{ REQUIREMENT : has
              PROJECT ||--o{ EXECUTION_RUN : runs
              PROJECT ||--o{ DELIVERY_PACKAGE : publishes
            """
        ),
        "pages": pages,
        "project_name": card.get("title") or "Autopilot Workspace",
    }


def _build_ui_prototype(card: dict, ia: dict, modules: dict) -> dict:
    title = card.get("title") or "Autopilot Workspace"
    summary = card.get("summary") or "AI 驱动的任务工作台"
    pages = [page.get("name") for page in ia.get("pages", [])]
    page_cards = "\n".join(
        [
            f"              <div className=\"rounded-2xl border border-white/10 bg-white/5 p-4\">\n"
            f"                <p className=\"text-xs uppercase tracking-[0.22em] text-cyan-200/60\">{index + 1:02d}</p>\n"
            f"                <h3 className=\"mt-2 text-lg font-semibold text-white\">{name}</h3>\n"
            f"                <p className=\"mt-2 text-sm text-slate-300\">围绕 {name} 组织任务、风险和交付信息。</p>\n"
            f"              </div>"
            for index, name in enumerate(pages or ["Mission Control", "Artifacts", "Runs"])
        ]
    )
    app_code = dedent(
        f"""\
        export default function App() {{
          const stats = [
            {{ label: "Active Missions", value: "12" }},
            {{ label: "Autopilot Success", value: "94%" }},
            {{ label: "Artifacts Ready", value: "36" }},
          ];

          return (
            <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.22),_transparent_34%),linear-gradient(160deg,_#0f172a,_#111827_42%,_#052e2b)] px-6 py-10 text-slate-100">
              <div className="mx-auto max-w-6xl">
                <div className="rounded-[30px] border border-white/10 bg-slate-950/70 p-8 shadow-2xl shadow-cyan-950/20 backdrop-blur">
                  <p className="text-sm uppercase tracking-[0.35em] text-cyan-200/70">Autopilot Workspace</p>
                  <h1 className="mt-4 max-w-3xl text-4xl font-semibold tracking-tight text-white">{title}</h1>
                  <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">{summary}</p>
                  <div className="mt-8 grid gap-4 md:grid-cols-3">
                    {{stats.map((stat) => (
                      <div key={{stat.label}} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                        <p className="text-sm text-slate-400">{{stat.label}}</p>
                        <p className="mt-3 text-3xl font-semibold text-white">{{stat.value}}</p>
                      </div>
                    ))}}
                  </div>
                  <div className="mt-8 grid gap-4 md:grid-cols-3">
{page_cards}
                  </div>
                </div>
              </div>
            </div>
          );
        }}
        """
    )

    return {
        "files": [
            {"path": "src/App.jsx", "content": app_code},
        ],
        "dependencies": {
            "react": "^19.0.0",
            "react-dom": "^19.0.0",
            "tailwindcss": "^3.4.17",
        },
        "notes": modules.get("mermaid_architecture"),
    }


def _build_orchestration_plan(card: dict, ia: dict, modules: dict) -> dict:
    title = card.get("title") or "autopilot_workspace"
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()) or "autopilot_workspace"
    return {
        "epic": f"{title} MVP",
        "features": [
            {
                "name": "Mission Intake",
                "tasks": [
                    {
                        "key": f"{slug}_mission_api",
                        "name": "实现统一 mission bootstrap API",
                        "executor": "backend_builder",
                        "depends_on": [],
                        "description": "新增统一入口，能够创建项目并串联 requirement / clarification / prototype / orchestration。",
                        "estimated_files": ["app/routers/manus.py", "app/services/manus_workspace_service.py"],
                        "required_skills": ["python", "fastapi", "sql"],
                        "acceptance_criteria": ["可以通过单个 API 创建并推进项目。"],
                    },
                    {
                        "key": f"{slug}_workspace_ui",
                        "name": "实现工作台总览界面",
                        "executor": "frontend_builder",
                        "depends_on": [f"{slug}_mission_api"],
                        "description": "展示任务概览、阶段轨道、最近活动与产物列表。",
                        "estimated_files": ["frontend/src/pages/ManusPage.jsx", "frontend/src/components/manus/WorkspacePanel.jsx"],
                        "required_skills": ["react", "tailwind"],
                        "acceptance_criteria": ["工作台可展示 workspace snapshot。"],
                    },
                ],
            },
            {
                "name": "Execution Visibility",
                "tasks": [
                    {
                        "key": f"{slug}_artifact_summary",
                        "name": "聚合代码、测试与交付产物摘要",
                        "executor": "fullstack_builder",
                        "depends_on": [f"{slug}_workspace_ui"],
                        "description": "在后端生成 artifact summary，并在前端展示。",
                        "estimated_files": ["app/services/manus_workspace_service.py", "frontend/src/components/manus/WorkspacePanel.jsx"],
                        "required_skills": ["python", "react"],
                        "acceptance_criteria": ["工作台可看到产物目录与最近事件。"],
                    }
                ],
            },
        ],
        "execution_order": [
            f"{slug}_mission_api",
            f"{slug}_workspace_ui",
            f"{slug}_artifact_summary",
        ],
        "risk_notes": [
            "真实 LLM 不可用时需要本地兜底，避免整条 pipeline 中断。",
            "测试与交付阶段需允许 mock 结果，以保障演示连续性。",
        ],
    }


def _build_execution_payload(job: dict) -> dict:
    task_name = job.get("payload", {}).get("task_name") or job.get("name") or "Autopilot task"
    executor = job.get("executor") or "fullstack_builder"
    slug = re.sub(r"[^a-z0-9]+", "_", task_name.lower()) or "autopilot_task"

    files = []
    if executor in ("backend_builder", "fullstack_builder"):
        files.append(
            {
                "path": f"services/{slug}.py",
                "content": dedent(
                    f"""\
                    \"\"\"Generated service for {task_name}.\"\"\"

                    def build_{slug}():
                        return {{
                            "task": "{task_name}",
                            "status": "completed",
                            "source": "mock-provider",
                        }}
                    """
                ),
            }
        )
    if executor in ("frontend_builder", "fullstack_builder"):
        files.append(
            {
                "path": f"ui/{slug}.jsx",
                "content": dedent(
                    f"""\
                    export default function {''.join(part.title() for part in slug.split('_'))}() {{
                      return (
                        <section style={{{{ padding: 24, borderRadius: 16, background: "#0f172a", color: "#e2e8f0" }}}}>
                          <h2>{task_name}</h2>
                          <p>Generated in local mock mode to keep the autopilot pipeline runnable.</p>
                        </section>
                      );
                    }}
                    """
                ),
            }
        )
    if not files:
        files.append(
            {
                "path": f"docs/{slug}.md",
                "content": f"# {task_name}\n\nThis artifact was generated by the local mock execution provider.\n",
            }
        )
    return {
        "files": files,
        "summary": f"完成任务：{task_name}",
        "dependencies": [],
        "notes": "Generated by MockLLMProvider",
    }


def _build_test_payload(requirement: dict, source_files: list[dict]) -> dict:
    framework = "pytest" if any(str(file.get("path", "")).endswith(".py") for file in source_files) else "vitest"
    if framework == "pytest":
        test_file = {
            "path": "tests/test_smoke_generated.py",
            "content": dedent(
                """\
                def test_generated_smoke():
                    payload = {"status": "completed"}
                    assert payload["status"] == "completed"
                """
            ),
        }
        command = "pytest tests/ -v"
    else:
        test_file = {
            "path": "tests/generated.smoke.test.js",
            "content": dedent(
                """\
                import { describe, expect, it } from "vitest";

                describe("generated smoke", () => {
                  it("passes", () => {
                    expect("completed").toBe("completed");
                  });
                });
                """
            ),
        }
        command = "npx vitest run"
    return {
        "test_files": [test_file],
        "test_config": {
            "framework": framework,
            "run_command": command,
            "coverage_target": 80,
        },
        "requirement_title": requirement.get("title"),
    }


def _build_code_review(source_files: list[dict]) -> dict:
    issues = []
    for file in source_files[:3]:
        path = str(file.get("path", ""))
        if "secret" in path.lower():
            issues.append(
                {
                    "severity": "warning",
                    "file": path,
                    "line": 1,
                    "category": "security",
                    "message": "检测到疑似敏感命名，请确认未提交真实密钥。",
                    "suggestion": "将密钥替换为环境变量并清理历史记录。",
                }
            )
    return {
        "issues": issues,
        "overall_score": 92 if not issues else 78,
        "summary": "Mock 审查已完成。建议在接入真实模型后补做更细粒度安全审查。",
    }


def _build_docs(requirement: dict, api_design: list[dict], architecture: dict) -> dict:
    title = requirement.get("title") or "Autopilot Workspace"
    api_lines = "\n".join(
        [f"- `{item.get('method', 'GET')} {item.get('path', '/')}`: {item.get('description', '')}" for item in api_design[:6]]
    ) or "- 暂无 API 明细"
    architecture_md = architecture.get("mermaid_architecture") if isinstance(architecture, dict) else ""
    return {
        "readme": dedent(
            f"""\
            # {title}

            {requirement.get('summary', 'AI 驱动的多阶段任务工作台。')}

            ## Features
            - 单入口创建项目并驱动 autopilot
            - 可视化阶段状态与最近活动
            - 聚合代码、测试和交付产物
            """
        ),
        "api_docs": f"# API\n\n{api_lines}\n",
        "architecture": f"# Architecture\n\n```mermaid\n{architecture_md or 'graph TD\\n  A[Workspace] --> B[Mission API]'}\n```\n",
        "changelog": "## 0.1.0\n- Added local autopilot workspace baseline.\n",
    }


def _build_deploy_config(requirement: dict, tech_stack: dict) -> dict:
    backend = tech_stack.get("backend") if isinstance(tech_stack, dict) else "FastAPI"
    return {
        "dockerfile": dedent(
            f"""\
            FROM python:3.12-slim
            WORKDIR /app
            COPY requirements.txt ./
            RUN pip install -r requirements.txt
            COPY . .
            CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
            """
        ),
        "docker_compose": dedent(
            """\
            services:
              api:
                build: .
                ports:
                  - "8000:8000"
            """
        ),
        "ci_workflow": dedent(
            """\
            name: ci
            on: [push]
            jobs:
              test:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-python@v5
                    with:
                      python-version: "3.12"
                  - run: pip install -r requirements.txt
                  - run: pytest
            """
        ),
        "env_example": f"LLM_PROVIDER=mock\nAPP_BACKEND={backend}\n",
    }
