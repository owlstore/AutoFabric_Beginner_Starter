from typing import Dict, Any


def parse_goal(raw_input: str) -> Dict[str, Any]:
    raw_lower = raw_input.lower()
    packages = []
    for pkg in ["docker", "git", "python", "node", "vscode", "postgresql"]:
        if pkg in raw_lower:
            packages.append(pkg)
    output_format = "docker" if "docker" in raw_lower or "container" in raw_lower else "vm"
    os_name = "ubuntu-22.04" if "ubuntu" in raw_lower or not raw_lower else "ubuntu-22.04"
    return {
        "goal_type": "environment_build",
        "os": os_name,
        "packages": packages or ["git", "python"],
        "output_format": output_format,
        "success_criteria": [
            "构建成功",
            "关键软件可执行",
            "有验证记录",
        ],
    }


def judge_result(execution_output: Dict[str, Any]) -> Dict[str, Any]:
    ok = execution_output.get("status") == "success"
    return {
        "result": "pass" if ok else "fail",
        "reason": "执行成功" if ok else execution_output.get("error", "未知错误"),
    }
