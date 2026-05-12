from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.knowledge import KnowledgeEntry
from app.schemas.knowledge import (
    KnowledgeEntryCreate,
    KnowledgeEntryUpdate,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.embedding import embed_text


class KnowledgeService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, data: KnowledgeEntryCreate) -> KnowledgeEntry:
        embedding = await embed_text(data.content)
        entry = KnowledgeEntry(
            **data.model_dump(by_alias=True, exclude={"metadata_"}),
            embedding=embedding,
        )
        self.db.add(entry)
        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def update(self, entry_id: uuid.UUID, data: KnowledgeEntryUpdate) -> KnowledgeEntry | None:
        entry = await self.db.get(KnowledgeEntry, entry_id)
        if not entry:
            return None
        updates = data.model_dump(exclude_none=True)
        for k, v in updates.items():
            setattr(entry, k, v)
        if "content" in updates:
            entry.embedding = await embed_text(updates["content"])
            entry.version += 1
        await self.db.flush()
        await self.db.refresh(entry)
        return entry

    async def hybrid_search(self, req: SearchRequest) -> SearchResponse:
        embedding = await embed_text(req.q)
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        vw = req.vector_weight
        bw = 1.0 - vw

        sql = text("""
            WITH vector_scores AS (
                SELECT id,
                       1 - (embedding <=> :embedding::vector) AS vscore
                FROM knowledge_entries
                WHERE status != 'deprecated'
            ),
            bm25_scores AS (
                SELECT id,
                       ts_rank_cd(to_tsvector('simple', content), plainto_tsquery('simple', :query)) AS bscore
                FROM knowledge_entries
                WHERE status != 'deprecated'
            )
            SELECT
                ke.id,
                ke.content,
                ge.name AS geo_name,
                (:vw * COALESCE(vs.vscore, 0) + :bw * COALESCE(bs.bscore, 0)) AS hybrid_score,
                COALESCE(bs.bscore, 0) AS bm25_score,
                COALESCE(vs.vscore, 0) AS vector_score
            FROM knowledge_entries ke
            JOIN square_containers sc ON sc.id = ke.container_id
            JOIN geo_entities ge ON ge.id = sc.geo_entity_id
            LEFT JOIN vector_scores vs ON vs.id = ke.id
            LEFT JOIN bm25_scores bs ON bs.id = ke.id
            WHERE ke.status != 'deprecated'
            ORDER BY hybrid_score DESC
            LIMIT :limit
        """)

        result = await self.db.execute(
            sql,
            {"embedding": embedding_str, "query": req.q, "vw": vw, "bw": bw, "limit": req.limit}
        )
        rows = result.fetchall()

        results = [
            SearchResult(
                id=row.id,
                content=row.content,
                geo_name=row.geo_name,
                hybrid_score=float(row.hybrid_score),
                bm25_score=float(row.bm25_score),
                vector_score=float(row.vector_score),
            )
            for row in rows
        ]
        return SearchResponse(query=req.q, total=len(results), results=results)
