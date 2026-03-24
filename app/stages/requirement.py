"""Stage 1: Requirement Analyzer — LLM-powered requirement parsing."""
from __future__ import annotations

from app.llm import get_llm

SYSTEM_PROMPT = """\
你是一名资深需求分析师。分析用户的项目需求描述，输出结构化需求卡。

输出严格遵循以下 JSON 格式：
{
  "title": "简短标题（10字以内）",
  "summary": "一段话需求摘要",
  "goal_type": "system_build|feature|bug_fix|analysis|integration",
  "risk_level": "low|medium|high",
  "target_users": "目标用户群体",
  "problem_statement": "要解决的核心问题",
  "functional_requirements": ["FR1: ...", "FR2: ...", "..."],
  "non_functional_requirements": ["NFR1: ...", "..."],
  "tech_stack_suggestion": {
    "frontend": "推荐前端技术",
    "backend": "推荐后端技术",
    "database": "推荐数据库",
    "other": "其他工具/服务"
  },
  "estimated_complexity": "simple|medium|complex",
  "key_entities": ["实体1", "实体2", "..."]
}"""


def analyze_requirement(user_input: str) -> dict:
    """Parse user input into a structured requirement card using LLM."""
    llm = get_llm()
    return llm.complete_json(
        system=SYSTEM_PROMPT,
        user=user_input,
        tier="fast",
        max_tokens=2048,
    )
