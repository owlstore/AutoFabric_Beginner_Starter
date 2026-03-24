"""App-wide configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / ".env", override=True)


@dataclass
class LLMConfig:
    provider: str = "claude"
    model_fast: str = "claude-haiku-4-5-20251001"
    model_strong: str = "claude-sonnet-4-20250514"

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "claude"),
            model_fast=os.getenv("LLM_MODEL_FAST", cls.model_fast),
            model_strong=os.getenv("LLM_MODEL_STRONG", cls.model_strong),
        )


@dataclass
class OpenClawConfig:
    enabled: bool = True
    bridge_mode: str = "llm"  # "llm" | "shell" | "mock" | "gateway"
    executor_timeout: int = 120
    max_retries: int = 2
    output_dir: str = "generated"
    gateway_url: str = "ws://127.0.0.1:18789"
    gateway_agent: str = "main"

    @classmethod
    def from_env(cls) -> "OpenClawConfig":
        return cls(
            enabled=os.getenv("OPENCLAW_ENABLED", "true").lower() == "true",
            bridge_mode=os.getenv("OPENCLAW_BRIDGE_MODE", "llm"),
            executor_timeout=int(os.getenv("OPENCLAW_EXECUTOR_TIMEOUT", "120")),
            output_dir=os.getenv("OPENCLAW_OUTPUT_DIR", "generated"),
            gateway_url=os.getenv("OPENCLAW_GATEWAY_URL", "ws://127.0.0.1:18789"),
            gateway_agent=os.getenv("OPENCLAW_GATEWAY_AGENT", "main"),
        )


@dataclass
class AppConfig:
    llm: LLMConfig = field(default_factory=LLMConfig)
    openclaw: OpenClawConfig = field(default_factory=OpenClawConfig)

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            llm=LLMConfig.from_env(),
            openclaw=OpenClawConfig.from_env(),
        )


# Singleton
config = AppConfig.from_env()
