from __future__ import annotations
import uuid
from typing import Any
from pydantic import BaseModel, Field, ConfigDict


class GeoEntityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    name_local: str | None = None
    iso_code: str | None = Field(None, max_length=10)
    geo_level: str = Field(..., description="world|continent|country|region|locality|district")
    parent_id: uuid.UUID | None = None
    world_band_row: int | None = Field(None, ge=0, le=2)
    world_band_col: int | None = Field(None, ge=0, le=2)
    h3_index: str | None = None
    area_km2: float | None = None
    population: int | None = None
    timezone: str | None = None
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata")


class GeoEntityCreate(GeoEntityBase):
    pass


class GeoEntityUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    name_local: str | None = None
    iso_code: str | None = None
    geo_level: str | None = None
    parent_id: uuid.UUID | None = None
    world_band_row: int | None = None
    world_band_col: int | None = None
    area_km2: float | None = None
    population: int | None = None
    timezone: str | None = None


class GeoEntityRead(GeoEntityBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    children_count: int = 0


class GeoEntityTree(GeoEntityRead):
    children: list[GeoEntityTree] = []
