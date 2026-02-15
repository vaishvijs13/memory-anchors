from __future__ import annotations

"""Voice service — TTS orchestration + audio caching."""

import hashlib
import uuid
from typing import AsyncIterator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..ai import get_tts_provider
from ..config import settings
from ..models.memory import Memory
from ..models.session import AudioCache


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


async def synthesize(
    text: str,
    voice_id: str | None = None,
    provider_name: str | None = None,
) -> bytes:
    tts = get_tts_provider()
    return await tts.synthesize(text, voice_id=voice_id)


async def synthesize_stream(
    text: str,
    voice_id: str | None = None,
) -> AsyncIterator[bytes]:
    tts = get_tts_provider()
    async for chunk in tts.synthesize_stream(text, voice_id=voice_id):
        yield chunk


async def synthesize_memory(
    db: AsyncSession,
    memory_id: uuid.UUID,
    user_id: uuid.UUID,
    voice_id: str | None = None,
) -> bytes:
    # Fetch memory
    result = await db.execute(
        select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
    )
    memory = result.scalar_one_or_none()
    if not memory:
        raise ValueError("Memory not found")

    vid = voice_id or settings.ELEVENLABS_VOICE_ID
    text_h = _text_hash(memory.narrative_text)

    # Check cache
    cache_result = await db.execute(
        select(AudioCache).where(
            AudioCache.memory_id == memory_id,
            AudioCache.text_hash == text_h,
            AudioCache.voice_id == vid,
        )
    )
    cached = cache_result.scalar_one_or_none()
    if cached:
        # In a real app, this would return the cached audio file/URL
        # For now, re-synthesize
        pass

    tts = get_tts_provider()
    audio = await tts.synthesize(memory.narrative_text, voice_id=vid)

    # Cache for next time
    cache_entry = AudioCache(
        memory_id=memory_id,
        text_hash=text_h,
        provider=settings.TTS_PROVIDER,
        voice_id=vid,
        audio_url="cached",  # Placeholder — would store to S3/local in production
        duration_ms=None,
    )
    db.add(cache_entry)
    await db.commit()

    return audio


def get_voice_profiles() -> list[dict]:
    return [
        {
            "voice_id": "EXAVITQu4vr4xnSDxMaL",
            "name": "Sarah",
            "provider": "elevenlabs",
            "preview_url": None,
        },
        {
            "voice_id": "alloy",
            "name": "Alloy",
            "provider": "openai",
            "preview_url": None,
        },
        {
            "voice_id": "nova",
            "name": "Nova",
            "provider": "openai",
            "preview_url": None,
        },
        {
            "voice_id": "shimmer",
            "name": "Shimmer",
            "provider": "openai",
            "preview_url": None,
        },
    ]
