from __future__ import annotations
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.geo import GeoEntity
from app.models.container import SquareContainer
from app.schemas.treemap import TreemapNode, TreemapRequest


class TreemapService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def build(self, geo_id: uuid.UUID, req: TreemapRequest) -> TreemapNode:
        entity = await self.db.get(GeoEntity, geo_id)
        if not entity:
            raise ValueError(f"GeoEntity {geo_id} not found")

        value = float(getattr(entity, req.value_field) or 1.0)
        node = TreemapNode(
            id=entity.id,
            name=entity.name,
            value=value,
            visual_area=req.width * req.height,
            level=0,
            geo_level=entity.geo_level,
        )

        if req.max_depth > 1:
            await self._add_children(node, entity.id, req, depth=1)

        return node

    async def _add_children(
        self, parent_node: TreemapNode, parent_id: uuid.UUID, req: TreemapRequest, depth: int
    ) -> None:
        if depth >= req.max_depth:
            return
        result = await self.db.execute(
            select(GeoEntity).where(GeoEntity.parent_id == parent_id)
        )
        children = result.scalars().all()
        total = sum(float(getattr(c, req.value_field) or 1.0) for c in children) or 1.0

        for child in children:
            child_value = float(getattr(child, req.value_field) or 1.0)
            child_area = parent_node.visual_area * (child_value / total)
            child_node = TreemapNode(
                id=child.id,
                name=child.name,
                value=child_value,
                visual_area=child_area,
                level=depth,
                geo_level=child.geo_level,
            )
            parent_node.children.append(child_node)
            await self._add_children(child_node, child.id, req, depth + 1)
