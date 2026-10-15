"""
Script de Ingestão, Sanitização, Chunking e Persistência Vetorial (RF01, RF02, RF03)
Conforme especificação da Seção 2.1 e 2.4 do TCC.
"""

import json
import re
import time
import os
import ssl
from typing import List, Dict, Any
from pgvector import Vector

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from app.database import get_db
from app.services.embedding_service import embedding_service

def clean_text(text: str) -> str:
    """Higieniza o texto removendo quebras repetitivas e espaços múltiplos."""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def chunk_text(text: str, max_chars: int = 500, overlap: int = 50) -> List[str]:
    """
    Segmentação estruturada (chunking) com overlapping para preservação
    de fronteiras e contexto local dentro do limite de tokens dos transformers.
    """
    cleaned = clean_text(text)
    if len(cleaned) <= max_chars:
        return [cleaned]

    chunks = []
    start = 0
    while start < len(cleaned):
        end = start + max_chars
        # Tenta quebrar em limite de frase ou palavra
        if end < len(cleaned):
            last_space = cleaned.rfind(' ', start, end)
            if last_space != -1 and last_space > start + 100:
                end = last_space
        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start >= len(cleaned) - overlap:
            break
    return chunks

def run_ingestion():
    print("=" * 60)
    print("INICIANDO PIPELINE DE INGESTÃO E VETORIZAÇÃO (TCC 2)")
    print("=" * 60)

    t_start_total = time.perf_counter()

    # 1. Carregar datasets brutos
    ms_path = "data/raw/microsoft_faq.json"
    ub_path = "data/raw/ubuntu_logs.json"

    with open(ms_path, "r", encoding="utf-8") as f:
        ms_docs = json.load(f)

    with open(ub_path, "r", encoding="utf-8") as f:
        ub_docs = json.load(f)

    all_raw_docs = ms_docs + ub_docs
    print(f"[*] Total de documentos brutos carregados: {len(all_raw_docs)}")

    # 2. Conectar ao PostgreSQL e limpar tabelas anteriores se existirem
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE documento_chunks, documentos RESTART IDENTITY CASCADE;")
            print("[*] Tabelas limpas para nova carga inicial.")

            # Inserir documentos pais
            print("[*] Gravando documentos originais na tabela 'documentos'...")
            for doc in all_raw_docs:
                cur.execute(
                    "INSERT INTO documentos (id, titulo, fonte) VALUES (%s, %s, %s);",
                    (doc["id"], doc["titulo"], doc["fonte"])
                )

    # 3. Processar Chunks
    print("[*] Executando pipeline de sanitização e chunking...")
    chunk_records = []
    texts_to_embed = []

    for doc in all_raw_docs:
        doc_id = doc["id"]
        fonte = doc["fonte"]
        categoria = doc["categoria"]
        conteudo = doc["conteudo"]
        metadados = doc.get("metadados", {})

        chunks = chunk_text(conteudo)
        for idx, ch in enumerate(chunks):
            chunk_meta = dict(metadados)
            chunk_meta["chunk_index"] = idx
            chunk_meta["total_chunks"] = len(chunks)

            chunk_records.append({
                "documento_id": doc_id,
                "conteudo": ch,
                "categoria": categoria,
                "metadados": chunk_meta
            })
            texts_to_embed.append(ch)

    print(f"[*] Gerados {len(chunk_records)} fragmentos (chunks) estruturados a partir dos {len(all_raw_docs)} documentos.")

    # 4. Geração de Embeddings em Lote (Sentence-Transformers 768d)
    print(f"[*] Computando embeddings com o modelo {embedding_service.model.tokenizer.name_or_path}...")
    t_emb_start = time.perf_counter()
    embeddings = embedding_service.generate_batch_embeddings(texts_to_embed, batch_size=32)
    t_emb_end = time.perf_counter()
    print(f"[OK] {len(embeddings)} vetores densos (768d) gerados em {t_emb_end - t_emb_start:.2f}s.")

    # 5. Persistência no PostgreSQL com pgvector
    print("[*] Inserindo fragmentos e vetores na tabela 'documento_chunks'...")
    with get_db() as conn:
        with conn.cursor() as cur:
            for rec, emb in zip(chunk_records, embeddings):
                cur.execute(
                    """
                    INSERT INTO documento_chunks (documento_id, conteudo, embedding, categoria, metadados)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (
                        rec["documento_id"],
                        rec["conteudo"],
                        Vector(emb),
                        rec["categoria"],
                        json.dumps(rec["metadados"])
                    )
                )

    t_end_total = time.perf_counter()
    t_idx_total = t_end_total - t_start_total

    print("=" * 60)
    print(f"INGESTÃO CONCLUÍDA COM SUCESSO!")
    print(f"- Custo Temporal de Indexação (T_idx): {t_idx_total:.2f} segundos")
    print(f"- Total de documentos indexados: {len(all_raw_docs)}")
    print(f"- Total de chunks persistidos no pgvector: {len(chunk_records)}")
    print("=" * 60)

if __name__ == "__main__":
    run_ingestion()
