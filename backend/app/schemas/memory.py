import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryPersonSchema(BaseModel):
    person_name: str
    relationship: Optional[str] = None


class MemoryEmotionSchema(BaseModel):
    emotion: str
    intensity: float = Field(ge=0, le=1, default=0.5)


class MemoryCreate(BaseModel):
    title: str
    narrative_text: str
    object_label: Optional[str] = None
    context_hint: Optional[str] = None
    sensory_details: Optional[Dict[str, Any]] = None
    time_period: Optional[str] = None
    location: Optional[str] = None
    significance: Optional[int] = Field(None, ge=1, le=10)
    people: List[MemoryPersonSchema] = []
    emotions: List[MemoryEmotionSchema] = []


class MemoryUpdate(BaseModel):
    title: Optional[str] = None
    narrative_text: Optional[str] = None
    context_hint: Optional[str] = None
    sensory_details: Optional[Dict[str, Any]] = None
    time_period: Optional[str] = None
    location: Optional[str] = None
    significance: Optional[int] = Field(None, ge=1, le=10)


class MemoryGenerateRequest(BaseModel):
    object_label: str
    context_hint: Optional[str] = None
    time_period: Optional[str] = None
    location: Optional[str] = None
    people: List[str] = []


class MemoryExpandRequest(BaseModel):
    depth: str = Field(default="deeper", pattern="^(deeper|sensory|people)$")


class MemoryResponse(BaseModel):
    id: uuid.UUID
    title: str
    narrative_text: str
    context_hint: Optional[str] = None
    sensory_details: Optional[Dict[str, Any]] = None
    time_period: Optional[str] = None
    location: Optional[str] = None
    significance: Optional[int] = None
    is_ai_generated: bool = False
    ai_model_used: Optional[str] = None
    audio_url: Optional[str] = None
    image_url: Optional[str] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    created_at: Optional[datetime] = None
    people: List[MemoryPersonSchema] = []
    emotions: List[MemoryEmotionSchema] = []
    object_labels: List[str] = []

    model_config = {"from_attributes": True}


class MemoryListResponse(BaseModel):
    items: List[MemoryResponse]
    total: int
    page: int
    page_size: int
