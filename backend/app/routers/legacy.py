from __future__ import annotations

"""Legacy routes that replicate the original main.py endpoints for frontend compatibility.

The frontend expects:
  GET /memory       -> list of {object_label, title, memory_text, audio_url}
  GET /memory/{label} -> single {object_label, title, memory_text, audio_url}
  POST /memory      -> create/update with {object_label, title, memory_text, audio_url?}
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..dependencies import get_db
from ..models.memory import Memory, MemoryObject
from ..models.object import RegisteredObject

router = APIRouter()


class LegacyMemoryAnchor(BaseModel):
    object_label: str
    title: str
    memory_text: str
    audio_url: Optional[str] = None


def _to_legacy(memory: Memory, label: str) -> dict:
    return {
        "object_label": label,
        "title": memory.title,
        "memory_text": memory.narrative_text,
        "audio_url": memory.audio_url,
    }


@router.get("/health")
async def health_check():
    return {"ok": True}


@router.get("/memory", response_model=list[LegacyMemoryAnchor])
async def list_memories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Memory)
        .where(Memory.is_deleted == False)
        .options(selectinload(Memory.objects).selectinload(MemoryObject.registered_object))
    )
    memories = result.scalars().all()
    out = []
    for mem in memories:
        label = ""
        for mo in mem.objects:
            if mo.is_primary and mo.registered_object:
                label = mo.registered_object.label
                break
        if not label and mem.objects and mem.objects[0].registered_object:
            label = mem.objects[0].registered_object.label
        out.append(_to_legacy(mem, label))
    return out


@router.get("/memory/{object_label}", response_model=LegacyMemoryAnchor)
async def get_memory(object_label: str, db: AsyncSession = Depends(get_db)):
    label = object_label.lower().strip()
    result = await db.execute(
        select(Memory)
        .join(MemoryObject, MemoryObject.memory_id == Memory.id)
        .join(RegisteredObject, RegisteredObject.id == MemoryObject.object_id)
        .where(RegisteredObject.label == label, Memory.is_deleted == False)
        .options(selectinload(Memory.objects).selectinload(MemoryObject.registered_object))
        .limit(1)
    )
    memory = result.scalar_one_or_none()
    if memory is None:
        raise HTTPException(status_code=404, detail=f"No memory found for '{object_label}'")
    return _to_legacy(memory, label)


@router.post("/memory", response_model=LegacyMemoryAnchor)
async def create_or_update_memory(
    anchor: LegacyMemoryAnchor, db: AsyncSession = Depends(get_db)
):
    label = anchor.object_label.lower().strip()

    # Find or create registered object (use a default seed user)
    from ..models.user import User
    default_user = (await db.execute(select(User).limit(1))).scalar_one_or_none()
    if default_user is None:
        raise HTTPException(status_code=500, detail="No user exists. Run seed.py first.")
    user_id = default_user.id

    obj_result = await db.execute(
        select(RegisteredObject).where(
            RegisteredObject.label == label, RegisteredObject.user_id == user_id
        )
    )
    obj = obj_result.scalar_one_or_none()
    if obj is None:
        obj = RegisteredObject(user_id=user_id, label=label, coco_label=label)
        db.add(obj)
        await db.flush()

    # Check for existing memory linked to this object
    existing_result = await db.execute(
        select(Memory)
        .join(MemoryObject, MemoryObject.memory_id == Memory.id)
        .where(MemoryObject.object_id == obj.id, Memory.is_deleted == False)
        .limit(1)
    )
    existing = existing_result.scalar_one_or_none()

    if existing:
        existing.title = anchor.title
        existing.narrative_text = anchor.memory_text
        existing.audio_url = anchor.audio_url
        await db.commit()
        return _to_legacy(existing, label)

    memory = Memory(
        user_id=user_id,
        title=anchor.title,
        narrative_text=anchor.memory_text,
        audio_url=anchor.audio_url,
    )
    db.add(memory)
    await db.flush()

    link = MemoryObject(memory_id=memory.id, object_id=obj.id, is_primary=True)
    db.add(link)
    await db.commit()
    return _to_legacy(memory, label)
