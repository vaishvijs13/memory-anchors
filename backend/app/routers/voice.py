from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user, get_db
from ..models.user import User
from ..schemas.voice import (
    SynthesizeMemoryRequest,
    SynthesizeRequest,
    VoicePreferencesUpdate,
    VoiceProfilesResponse,
)
from ..services import voice_service

router = APIRouter()


@router.post("/synthesize")
async def synthesize(
    req: SynthesizeRequest,
    user: Annotated[User, Depends(get_current_user)],
):
    async def stream():
        async for chunk in voice_service.synthesize_stream(req.text, voice_id=req.voice_id):
            yield chunk

    return StreamingResponse(stream(), media_type="audio/mpeg")


@router.post("/synthesize-memory/{memory_id}")
async def synthesize_memory(
    memory_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    req: Optional[SynthesizeMemoryRequest] = None,
):
    voice_id = req.voice_id if req else None
    try:
        audio = await voice_service.synthesize_memory(db, memory_id, user.id, voice_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Memory not found")
    return StreamingResponse(iter([audio]), media_type="audio/mpeg")


@router.get("/profiles", response_model=VoiceProfilesResponse)
async def get_profiles(user: Annotated[User, Depends(get_current_user)]):
    return VoiceProfilesResponse(profiles=voice_service.get_voice_profiles())


@router.put("/preferences")
async def update_preferences(
    req: VoicePreferencesUpdate,
    user: Annotated[User, Depends(get_current_user)],
):
    # In production, save to user preferences table
    return {"status": "ok", "voice_id": req.preferred_voice_id}
