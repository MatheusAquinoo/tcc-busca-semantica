import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.embedding_service import embedding_service

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

def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["dimensao_vetorial"] == 768
    assert data["total_documentos"] >= 200
    assert data["total_chunks"] >= 200

def test_embedding_vector_dimension():
    vec, t_emb = embedding_service.generate_embedding("teste de dimensao vetorial")
    assert len(vec) == 768
    assert t_emb >= 0.0

def test_semantic_search_endpoint():
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
    assert data["telemetria"]["t_sql_ms"] > 0
    # O primeiro resultado deve ter score coerente
    assert data["resultados"][0]["score"] > 0.0

def test_semantic_search_with_category_prefiltering():
    payload = {
        "query": "como redefinir a senha do usuario no active directory",
        "top_n": 3,
        "categoria": "Autenticação"
    }
    response = client.post("/search/semantic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["categoria_filtro"] == "Autenticação"
    for item in data["resultados"]:
        assert item["categoria"] == "Autenticação"

def test_lexical_search_endpoint():
    payload = {
        "query": "ipconfig",
        "top_n": 5
    }
    response = client.post("/search/lexical", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tipo_busca"] == "lexical"
    assert data["telemetria"]["t_emb_ms"] == 0.0
    assert data["telemetria"]["t_sql_ms"] >= 0.0
