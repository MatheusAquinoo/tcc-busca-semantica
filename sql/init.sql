-- Habilitação da Extensão Vetorial pgvector (no PostgreSQL a extensão se chama 'vector')
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabela 1: Documentos originais (Quadro 3)
CREATE TABLE IF NOT EXISTS documentos (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    fonte VARCHAR(50) NOT NULL -- "Microsoft" ou "Ubuntu"
);

-- Tabela 2: Chunks e persistência vetorial (Quadro 3)
CREATE TABLE IF NOT EXISTS documento_chunks (
    id SERIAL PRIMARY KEY,
    documento_id INTEGER REFERENCES documentos(id) ON DELETE CASCADE,
    conteudo TEXT NOT NULL,
    embedding VECTOR(768),
    categoria VARCHAR(50),
    metadados JSONB
);

-- 1. Índice de Busca Otimizada HNSW para Similaridade de Cosseno (vector_cosine_ops)
CREATE INDEX IF NOT EXISTS idx_chunks_embedding_hnsw
ON documento_chunks
USING hnsw (embedding vector_cosine_ops);

-- 2. Índices de Metadados e Relacional para Pre-filtering (RF04 e RF07)
CREATE INDEX IF NOT EXISTS idx_chunks_categoria
ON documento_chunks (categoria);

CREATE INDEX IF NOT EXISTS idx_chunks_documento_id
ON documento_chunks (documento_id);

-- 3. Índices de Busca Lexical (Full-Text Search nativo do PostgreSQL - Grupo de Controle RF05)
CREATE INDEX IF NOT EXISTS idx_chunks_fts_pt
ON documento_chunks
USING gin (to_tsvector('portuguese', conteudo));

CREATE INDEX IF NOT EXISTS idx_chunks_fts_en
ON documento_chunks
USING gin (to_tsvector('english', conteudo));

