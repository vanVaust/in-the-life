from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.treemap import TreemapNode, TreemapRequest
from app.services.treemap import TreemapService

router = APIRouter()


@router.get("/{geo_id}", response_model=TreemapNode)
async def get_treemap(
    geo_id: uuid.UUID,
    width: float = Query(800, gt=0),
    height: float = Query(600, gt=0),
    value_field: str = Query("area_km2"),
    max_depth: int = Query(3, ge=1, le=6),
    db: AsyncSession = Depends(get_db),
):
    svc = TreemapService(db)
    req = TreemapRequest(width=width, height=height, value_field=value_field, max_depth=max_depth)
    return await svc.build(geo_id, req)
