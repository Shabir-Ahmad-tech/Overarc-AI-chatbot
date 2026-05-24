-- =============================================================================
-- Overarc SmartBot — RAG System: Supabase SQL Migration
-- Run this once in your Supabase SQL Editor (https://supabase.com/dashboard)
-- =============================================================================

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create document_chunks table for RAG storage
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    source_name TEXT NOT NULL DEFAULT 'unknown',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Create an index on bot_id for fast filtering
CREATE INDEX IF NOT EXISTS idx_document_chunks_bot_id ON document_chunks (bot_id);

-- 4. Create HNSW index for fast cosine similarity search on embeddings
--    (HNSW is faster than IVFFlat for high-dimensional vectors)
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
    ON document_chunks 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 200);

-- 5. Create the match_documents function for cosine similarity search
--    Returns top-k chunks for a given bot_id that exceed the similarity threshold
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding VECTOR(1536),
    match_bot_id TEXT,
    match_threshold FLOAT DEFAULT 0.75,
    match_count INT DEFAULT 3
)
RETURNS TABLE (
    id UUID,
    bot_id TEXT,
    content TEXT,
    source_name TEXT,
    similarity FLOAT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.bot_id,
        dc.content,
        dc.source_name,
        1 - (dc.embedding <=> query_embedding) AS similarity,
        dc.created_at
    FROM document_chunks dc
    WHERE
        dc.bot_id = match_bot_id
        AND 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 6. Create a documents metadata table to track uploaded files
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bot_id TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'pdf',  -- 'pdf' or 'text'
    chunk_count INT NOT NULL DEFAULT 0,
    extraction_summary JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_bot_id ON documents (bot_id);

-- =============================================================================
-- ADDITIONAL: Add status column to businesses table (if using schema.sql)
-- Run only if you already applied schema.sql and need to upgrade:
-- =============================================================================
-- ALTER TABLE businesses ADD COLUMN IF NOT EXISTS email TEXT;
-- ALTER TABLE businesses ADD COLUMN IF NOT EXISTS password_hash TEXT;
-- ALTER TABLE businesses ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';