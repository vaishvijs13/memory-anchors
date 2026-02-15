from __future__ import annotations

"""Vision service — scene analysis and object identification."""

import json
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..ai import get_vision_provider
from ..ai.prompts import OBJECT_IDENTIFY_PROMPT, SCENE_ANALYSIS_PROMPT, SCENE_DESCRIBE_PROMPT
from ..models.memory import MemoryObject
from ..models.object import RegisteredObject


async def analyze_scene(
    db: AsyncSession,
    user_id: uuid.UUID,
    image_b64: str,
    custom_prompt: str | None = None,
) -> dict:
    vision = get_vision_provider()
    prompt = custom_prompt or SCENE_ANALYSIS_PROMPT
    raw = await vision.analyze_image(image_b64, prompt)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        if "```" in raw:
            json_str = raw.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            data = json.loads(json_str.strip())
        else:
            return {"objects": [], "scene": None, "raw_analysis": raw}

    # Cross-reference detected objects with user's registered objects
    detected_labels = [obj.get("label", "").lower() for obj in data.get("objects", [])]
    if detected_labels:
        result = await db.execute(
            select(RegisteredObject).where(
                RegisteredObject.user_id == user_id,
                RegisteredObject.label.in_(detected_labels),
            )
        )
        registered = {obj.label: obj for obj in result.scalars().all()}

        for obj in data.get("objects", []):
            label = obj.get("label", "").lower()
            if label in registered:
                # Find memory IDs linked to this object
                mem_result = await db.execute(
                    select(MemoryObject.memory_id).where(
                        MemoryObject.object_id == registered[label].id
                    )
                )
                obj["memory_ids"] = [str(mid) for (mid,) in mem_result.all()]

    return {
        "objects": data.get("objects", []),
        "scene": {
            "description": data.get("scene_description", ""),
            "mood": data.get("mood"),
            "suggested_memory_prompt": None,
        },
        "raw_analysis": None,
    }


async def identify_object(image_b64: str, bbox: list[float] | None = None) -> dict:
    vision = get_vision_provider()
    raw = await vision.analyze_image(image_b64, OBJECT_IDENTIFY_PROMPT)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        if "```" in raw:
            json_str = raw.split("```")[1]
            if json_str.startswith("json"):
                json_str = json_str[4:]
            return json.loads(json_str.strip())
        return {"label": "unknown", "confidence": 0.0, "description": raw}


async def describe_scene(image_b64: str) -> dict:
    vision = get_vision_provider()
    raw = await vision.analyze_image(image_b64, SCENE_DESCRIBE_PROMPT)

    try:
        data = json.loads(raw)
        return data
    except json.JSONDecodeError:
        return {
            "description": raw,
            "objects": [],
            "mood": None,
            "memory_suggestions": [],
        }
