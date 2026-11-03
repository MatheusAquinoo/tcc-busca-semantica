import threading
import psycopg
from pgvector.psycopg import register_vector
from app.config import settings
from contextlib import contextmanager

_conn_lock = threading.Lock()
_persistent_conn = None

def get_connection():
    """Cria e retorna uma nova conexão com o PostgreSQL registrando o adaptador de vetores."""
    conn = psycopg.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB,
        autocommit=False
    )
    register_vector(conn)
    return conn

def _get_pooled_connection():
    """Retorna uma conexão persistente reutilizável, reconectando automaticamente se necessário."""
    global _persistent_conn
    if _persistent_conn is None or _persistent_conn.closed:
        _persistent_conn = get_connection()
    return _persistent_conn

@contextmanager
def get_db():
    """Gerenciador de contexto thread-safe com reutilização de conexão para baixa latência."""
    global _persistent_conn
    with _conn_lock:
        conn = _get_pooled_connection()
        try:
            yield conn
            conn.commit()
        except psycopg.OperationalError:
            # Reconecta caso a conexão tenha caído
            try:
                conn.close()
            except Exception:
                pass
            _persistent_conn = get_connection()
            conn = _persistent_conn
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
