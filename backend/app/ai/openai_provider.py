from __future__ import annotations

"""OpenAI-based providers: GPT-4 (text), GPT-4V (vision), tts-1, DALL-E 3."""

from typing import AsyncIterator

from openai import AsyncOpenAI

from .base import LLMProvider, VisionProvider, TTSProvider, ImageGenerationProvider


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_text(self, prompt: str, system: str | None = None, **kwargs) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, **kwargs
        )
        return response.choices[0].message.content

    async def generate_text_stream(
        self, prompt: str, system: str | None = None, **kwargs
    ) -> AsyncIterator[str]:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        stream = await self.client.chat.completions.create(
            model=self.model, messages=messages, stream=True, **kwargs
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class OpenAIVisionProvider(VisionProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def analyze_image(self, image_b64: str, prompt: str, **kwargs) -> str:
        # Ensure data URI prefix
        if not image_b64.startswith("data:"):
            image_b64 = f"data:image/jpeg;base64,{image_b64}"
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_b64}},
                    ],
                }
            ],
            max_tokens=1000,
            **kwargs,
        )
        return response.choices[0].message.content


class OpenAITTSProvider(TTSProvider):
    def __init__(self, api_key: str, model: str = "tts-1"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def synthesize(self, text: str, voice_id: str | None = None, **kwargs) -> bytes:
        voice = voice_id or "alloy"
        response = await self.client.audio.speech.create(
            model=self.model, voice=voice, input=text, **kwargs
        )
        return response.content

    async def synthesize_stream(
        self, text: str, voice_id: str | None = None, **kwargs
    ) -> AsyncIterator[bytes]:
        voice = voice_id or "alloy"
        response = await self.client.audio.speech.create(
            model=self.model, voice=voice, input=text, **kwargs
        )
        # OpenAI TTS doesn't natively stream chunks, yield full content
        yield response.content


class OpenAIImageProvider(ImageGenerationProvider):
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate_image(self, prompt: str, **kwargs) -> str:
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=kwargs.get("size", "1024x1024"),
            quality="standard",
            n=1,
        )
        return response.data[0].url
