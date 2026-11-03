import time
from typing import Optional, List, Dict, Any
from pgvector import Vector

from app.database import get_db
from app.services.embedding_service import embedding_service
from app.models.schemas import SearchResponse, SearchResultItem, Telemetry, CompareSearchResponse


class SearchService:
    def semantic_search(
        self,
        query: str,
        top_n: int = 5,
        categoria: Optional[str] = None,
        fonte: Optional[str] = None,
        tag: Optional[str] = None,
        ef_search: Optional[int] = None
    ) -> SearchResponse:
        """
        Executa a busca semântica vetorial utilizando a distância de cosseno (<=>)
        e o índice HNSW no pgvector, com suporte a pre-filtering relacional e JSONB (RF04, RF06 e RF07).
        """
        # 1. Geração de embedding em tempo real + Telemetria T_emb
        query_vector, t_emb_ms = embedding_service.generate_embedding(query)
        vec_param = Vector(query_vector)

        # 2. Construção da query SQL conforme Seção 2.4 do TCC
        # Busca um conjunto maior de candidatos para deduplicar múltiplos chunks do mesmo documento
        limit_candidates = max(top_n * 6, 30)
        where_clauses = []
        params: Dict[str, Any] = {
            "vetor_consulta": vec_param,
            "limit_candidates": limit_candidates
        }

        if categoria:
            where_clauses.append("c.categoria = %(categoria)s")
            params["categoria"] = categoria

        if fonte:
            where_clauses.append("d.fonte = %(fonte)s")
            params["fonte"] = fonte

        if tag:
            where_clauses.append("c.metadados->'tags' ? %(tag)s")
            params["tag"] = tag.lower()

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        sql = f"""
        SELECT
            c.id AS chunk_id,
            c.documento_id,
            d.titulo,
            d.fonte,
            c.conteudo,
            c.categoria,
            c.metadados,
            (c.embedding <=> %(vetor_consulta)s) AS distancia_cosseno
        FROM documento_chunks c
        JOIN documentos d ON c.documento_id = d.id
        {where_sql}
        ORDER BY c.embedding <=> %(vetor_consulta)s ASC
        LIMIT %(limit_candidates)s;
        """

        # 3. Execução da query no PostgreSQL + Telemetria T_sql
        results: List[SearchResultItem] = []
        seen_doc_ids = set()
        seen_titles = set()

        with get_db() as conn:
            with conn.cursor() as cur:
                t_sql_start = time.perf_counter()
                if ef_search is not None:
                    cur.execute(f"SET LOCAL hnsw.ef_search = {int(ef_search)};")
                cur.execute(sql, params)
                rows = cur.fetchall()
                t_sql_end = time.perf_counter()

                for row in rows:
                    chunk_id, doc_id, titulo, doc_fonte, conteudo, cat, meta, dist = row

                    # Deduplicação por documento: preserva o chunk de maior similaridade semântica
                    if doc_id in seen_doc_ids:
                        continue

                    norm_title = " ".join(titulo.lower().split())
                    if norm_title in seen_titles:
                        continue

                    seen_doc_ids.add(doc_id)
                    seen_titles.add(norm_title)

                    dist_float = float(dist) if dist is not None else 1.0
                    sim_score = round(max(0.0, 1.0 - dist_float), 4)

                    results.append(SearchResultItem(
                        chunk_id=chunk_id,
                        documento_id=doc_id,
                        titulo=titulo,
                        fonte=doc_fonte,
                        categoria=cat,
                        conteudo=conteudo,
                        score=sim_score,
                        distancia_cosseno=round(dist_float, 4),
                        metadados=meta or {}
                    ))

                    if len(results) >= top_n:
                        break

        t_sql_ms = round((t_sql_end - t_sql_start) * 1000.0, 2)
        t_total_ms = round(t_emb_ms + t_sql_ms, 2)

        return SearchResponse(
            query=query,
            tipo_busca="semantica",
            categoria_filtro=categoria,
            fonte_filtro=fonte,
            tag_filtro=tag,
            total_encontrados=len(results),
            resultados=results,
            telemetria=Telemetry(
                t_emb_ms=t_emb_ms,
                t_sql_ms=t_sql_ms,
                t_total_ms=t_total_ms
            )
        )

    def lexical_search(
        self,
        query: str,
        top_n: int = 5,
        categoria: Optional[str] = None,
        fonte: Optional[str] = None,
        tag: Optional[str] = None,
        modo_lexical: str = "disjuntivo"
    ) -> SearchResponse:
        """
        Executa a busca lexical tradicional baseada em palavras-chave
        utilizando Full-Text Search nativo do PostgreSQL (Grupo de Controle - RF05).
        Suporta modo 'estrito' (operador conjuntivo AND via plainto_tsquery)
        e modo 'disjuntivo' (operador OR entre radicais via ts_rank_cd).
        """
        limit_candidates = max(top_n * 6, 30)
        params: Dict[str, Any] = {
            "query": query,
            "query_like": f"%{query}%",
            "limit_candidates": limit_candidates
        }

        extra_filters = []
        if categoria:
            extra_filters.append("c.categoria = %(categoria)s")
            params["categoria"] = categoria

        if fonte:
            extra_filters.append("d.fonte = %(fonte)s")
            params["fonte"] = fonte

        if tag:
            extra_filters.append("c.metadados->'tags' ? %(tag)s")
            params["tag"] = tag.lower()

        extra_where = (" AND " + " AND ".join(extra_filters)) if extra_filters else ""

        if modo_lexical == "estrito":
            sql = f"""
            SELECT
                c.id AS chunk_id,
                c.documento_id,
                d.titulo,
                d.fonte,
                c.conteudo,
                c.categoria,
                c.metadados,
                GREATEST(
                    ts_rank_cd(to_tsvector('portuguese', c.conteudo), plainto_tsquery('portuguese', %(query)s), 32),
                    ts_rank_cd(to_tsvector('english', c.conteudo), plainto_tsquery('english', %(query)s), 32)
                ) AS rank_lexical
            FROM documento_chunks c
            JOIN documentos d ON c.documento_id = d.id
            WHERE (
                to_tsvector('portuguese', c.conteudo) @@ plainto_tsquery('portuguese', %(query)s)
                OR to_tsvector('english', c.conteudo) @@ plainto_tsquery('english', %(query)s)
                OR c.conteudo ILIKE %(query_like)s
            )
            {extra_where}
            ORDER BY rank_lexical DESC, c.id ASC
            LIMIT %(limit_candidates)s;
            """
        else:
            # Modo disjuntivo (padrão FTS): utiliza os índices GIN com tsquery disjuntiva (|) e ts_rank_cd
            sql = f"""
            WITH queries AS (
                SELECT
                    plainto_tsquery('portuguese', %(query)s) AS conj_pt,
                    plainto_tsquery('english', %(query)s) AS conj_en,
                    NULLIF(replace(plainto_tsquery('portuguese', %(query)s)::text, ' & ', ' | '), '')::tsquery AS disj_pt,
                    NULLIF(replace(plainto_tsquery('english', %(query)s)::text, ' & ', ' | '), '')::tsquery AS disj_en
            )
            SELECT
                c.id AS chunk_id,
                c.documento_id,
                d.titulo,
                d.fonte,
                c.conteudo,
                c.categoria,
                c.metadados,
                (
                    COALESCE(ts_rank_cd(to_tsvector('portuguese', c.conteudo), q.disj_pt, 32), 0.0) +
                    COALESCE(ts_rank_cd(to_tsvector('english', c.conteudo), q.disj_en, 32), 0.0) * 0.5 +
                    CASE WHEN to_tsvector('portuguese', c.conteudo) @@ q.conj_pt THEN 0.5 ELSE 0.0 END
                ) AS rank_lexical
            FROM documento_chunks c
            JOIN documentos d ON c.documento_id = d.id
            CROSS JOIN queries q
            WHERE (
                (q.disj_pt IS NOT NULL AND to_tsvector('portuguese', c.conteudo) @@ q.disj_pt)
                OR (q.disj_en IS NOT NULL AND to_tsvector('english', c.conteudo) @@ q.disj_en)
                OR c.conteudo ILIKE %(query_like)s
            )
            {extra_where}
            ORDER BY rank_lexical DESC, c.id ASC
            LIMIT %(limit_candidates)s;
            """

        results: List[SearchResultItem] = []
        seen_doc_ids = set()
        seen_titles = set()

        with get_db() as conn:
            with conn.cursor() as cur:
                t_sql_start = time.perf_counter()
                cur.execute(sql, params)
                rows = cur.fetchall()
                t_sql_end = time.perf_counter()

                for row in rows:
                    chunk_id, doc_id, titulo, doc_fonte, conteudo, cat, meta, rank_score = row

                    if doc_id in seen_doc_ids:
                        continue

                    norm_title = " ".join(titulo.lower().split())
                    if norm_title in seen_titles:
                        continue

                    seen_doc_ids.add(doc_id)
                    seen_titles.add(norm_title)

                    score_val = float(rank_score) if rank_score is not None else 0.0

                    results.append(SearchResultItem(
                        chunk_id=chunk_id,
                        documento_id=doc_id,
                        titulo=titulo,
                        fonte=doc_fonte,
                        categoria=cat,
                        conteudo=conteudo,
                        score=round(score_val, 4),
                        distancia_cosseno=None,
                        metadados=meta or {}
                    ))

                    if len(results) >= top_n:
                        break

        t_sql_ms = round((t_sql_end - t_sql_start) * 1000.0, 2)
        t_total_ms = t_sql_ms

        return SearchResponse(
            query=query,
            tipo_busca="lexical",
            categoria_filtro=categoria,
            fonte_filtro=fonte,
            tag_filtro=tag,
            total_encontrados=len(results),
            resultados=results,
            telemetria=Telemetry(
                t_emb_ms=0.0,
                t_sql_ms=t_sql_ms,
                t_total_ms=t_total_ms
            )
        )

    def compare_search(
        self,
        query: str,
        top_n: int = 5,
        categoria: Optional[str] = None,
        fonte: Optional[str] = None,
        tag: Optional[str] = None,
        ef_search: Optional[int] = None,
        modo_lexical: str = "disjuntivo"
    ) -> CompareSearchResponse:
        """Executa simultaneamente as buscas semântica e lexical para comparação experimental direta."""
        sem = self.semantic_search(query=query, top_n=top_n, categoria=categoria, fonte=fonte, tag=tag, ef_search=ef_search)
        lex = self.lexical_search(query=query, top_n=top_n, categoria=categoria, fonte=fonte, tag=tag, modo_lexical=modo_lexical)
        return CompareSearchResponse(query=query, semantica=sem, lexical=lex)

    def get_categories(self) -> List[Dict[str, Any]]:
        """Retorna todas as categorias técnicas cadastradas com contagem de documentos e fragmentos."""
        sql = """
        SELECT
            c.categoria,
            d.fonte,
            COUNT(DISTINCT d.id) AS total_documentos,
            COUNT(c.id) AS total_chunks
        FROM documento_chunks c
        JOIN documentos d ON c.documento_id = d.id
        GROUP BY c.categoria, d.fonte
        ORDER BY c.categoria, d.fonte;
        """
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        return [
            {
                "categoria": r[0],
                "fonte": r[1],
                "total_documentos": r[2],
                "total_chunks": r[3]
            }
            for r in rows
        ]

    def get_database_stats(self) -> Dict[str, Any]:
        """Coleta estatísticas estruturais das tabelas, índices HNSW/GIN e distribuição da base vetorial."""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM documentos;")
                total_docs = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM documento_chunks;")
                total_chunks = cur.fetchone()[0]

                cur.execute("""
                    SELECT indexname, indexdef, pg_size_pretty(pg_relation_size(indexname::regclass)) AS tamanho
                    FROM pg_indexes
                    WHERE tablename IN ('documentos', 'documento_chunks')
                    ORDER BY indexname;
                """)
                indexes = [
                    {"nome": r[0], "definicao": r[1], "tamanho": r[2]}
                    for r in cur.fetchall()
                ]

                cur.execute("SELECT pg_size_pretty(pg_total_relation_size('documento_chunks'));")
                chunks_table_size = cur.fetchone()[0]

        return {
            "total_documentos": total_docs,
            "total_chunks": total_chunks,
            "media_chunks_por_documento": round(total_chunks / max(total_docs, 1), 2),
            "tamanho_total_tabela_vetorial": chunks_table_size,
            "indices_ativos": indexes,
            "distribuicao_categorias": self.get_categories()
        }

    def list_documents(
        self,
        fonte: Optional[str] = None,
        categoria: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Lista os documentos cadastrados com contagem de fragmentos."""
        where_clauses = []
        params: Dict[str, Any] = {"limit": limit, "offset": offset}
        if fonte:
            where_clauses.append("d.fonte = %(fonte)s")
            params["fonte"] = fonte
        if categoria:
            where_clauses.append("c.categoria = %(categoria)s")
            params["categoria"] = categoria

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
        sql = f"""
        SELECT
            d.id,
            d.titulo,
            d.fonte,
            MAX(c.categoria) AS categoria,
            COUNT(c.id) AS total_chunks
        FROM documentos d
        LEFT JOIN documento_chunks c ON c.documento_id = d.id
        {where_sql}
        GROUP BY d.id, d.titulo, d.fonte
        ORDER BY d.id ASC
        LIMIT %(limit)s OFFSET %(offset)s;
        """
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
        return [
            {
                "id": r[0],
                "titulo": r[1],
                "fonte": r[2],
                "categoria": r[3],
                "total_chunks": r[4]
            }
            for r in rows
        ]

    def get_document_by_id(self, documento_id: int) -> Optional[Dict[str, Any]]:
        """Recupera um documento original pelo ID e todos os seus fragmentos (chunks) indexados."""
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, titulo, fonte FROM documentos WHERE id = %s;", (documento_id,))
                doc_row = cur.fetchone()
                if not doc_row:
                    return None

                cur.execute(
                    """
                    SELECT id, conteudo, categoria, metadados, vector_dims(embedding) AS dimensao
                    FROM documento_chunks
                    WHERE documento_id = %s
                    ORDER BY id ASC;
                    """,
                    (documento_id,)
                )
                chunk_rows = cur.fetchall()

        return {
            "id": doc_row[0],
            "titulo": doc_row[1],
            "fonte": doc_row[2],
            "total_chunks": len(chunk_rows),
            "chunks": [
                {
                    "chunk_id": r[0],
                    "conteudo": r[1],
                    "categoria": r[2],
                    "metadados": r[3],
                    "dimensao_vetor": r[4]
                }
                for r in chunk_rows
            ]
        }


search_service = SearchService()
