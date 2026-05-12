-- In-The-Life: PostgreSQL Init Script
-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- GIN index for full-text search on knowledge_entries
CREATE INDEX IF NOT EXISTS idx_knowledge_content_fts
    ON knowledge_entries USING GIN (to_tsvector('simple', content));

-- HNSW index for vector similarity search
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding_hnsw
    ON knowledge_entries USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- GIN index for JSONB metadata
CREATE INDEX IF NOT EXISTS idx_geo_metadata_gin
    ON geo_entities USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_gin
    ON knowledge_entries USING GIN (metadata);
