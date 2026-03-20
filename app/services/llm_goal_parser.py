import json
from typing import Any

import httpx

from app.core.config import settings

SYSTEM_PROMPT = """You are a goal parsing engine for an engineering workspace system.

Return only valid JSON with this exact shape:

{
  "raw_input": "<original user text>",
  "parsed_goal": {
    "intent": "<fix_issue|understand_system|build_system|general_task>",
    "scope": "<frontend|backend|infra|data|unspecified>",
    "target": "<short main target>",
    "source_text": "<original user text>"
  },
  "goal_type": "<bug_fix|system_understanding|system_build|general_task>",
  "risk_level": "<low|medium|high>",
  "recommended_next_action": {
    "summary": "<one short product-style sentence, <= 120 chars>",
    "step_type": "<collect_context|analyze_system|define_build_scope|clarify_goal>",
    "steps": [
      "<short actionable step 1>",
      "<short actionable step 2>",
      "<short actionable step 3>"
    ],
    "requires_human_confirmation": false
  }
}

Rules:
- Use only the allowed enum values above.
- Keep target short and specific.
- Keep summary concise and product-style.
- Always return exactly 3 steps.
- Each step must be short, imperative, and actionable.
- Do not include markdown.
- Do not include explanations outside JSON.
"""

def is_llm_enabled() -> bool:
    return (
        settings.llm.enabled
        and settings.llm.provider == "openai"
        and bool(settings.llm.openai_api_key.strip())
    )

def parse_goal_with_llm(user_input: str) -> dict[str, Any]:
    if not is_llm_enabled():
        raise RuntimeError("LLM parser is disabled")

    headers = {
        "Authorization": f"Bearer {settings.llm.openai_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.llm.model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_input}],
            },
        ],
    }

    print("LLM_PARSE_START =", {
        "provider": settings.llm.provider,
        "model": settings.llm.model,
        "enabled": settings.llm.enabled,
        "has_api_key": bool(settings.llm.openai_api_key.strip()),
    })

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                "https://api.openai.com/v1/responses",
                headers=headers,
                json=payload,
            )
            print("LLM_PARSE_HTTP_STATUS =", response.status_code)
            if response.status_code >= 400:
                print("LLM_PARSE_HTTP_BODY =", response.text)
            response.raise_for_status()
            data = response.json()

        text_output = _extract_text(data)
        print("LLM_PARSE_TEXT_OUTPUT =", text_output)

        parsed = json.loads(text_output)

        if parsed.get("raw_input") != user_input:
            parsed["raw_input"] = user_input

        parsed.setdefault("parsed_goal", {})
        parsed["parsed_goal"].setdefault("source_text", user_input)

        return parsed
    except Exception as e:
        print("LLM_PARSE_ERROR =", repr(e))
        raise

def _extract_text(response_json: dict[str, Any]) -> str:
    output = response_json.get("output", [])
    texts: list[str] = []

    for item in output:
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                texts.append(content.get("text", ""))

    text = "\n".join(t for t in texts if t).strip()
    if not text:
        raise ValueError("No text returned from LLM")
    return text
