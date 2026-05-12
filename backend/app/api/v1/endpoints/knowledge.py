from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.knowledge import KnowledgeEntry
from app.schemas.knowledge import (
    KnowledgeEntryCreate,
    KnowledgeEntryRead,
    KnowledgeEntryUpdate,
    SearchRequest,
    SearchResponse,
)
from app.services.knowledge import KnowledgeService

router = APIRouter()


@router.get("", response_model=list[KnowledgeEntryRead])
async def list_entries(
    container_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    q = select(KnowledgeEntry)
    if container_id:
        q = q.where(KnowledgeEntry.container_id == container_id)
    if status:
        q = q.where(KnowledgeEntry.status == status)
    result = await db.execute(q.offset(offset).limit(limit))
    return result.scalars().all()


@router.post("", response_model=KnowledgeEntryRead, status_code=201)
async def create_entry(
    body: KnowledgeEntryCreate,
    db: AsyncSession = Depends(get_db),
):
    svc = KnowledgeService(db)
    return await svc.create(body)


@router.patch("/{entry_id}", response_model=KnowledgeEntryRead)
async def update_entry(
    entry_id: uuid.UUID,
    body: KnowledgeEntryUpdate,
    db: AsyncSession = Depends(get_db),
):
    svc = KnowledgeService(db)
    entry = await svc.update(entry_id, body)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.post("/search", response_model=SearchResponse)
async def search(
    body: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    svc = KnowledgeService(db)
    return await svc.hybrid_search(body)
