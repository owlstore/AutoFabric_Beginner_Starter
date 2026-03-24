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
        """Complete and parse JSON from the response.

        Adds an instruction to output valid JSON, then extracts
        the first JSON object/array from the response text.
        """
        json_system = system + "\n\nIMPORTANT: Respond with valid JSON only. No markdown, no explanation."
        resp = self.complete(json_system, user, **kwargs)
        return _extract_json(resp.content)


def _extract_json(text: str) -> dict:
    """Extract JSON from text that may contain markdown fences."""
    text = text.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    return json.loads(text)
