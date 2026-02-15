from __future__ import annotations

"""AI provider factory and registry."""

from .base import LLMProvider, VisionProvider, TTSProvider, ImageGenerationProvider
from ..config import settings

_providers: dict = {}


def get_llm_provider() -> LLMProvider:
    if "llm" not in _providers:
        name = settings.LLM_PROVIDER
        if name == "anthropic":
            from .anthropic_provider import AnthropicLLMProvider
            _providers["llm"] = AnthropicLLMProvider(api_key=settings.ANTHROPIC_API_KEY)
        else:
            from .openai_provider import OpenAILLMProvider
            _providers["llm"] = OpenAILLMProvider(api_key=settings.OPENAI_API_KEY)
    return _providers["llm"]


def get_vision_provider() -> VisionProvider:
    if "vision" not in _providers:
        name = settings.VISION_PROVIDER
        if name == "anthropic":
            from .anthropic_provider import AnthropicVisionProvider
            _providers["vision"] = AnthropicVisionProvider(api_key=settings.ANTHROPIC_API_KEY)
        else:
            from .openai_provider import OpenAIVisionProvider
            _providers["vision"] = OpenAIVisionProvider(api_key=settings.OPENAI_API_KEY)
    return _providers["vision"]


def get_tts_provider() -> TTSProvider:
    if "tts" not in _providers:
        name = settings.TTS_PROVIDER
        if name == "openai":
            from .openai_provider import OpenAITTSProvider
            _providers["tts"] = OpenAITTSProvider(api_key=settings.OPENAI_API_KEY)
        else:
            from .elevenlabs_provider import ElevenLabsTTSProvider
            _providers["tts"] = ElevenLabsTTSProvider(
                api_key=settings.ELEVENLABS_API_KEY,
                default_voice_id=settings.ELEVENLABS_VOICE_ID,
            )
    return _providers["tts"]


def get_image_provider() -> ImageGenerationProvider:
    if "image" not in _providers:
        from .openai_provider import OpenAIImageProvider
        _providers["image"] = OpenAIImageProvider(api_key=settings.OPENAI_API_KEY)
    return _providers["image"]
