from typing import List, Optional

from pydantic import BaseModel


class VisionAnalyzeRequest(BaseModel):
    image: str  # base64-encoded image
    prompt: Optional[str] = None


class DetectedObject(BaseModel):
    label: str
    confidence: float
    description: Optional[str] = None
    memory_ids: List[str] = []


class SceneDescription(BaseModel):
    description: str
    mood: Optional[str] = None
    suggested_memory_prompt: Optional[str] = None


class VisionAnalyzeResponse(BaseModel):
    objects: List[DetectedObject] = []
    scene: Optional[SceneDescription] = None
    raw_analysis: Optional[str] = None


class IdentifyObjectRequest(BaseModel):
    image: str
    bbox: List[float] = []  # [x, y, width, height]


class IdentifyObjectResponse(BaseModel):
    label: str
    confidence: float
    description: str


class DescribeSceneRequest(BaseModel):
    image: str


class DescribeSceneResponse(BaseModel):
    description: str
    objects: List[str] = []
    mood: Optional[str] = None
    memory_suggestions: List[str] = []
