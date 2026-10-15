import time
import os
import ssl
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from app.config import settings

# Configurações de ambiente para SSL e Hugging Face
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            print(f"[EmbeddingService] Carregando modelo '{settings.MODEL_NAME}' ({settings.EMBEDDING_DIM}d)...")
            cls._model = SentenceTransformer(settings.MODEL_NAME)
            print(f"[EmbeddingService] Modelo carregado com sucesso!")
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        return self._model

    def generate_embedding(self, text: str) -> Tuple[List[float], float]:
        """
        Gera o vetor de embedding para uma consulta em tempo real (RF03/Seção 2.1.2)
        e calcula a latência de inferência T_emb em milissegundos (Seção 2.2.3).
        """
        t_start = time.perf_counter()
        # normalizar para similaridade de cosseno
        embedding = self._model.encode(text, normalize_embeddings=True)
        t_end = time.perf_counter()
        t_emb_ms = (t_end - t_start) * 1000.0
        return embedding.tolist(), round(t_emb_ms, 2)

    def generate_batch_embeddings(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Gera embeddings em lote para otimizar o processo de ingestão de dados.
        """
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True
        )
        return [emb.tolist() for emb in embeddings]

embedding_service = EmbeddingService()

