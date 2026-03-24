"""Stage 2: Clarification Generator — LLM generates targeted questions."""
from __future__ import annotations

import json

from app.llm import get_llm

GENERATE_QUESTIONS_PROMPT = """\
你是一名需求澄清专家。基于以下需求卡，生成 3-5 个有针对性的澄清问题。

问题应帮助明确：
- 模糊的功能边界（哪些要做，哪些不做）
- 未指定的技术约束（性能、并发、部署环境）
- 用户体验期望（交互方式、设计风格）
- 外部集成需求（第三方API、数据源）
- 优先级和阶段划分

输出 JSON 格式：
{
  "questions": [
    {"question": "问题文本", "category": "功能|技术|体验|集成|优先级", "why": "为什么需要问这个"},
    ...
  ]
}"""

REFINE_REQUIREMENT_PROMPT = """\
你是一名需求分析师。根据用户对澄清问题的回答，更新和完善需求卡。

保留原需求卡中正确的内容，补充/修正用户回答中透露的新信息。

输出更新后的完整需求卡 JSON（与原格式一致）。"""


def generate_questions(requirement_card: dict) -> dict:
    """Generate clarification questions based on requirement card."""
    llm = get_llm()
    return llm.complete_json(
        system=GENERATE_QUESTIONS_PROMPT,
        user=f"需求卡：\n{json.dumps(requirement_card, ensure_ascii=False, indent=2)}",
        tier="fast",
        max_tokens=1024,
    )


def refine_requirement(requirement_card: dict, answers: list[dict]) -> dict:
    """Refine requirement card based on clarification answers."""
    llm = get_llm()
    user_msg = (
        f"原始需求卡：\n{json.dumps(requirement_card, ensure_ascii=False, indent=2)}\n\n"
        f"澄清回答：\n{json.dumps(answers, ensure_ascii=False, indent=2)}"
    )
    return llm.complete_json(
        system=REFINE_REQUIREMENT_PROMPT,
        user=user_msg,
        tier="fast",
        max_tokens=2048,
    )
