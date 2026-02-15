from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user, get_db
from ..models.user import User
from ..schemas.toolkit import (
    CognitiveReportResponse,
    DailyPromptResponse,
    EngagementReportResponse,
    ExerciseResult,
    ExerciseSubmit,
    MoodCreate,
    MoodHistoryResponse,
    MoodResponse,
)
from ..services import toolkit_service

router = APIRouter()


@router.get("/daily-prompt", response_model=DailyPromptResponse)
async def daily_prompt(
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    return await toolkit_service.get_daily_prompt(db, user.id)


@router.post("/exercises", response_model=ExerciseResult, status_code=201)
async def submit_exercise(
    req: ExerciseSubmit,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    exercise = await toolkit_service.submit_exercise(
        db, user.id, req.exercise_type, req.prompt_text, req.response_text
    )
    return exercise


@router.post("/mood", response_model=MoodResponse, status_code=201)
async def log_mood(
    req: MoodCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    return await toolkit_service.log_mood(db, user.id, req.mood_score, req.notes)


@router.get("/mood/history", response_model=MoodHistoryResponse)
async def mood_history(
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    days: int = 30,
):
    entries = await toolkit_service.get_mood_history(db, user.id, days)
    return MoodHistoryResponse(entries=entries)


@router.get("/reports/cognitive", response_model=CognitiveReportResponse)
async def cognitive_report(
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    return await toolkit_service.get_cognitive_report(db, user.id)


@router.get("/reports/engagement", response_model=EngagementReportResponse)
async def engagement_report(
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    return await toolkit_service.get_engagement_report(db, user.id)
