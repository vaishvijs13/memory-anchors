from __future__ import annotations

"""Toolkit service — daily prompts, exercises, mood tracking, reports."""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..ai import get_llm_provider
from ..ai.prompts import COGNITIVE_REPORT_PROMPT, DAILY_PROMPT_SYSTEM, DAILY_PROMPT_TEMPLATE
from ..models.memory import Memory
from ..models.session import CognitiveExercise, MoodEntry


async def get_daily_prompt(db: AsyncSession, user_id: uuid.UUID) -> dict:
    # Gather context
    mood_result = await db.execute(
        select(MoodEntry)
        .where(MoodEntry.user_id == user_id)
        .order_by(MoodEntry.recorded_at.desc())
        .limit(1)
    )
    recent_mood = mood_result.scalar_one_or_none()
    mood_str = f"{recent_mood.mood_score}/5" if recent_mood else "unknown"

    mem_count = (
        await db.execute(
            select(func.count()).select_from(Memory).where(
                Memory.user_id == user_id, Memory.is_deleted == False
            )
        )
    ).scalar() or 0

    recent_mems = await db.execute(
        select(Memory.title)
        .where(Memory.user_id == user_id, Memory.is_deleted == False)
        .order_by(Memory.created_at.desc())
        .limit(5)
    )
    topics = ", ".join(title for (title,) in recent_mems.all()) or "none yet"

    llm = get_llm_provider()
    prompt = DAILY_PROMPT_TEMPLATE.format(
        mood=mood_str, memory_count=mem_count, recent_topics=topics
    )
    text = await llm.generate_text(prompt, system=DAILY_PROMPT_SYSTEM)

    return {
        "prompt_text": text,
        "exercise_type": "memory_recall",
        "suggested_duration_minutes": 5,
    }


async def submit_exercise(
    db: AsyncSession,
    user_id: uuid.UUID,
    exercise_type: str,
    prompt_text: str,
    response_text: str,
) -> CognitiveExercise:
    exercise = CognitiveExercise(
        user_id=user_id,
        exercise_type=exercise_type,
        prompt_text=prompt_text,
        response_text=response_text,
        score=None,  # Could be scored by LLM in future
    )
    db.add(exercise)
    await db.commit()
    await db.refresh(exercise)
    return exercise


async def log_mood(
    db: AsyncSession,
    user_id: uuid.UUID,
    mood_score: int,
    notes: str | None = None,
    recorded_by: uuid.UUID | None = None,
) -> MoodEntry:
    entry = MoodEntry(
        user_id=user_id,
        mood_score=mood_score,
        notes=notes,
        recorded_by=recorded_by,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


async def get_mood_history(
    db: AsyncSession, user_id: uuid.UUID, days: int = 30
) -> list[MoodEntry]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(MoodEntry)
        .where(MoodEntry.user_id == user_id, MoodEntry.recorded_at >= since)
        .order_by(MoodEntry.recorded_at.desc())
    )
    return list(result.scalars().all())


async def get_cognitive_report(db: AsyncSession, user_id: uuid.UUID) -> dict:
    exercises = await db.execute(
        select(CognitiveExercise).where(CognitiveExercise.user_id == user_id)
    )
    all_exercises = list(exercises.scalars().all())

    scores = [e.score for e in all_exercises if e.score is not None]
    avg_score = sum(scores) / len(scores) if scores else None

    moods = await get_mood_history(db, user_id, days=30)
    mood_strs = [f"{m.mood_score}/5" for m in moods[:10]]

    exercise_types = list({e.exercise_type for e in all_exercises})

    llm = get_llm_provider()
    prompt = COGNITIVE_REPORT_PROMPT.format(
        exercise_count=len(all_exercises),
        avg_score=avg_score or "N/A",
        mood_entries=", ".join(mood_strs) or "none",
        exercise_types=", ".join(exercise_types) or "none",
    )
    summary = await llm.generate_text(prompt)

    return {
        "summary": summary,
        "average_score": avg_score,
        "exercise_count": len(all_exercises),
        "mood_trend": "stable" if moods else None,
        "recommendations": [],
    }


async def get_engagement_report(db: AsyncSession, user_id: uuid.UUID) -> dict:
    total_memories = (
        await db.execute(
            select(func.count()).select_from(Memory).where(
                Memory.user_id == user_id, Memory.is_deleted == False
            )
        )
    ).scalar() or 0

    total_accesses = (
        await db.execute(
            select(func.sum(Memory.access_count)).where(
                Memory.user_id == user_id, Memory.is_deleted == False
            )
        )
    ).scalar() or 0

    top_memories = await db.execute(
        select(Memory.id, Memory.title, Memory.access_count)
        .where(Memory.user_id == user_id, Memory.is_deleted == False)
        .order_by(Memory.access_count.desc())
        .limit(5)
    )

    return {
        "total_memories": total_memories,
        "total_accesses": total_accesses,
        "most_accessed_memories": [
            {"id": str(mid), "title": title, "access_count": cnt}
            for mid, title, cnt in top_memories.all()
        ],
        "active_days": 0,
    }
