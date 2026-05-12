from __future__ import annotations
import uuid
from sqlalchemy import (
    Column, String, Integer, Text, Numeric, ForeignKey,
    UniqueConstraint, Index, text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ
from sqlalchemy.orm import relationship, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    container_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("square_containers.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = Column(Vector(384))
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    stability_counter: Mapped[int] = mapped_column(Integer, default=0)
    fact_check: Mapped[str] = mapped_column(String(20), default="unverified")
    confidence_score: Mapped[float | None] = mapped_column(Numeric(4, 3))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'"))
    last_changed_at = mapped_column(TIMESTAMPTZ, server_default=text("NOW()"))
    created_at = mapped_column(TIMESTAMPTZ, server_default=text("NOW()"))
    updated_at = mapped_column(TIMESTAMPTZ, server_default=text("NOW()"), onupdate=text("NOW()"))

    container: Mapped[SquareContainer] = relationship("SquareContainer", back_populates="knowledge_entries")
    sources: Mapped[list[Source]] = relationship("Source", secondary="knowledge_sources", back_populates="entries")
    change_logs: Mapped[list[ChangeLog]] = relationship("ChangeLog", back_populates="entry")

    __table_args__ = (
        Index("idx_knowledge_container", "container_id"),
        Index("idx_knowledge_status_updated", "status", "updated_at"),
    )


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    url: Mapped[str | None] = mapped_column(Text)
    doi: Mapped[str | None] = mapped_column(String(100))
    reliability_score: Mapped[float | None] = mapped_column(Numeric(3, 2))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'"))
    created_at = mapped_column(TIMESTAMPTZ, server_default=text("NOW()"))

    entries: Mapped[list[KnowledgeEntry]] = relationship("KnowledgeEntry", secondary="knowledge_sources", back_populates="sources")


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_entries.id", ondelete="CASCADE"), primary_key=True
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), primary_key=True
    )
