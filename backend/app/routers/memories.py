from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user, get_db
from ..models.user import User
from ..schemas.memory import (
    MemoryCreate,
    MemoryExpandRequest,
    MemoryGenerateRequest,
    MemoryListResponse,
    MemoryResponse,
    MemoryUpdate,
)
from ..services import memory_service

router = APIRouter()


def _to_response(mem) -> MemoryResponse:
    labels = []
    for mo in getattr(mem, "objects", []):
        if mo.registered_object:
            labels.append(mo.registered_object.label)
    people = [
        {"person_name": p.person_name, "relationship": p.relationship}
        for p in getattr(mem, "people", [])
    ]
    emotions = [
        {"emotion": e.emotion, "intensity": e.intensity}
        for e in getattr(mem, "emotions", [])
    ]
    return MemoryResponse(
        id=mem.id,
        title=mem.title,
        narrative_text=mem.narrative_text,
        context_hint=mem.context_hint,
        sensory_details=mem.sensory_details,
        time_period=mem.time_period,
        location=mem.location,
        significance=mem.significance,
        is_ai_generated=mem.is_ai_generated,
        ai_model_used=mem.ai_model_used,
        audio_url=mem.audio_url,
        image_url=mem.image_url,
        access_count=mem.access_count,
        last_accessed=mem.last_accessed,
        created_at=mem.created_at,
        people=people,
        emotions=emotions,
        object_labels=labels,
    )


@router.get("/", response_model=MemoryListResponse)
async def list_memories(
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 20,
    object_label: Optional[str] = None,
    emotion: Optional[str] = None,
    search: Optional[str] = None,
):
    memories, total = await memory_service.list_memories(
        db, user.id, page, page_size, object_label, emotion, search
    )
    return MemoryListResponse(
        items=[_to_response(m) for m in memories],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    mem = await memory_service.get_memory(db, memory_id, user.id)
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")
    return _to_response(mem)


@router.post("/", response_model=MemoryResponse, status_code=201)
async def create_memory(
    req: MemoryCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    mem = await memory_service.create_memory(
        db,
        user_id=user.id,
        title=req.title,
        narrative_text=req.narrative_text,
        object_label=req.object_label,
        context_hint=req.context_hint,
        sensory_details=req.sensory_details,
        time_period=req.time_period,
        location=req.location,
        significance=req.significance,
    )
    return _to_response(mem)


@router.post("/generate", response_model=MemoryResponse, status_code=201)
async def generate_memory(
    req: MemoryGenerateRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    mem = await memory_service.generate_memory(
        db,
        user_id=user.id,
        object_label=req.object_label,
        context_hint=req.context_hint,
        time_period=req.time_period,
        location=req.location,
        people=req.people,
    )
    return _to_response(mem)


@router.post("/{memory_id}/expand")
async def expand_memory(
    memory_id: uuid.UUID,
    req: MemoryExpandRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    try:
        expansion = await memory_service.expand_memory(db, memory_id, user.id, req.depth)
    except ValueError:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"expansion": expansion}


@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: uuid.UUID,
    req: MemoryUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    mem = await memory_service.update_memory(
        db, memory_id, user.id, **req.model_dump(exclude_none=True)
    )
    if not mem:
        raise HTTPException(status_code=404, detail="Memory not found")
    return _to_response(mem)


@router.delete("/{memory_id}", status_code=204)
async def delete_memory(
    memory_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    deleted = await memory_service.delete_memory(db, memory_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")


@router.get("/by-object/{label}", response_model=MemoryResponse)
async def get_by_object(
    label: str,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    mem = await memory_service.get_memory_by_object(db, label, user.id)
    if not mem:
        raise HTTPException(status_code=404, detail=f"No memory for object '{label}'")
    return _to_response(mem)
