"""LLM provider abstraction — supports Claude and OpenAI."""
from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: dict = field(default_factory=dict)
    raw: object = None


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def complete(self, system: str, user: str, **kwargs) -> LLMResponse:
        """Return free-text completion."""
        ...

    @abstractmethod
    def complete_json(self, system: str, user: str, **kwargs) -> dict:
        """Return parsed JSON completion."""
        ...
