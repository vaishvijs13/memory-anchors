from __future__ import annotations

"""Abstract base classes for AI providers."""

from abc import ABC, abstractmethod
from typing import AsyncIterator


class LLMProvider(ABC):
    @abstractmethod
    async def generate_text(self, prompt: str, system: str | None = None, **kwargs) -> str:
        ...

    @abstractmethod
    async def generate_text_stream(
        self, prompt: str, system: str | None = None, **kwargs
    ) -> AsyncIterator[str]:
        ...


class VisionProvider(ABC):
    @abstractmethod
    async def analyze_image(
        self, image_b64: str, prompt: str, **kwargs
    ) -> str:
        ...


class TTSProvider(ABC):
    @abstractmethod
    async def synthesize(self, text: str, voice_id: str | None = None, **kwargs) -> bytes:
        ...

    @abstractmethod
    async def synthesize_stream(
        self, text: str, voice_id: str | None = None, **kwargs
    ) -> AsyncIterator[bytes]:
        ...


class ImageGenerationProvider(ABC):
    @abstractmethod
    async def generate_image(self, prompt: str, **kwargs) -> str:
        """Returns a URL or base64 of the generated image."""
        ...
