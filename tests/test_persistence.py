"""
Testes de Integração e Persistência Vetorial/Relacional (PostgreSQL + pgvector)
Valida o esquema físico das tabelas, restrições de integridade referencial,
existência dos índices HNSW e GIN, operadores de distância de cosseno (<=>) e JSONB.
"""

import os
import sys
import json
from pgvector import Vector

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import get_db, get_connection
from app.services.embedding_service import embedding_service


def test_pgvector_extension_installed():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "vector"


def test_tables_and_columns_schema():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'documentos'
                ORDER BY ordinal_position;
            """)
            doc_cols = {r[0]: r[1] for r in cur.fetchall()}
            assert "id" in doc_cols
            assert "titulo" in doc_cols
            assert "fonte" in doc_cols

            cur.execute("""
                SELECT column_name, data_type, udt_name
                FROM information_schema.columns
                WHERE table_name = 'documento_chunks'
                ORDER BY ordinal_position;
            """)
            chunk_cols = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
            assert "id" in chunk_cols
            assert "documento_id" in chunk_cols
            assert "conteudo" in chunk_cols
            assert chunk_cols["embedding"][1] == "vector"
            assert "categoria" in chunk_cols
            assert chunk_cols["metadados"][1] == "jsonb"


def test_hnsw_and_gin_indexes_exist():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'documento_chunks';
            """)
            indexes = {r[0]: r[1] for r in cur.fetchall()}
            assert "idx_chunks_embedding_hnsw" in indexes
            assert "USING hnsw" in indexes["idx_chunks_embedding_hnsw"]
            assert "vector_cosine_ops" in indexes["idx_chunks_embedding_hnsw"]
            assert "idx_chunks_categoria" in indexes
            assert "idx_chunks_documento_id" in indexes
            assert "idx_chunks_metadados_gin" in indexes
            assert "idx_chunks_fts_pt" in indexes
            assert "idx_chunks_fts_en" in indexes


def test_referential_integrity_cascade_delete():
    """Verifica que a exclusão de um registro em 'documentos' remove seus 'documento_chunks' em cascata."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documentos (titulo, fonte) VALUES (%s, %s) RETURNING id;",
                ("Documento Temporário de Teste Transacional", "Microsoft")
            )
            temp_doc_id = cur.fetchone()[0]

            dummy_vec = Vector([0.01] * 768)
            cur.execute(
                """
                INSERT INTO documento_chunks (documento_id, conteudo, embedding, categoria, metadados)
                VALUES (%s, %s, %s, %s, %s) RETURNING id;
                """,
                (temp_doc_id, "Conteúdo de teste cascade", dummy_vec, "Conectividade", json.dumps({"teste": True}))
            )
            temp_chunk_id = cur.fetchone()[0]

            # Deleta o documento pai e verifica remoção em cascata do fragmento filho
            cur.execute("DELETE FROM documentos WHERE id = %s;", (temp_doc_id,))
            cur.execute("SELECT COUNT(*) FROM documento_chunks WHERE id = %s;", (temp_chunk_id,))
            assert cur.fetchone()[0] == 0
        conn.rollback()
    finally:
        conn.close()


def test_cosine_distance_operator_and_ordering():
    vec, _ = embedding_service.generate_embedding("problema para resolver nomes dns internos")
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT documento_id, (embedding <=> %s) AS dist
                FROM documento_chunks
                ORDER BY embedding <=> %s ASC
                LIMIT 5;
                """,
                (Vector(vec), Vector(vec))
            )
            rows = cur.fetchall()
            assert len(rows) == 5
            distances = [float(r[1]) for r in rows]
            # Garante ordenação ascendente estrita das distâncias angulares
            assert distances == sorted(distances)
            assert 0.0 <= distances[0] <= 1.0
