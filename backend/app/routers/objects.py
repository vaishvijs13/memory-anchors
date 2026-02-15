from __future__ import annotations

import uuid
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user, get_db
from ..models.object import RegisteredObject
from ..models.user import User

router = APIRouter()


class ObjectCreate(BaseModel):
    label: str
    display_name: Optional[str] = None
    coco_label: Optional[str] = None


class ObjectUpdate(BaseModel):
    display_name: Optional[str] = None
    coco_label: Optional[str] = None


class ObjectResponse(BaseModel):
    id: uuid.UUID
    label: str
    display_name: Optional[str] = None
    coco_label: Optional[str] = None

    model_config = {"from_attributes": True}


@router.get("/", response_model=List[ObjectResponse])
async def list_objects(
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RegisteredObject).where(RegisteredObject.user_id == user.id)
    )
    return list(result.scalars().all())


@router.get("/{object_id}", response_model=ObjectResponse)
async def get_object(
    object_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RegisteredObject).where(
            RegisteredObject.id == object_id, RegisteredObject.user_id == user.id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    return obj


@router.post("/", response_model=ObjectResponse, status_code=201)
async def create_object(
    req: ObjectCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    obj = RegisteredObject(
        user_id=user.id,
        label=req.label.lower().strip(),
        display_name=req.display_name,
        coco_label=req.coco_label or req.label.lower().strip(),
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.patch("/{object_id}", response_model=ObjectResponse)
async def update_object(
    object_id: uuid.UUID,
    req: ObjectUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RegisteredObject).where(
            RegisteredObject.id == object_id, RegisteredObject.user_id == user.id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    if req.display_name is not None:
        obj.display_name = req.display_name
    if req.coco_label is not None:
        obj.coco_label = req.coco_label
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{object_id}", status_code=204)
async def delete_object(
    object_id: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RegisteredObject).where(
            RegisteredObject.id == object_id, RegisteredObject.user_id == user.id
        )
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Object not found")
    await db.delete(obj)
    await db.commit()
