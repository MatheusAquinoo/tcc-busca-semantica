import time
from typing import Optional, List, Dict, Any
import numpy as np
from pgvector import Vector

from app.database import get_db
from app.services.embedding_service import embedding_service
from app.models.schemas import SearchResponse, SearchResultItem, Telemetry

class SearchService:
    def semantic_search(
        self,
        query: str,
        top_n: int = 5,
        categoria: Optional[str] = None,
        fonte: Optional[str] = None
    ) -> SearchResponse:
        """
        Executa a busca semântica vetorial utilizando a distância de cosseno (<=>)
        e o índice HNSW no pgvector, com suporte a pre-filtering relacional (RF04 e RF07).
        """
        # 1. Geração de embedding em tempo real + Telemetria T_emb
        query_vector, t_emb_ms = embedding_service.generate_embedding(query)
        vec_param = Vector(query_vector)

        # 2. Construção da query SQL conforme Seção 2.4 do PDF
        # Puxa um conjunto maior de candidatos para aplicar deduplicação de chunks/documentos repetidos
        limit_candidates = max(top_n * 4, 25)
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
        t_sql_start = time.perf_counter()
        results: List[SearchResultItem] = []
        seen_doc_ids = set()
        seen_titles = set()

        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
                for row in rows:
                    chunk_id, doc_id, titulo, doc_fonte, conteudo, cat, meta, dist = row

                    # Deduplicação: se já temos o melhor chunk desse documento no Top-N, ignora os demais
                    if doc_id in seen_doc_ids:
                        continue
                    
                    # Normalização simples de título para desduplicar problemas gêmeos
                    norm_title = " ".join(titulo.lower().split())
                    if norm_title in seen_titles:
                        continue

                    seen_doc_ids.add(doc_id)
                    seen_titles.add(norm_title)

                    # Similaridade de cosseno normalizada: [0, 1] onde 1.0 é identidade
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

        t_sql_end = time.perf_counter()
        t_sql_ms = round((t_sql_end - t_sql_start) * 1000.0, 2)
        t_total_ms = round(t_emb_ms + t_sql_ms, 2)

        return SearchResponse(
            query=query,
            tipo_busca="semantica",
            categoria_filtro=categoria,
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
        fonte: Optional[str] = None
    ) -> SearchResponse:
        """
        Executa a busca lexical tradicional baseada em palavras-chave
        utilizando Full-Text Search nativo do PostgreSQL (Grupo de Controle - RF05).
        """
        limit_candidates = max(top_n * 4, 25)
        where_clauses = [
            "(to_tsvector('portuguese', c.conteudo) @@ plainto_tsquery('portuguese', %(query)s) "
            "OR to_tsvector('english', c.conteudo) @@ plainto_tsquery('english', %(query)s) "
            "OR c.conteudo ILIKE %(query_like)s)"
        ]
        params: Dict[str, Any] = {
            "query": query,
            "query_like": f"%{query}%",
            "limit_candidates": limit_candidates
        }

        if categoria:
            where_clauses.append("c.categoria = %(categoria)s")
            params["categoria"] = categoria

        if fonte:
            where_clauses.append("d.fonte = %(fonte)s")
            params["fonte"] = fonte

        where_sql = "WHERE " + " AND ".join(where_clauses)

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
                ts_rank(to_tsvector('portuguese', c.conteudo), plainto_tsquery('portuguese', %(query)s)),
                ts_rank(to_tsvector('english', c.conteudo), plainto_tsquery('english', %(query)s))
            ) AS rank_lexical
        FROM documento_chunks c
        JOIN documentos d ON c.documento_id = d.id
        {where_sql}
        ORDER BY rank_lexical DESC, c.id ASC
        LIMIT %(limit_candidates)s;
        """

        t_sql_start = time.perf_counter()
        results: List[SearchResultItem] = []
        seen_doc_ids = set()
        seen_titles = set()

        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                rows = cur.fetchall()
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

        t_sql_end = time.perf_counter()
        t_sql_ms = round((t_sql_end - t_sql_start) * 1000.0, 2)
        # Na busca lexical pura, T_emb é zero
        t_total_ms = t_sql_ms

        return SearchResponse(
            query=query,
            tipo_busca="lexical",
            categoria_filtro=categoria,
            total_encontrados=len(results),
            resultados=results,
            telemetria=Telemetry(
                t_emb_ms=0.0,
                t_sql_ms=t_sql_ms,
                t_total_ms=t_total_ms
            )
        )

search_service = SearchService()

