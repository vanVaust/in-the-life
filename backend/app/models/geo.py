from __future__ import annotations
import uuid
from sqlalchemy import (
    Column, String, Integer, SmallInteger, Numeric,
    BigInteger, ForeignKey, CheckConstraint, Index, text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, TIMESTAMPTZ
from sqlalchemy.orm import relationship, Mapped, mapped_column
from geoalchemy2 import Geometry
from app.core.database import Base


class GeoEntity(Base):
    __tablename__ = "geo_entities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()")
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name_local: Mapped[str | None] = mapped_column(String(255))
    iso_code: Mapped[str | None] = mapped_column(String(10), index=True)
    geo_level: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("geo_entities.id", ondelete="RESTRICT")
    )
    world_band_row: Mapped[int | None] = mapped_column(SmallInteger)
    world_band_col: Mapped[int | None] = mapped_column(SmallInteger)
    h3_index: Mapped[str | None] = mapped_column(String(20))
    geometry = Column(Geometry("GEOMETRY", srid=4326))
    area_km2: Mapped[float | None] = mapped_column(Numeric(15, 2))
    population: Mapped[int | None] = mapped_column(BigInteger)
    timezone: Mapped[str | None] = mapped_column(String(50))
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, server_default=text("'{}'"))
    created_at = mapped_column(TIMESTAMPTZ, server_default=text("NOW()"))
    updated_at = mapped_column(TIMESTAMPTZ, server_default=text("NOW()"), onupdate=text("NOW()"))

    # Relationships
    parent: Mapped[GeoEntity | None] = relationship("GeoEntity", remote_side="GeoEntity.id", back_populates="children")
    children: Mapped[list[GeoEntity]] = relationship("GeoEntity", back_populates="parent")
    containers: Mapped[list[SquareContainer]] = relationship("SquareContainer", back_populates="geo_entity")

    __table_args__ = (
        CheckConstraint("world_band_row BETWEEN 0 AND 2", name="ck_geo_world_band_row"),
        CheckConstraint("world_band_col BETWEEN 0 AND 2", name="ck_geo_world_band_col"),
        Index("idx_geo_world_band", "world_band_row", "world_band_col"),
        Index("idx_geo_parent", "parent_id"),
    )
