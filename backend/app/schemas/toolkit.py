import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DailyPromptResponse(BaseModel):
    prompt_text: str
    exercise_type: str
    suggested_duration_minutes: int = 5


class ExerciseSubmit(BaseModel):
    exercise_type: str
    prompt_text: str
    response_text: str


class ExerciseResult(BaseModel):
    id: uuid.UUID
    exercise_type: str
    prompt_text: str
    response_text: str
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MoodCreate(BaseModel):
    mood_score: int = Field(ge=1, le=5)
    notes: Optional[str] = None


class MoodResponse(BaseModel):
    id: uuid.UUID
    mood_score: int
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MoodHistoryResponse(BaseModel):
    entries: List[MoodResponse]


class CognitiveReportResponse(BaseModel):
    summary: str
    average_score: Optional[float] = None
    exercise_count: int = 0
    mood_trend: Optional[str] = None
    recommendations: List[str] = []


class EngagementReportResponse(BaseModel):
    total_memories: int = 0
    total_accesses: int = 0
    most_accessed_memories: List[Dict[str, Any]] = []
    active_days: int = 0
