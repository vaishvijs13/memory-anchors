from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_current_user, get_db
from ..models.user import User
from ..schemas.vision import (
    DescribeSceneRequest,
    DescribeSceneResponse,
    IdentifyObjectRequest,
    IdentifyObjectResponse,
    VisionAnalyzeRequest,
    VisionAnalyzeResponse,
)
from ..services import vision_service

router = APIRouter()


@router.post("/analyze", response_model=VisionAnalyzeResponse)
async def analyze(
    req: VisionAnalyzeRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
):
    result = await vision_service.analyze_scene(db, user.id, req.image, req.prompt)
    return result


@router.post("/identify-object", response_model=IdentifyObjectResponse)
async def identify_object(
    req: IdentifyObjectRequest,
    user: Annotated[User, Depends(get_current_user)],
):
    return await vision_service.identify_object(req.image, req.bbox)


@router.post("/describe-scene", response_model=DescribeSceneResponse)
async def describe_scene(
    req: DescribeSceneRequest,
    user: Annotated[User, Depends(get_current_user)],
):
    return await vision_service.describe_scene(req.image)
