from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class KnowledgeEntryCreate(BaseModel):
    container_id: uuid.UUID
    content: str = Field(..., min_length=1)
    status: Literal["active", "changed", "stable", "deprecated", "disputed"] = "active"
    fact_check: Literal["unverified", "verified", "disputed", "retracted"] = "unverified"
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)
    metadata_: dict[str, Any] = Field(default_factory=dict, alias="metadata")


class KnowledgeEntryUpdate(BaseModel):
    content: str | None = Field(None, min_length=1)
    status: str | None = None
    fact_check: str | None = None
    confidence_score: float | None = None


class KnowledgeEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    container_id: uuid.UUID
    content: str
    version: int
    status: str
    stability_counter: int
    fact_check: str
    confidence_score: float | None
    created_at: datetime
    updated_at: datetime


class SearchRequest(BaseModel):
    q: str = Field(..., min_length=2, max_length=500)
    geo_id: uuid.UUID | None = None
    limit: int = Field(20, ge=1, le=100)
    vector_weight: float = Field(0.6, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    id: uuid.UUID
    content: str
    geo_name: str
    hybrid_score: float
    bm25_score: float
    vector_score: float


class SearchResponse(BaseModel):
    query: str
    total: int
    results: list[SearchResult]
