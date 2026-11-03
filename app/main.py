import os
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.models.schemas import (
    SearchRequest,
    SearchResponse,
    CompareSearchResponse,
    DocumentIngestRequest,
    DocumentIngestResponse,
)
from app.services.search_service import search_service
from app.services.ingestion_service import ingestion_service
from app.database import get_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "API REST para Mecanismo de Busca Semântica em Bases de Conhecimento de Help Desk (TCC 2 - UTFPR). "
        "Utiliza representações vetoriais densas (Sentence-Transformers 768d) persistidas no PostgreSQL 16 com a extensão pgvector e índice HNSW. "
        "Inclui pipeline de ingestão/chunking (RF01-RF03), busca semântica híbrida com pré-filtragem relacional (RF04, RF06, RF07) "
        "e motor de busca lexical via PostgreSQL Full-Text Search (RF05 - Grupo de Controle)."
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=FileResponse, tags=["Interface Web"])
def read_root():
    """Interface Web interativa para realização de buscas semânticas, lexicais e comparativas."""
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    return FileResponse(html_path)


@app.get("/api/info", tags=["Infraestrutura e Monitoramento"])
def get_api_info():
    """Metadados institucionais e arquiteturais do projeto acadêmico."""
    return {
        "projeto": settings.PROJECT_NAME,
        "versao": settings.VERSION,
        "autor": "Matheus de Aquino da Silva",
        "instituicao": "Universidade Tecnológica Federal do Paraná (UTFPR) - Engenharia de Software",
        "orientador": "Prof. Dr. Bruno Honorato",
        "modelo_embeddings": settings.MODEL_NAME,
        "dimensao_vetorial": settings.EMBEDDING_DIM,
        "documentacao": "/docs",
        "status": "online"
    }


@app.get("/health", tags=["Infraestrutura e Monitoramento"])
def health_check():
    """Verifica a integridade da conexão com o PostgreSQL, da extensão pgvector e dos índices HNSW/GIN."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
                row = cur.fetchone()
                if not row:
                    raise Exception("Extensão vector não encontrada no banco.")
                vec_version = row[0]

                cur.execute("SELECT COUNT(*) FROM documentos;")
                total_docs = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM documento_chunks;")
                total_chunks = cur.fetchone()[0]

                cur.execute("""
                    SELECT indexname FROM pg_indexes
                    WHERE tablename = 'documento_chunks'
                    ORDER BY indexname;
                """)
                indexes = [r[0] for r in cur.fetchall()]

        return {
            "status": "healthy",
            "postgres_pgvector": f"Ativo (versão {vec_version})",
            "total_documentos": total_docs,
            "total_chunks": total_chunks,
            "indices_ativos": indexes,
            "modelo_embeddings": settings.MODEL_NAME,
            "dimensao_vetorial": settings.EMBEDDING_DIM
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com infraestrutura: {str(e)}")


@app.get("/categories", tags=["Persistência e Catálogo"])
def list_categories():
    """Lista todas as categorias técnicas disponíveis para pré-filtragem relacional (RF07)."""
    try:
        return {
            "categorias": search_service.get_categories()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar categorias: {str(e)}")


@app.get("/stats", tags=["Infraestrutura e Monitoramento"])
def get_stats():
    """Retorna estatísticas detalhadas do banco de dados, tamanho físico das tabelas e índices HNSW/GIN."""
    try:
        return search_service.get_database_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao coletar estatísticas do banco: {str(e)}")


@app.get("/documents", tags=["Persistência e Catálogo"])
def list_documents(
    fonte: Optional[str] = Query(default=None, description="Filtrar por fonte (Microsoft ou Ubuntu)"),
    categoria: Optional[str] = Query(default=None, description="Filtrar por categoria técnica"),
    limit: int = Query(default=50, ge=1, le=200, description="Quantidade máxima de registros"),
    offset: int = Query(default=0, ge=0, description="Deslocamento para paginação")
):
    """Lista os documentos técnicos armazenados na tabela 'documentos' com contagem de chunks."""
    try:
        docs = search_service.list_documents(fonte=fonte, categoria=categoria, limit=limit, offset=offset)
        return {
            "total_retornados": len(docs),
            "documentos": docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar documentos: {str(e)}")


@app.get("/documents/{documento_id}", tags=["Persistência e Catálogo"])
def get_document(documento_id: int):
    """Recupera um documento original pelo ID e todos os seus fragmentos (chunks) na tabela 'documento_chunks'."""
    doc = search_service.get_document_by_id(documento_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Documento com id={documento_id} não encontrado.")
    return doc


@app.post(
    "/documents/ingest",
    response_model=DocumentIngestResponse,
    status_code=201,
    summary="Ingestão, Chunking e Vetorização de Documento (RF01, RF02, RF03)",
    tags=["Persistência e Catálogo"]
)
def ingest_document(request: DocumentIngestRequest):
    """
    Recebe um novo documento técnico, executa a higienização de texto, fragmentação
    estruturada com sobreposição (chunking), geração de embeddings de 768 dimensões
    e persistência transacional nas tabelas 'documentos' e 'documento_chunks'.
    """
    try:
        result = ingestion_service.ingest_single_document(
            titulo=request.titulo,
            fonte=request.fonte,
            categoria=request.categoria,
            conteudo=request.conteudo,
            metadados=request.metadados
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na ingestão do documento: {str(e)}")


@app.post(
    "/search/semantic",
    response_model=SearchResponse,
    summary="Busca Semântica Vetorial (HNSW + Cosseno + Pre-filtering - RF04, RF06, RF07)",
    tags=["Motores de Busca"]
)
def search_semantic(request: SearchRequest):
    """
    Recebe uma consulta em texto livre, projeta no espaço vetorial de 768d,
    calcula a distância de cosseno (<=>) com índice HNSW no pgvector,
    aplica pré-filtragem relacional opcional e retorna os Top-N resultados ranqueados.
    """
    try:
        return search_service.semantic_search(
            query=request.query,
            top_n=request.top_n,
            categoria=request.categoria,
            fonte=request.fonte,
            tag=request.tag,
            ef_search=request.ef_search
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento da busca semântica: {str(e)}")


@app.post(
    "/search/lexical",
    response_model=SearchResponse,
    summary="Busca Lexical Tradicional (PostgreSQL FTS - Grupo de Controle RF05)",
    tags=["Motores de Busca"]
)
def search_lexical(request: SearchRequest):
    """
    Executa busca por correspondência de palavras-chave através do Full-Text Search
    nativo do PostgreSQL (índices GIN + ts_rank_cd), servindo como Grupo de Controle no desenho experimental.
    """
    try:
        return search_service.lexical_search(
            query=request.query,
            top_n=request.top_n,
            categoria=request.categoria,
            fonte=request.fonte,
            tag=request.tag,
            modo_lexical=request.modo_lexical
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento da busca lexical: {str(e)}")


@app.post(
    "/search/compare",
    response_model=CompareSearchResponse,
    summary="Comparação Experimental Lado a Lado (Semântica vs Lexical)",
    tags=["Motores de Busca"]
)
def search_compare(request: SearchRequest):
    """
    Executa simultaneamente os motores de busca semântica (pgvector HNSW) e lexical (PostgreSQL FTS)
    para uma mesma consulta e retorna ambos os rankings e telemetrias de latência.
    """
    try:
        return search_service.compare_search(
            query=request.query,
            top_n=request.top_n,
            categoria=request.categoria,
            fonte=request.fonte,
            tag=request.tag,
            ef_search=request.ef_search,
            modo_lexical=request.modo_lexical
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na comparação de buscas: {str(e)}")
