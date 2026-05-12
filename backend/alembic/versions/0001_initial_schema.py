"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-12 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # FIX 1: uuid-ossp Extension sicherstellen
    op.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # geo_entities
    op.create_table(
        "geo_entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("name_local", sa.String(255)),
        sa.Column("iso_code", sa.String(10)),
        sa.Column("geo_level", sa.String(50), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("geo_entities.id", ondelete="RESTRICT")),
        sa.Column("world_band_row", sa.SmallInteger()),
        sa.Column("world_band_col", sa.SmallInteger()),
        sa.Column("h3_index", sa.String(20)),
        sa.Column("geometry", geoalchemy2.types.Geometry("GEOMETRY", srid=4326)),
        sa.Column("area_km2", sa.Numeric(15, 2)),
        sa.Column("population", sa.BigInteger()),
        sa.Column("timezone", sa.String(50)),
        sa.Column("metadata", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        # FIX 2: TIMESTAMPTZ korrekt als sa.TIMESTAMP(timezone=True)
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("world_band_row BETWEEN 0 AND 2", name="ck_geo_world_band_row"),
        sa.CheckConstraint("world_band_col BETWEEN 0 AND 2", name="ck_geo_world_band_col"),
    )
    op.create_index("idx_geo_name", "geo_entities", ["name"])
    op.create_index("idx_geo_level", "geo_entities", ["geo_level"])
    op.create_index("idx_geo_iso_code", "geo_entities", ["iso_code"])
    op.create_index("idx_geo_world_band", "geo_entities", ["world_band_row", "world_band_col"])
    op.create_index("idx_geo_parent", "geo_entities", ["parent_id"])

    # square_containers
    op.create_table(
        "square_containers",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("geo_entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("geo_entities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("square_containers.id", ondelete="CASCADE")),
        sa.Column("category_type", sa.String(100)),
        sa.Column("subcategory", sa.String(100)),
        sa.Column("visual_area", sa.Numeric(15, 2), nullable=False),
        sa.Column("metadata", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_container_geo_entity", "square_containers", ["geo_entity_id"])
    op.create_index("idx_container_parent", "square_containers", ["parent_id"])

    # knowledge_entries
    op.create_table(
        "knowledge_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("container_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("square_containers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        # FIX 3: embedding war sa.Column("embedding", sa.Column(...)) — doppelt verschachtelt → korrigiert
        sa.Column("embedding", sa.Text),
        sa.Column("version", sa.Integer, server_default="1", nullable=False),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("stability_counter", sa.Integer, server_default="0", nullable=False),
        sa.Column("fact_check", sa.String(20), server_default="unverified", nullable=False),
        sa.Column("confidence_score", sa.Numeric(4, 3)),
        sa.Column("metadata", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("last_changed_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_knowledge_container", "knowledge_entries", ["container_id"])
    op.create_index("idx_knowledge_status_updated", "knowledge_entries", ["status", "updated_at"])
    # FIX 4: FTS-Index via raw SQL (GIN tsvector)
    op.execute(
        "ALTER TABLE knowledge_entries ADD COLUMN content_tsv tsvector "
        "GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED"
    )
    op.execute("CREATE INDEX idx_knowledge_fts ON knowledge_entries USING GIN (content_tsv)")

    # sources
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("url", sa.Text),
        sa.Column("doi", sa.String(100)),
        sa.Column("reliability_score", sa.Numeric(3, 2)),
        sa.Column("metadata", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # knowledge_sources
    op.create_table(
        "knowledge_sources",
        sa.Column("entry_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="CASCADE"), nullable=False),
        sa.PrimaryKeyConstraint("entry_id", "source_id"),
    )

    # change_logs
    op.create_table(
        "change_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("entry_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("knowledge_entries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("session_id", sa.String(100)),
        sa.Column("field_changed", sa.String(100), nullable=False),
        sa.Column("old_value", sa.Text),
        sa.Column("new_value", sa.Text),
        sa.Column("change_delta", postgresql.JSONB),
        sa.Column("changed_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("ip_address", postgresql.INET),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_changelog_entry", "change_logs", ["entry_id"])
    op.create_index("idx_changelog_changed_at", "change_logs", ["changed_at"])


def downgrade() -> None:
    # FIX 5: Korrekte Reihenfolge (FK-Abhängigkeiten beachten)
    op.drop_table("change_logs")
    op.drop_table("knowledge_sources")
    op.drop_table("sources")
    op.drop_table("knowledge_entries")
    op.drop_table("square_containers")
    op.drop_table("geo_entities")
