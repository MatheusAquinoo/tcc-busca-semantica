import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Mecanismo de Busca Semântica - TCC UTFPR"
    VERSION: str = "1.0.0"
    
    # Banco de Dados PostgreSQL + pgvector
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgrespassword")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "helpdesk_db")
    
    # Modelo Sentence-Transformers (768 dimensões conforme especificado no TCC)
    MODEL_NAME: str = os.getenv("MODEL_NAME", "paraphrase-multilingual-mpnet-base-v2")
    EMBEDDING_DIM: int = 768
    
    # Configuração de Busca
    DEFAULT_TOP_N: int = 5
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()

