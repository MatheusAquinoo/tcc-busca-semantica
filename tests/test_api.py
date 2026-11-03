"""
Testes de Sistema e Integração de Endpoints da API (FastAPI TestClient)
Valida todos os contratos REST de busca semântica, busca lexical, comparação,
catálogo de documentos, categorias, ingestão dinâmica e monitoramento de saúde.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Busca Semântica" in response.text
    assert "UTFPR" in response.text


def test_api_info_endpoint():
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Matheus de Aquino da Silva" in data["autor"]
    assert data["dimensao_vetorial"] == 768


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dimensao_vetorial"] == 768
    assert data["total_documentos"] == 200
    assert data["total_chunks"] >= 400
    assert "idx_chunks_embedding_hnsw" in data["indices_ativos"]


def test_categories_and_stats_endpoints():
    cat_res = client.get("/categories")
    assert cat_res.status_code == 200
    categorias = cat_res.json()["categorias"]
    assert len(categorias) >= 10

    stats_res = client.get("/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_documentos"] == 200
    assert stats["total_chunks"] >= 400
    assert stats["media_chunks_por_documento"] >= 2.0


def test_documents_listing_and_detail_endpoints():
    list_res = client.get("/documents?fonte=Microsoft&limit=10")
    assert list_res.status_code == 200
    docs = list_res.json()["documentos"]
    assert len(docs) == 10
    assert all(d["fonte"] == "Microsoft" for d in docs)

    doc_res = client.get("/documents/1")
    assert doc_res.status_code == 200
    doc_detail = doc_res.json()
    assert doc_detail["id"] == 1
    assert doc_detail["total_chunks"] >= 1
    assert doc_detail["chunks"][0]["dimensao_vetor"] == 768

    not_found = client.get("/documents/99999")
    assert not_found.status_code == 404


def test_semantic_search_endpoint_and_deduplication():
    payload = {
        "query": "minha internet caiu e o ip comecou com 169",
        "top_n": 5
    }
    response = client.post("/search/semantic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tipo_busca"] == "semantica"
    assert len(data["resultados"]) == 5
    assert data["telemetria"]["t_total_ms"] > 0
    assert data["telemetria"]["t_emb_ms"] > 0
    assert data["telemetria"]["t_sql_ms"] >= 0
    assert data["resultados"][0]["score"] > 0.5
    # Verifica que não há documentos duplicados no Top-5
    doc_ids = [r["documento_id"] for r in data["resultados"]]
    assert len(doc_ids) == len(set(doc_ids))
    # O documento 1 (IP 169.254.x.x / DHCP) deve estar no topo
    assert 1 in doc_ids[:2]


def test_semantic_search_with_category_and_tag_prefiltering():
    payload = {
        "query": "como redefinir a senha do usuario no active directory",
        "top_n": 3,
        "categoria": "Autenticação",
        "fonte": "Microsoft",
        "tag": "windows",
        "ef_search": 64
    }
    response = client.post("/search/semantic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["categoria_filtro"] == "Autenticação"
    assert data["fonte_filtro"] == "Microsoft"
    assert data["tag_filtro"] == "windows"
    for item in data["resultados"]:
        assert item["categoria"] == "Autenticação"
        assert item["fonte"] == "Microsoft"


def test_lexical_search_modes():
    # Modo disjuntivo (padrão FTS)
    payload_disj = {
        "query": "como conectar na vpn da empresa no windows",
        "top_n": 5,
        "modo_lexical": "disjuntivo"
    }
    res_disj = client.post("/search/lexical", json=payload_disj)
    assert res_disj.status_code == 200
    data_disj = res_disj.json()
    assert data_disj["tipo_busca"] == "lexical"
    assert data_disj["telemetria"]["t_emb_ms"] == 0.0
    assert len(data_disj["resultados"]) > 0

    # Modo estrito (conjuntivo AND) com termo exato
    payload_estrito = {
        "query": "ipconfig",
        "top_n": 5,
        "modo_lexical": "estrito"
    }
    res_estrito = client.post("/search/lexical", json=payload_estrito)
    assert res_estrito.status_code == 200
    assert len(res_estrito.json()["resultados"]) >= 1


def test_compare_search_endpoint():
    payload = {
        "query": "computador travado com disco em 100 porcento",
        "top_n": 5
    }
    response = client.post("/search/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "semantica" in data
    assert "lexical" in data
    assert data["semantica"]["tipo_busca"] == "semantica"
    assert data["lexical"]["tipo_busca"] == "lexical"


def test_document_ingest_endpoint_lifecycle():
    payload = {
        "titulo": "Diagnóstico de Erro de Certificado SSL Interno no Nginx",
        "fonte": "Ubuntu",
        "categoria": "Segurança",
        "conteudo": (
            "Sintoma: Navegador exibe alerta NET::ERR_CERT_AUTHORITY_INVALID ao acessar intranet. "
            "Causa: Certificado raiz da autoridade certificadora interna ausente no repositório confiável. "
            "Solução: Copie o arquivo ca-corporativa.crt para /usr/local/share/ca-certificates/ e execute sudo update-ca-certificates."
        ),
        "metadados": {"versao": "Ubuntu 24.04", "autor": "Teste Automatizado"}
    }
    res = client.post("/documents/ingest", json=payload)
    assert res.status_code == 201
    ingested = res.json()
    new_doc_id = ingested["documento_id"]
    assert ingested["total_chunks"] >= 1
    assert ingested["t_idx_ms"] > 0

    # Limpa o documento de teste inserido para preservar os 200 documentos do experimento
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM documentos WHERE id = %s;", (new_doc_id,))
            cur.execute("SELECT setval(pg_get_serial_sequence('documentos', 'id'), (SELECT MAX(id) FROM documentos));")
