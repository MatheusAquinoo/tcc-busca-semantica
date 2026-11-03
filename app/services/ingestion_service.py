"""
Subsistema de Ingestão e Processamento de Dados (Camada de Dados - RF01, RF02, RF03)
Responsável pela extração de arquivos brutos (JSON/CSV), sanitização de texto,
fragmentação estruturada com sobreposição (overlapping chunking) e persistência vetorial.
"""

import csv
import json
import os
import re
import time
from typing import List, Dict, Any, Optional
from pgvector import Vector

from app.database import get_db
from app.services.embedding_service import embedding_service


def clean_text(text: str) -> str:
    """
    Higieniza o texto removendo caracteres de controle, quebras de linha
    repetitivas e múltiplos espaços consecutivos (Seção 2.1.1 - Sanitização).
    """
    if not text:
        return ""
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def chunk_text(text: str, max_chars: int = 260, overlap: int = 50) -> List[str]:
    """
    Segmentação estruturada (chunking) com sobreposição (overlapping) para
    preservação de fronteiras semânticas e contexto local (RF02 / Seção 2.1.1).
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []
    if len(cleaned) <= max_chars:
        return [cleaned]

    chunks: List[str] = []
    start = 0
    text_len = len(cleaned)

    while start < text_len:
        end = min(start + max_chars, text_len)
        if end < text_len:
            # Prioriza quebra em fim de sentença (. ) ou espaço para não truncar palavras
            sentence_break = cleaned.rfind('. ', start + int(max_chars * 0.5), end)
            if sentence_break != -1:
                end = sentence_break + 1
            else:
                space_break = cleaned.rfind(' ', start + int(max_chars * 0.4), end)
                if space_break != -1:
                    end = space_break

        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        next_start = max(0, end - overlap)
        # Ajusta o início do overlap para o próximo espaço para não iniciar no meio de uma palavra
        if next_start > start:
            first_space = cleaned.find(' ', next_start, min(next_start + 25, end))
            if first_space != -1:
                next_start = first_space + 1
        if next_start <= start:
            next_start = end
        start = next_start

    return chunks


def load_dataset_file(filepath: str) -> List[Dict[str, Any]]:
    """
    Realiza a leitura e extração de datasets técnicos nos formatos JSON ou CSV (RF01).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo de dataset não encontrado: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    elif ext == ".csv":
        records: List[Dict[str, Any]] = []
        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                meta = row.get("metadados", "{}")
                if isinstance(meta, str):
                    try:
                        meta = json.loads(meta)
                    except Exception:
                        meta = {}
                records.append({
                    "id": int(row["id"]) if row.get("id") else None,
                    "titulo": row["titulo"],
                    "fonte": row["fonte"],
                    "categoria": row.get("categoria"),
                    "conteudo": row["conteudo"],
                    "metadados": meta
                })
        return records
    else:
        raise ValueError(f"Formato de arquivo não suportado ({ext}). Utilize .json ou .csv.")


class IngestionService:
    def ingest_single_document(
        self,
        titulo: str,
        fonte: str,
        categoria: str,
        conteudo: str,
        metadados: Optional[Dict[str, Any]] = None,
        max_chars: int = 260,
        overlap: int = 50
    ) -> Dict[str, Any]:
        """
        Ingere um único documento técnico em tempo real via API:
        higieniza, aplica chunking com overlap, gera embeddings (768d) e persiste no PostgreSQL.
        """
        t_start = time.perf_counter()
        cleaned_title = clean_text(titulo)
        chunks = chunk_text(conteudo, max_chars=max_chars, overlap=overlap)
        if not chunks:
            raise ValueError("O conteúdo do documento não pode ser vazio após sanitização.")

        # Contextualiza cada fragmento com o título do manual para preservar o tópico na projeção vetorial
        texts_to_embed = [f"{cleaned_title}. {ch}" for ch in chunks]
        embeddings = [embedding_service.generate_embedding(t)[0] for t in texts_to_embed]

        base_meta = dict(metadados) if metadados else {}
        if "tags" not in base_meta:
            base_meta["tags"] = [categoria.lower(), fonte.lower(), "helpdesk"]

        chunk_ids: List[int] = []
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO documentos (titulo, fonte) VALUES (%s, %s) RETURNING id;",
                    (cleaned_title, fonte)
                )
                doc_id = cur.fetchone()[0]

                for idx, (ch_text, emb) in enumerate(zip(chunks, embeddings)):
                    ch_meta = dict(base_meta)
                    ch_meta["doc_id"] = doc_id
                    ch_meta["chunk_index"] = idx
                    ch_meta["total_chunks"] = len(chunks)

                    cur.execute(
                        """
                        INSERT INTO documento_chunks (documento_id, conteudo, embedding, categoria, metadados)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id;
                        """,
                        (doc_id, ch_text, Vector(emb), categoria, json.dumps(ch_meta, ensure_ascii=False))
                    )
                    chunk_ids.append(cur.fetchone()[0])

        t_idx_ms = round((time.perf_counter() - t_start) * 1000.0, 2)
        return {
            "documento_id": doc_id,
            "titulo": cleaned_title,
            "fonte": fonte,
            "categoria": categoria,
            "total_chunks": len(chunks),
            "chunk_ids": chunk_ids,
            "t_idx_ms": t_idx_ms
        }


ingestion_service = IngestionService()
