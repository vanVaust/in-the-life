from __future__ import annotations
import uuid
from sqlalchemy import Column, String, Numeric, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base


class SquareContainer(Base):
    __tablename__ = "square_containers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    geo_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("geo_entities.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("square_containers.id", ondelete="CASCADE")
    )
    category_type: Mapped[str | None] = mapped_column(String(100))
    subcategory: Mapped[str | None] = mapped_column(String(100))
    visual_area: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'"))
    created_at = mapped_column(TIMESTAMPTZ, server_default=text("NOW()"))
    updated_at = mapped_column(TIMESTAMPTZ, server_default=text("NOW()"), onupdate=text("NOW()"))

    geo_entity: Mapped[GeoEntity] = relationship("GeoEntity", back_populates="containers")
    parent: Mapped[SquareContainer | None] = relationship("SquareContainer", remote_side="SquareContainer.id", back_populates="children")
    children: Mapped[list[SquareContainer]] = relationship("SquareContainer", back_populates="parent")
    knowledge_entries: Mapped[list[KnowledgeEntry]] = relationship("KnowledgeEntry", back_populates="container")

    __table_args__ = (
        Index("idx_container_geo_entity", "geo_entity_id"),
        Index("idx_container_parent", "parent_id"),
    )
