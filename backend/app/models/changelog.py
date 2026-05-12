from __future__ import annotations
import uuid
from sqlalchemy import String, Text, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ, INET
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base


class ChangeLog(Base):
    __tablename__ = "change_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_entries.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    session_id: Mapped[str | None] = mapped_column(String(100))
    field_changed: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text)
    new_value: Mapped[str | None] = mapped_column(Text)
    change_delta: Mapped[dict | None] = mapped_column(JSONB)
    changed_at = mapped_column(TIMESTAMPTZ, server_default=text("NOW()"), index=True)
    ip_address = mapped_column(INET)

    entry: Mapped[KnowledgeEntry] = relationship("KnowledgeEntry", back_populates="change_logs")

    __table_args__ = (
        Index("idx_changelog_entry", "entry_id"),
        Index("idx_changelog_changed_at", "changed_at"),
    )
