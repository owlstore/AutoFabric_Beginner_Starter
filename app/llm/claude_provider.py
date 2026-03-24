"""Claude LLM provider using the Anthropic SDK."""
from __future__ import annotations

import json
import os

import anthropic

from app.llm.provider import LLMProvider, LLMResponse


class ClaudeProvider(LLMProvider):
    def __init__(self):
        base_url = os.getenv("ANTHROPIC_BASE_URL") or None
        self.client = anthropic.Anthropic(base_url=base_url) if base_url else anthropic.Anthropic()
        self.model_fast = os.getenv("LLM_MODEL_FAST", "claude-haiku-4-5-20251001")
        self.model_strong = os.getenv("LLM_MODEL_STRONG", "claude-sonnet-4-20250514")

    def _pick_model(self, kwargs: dict) -> str:
        if "model" in kwargs:
            return kwargs.pop("model")
        tier = kwargs.pop("tier", "strong")
        return self.model_fast if tier == "fast" else self.model_strong

    def complete(self, system: str, user: str, **kwargs) -> LLMResponse:
        model = self._pick_model(kwargs)
        max_tokens = kwargs.pop("max_tokens", 4096)

        resp = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        # If truncated, retry with doubled max_tokens (up to once)
        if resp.stop_reason == "max_tokens" and max_tokens < 32000:
            resp = self.client.messages.create(
                model=model,
                max_tokens=min(max_tokens * 2, 32000),
                system=system + "\n\nBe concise. Keep JSON compact — no excessive descriptions.",
                messages=[{"role": "user", "content": user}],
            )
        return LLMResponse(
            content=resp.content[0].text,
            model=resp.model,
            usage={
                "input_tokens": resp.usage.input_tokens,
                "output_tokens": resp.usage.output_tokens,
            },
            raw=resp,
        )

    def complete_json(self, system: str, user: str, **kwargs) -> dict:
        """Complete and parse JSON from the response, with retry on parse failure."""
        json_system = system + "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no explanation."
        resp = self.complete(json_system, user, **kwargs)
        try:
            return _extract_json(resp.content)
        except (json.JSONDecodeError, ValueError):
            # Retry once: ask LLM to fix its own output
            fix_resp = self.client.messages.create(
                model=self.model_fast,
                max_tokens=kwargs.get("max_tokens", 4096),
                system="Fix the following broken JSON. Output ONLY valid JSON, nothing else.",
                messages=[{"role": "user", "content": resp.content}],
            )
            return _extract_json(fix_resp.content[0].text)


def _extract_json(text: str) -> dict:
    """Extract JSON from text that may contain markdown fences or extra text."""
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Find first { ... } or [ ... ] block
    for start_char, end_char in [('{', '}'), ('[', ']')]:
        start = text.find(start_char)
        if start == -1:
            continue
        depth = 0
        for i in range(start, len(text)):
            if text[i] == start_char:
                depth += 1
            elif text[i] == end_char:
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
    # Last resort: try fixing common issues (trailing commas)
    import re
    cleaned = re.sub(r',\s*([}\]])', r'\1', text)
    return json.loads(cleaned)
