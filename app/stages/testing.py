"""Stage 6: Testing — LLM generates tests + optional Docker sandbox execution."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from app.llm import get_llm
from app.config import config

GENERATE_TESTS_PROMPT = """\
你是一名 QA 工程师。为以下代码生成完整的自动化测试用例。

要求：
1. 使用 pytest（Python）或 vitest/jest（JavaScript）
2. 覆盖正常路径和边界情况
3. 包含必要的 fixture 和 mock
4. 测试文件路径遵循项目惯例（tests/ 目录）

输出 JSON：
{
  "test_files": [
    {"path": "tests/test_xxx.py", "content": "完整测试代码"},
    ...
  ],
  "test_config": {
    "framework": "pytest|vitest|jest",
    "run_command": "pytest tests/ -v",
    "coverage_target": 80
  }
}"""

CODE_REVIEW_PROMPT = """\
你是一名代码审查专家。审查以下代码的质量和安全性。

关注：
- 安全漏洞（注入、XSS、硬编码密钥等）
- 代码质量（重复代码、过长函数、命名不清晰）
- 最佳实践（错误处理、日志、类型提示）
- 性能问题（N+1 查询、内存泄漏）

输出 JSON：
{
  "issues": [
    {
      "severity": "critical|warning|info",
      "file": "文件路径",
      "line": 行号或null,
      "category": "security|quality|performance|best_practice",
      "message": "问题描述",
      "suggestion": "修复建议"
    }
  ],
  "overall_score": 0-100,
  "summary": "总体评价"
}"""


def generate_tests(source_files: list[dict], requirement_card: dict) -> dict:
    """Generate test files using LLM."""
    llm = get_llm()
    # Limit source context to avoid token overflow
    truncated = []
    total_chars = 0
    for f in source_files:
        content = f.get("content", "")
        if total_chars + len(content) > 30000:
            truncated.append({"path": f["path"], "content": content[:2000] + "\n# ... truncated"})
        else:
            truncated.append(f)
            total_chars += len(content)

    user_msg = (
        f"需求卡：\n{json.dumps(requirement_card, ensure_ascii=False, indent=2)}\n\n"
        f"源代码文件：\n{json.dumps(truncated, ensure_ascii=False, indent=2)}"
    )
    return llm.complete_json(
        system=GENERATE_TESTS_PROMPT,
        user=user_msg,
        tier="strong",
        max_tokens=6000,
    )


def review_code(source_files: list[dict]) -> dict:
    """Run LLM-based code review."""
    llm = get_llm()
    truncated = []
    total_chars = 0
    for f in source_files:
        content = f.get("content", "")
        if total_chars + len(content) > 30000:
            truncated.append({"path": f["path"], "content": content[:2000] + "\n# ... truncated"})
        else:
            truncated.append(f)
            total_chars += len(content)

    return llm.complete_json(
        system=CODE_REVIEW_PROMPT,
        user=f"代码文件：\n{json.dumps(truncated, ensure_ascii=False, indent=2)}",
        tier="strong",
        max_tokens=4000,
    )


def write_test_files(project_id: int, test_data: dict) -> list[str]:
    """Write generated test files to disk."""
    output_dir = config.openclaw.output_dir
    project_dir = Path(output_dir) / f"project_{project_id}"
    written = []
    for f in test_data.get("test_files", []):
        path = project_dir / f["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f["content"], encoding="utf-8")
        written.append(str(path))
    return written


def run_tests_in_sandbox(project_id: int, framework: str = "pytest") -> dict:
    """Run tests in a Docker sandbox. Returns test results."""
    output_dir = config.openclaw.output_dir
    project_dir = Path(output_dir) / f"project_{project_id}"
    abs_dir = str(project_dir.resolve())

    if framework in ("pytest", "python"):
        image = "python:3.12-slim"
        cmd = "pip install -r requirements.txt 2>/dev/null; pip install pytest pytest-cov; pytest tests/ -v --tb=short -q 2>&1"
    else:
        image = "node:20-slim"
        cmd = "npm ci 2>/dev/null; npm test -- --watchAll=false 2>&1"

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--network=none",
                "-v", f"{abs_dir}:/app",
                "-w", "/app",
                image,
                "sh", "-c", cmd,
            ],
            capture_output=True,
            text=True,
            timeout=config.openclaw.executor_timeout,
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout[-5000:],  # limit output size
            "stderr": result.stderr[-2000:],
            "passed": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": "Test execution timed out",
            "passed": False,
        }
    except FileNotFoundError:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": "Docker not available — skipping sandbox execution",
            "passed": None,
        }
