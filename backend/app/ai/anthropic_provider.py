from __future__ import annotations

"""Anthropic-based providers: Claude for text + Claude Vision."""

from typing import AsyncIterator

import anthropic

from .base import LLMProvider, VisionProvider


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate_text(self, prompt: str, system: str | None = None, **kwargs) -> str:
        params = {"model": self.model, "max_tokens": kwargs.get("max_tokens", 1024)}
        if system:
            params["system"] = system
        params["messages"] = [{"role": "user", "content": prompt}]
        response = await self.client.messages.create(**params)
        return response.content[0].text

    async def generate_text_stream(
        self, prompt: str, system: str | None = None, **kwargs
    ) -> AsyncIterator[str]:
        params = {"model": self.model, "max_tokens": kwargs.get("max_tokens", 1024)}
        if system:
            params["system"] = system
        params["messages"] = [{"role": "user", "content": prompt}]
        async with self.client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text


class AnthropicVisionProvider(VisionProvider):
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def analyze_image(self, image_b64: str, prompt: str, **kwargs) -> str:
        # Strip data URI prefix if present
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )
        return response.content[0].text
