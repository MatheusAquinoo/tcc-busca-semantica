from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Dict


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Texto livre da consulta do usuário (coloquial ou técnico)")
    top_n: int = Field(default=5, ge=1, le=50, description="Quantidade de resultados no ranqueamento Top-N")
    categoria: Optional[str] = Field(default=None, description="Categoria técnica para pré-filtragem relacional (ex: Conectividade, Autenticação)")
    fonte: Optional[str] = Field(default=None, description="Filtro opcional pelo dataset de origem (Microsoft ou Ubuntu)")
    tag: Optional[str] = Field(default=None, description="Filtro opcional por tag no JSONB de metadados (ex: windows, linux, sysadmin)")
    ef_search: Optional[int] = Field(default=None, ge=1, le=500, description="Parâmetro ef_search do índice HNSW para controle de revocação/latência")
    modo_lexical: str = Field(default="disjuntivo", description="Modo de busca lexical: 'disjuntivo' (OR/ts_rank_cd) ou 'estrito' (AND/plainto_tsquery)")

    @field_validator("query")
    @classmethod
    def query_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("A consulta não pode estar vazia ou conter apenas espaços.")
        return v.strip()


class SearchResultItem(BaseModel):
    chunk_id: int
    documento_id: int
    titulo: str
    fonte: str
    categoria: Optional[str] = None
    conteudo: str
    score: float = Field(..., description="Métrica de relevância (similaridade de cosseno ou ts_rank_cd)")
    distancia_cosseno: Optional[float] = Field(default=None, description="Distância angular de cosseno calculada pelo pgvector")
    metadados: Optional[Dict[str, Any]] = None


class Telemetry(BaseModel):
    t_emb_ms: float = Field(default=0.0, description="Tempo de inferência do modelo vetorial (ms)")
    t_sql_ms: float = Field(..., description="Tempo de execução da query SQL no PostgreSQL (ms)")
    t_total_ms: float = Field(..., description="Latência total de resposta da requisição (ms)")


class SearchResponse(BaseModel):
    query: str
    tipo_busca: str = Field(..., description="'semantica' ou 'lexical'")
    categoria_filtro: Optional[str] = None
    fonte_filtro: Optional[str] = None
    tag_filtro: Optional[str] = None
    total_encontrados: int
    resultados: List[SearchResultItem]
    telemetria: Telemetry


class CompareSearchResponse(BaseModel):
    query: str
    semantica: SearchResponse
    lexical: SearchResponse


class DocumentIngestRequest(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=255, description="Título do manual ou FAQ de suporte técnico")
    fonte: str = Field(..., min_length=2, max_length=50, description="Dataset ou sistema de origem (ex: Microsoft, Ubuntu)")
    categoria: str = Field(..., min_length=2, max_length=50, description="Categoria técnica (ex: Conectividade, Autenticação)")
    conteudo: str = Field(..., min_length=10, description="Conteúdo técnico completo do documento para sanitização e chunking")
    metadados: Optional[Dict[str, Any]] = Field(default=None, description="Metadados complementares opcionais (versão, autor, tags)")


class DocumentIngestResponse(BaseModel):
    documento_id: int
    titulo: str
    fonte: str
    categoria: str
    total_chunks: int
    chunk_ids: List[int]
    t_idx_ms: float
