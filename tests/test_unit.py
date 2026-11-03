"""
Testes Unitários (Camada de Dados, Camada de Negócio e Validação de Schemas)
Verifica isoladamente a higienização de texto, fragmentação com sobreposição (chunking),
leitura de arquivos JSON/CSV, geração de embeddings 768d e validação Pydantic.
"""

import os
import sys
import numpy as np
import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ingestion_service import clean_text, chunk_text, load_dataset_file
from app.services.embedding_service import embedding_service
from app.models.schemas import SearchRequest, DocumentIngestRequest


def test_clean_text_removes_control_chars_and_multiple_spaces():
    raw = "  Sintoma:\n\n\tComputador   sem   internet\r\n  no Windows.  "
    cleaned = clean_text(raw)
    assert cleaned == "Sintoma: Computador sem internet no Windows."


def test_chunk_text_short_document_single_chunk():
    short_text = "Sintoma: Falha simples de DNS. Solução: Execute ipconfig /flushdns."
    chunks = chunk_text(short_text, max_chars=260, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == short_text


def test_chunk_text_long_document_creates_overlapping_chunks():
    long_text = (
        "Sintoma: O computador exibe status Sem Internet ou endereço IP de autoconfiguração 169.254.x.x na interface. "
        "Causa: Falha na concessão de endereço pelo servidor DHCP corporativo ou corrupção da pilha TCP/IP local. "
        "Solução técnica: Abra o Prompt de Comando como Administrador e execute ipconfig /release seguido de ipconfig /renew e ipconfig /flushdns."
    )
    chunks = chunk_text(long_text, max_chars=180, overlap=40)
    assert len(chunks) >= 2
    for ch in chunks:
        assert len(ch) <= 180
    # Verifica que o conteúdo final do manual está preservado no último fragmento
    assert "ipconfig /flushdns" in chunks[-1]


def test_load_dataset_json_and_csv_equivalence():
    json_docs = load_dataset_file("data/raw/microsoft_faq.json")
    csv_docs = load_dataset_file("data/raw/microsoft_faq.csv")
    assert len(json_docs) == 100
    assert len(csv_docs) == 100
    assert json_docs[0]["id"] == csv_docs[0]["id"]
    assert json_docs[0]["titulo"] == csv_docs[0]["titulo"]
    assert json_docs[0]["categoria"] == csv_docs[0]["categoria"]


def test_embedding_dimension_and_l2_normalization():
    vec, t_emb_ms = embedding_service.generate_embedding("minha internet caiu e nao conecta")
    assert len(vec) == 768
    assert t_emb_ms > 0.0
    norm = float(np.linalg.norm(vec))
    assert abs(norm - 1.0) < 1e-4


def test_semantic_similarity_synonyms_vs_unrelated():
    vec_query, _ = embedding_service.generate_embedding("minha internet parou de funcionar no windows")
    vec_related, _ = embedding_service.generate_embedding("Como resolver falhas de conectividade e IP inválido no Windows")
    vec_unrelated, _ = embedding_service.generate_embedding("Como substituir a fita impressora matricial no almoxarifado")

    sim_related = float(np.dot(vec_query, vec_related))
    sim_unrelated = float(np.dot(vec_query, vec_unrelated))
    assert sim_related > sim_unrelated
    assert sim_related > 0.45


def test_pydantic_search_request_validation():
    with pytest.raises(ValidationError):
        SearchRequest(query="   ", top_n=5)

    with pytest.raises(ValidationError):
        SearchRequest(query="teste", top_n=0)

    with pytest.raises(ValidationError):
        SearchRequest(query="teste", top_n=100)

    valid = SearchRequest(query="  erro de rede  ", top_n=5, categoria="Conectividade")
    assert valid.query == "erro de rede"
    assert valid.top_n == 5


def test_pydantic_document_ingest_request_validation():
    with pytest.raises(ValidationError):
        DocumentIngestRequest(titulo="AB", fonte="Microsoft", categoria="Rede", conteudo="curto")

    valid = DocumentIngestRequest(
        titulo="Manual de Teste de Conectividade",
        fonte="Microsoft",
        categoria="Conectividade",
        conteudo="Sintoma: Falha ao conectar na rede corporativa. Solução: Reinicie o adaptador."
    )
    assert valid.fonte == "Microsoft"
