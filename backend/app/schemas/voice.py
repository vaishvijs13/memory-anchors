import uuid
from typing import List, Optional

from pydantic import BaseModel


class SynthesizeRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None
    provider: Optional[str] = None


class SynthesizeMemoryRequest(BaseModel):
    voice_id: Optional[str] = None
    provider: Optional[str] = None


class VoiceProfile(BaseModel):
    voice_id: str
    name: str
    provider: str
    preview_url: Optional[str] = None


class VoiceProfilesResponse(BaseModel):
    profiles: List[VoiceProfile]


class VoicePreferencesUpdate(BaseModel):
    preferred_voice_id: str
    preferred_provider: Optional[str] = None
