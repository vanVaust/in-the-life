from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.geo import GeoEntity
from app.schemas.geo import GeoEntityCreate, GeoEntityRead, GeoEntityUpdate

router = APIRouter()


@router.get("", response_model=list[GeoEntityRead])
async def list_geo_entities(
    geo_level: str | None = Query(None),
    parent_id: uuid.UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(GeoEntity)
    if geo_level:
        q = q.where(GeoEntity.geo_level == geo_level)
    if parent_id:
        q = q.where(GeoEntity.parent_id == parent_id)
    result = await db.execute(q.offset(offset).limit(limit))
    return result.scalars().all()


@router.get("/{entity_id}", response_model=GeoEntityRead)
async def get_geo_entity(entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    entity = await db.get(GeoEntity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="GeoEntity not found")
    return entity


@router.post("", response_model=GeoEntityRead, status_code=201)
async def create_geo_entity(body: GeoEntityCreate, db: AsyncSession = Depends(get_db)):
    entity = GeoEntity(**body.model_dump(by_alias=True))
    db.add(entity)
    await db.flush()
    await db.refresh(entity)
    return entity


@router.patch("/{entity_id}", response_model=GeoEntityRead)
async def update_geo_entity(
    entity_id: uuid.UUID,
    body: GeoEntityUpdate,
    db: AsyncSession = Depends(get_db),
):
    entity = await db.get(GeoEntity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="GeoEntity not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(entity, k, v)
    await db.flush()
    await db.refresh(entity)
    return entity


@router.delete("/{entity_id}", status_code=204)
async def delete_geo_entity(entity_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    entity = await db.get(GeoEntity, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="GeoEntity not found")
    await db.delete(entity)
