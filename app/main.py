from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from app.config import settings
from app.models.schemas import SearchRequest, SearchResponse
from app.services.search_service import search_service
from app.database import get_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "API REST para Mecanismo de Busca Semântica em Bases de Conhecimento de Help Desk. "
        "Utiliza representações vetoriais (Sentence-Transformers 768d) persistidas no PostgreSQL com a extensão pgvector e índice HNSW. "
        "Inclui endpoint de busca lexical (PostgreSQL FTS) para validação experimental de Grupo de Controle."
    )
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import FileResponse
import os

@app.get("/", response_class=FileResponse)
def read_root():
    """Interface Web interativa para realização de buscas semânticas e lexicais."""
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    return FileResponse(html_path)

@app.get("/api/info")
def get_api_info():
    """Metadados do projeto acadêmico."""
    return {
        "projeto": settings.PROJECT_NAME,
        "versao": settings.VERSION,
        "autor": "Matheus de Aquino da Silva",
        "instituicao": "UTFPR - Engenharia de Software",
        "orientador": "Prof. Dr. Bruno Honorato",
        "documentacao": "/docs",
        "status": "online"
    }

@app.get("/health")
def health_check():
    """Verifica a integridade da conexão com o banco e da extensão pgvector."""
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

        return {
            "status": "healthy",
            "postgres_pgvector": f"Ativo (versão {vec_version})",
            "total_documentos": total_docs,
            "total_chunks": total_chunks,
            "modelo_embeddings": settings.MODEL_NAME,
            "dimensao_vetorial": settings.EMBEDDING_DIM
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão com infraestrutura: {str(e)}")

@app.post("/search/semantic", response_model=SearchResponse, summary="Busca Semântica Vetorial (HNSW + Cosseno)")
def search_semantic(request: SearchRequest):
    """
    Recebe uma consulta em texto livre, projeta no espaço vetorial de 768d,
    calcula a distância de cosseno (<=>) com índice HNSW no pgvector,
    aplica pré-filtragem relacional opcional e retorna os Top-N resultados ranqueados.
    """
    try:
        response = search_service.semantic_search(
            query=request.query,
            top_n=request.top_n,
            categoria=request.categoria,
            fonte=request.fonte
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento da busca semântica: {str(e)}")

@app.post("/search/lexical", response_model=SearchResponse, summary="Busca Lexical Tradicional (Grupo de Controle)")
def search_lexical(request: SearchRequest):
    """
    Executa busca por correspondência de palavras-chave através do Full-Text Search
    nativo do PostgreSQL, servindo como Grupo de Controle no desenho experimental.
    """
    try:
        response = search_service.lexical_search(
            query=request.query,
            top_n=request.top_n,
            categoria=request.categoria,
            fonte=request.fonte
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento da busca lexical: {str(e)}")

