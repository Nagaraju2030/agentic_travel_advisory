from __future__ import annotations

from abc import ABC, abstractmethod


class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, *, system: str, user: str) -> str:
        raise NotImplementedError
