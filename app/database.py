import psycopg
from pgvector.psycopg import register_vector
from app.config import settings
from contextlib import contextmanager

def get_connection():
    """Cria e retorna uma conexão com o PostgreSQL registrando o adaptador de vetores."""
    conn = psycopg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB
    )
    register_vector(conn)
    return conn

@contextmanager
def get_db():
    """Gerenciador de contexto para transações do banco."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

