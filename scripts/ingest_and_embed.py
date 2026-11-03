"""
Script de Ingestão, Sanitização, Chunking e Persistência Vetorial (RF01, RF02, RF03)
Conforme especificação das Seções 2.1, 2.2.3 e 2.4 do TCC.
"""

import json
import time
import os
import sys
from pgvector import Vector

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from app.database import get_db
from app.services.embedding_service import embedding_service
from app.services.ingestion_service import clean_text, chunk_text, load_dataset_file


def run_ingestion(max_chars: int = 260, overlap: int = 50):
    print("=" * 65)
    print("INICIANDO PIPELINE DE INGESTÃO E VETORIZAÇÃO (TCC 2)")
    print("=" * 65)

    t_start_total = time.perf_counter()

    # 1. Carregar datasets brutos (suporta JSON e CSV conforme RF01)
    t_prep_start = time.perf_counter()
    ms_path = "data/raw/microsoft_faq.json"
    ub_path = "data/raw/ubuntu_logs.csv" if os.path.exists("data/raw/ubuntu_logs.csv") else "data/raw/ubuntu_logs.json"

    ms_docs = load_dataset_file(ms_path)
    ub_docs = load_dataset_file(ub_path)

    all_raw_docs = ms_docs + ub_docs
    print(f"[*] Total de documentos brutos carregados: {len(all_raw_docs)} (Microsoft JSON + Ubuntu CSV/JSON)")

    # 2. Processar Sanitização e Chunking com Overlap (RF02)
    print(f"[*] Executando pipeline de sanitização e chunking (max_chars={max_chars}, overlap={overlap})...")
    chunk_records = []
    texts_to_embed = []

    for doc in all_raw_docs:
        doc_id = int(doc["id"])
        titulo = clean_text(doc["titulo"])
        categoria = doc["categoria"]
        conteudo = doc["conteudo"]
        metadados = doc.get("metadados", {})

        chunks = chunk_text(conteudo, max_chars=max_chars, overlap=overlap)
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
            # Contextualiza cada chunk com o título do documento técnico
            texts_to_embed.append(f"{titulo}. {ch}")

    t_prep_end = time.perf_counter()
    t_prep_s = round(t_prep_end - t_prep_start, 4)
    print(f"[*] Gerados {len(chunk_records)} fragmentos (chunks) estruturados a partir dos {len(all_raw_docs)} documentos em {t_prep_s:.2f}s.")

    # 3. Geração de Embeddings em Lote (Sentence-Transformers 768d - RF03)
    print(f"[*] Computando embeddings (768d) em lote com Sentence-Transformers...")
    t_emb_start = time.perf_counter()
    embeddings = embedding_service.generate_batch_embeddings(texts_to_embed, batch_size=32)
    t_emb_end = time.perf_counter()
    t_emb_batch_s = round(t_emb_end - t_emb_start, 4)
    print(f"[OK] {len(embeddings)} vetores densos (768d) gerados em {t_emb_batch_s:.2f}s.")

    # 4. Persistência Relacional e Vetorial no PostgreSQL com pgvector (Seção 2.4)
    print("[*] Persistindo documentos, fragmentos e reconstruindo índices no PostgreSQL...")
    t_db_start = time.perf_counter()
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE documento_chunks, documentos RESTART IDENTITY CASCADE;")

            for doc in all_raw_docs:
                cur.execute(
                    "INSERT INTO documentos (id, titulo, fonte) VALUES (%s, %s, %s);",
                    (int(doc["id"]), clean_text(doc["titulo"]), doc["fonte"])
                )
            # Sincroniza a sequence da chave primária SERIAL da tabela documentos
            cur.execute("SELECT setval(pg_get_serial_sequence('documentos', 'id'), (SELECT MAX(id) FROM documentos));")

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
                        json.dumps(rec["metadados"], ensure_ascii=False)
                    )
                )
            cur.execute("ANALYZE documentos;")
            cur.execute("ANALYZE documento_chunks;")

    t_db_end = time.perf_counter()
    t_db_s = round(t_db_end - t_db_start, 4)
    t_idx_total = round(t_db_end - t_start_total, 4)

    os.makedirs("results", exist_ok=True)
    telemetry_idx = {
        "total_documentos": len(all_raw_docs),
        "total_chunks": len(chunk_records),
        "media_chunks_por_documento": round(len(chunk_records) / len(all_raw_docs), 2),
        "max_chars": max_chars,
        "overlap": overlap,
        "t_prep_segundos": t_prep_s,
        "t_emb_batch_segundos": t_emb_batch_s,
        "t_db_persist_segundos": t_db_s,
        "t_idx_total_segundos": t_idx_total
    }
    with open("results/indexing_telemetry.json", "w", encoding="utf-8") as f:
        json.dump(telemetry_idx, f, indent=2, ensure_ascii=False)

    print("=" * 65)
    print("INGESTÃO CONCLUÍDA COM SUCESSO!")
    print(f"- Tempo de Extração e Chunking: {t_prep_s:.2f} s")
    print(f"- Tempo de Vetorização em Lote (768d): {t_emb_batch_s:.2f} s")
    print(f"- Tempo de Persistência SQL + Índice HNSW: {t_db_s:.2f} s")
    print(f"- Custo Temporal Total de Indexação (T_idx): {t_idx_total:.2f} s")
    print(f"- Total de documentos indexados: {len(all_raw_docs)}")
    print(f"- Total de chunks persistidos no pgvector: {len(chunk_records)}")
    print("=" * 65)
    return telemetry_idx


if __name__ == "__main__":
    run_ingestion()
