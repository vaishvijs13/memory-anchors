from __future__ import annotations

"""ElevenLabs TTS provider."""

from typing import AsyncIterator

import httpx

from .base import TTSProvider

ELEVENLABS_API_BASE = "https://api.elevenlabs.io/v1"


class ElevenLabsTTSProvider(TTSProvider):
    def __init__(self, api_key: str, default_voice_id: str = "EXAVITQu4vr4xnSDxMaL"):
        self.api_key = api_key
        self.default_voice_id = default_voice_id

    async def synthesize(self, text: str, voice_id: str | None = None, **kwargs) -> bytes:
        vid = voice_id or self.default_voice_id
        url = f"{ELEVENLABS_API_BASE}/text-to-speech/{vid}"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": kwargs.get("stability", 0.75),
                        "similarity_boost": kwargs.get("similarity_boost", 0.75),
                    },
                },
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.content

    async def synthesize_stream(
        self, text: str, voice_id: str | None = None, **kwargs
    ) -> AsyncIterator[bytes]:
        vid = voice_id or self.default_voice_id
        url = f"{ELEVENLABS_API_BASE}/text-to-speech/{vid}/stream"
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                url,
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": kwargs.get("stability", 0.75),
                        "similarity_boost": kwargs.get("similarity_boost", 0.75),
                    },
                },
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                },
                timeout=30.0,
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk
