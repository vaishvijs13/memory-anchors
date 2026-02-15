from __future__ import annotations

"""Memory business logic — CRUD + AI generation + expansion."""

import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..ai import get_llm_provider
from ..ai.prompts import (
    MEMORY_EXPAND_DEEPER,
    MEMORY_EXPAND_PEOPLE,
    MEMORY_EXPAND_SENSORY,
    MEMORY_EXPAND_SYSTEM,
    MEMORY_GENERATION_PROMPT,
    MEMORY_GENERATION_SYSTEM,
)
from ..models.memory import Memory, MemoryEmotion, MemoryObject, MemoryPerson
from ..models.object import RegisteredObject


def _memory_load_options():
    return [
        selectinload(Memory.objects).selectinload(MemoryObject.registered_object),
        selectinload(Memory.people),
        selectinload(Memory.emotions),
    ]


async def list_memories(
    db: AsyncSession,
    user_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
    object_label: str | None = None,
    emotion: str | None = None,
    search: str | None = None,
):
    query = (
        select(Memory)
        .where(Memory.user_id == user_id, Memory.is_deleted == False)
        .options(*_memory_load_options())
    )

    if object_label:
        query = query.join(MemoryObject).join(RegisteredObject).where(
            RegisteredObject.label == object_label.lower()
        )
    if emotion:
        query = query.join(MemoryEmotion).where(MemoryEmotion.emotion == emotion)
    if search:
        query = query.where(
            Memory.title.ilike(f"%{search}%") | Memory.narrative_text.ilike(f"%{search}%")
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size).order_by(Memory.created_at.desc())
    result = await db.execute(query)
    memories = result.scalars().all()

    return memories, total


async def get_memory(db: AsyncSession, memory_id: uuid.UUID, user_id: uuid.UUID) -> Memory | None:
    result = await db.execute(
        select(Memory)
        .where(Memory.id == memory_id, Memory.user_id == user_id, Memory.is_deleted == False)
        .options(*_memory_load_options())
    )
    memory = result.scalar_one_or_none()
    if memory:
        memory.access_count += 1
        memory.last_accessed = datetime.now(timezone.utc)
        await db.commit()
    return memory


async def get_memory_by_object(
    db: AsyncSession, label: str, user_id: uuid.UUID
) -> Memory | None:
    result = await db.execute(
        select(Memory)
        .join(MemoryObject)
        .join(RegisteredObject)
        .where(
            RegisteredObject.label == label.lower(),
            Memory.user_id == user_id,
            Memory.is_deleted == False,
        )
        .options(*_memory_load_options())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_memory(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    narrative_text: str,
    object_label: str | None = None,
    **kwargs,
) -> Memory:
    memory = Memory(user_id=user_id, title=title, narrative_text=narrative_text, **kwargs)
    db.add(memory)
    await db.flush()

    if object_label:
        await _link_object(db, memory.id, user_id, object_label)

    await db.commit()
    await db.refresh(memory)
    return memory


async def update_memory(
    db: AsyncSession, memory_id: uuid.UUID, user_id: uuid.UUID, **updates
) -> Memory | None:
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id, Memory.user_id == user_id, Memory.is_deleted == False
        )
    )
    memory = result.scalar_one_or_none()
    if not memory:
        return None
    for key, value in updates.items():
        if value is not None and hasattr(memory, key):
            setattr(memory, key, value)
    await db.commit()
    await db.refresh(memory)
    return memory


async def delete_memory(db: AsyncSession, memory_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id, Memory.user_id == user_id, Memory.is_deleted == False
        )
    )
    memory = result.scalar_one_or_none()
    if not memory:
        return False
    memory.is_deleted = True
    await db.commit()
    return True


async def generate_memory(
    db: AsyncSession,
    user_id: uuid.UUID,
    object_label: str,
    context_hint: str | None = None,
    time_period: str | None = None,
    location: str | None = None,
    people: list[str] | None = None,
) -> Memory:
    llm = get_llm_provider()

    prompt = MEMORY_GENERATION_PROMPT.format(
        object_label=object_label,
        context=f"Context: {context_hint}" if context_hint else "",
        time_period=f"Time period: {time_period}" if time_period else "",
        location=f"Location: {location}" if location else "",
        people=f"People: {', '.join(people)}" if people else "",
    )

    raw = await llm.generate_text(prompt, system=MEMORY_GENERATION_SYSTEM)

    # Parse JSON response
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code block
        if "```" in raw:
            json_str = raw.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            data = json.loads(json_str.strip())
        else:
            data = {"title": f"Memory of {object_label}", "narrative": raw}

    memory = Memory(
        user_id=user_id,
        title=data.get("title", f"Memory of {object_label}"),
        narrative_text=data.get("narrative", raw),
        context_hint=context_hint,
        sensory_details=data.get("sensory_details"),
        time_period=time_period,
        location=location,
        is_ai_generated=True,
        ai_model_used=llm.__class__.__name__,
    )
    db.add(memory)
    await db.flush()

    # Link to object
    await _link_object(db, memory.id, user_id, object_label)

    # Add emotions
    for em in data.get("emotions", []):
        db.add(MemoryEmotion(
            memory_id=memory.id,
            emotion=em.get("emotion", ""),
            intensity=em.get("intensity", 0.5),
        ))

    # Add people
    for p in data.get("people", []):
        db.add(MemoryPerson(
            memory_id=memory.id,
            person_name=p.get("name", ""),
            relationship=p.get("relationship"),
        ))

    await db.commit()
    await db.refresh(memory)
    return memory


async def expand_memory(
    db: AsyncSession, memory_id: uuid.UUID, user_id: uuid.UUID, depth: str = "deeper"
) -> str:
    result = await db.execute(
        select(Memory).where(
            Memory.id == memory_id, Memory.user_id == user_id, Memory.is_deleted == False
        )
    )
    memory = result.scalar_one_or_none()
    if not memory:
        raise ValueError("Memory not found")

    llm = get_llm_provider()

    templates = {
        "deeper": MEMORY_EXPAND_DEEPER,
        "sensory": MEMORY_EXPAND_SENSORY,
        "people": MEMORY_EXPAND_PEOPLE,
    }
    prompt = templates.get(depth, MEMORY_EXPAND_DEEPER).format(narrative=memory.narrative_text)
    expansion = await llm.generate_text(prompt, system=MEMORY_EXPAND_SYSTEM)

    # Append expansion to the narrative
    memory.narrative_text = f"{memory.narrative_text}\n\n{expansion}"
    await db.commit()

    return expansion


async def _link_object(
    db: AsyncSession, memory_id: uuid.UUID, user_id: uuid.UUID, label: str
):
    label = label.lower().strip()
    obj_result = await db.execute(
        select(RegisteredObject).where(
            RegisteredObject.user_id == user_id, RegisteredObject.label == label
        )
    )
    obj = obj_result.scalar_one_or_none()
    if not obj:
        obj = RegisteredObject(user_id=user_id, label=label, coco_label=label)
        db.add(obj)
        await db.flush()
    db.add(MemoryObject(memory_id=memory_id, object_id=obj.id, is_primary=True))
