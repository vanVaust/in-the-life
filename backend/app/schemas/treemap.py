from __future__ import annotations
import uuid
from pydantic import BaseModel, Field


class TreemapNode(BaseModel):
    id: uuid.UUID
    name: str
    value: float
    visual_area: float
    level: int = 0
    geo_level: str = ""
    children: list[TreemapNode] = []


class TreemapRequest(BaseModel):
    width: float = Field(800, gt=0)
    height: float = Field(600, gt=0)
    value_field: str = Field("area_km2", description="area_km2 | population")
    max_depth: int = Field(3, ge=1, le=6)
