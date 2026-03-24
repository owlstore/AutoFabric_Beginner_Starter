import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    task_name: str
    task_type: str
    status: str = "pending"
    dependencies: List[str] = field(default_factory=list)

    def execute(self):
        print(f"[EXECUTE] {self.task_type} -> {self.task_name}")
        self.status = "completed"


class TaskManager:
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def parse_requirements(self, requirement_text: str) -> List[Task]:
        text = requirement_text.strip()

        generated_tasks: List[Task] = [
            Task(task_name="生成需求卡", task_type="requirement"),
            Task(task_name="生成澄清问题", task_type="clarification"),
            Task(task_name="生成原型说明", task_type="prototype"),
            Task(task_name="生成研发编排计划", task_type="orchestration"),
            Task(task_name="执行开发任务", task_type="execution"),
            Task(task_name="生成测试计划", task_type="testing"),
            Task(task_name="生成交付包", task_type="delivery"),
        ]

        if "注册" in text or "登录" in text or "用户" in text:
            generated_tasks.insert(
                4,
                Task(task_name="实现用户认证接口", task_type="execution"),
            )

        if "API" in text or "接口" in text:
            generated_tasks.insert(
                4,
                Task(task_name="设计 API 路由与数据结构", task_type="orchestration"),
            )

        if "前端" in text or "页面" in text:
            generated_tasks.insert(
                4,
                Task(task_name="生成前端页面结构", task_type="prototype"),
            )

        return generated_tasks

    def print_tasks(self):
        print("\n=== TASK LIST ===")
        for idx, task in enumerate(self.tasks, start=1):
            print(f"{idx}. [{task.status}] {task.task_type} - {task.task_name}")

    def export_tasks_json(self):
        payload = [
            {
                "task_name": t.task_name,
                "task_type": t.task_type,
                "status": t.status,
                "dependencies": t.dependencies,
            }
            for t in self.tasks
        ]
        print("\n=== TASK JSON ===")
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    requirement_text = "开发一个 API 接口，实现用户注册和登录功能"

    manager = TaskManager()
    tasks = manager.parse_requirements(requirement_text)

    for task in tasks:
        manager.add_task(task)

    manager.print_tasks()

    print("\n=== EXECUTION ===")
    for task in manager.tasks:
        task.execute()

    manager.print_tasks()
    manager.export_tasks_json()
