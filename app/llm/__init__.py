"""LLM factory — get configured provider instance."""
from __future__ import annotations

import os

from dotenv import load_dotenv
load_dotenv()

from app.llm.provider import LLMProvider


def get_llm() -> LLMProvider:
    """Return the best available LLM provider, with a local mock fallback."""
    provider = os.getenv("LLM_PROVIDER", "").lower().strip()

    if provider in ("", "auto"):
        if os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            provider = "claude"
        else:
            provider = "mock"

    if provider == "claude" and not os.getenv("ANTHROPIC_API_KEY"):
        provider = "mock"
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        provider = "mock"

    if provider == "claude":
        from app.llm.claude_provider import ClaudeProvider
        return ClaudeProvider()
    if provider == "openai":
        from app.llm.openai_provider import OpenAIProvider
        return OpenAIProvider()
    if provider == "mock":
        from app.llm.mock_provider import MockLLMProvider
        return MockLLMProvider()
    raise ValueError(f"Unknown LLM_PROVIDER: {provider}. Use 'claude', 'openai', or 'mock'.")
