"""OpenAI LLM provider."""
from __future__ import annotations

import json
import os

from openai import OpenAI

from app.llm.provider import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    def __init__(self):
        base_url = os.getenv("OPENAI_BASE_URL") or None
        self.client = OpenAI(base_url=base_url)  # reads OPENAI_API_KEY from env
        self.model_fast = os.getenv("LLM_MODEL_FAST", "gpt-4o-mini")
        self.model_strong = os.getenv("LLM_MODEL_STRONG", "gpt-4o")

    def _pick_model(self, kwargs: dict) -> str:
        if "model" in kwargs:
            return kwargs.pop("model")
        tier = kwargs.pop("tier", "strong")
        return self.model_fast if tier == "fast" else self.model_strong

    def complete(self, system: str, user: str, **kwargs) -> LLMResponse:
        model = self._pick_model(kwargs)
        max_tokens = kwargs.pop("max_tokens", 4096)

        resp = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        choice = resp.choices[0]
        return LLMResponse(
            content=choice.message.content,
            model=resp.model,
            usage={
                "input_tokens": resp.usage.prompt_tokens,
                "output_tokens": resp.usage.completion_tokens,
            },
            raw=resp,
        )

    def complete_json(self, system: str, user: str, **kwargs) -> dict:
        model = self._pick_model(kwargs)
        max_tokens = kwargs.pop("max_tokens", 4096)

        resp = self.client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system + "\nRespond with valid JSON only."},
                {"role": "user", "content": user},
            ],
        )
        return json.loads(resp.choices[0].message.content)
